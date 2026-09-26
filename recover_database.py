import os
import sqlite3
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "college_erp.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection, transaction

SQLITE_DB = r"D:\college_erp\db_recovered_WORKING.sqlite3"

User = get_user_model()


def sqlite_rows(db, table):
    cur = db.execute(f'SELECT * FROM "{table}"')
    columns = [x[0] for x in cur.description]
    return columns, cur.fetchall()


def pg_columns(table):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
            ORDER BY ordinal_position
        """, [table])

        return [r[0] for r in cur.fetchall()]


def pg_boolean_columns(table):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
              AND data_type = 'boolean'
        """, [table])

        return {r[0] for r in cur.fetchall()}


def pg_user_fk_columns(table):
    """
    Find every PostgreSQL foreign-key column in this table
    that references public.accounts_user.

    Uses PostgreSQL system catalogs directly.
    """

    with connection.cursor() as cur:
        cur.execute("""
            SELECT DISTINCT a.attname
            FROM pg_constraint con
            JOIN pg_class tbl
                ON tbl.oid = con.conrelid
            JOIN pg_namespace tbl_ns
                ON tbl_ns.oid = tbl.relnamespace
            JOIN pg_class ref_tbl
                ON ref_tbl.oid = con.confrelid
            JOIN pg_namespace ref_ns
                ON ref_ns.oid = ref_tbl.relnamespace
            JOIN LATERAL unnest(con.conkey) AS key_col(attnum)
                ON TRUE
            JOIN pg_attribute a
                ON a.attrelid = tbl.oid
               AND a.attnum = key_col.attnum
            WHERE con.contype = 'f'
              AND tbl_ns.nspname = 'public'
              AND ref_ns.nspname = 'public'
              AND tbl.relname = %s
              AND ref_tbl.relname = 'accounts_user'
        """, [table])

        columns = {r[0] for r in cur.fetchall()}

    # Explicitly include this known FK from the recovered database.
    if table == "students_student":
        columns.add("user_id")

    return columns


def copy_table(db, table, user_map):
    old_columns, old_rows = sqlite_rows(db, table)

    if not old_rows:
        print(f"{table}: 0")
        return

    current_columns = pg_columns(table)

    columns = [
        c for c in old_columns
        if c in current_columns
    ]

    if not columns:
        print(f"{table}: skipped - no matching columns")
        return

    user_columns = pg_user_fk_columns(table)
    boolean_columns = pg_boolean_columns(table)

    print(
        f"{table}: user FK columns -> "
        f"{sorted(user_columns) if user_columns else 'none'}"
    )

    processed = []

    for row_number, row in enumerate(old_rows, start=1):
        row = list(row)

        # ---------------------------------------------------------
        # TRANSLATE OLD auth_user IDs TO CURRENT accounts_user IDs
        # ---------------------------------------------------------
        for col in user_columns:

            if col not in columns:
                continue

            i = columns.index(col)
            old_user_id = row[i]

            if old_user_id is None:
                continue

            new_user_id = user_map.get(old_user_id)

            if new_user_id is None:
                raise RuntimeError(
                    f"{table} row {row_number}: "
                    f"cannot map old user ID {old_user_id} "
                    f"from column '{col}' to accounts_user."
                )

            row[i] = new_user_id

        # ---------------------------------------------------------
        # CONVERT SQLITE 0/1 VALUES TO POSTGRESQL BOOLEAN VALUES
        # ---------------------------------------------------------
        for col in boolean_columns:

            if col not in columns:
                continue

            i = columns.index(col)

            if row[i] is not None:
                row[i] = bool(row[i])

        processed.append(row)

    # -------------------------------------------------------------
    # INSERT
    # -------------------------------------------------------------
    quoted = ", ".join(
        f'"{c}"'
        for c in columns
    )

    placeholders = ", ".join(
        ["%s"] * len(columns)
    )

    with connection.cursor() as cur:
        for row in processed:
            cur.execute(
                f'''
                INSERT INTO "{table}"
                ({quoted})
                VALUES ({placeholders})
                ''',
                row
            )

    print(f"{table}: {len(processed)}")


def reset_sequences():
    """
    Reset PostgreSQL sequences to MAX(id) after explicit
    insertion of recovered primary keys.
    """

    tables = [
        "students_academicyear",
        "students_department",
        "students_course",
        "students_programme",
        "students_programmelevel",
        "students_intake",
        "students_semester",
        "students_unit",
        "students_unitoffering",

        "students_student",
        "students_applicant",
        "students_registration",
        "students_semesterenrollment",

        "students_resultbatch",
        "students_resultbatchlog",
        "students_result",
        "students_progressionlog",
        "students_lecturerassignment",

        "finance_feecategory",
        "finance_feestructure",
        "finance_feestructureitem",

        "finance_studentcredit",
        "finance_studentinvoice",
        "finance_invoiceitem",
        "finance_payment",
        "finance_receipt",
        "finance_financialclearance",

        "graduation_graduation",

        "system_activitylog",
    ]

    print("\n=== RESETTING SEQUENCES ===")

    with connection.cursor() as cur:

        for table in tables:

            cur.execute(
                """
                SELECT pg_get_serial_sequence(%s, 'id')
                """,
                [table]
            )

            result = cur.fetchone()

            if not result or not result[0]:
                continue

            sequence = result[0]

            cur.execute(
                f'''
                SELECT COALESCE(MAX(id), 0)
                FROM "{table}"
                '''
            )

            max_id = cur.fetchone()[0]

            if max_id == 0:

                cur.execute(
                    "SELECT setval(%s, 1, false)",
                    [sequence]
                )

            else:

                cur.execute(
                    "SELECT setval(%s, %s, true)",
                    [sequence, max_id]
                )

            print(
                f"{table}: sequence -> {max_id}"
            )


def main():

    # -------------------------------------------------------------
    # VERIFY SOURCE DATABASE EXISTS
    # -------------------------------------------------------------
    if not os.path.exists(SQLITE_DB):
        raise FileNotFoundError(
            f"Recovered SQLite database not found:\n{SQLITE_DB}"
        )

    db = sqlite3.connect(SQLITE_DB)

    print("======================================")
    print("XORADEX EDUCORE DATABASE RECOVERY")
    print("======================================")

    print("\n=== RECOVERING USERS ===")

    user_map = {}

    # -------------------------------------------------------------
    # LOAD OLD USERS
    # -------------------------------------------------------------
    old_users = db.execute("""
        SELECT
            id,
            username,
            email,
            first_name,
            last_name,
            password,
            is_staff,
            is_active,
            is_superuser,
            date_joined,
            last_login
        FROM auth_user
        ORDER BY id
    """).fetchall()

    with transaction.atomic():

        # =========================================================
        # USERS
        # =========================================================
        for (
            old_id,
            username,
            email,
            first_name,
            last_name,
            password,
            is_staff,
            is_active,
            is_superuser,
            date_joined,
            last_login
        ) in old_users:

            user = User.objects.filter(
                username=username
            ).first()

            if not user and email:
                user = User.objects.filter(
                    email=email
                ).first()

            if user:

                print(
                    f"USER {old_id}: existing -> "
                    f"{user.id} ({user.username})"
                )

            else:

                user = User(
                    username=username,
                    email=email or "",
                    first_name=first_name or "",
                    last_name=last_name or "",
                    is_staff=bool(is_staff),
                    is_active=bool(is_active),
                    is_superuser=bool(is_superuser),
                )

                if hasattr(user, "date_joined") and date_joined:
                    user.date_joined = date_joined

                if hasattr(user, "last_login"):
                    user.last_login = last_login

                # Preserve the original Django password hash.
                user.password = password

                user.save()

                print(
                    f"USER {old_id}: created -> "
                    f"{user.id} ({username})"
                )

            user_map[old_id] = user.id

        # =========================================================
        # DISPLAY USER MAP
        # =========================================================
        print("\n=== USER ID MAPPING ===")

        for old_id, new_id in sorted(user_map.items()):
            print(
                f"old auth_user ID {old_id} "
                f"-> current accounts_user ID {new_id}"
            )

        # =========================================================
        # RECOVER ERP DATA
        # =========================================================
        print("\n=== RECOVERING ERP DATA ===")

        tables = [

            # -----------------------------------------------------
            # ACADEMIC STRUCTURE
            # -----------------------------------------------------
            "students_academicyear",
            "students_department",
            "students_course",
            "students_programme",
            "students_programmelevel",
            "students_intake",
            "students_semester",
            "students_unit",
            "students_unitoffering",

            # -----------------------------------------------------
            # STUDENTS
            # -----------------------------------------------------
            "students_student",
            "students_applicant",
            "students_registration",
            "students_semesterenrollment",

            # -----------------------------------------------------
            # RESULTS / PROGRESSION
            # -----------------------------------------------------
            "students_resultbatch",
            "students_resultbatchlog",
            "students_result",
            "students_progressionlog",
            "students_lecturerassignment",

            # -----------------------------------------------------
            # FINANCE
            # -----------------------------------------------------
            "finance_feecategory",
            "finance_feestructure",
            "finance_feestructureitem",

            # Existing PostgreSQL finance setting is preserved.
            # "finance_financesetting",

            "finance_studentcredit",
            "finance_studentinvoice",
            "finance_invoiceitem",
            "finance_payment",
            "finance_receipt",
            "finance_financialclearance",

            # -----------------------------------------------------
            # GRADUATION
            # -----------------------------------------------------
            "graduation_graduation",

            # Existing PostgreSQL activity log is preserved.
            # "system_activitylog",
        ]

        for table in tables:
            copy_table(
                db,
                table,
                user_map
            )

        # =========================================================
        # RESET SEQUENCES
        # =========================================================
        reset_sequences()

        # =========================================================
        # FORCE DEFERRED FOREIGN KEYS TO BE CHECKED NOW
        # =========================================================
        print("\n=== VALIDATING FOREIGN KEYS ===")

        with connection.cursor() as cur:
            cur.execute(
                "SET CONSTRAINTS ALL IMMEDIATE"
            )

        print(
            "Foreign-key validation passed."
        )

    db.close()

    print("\n======================================")
    print("RECOVERY COMPLETED SUCCESSFULLY.")
    print("======================================")


if __name__ == "__main__":
    main()