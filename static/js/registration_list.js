document.addEventListener("DOMContentLoaded", function () {

    const records = Array.from(
        document.querySelectorAll(".registration-record")
    );

    const studentTable =
        document.getElementById(
            "studentRegistrationTable"
        );

    const noRegistrationsMessage =
        document.getElementById(
            "noRegistrationsMessage"
        );

    const academicYearFilter =
        document.getElementById(
            "academicYearFilter"
        );

    const semesterFilter =
        document.getElementById(
            "semesterFilter"
        );

    const searchInput =
        document.getElementById(
            "registrationSearch"
        );

    const filterForm =
        document.getElementById(
            "registrationFilterForm"
        );


    /*
     * =====================================================
     * CREATE UNIQUE ACADEMIC YEAR LIST
     * =====================================================
     */

    const academicYears =
        new Set();

    records.forEach(function (record) {

        const year =
            (record.dataset.academicYear || "").trim();

        if (year) {
            academicYears.add(year);
        }

    });


    Array.from(academicYears)
        .sort()
        .forEach(function (year) {

            const option =
                document.createElement("option");

            option.value =
                year;

            option.textContent =
                year;

            academicYearFilter.appendChild(
                option
            );

        });


    /*
     * =====================================================
     * CREATE UNIQUE SEMESTER LIST
     * =====================================================
     */

    const semesters =
        new Set();

    records.forEach(function (record) {

        const semester =
            (record.dataset.semester || "").trim();

        if (semester) {
            semesters.add(semester);
        }

    });


    Array.from(semesters)
        .forEach(function (semester) {

            const option =
                document.createElement("option");

            option.value =
                semester;

            option.textContent =
                semester;

            semesterFilter.appendChild(
                option
            );

        });


    /*
     * =====================================================
     * FILTER
     * =====================================================
     *
     * All three fields are applied together:
     *
     * Admission Number
     * Academic Year
     * Semester
     *
     */

    function filterRegistrations() {

        studentTable.innerHTML = "";

        noRegistrationsMessage.style.display =
            "none";


        const admission =
            searchInput.value
                .trim()
                .toLowerCase();

        const selectedYear =
            academicYearFilter.value
                .trim();

        const selectedSemester =
            semesterFilter.value
                .trim();


        /*
         * Filter the original records.
         */

        const filteredRecords =
            records.filter(function (record) {

                const recordAdmission =
                    (
                        record.dataset.admissionNo || ""
                    )
                    .trim()
                    .toLowerCase();

                const recordYear =
                    (
                        record.dataset.academicYear || ""
                    )
                    .trim();

                const recordSemester =
                    (
                        record.dataset.semester || ""
                    )
                    .trim();


                /*
                 * ADMISSION NUMBER
                 */

                if (
                    admission &&
                    recordAdmission !== admission
                ) {
                    return false;
                }


                /*
                 * ACADEMIC YEAR
                 */

                if (
                    selectedYear &&
                    recordYear !== selectedYear
                ) {
                    return false;
                }


                /*
                 * SEMESTER
                 */

                if (
                    selectedSemester &&
                    recordSemester !== selectedSemester
                ) {
                    return false;
                }


                return true;

            });


        /*
         * NO RESULTS
         */

        if (filteredRecords.length === 0) {

            noRegistrationsMessage.style.display =
                "block";

            return;
        }


        /*
         * =================================================
         * GROUP BY STUDENT
         * =================================================
         */

        const students =
            new Map();


        filteredRecords.forEach(function (record) {

            const studentId =
                record.dataset.studentId;


            if (!students.has(studentId)) {

                students.set(studentId, {

                    name:
                        record.dataset.studentName,

                    registrations: []

                });

            }


            students
                .get(studentId)
                .registrations
                .push({

                    academicYear:
                        record.dataset.academicYear,

                    semester:
                        record.dataset.semester,

                    unit:
                        record.dataset.unit,

                    registeredAt:
                        record.dataset.registeredAt,

                    timestamp:
                        Number(
                            record.dataset.timestamp
                        ),

                    editUrl:
                        record.dataset.editUrl,

                    deleteUrl:
                        record.dataset.deleteUrl

                });

        });


        /*
         * =================================================
         * CREATE ONE ROW PER STUDENT
         * =================================================
         */

        students.forEach(function (student) {

            student.registrations.sort(
                function (a, b) {

                    return (
                        b.timestamp -
                        a.timestamp
                    );

                }
            );


            const current =
                student.registrations[0];


            /*
             * MAIN ROW
             */

            const studentRow =
                document.createElement("tr");


            const studentCell =
                document.createElement("td");

            studentCell.textContent =
                student.name;


            const yearCell =
                document.createElement("td");

            yearCell.textContent =
                current.academicYear;


            const semesterCell =
                document.createElement("td");

            semesterCell.textContent =
                current.semester;


            const dateCell =
                document.createElement("td");

            dateCell.className =
                "date";

            dateCell.textContent =
                current.registeredAt;


            /*
             * ACTIONS
             */

            const actionCell =
                document.createElement("td");


            const actions =
                document.createElement("div");

            actions.className =
                "table-actions";


            const viewButton =
                document.createElement("button");

            viewButton.type =
                "button";

            viewButton.className =
                "btn btn-primary btn-sm";

            viewButton.textContent =
                "View Units";


            actions.appendChild(
                viewButton
            );

            actionCell.appendChild(
                actions
            );


            studentRow.appendChild(
                studentCell
            );

            studentRow.appendChild(
                yearCell
            );

            studentRow.appendChild(
                semesterCell
            );

            studentRow.appendChild(
                dateCell
            );

            studentRow.appendChild(
                actionCell
            );


            studentTable.appendChild(
                studentRow
            );


            /*
             * =================================================
             * HISTORY ROW
             * =================================================
             */

            const detailsRow =
                document.createElement("tr");

            detailsRow.style.display =
                "none";


            const detailsCell =
                document.createElement("td");

            detailsCell.colSpan =
                5;


            const historyTable =
                document.createElement("table");

            historyTable.className =
                "table table-hover";


            /*
             * HISTORY HEADER
             */

            const historyHead =
                document.createElement("thead");


            const historyHeader =
                document.createElement("tr");


            [
                "Academic Year",
                "Semester",
                "Unit",
                "Registration Date",
                "Actions"
            ].forEach(function (text) {

                const th =
                    document.createElement("th");

                th.textContent =
                    text;

                historyHeader.appendChild(
                    th
                );

            });


            historyHead.appendChild(
                historyHeader
            );

            historyTable.appendChild(
                historyHead
            );


            /*
             * HISTORY BODY
             */

            const historyBody =
                document.createElement("tbody");


            student.registrations.forEach(
                function (registration) {

                    const row =
                        document.createElement("tr");


                    const yearCell =
                        document.createElement("td");

                    yearCell.textContent =
                        registration.academicYear;


                    const semesterCell =
                        document.createElement("td");

                    semesterCell.textContent =
                        registration.semester;


                    const unitCell =
                        document.createElement("td");

                    unitCell.textContent =
                        registration.unit;


                    const dateCell =
                        document.createElement("td");

                    dateCell.className =
                        "date";

                    dateCell.textContent =
                        registration.registeredAt;


                    /*
                     * ACTIONS
                     */

                    const actionsCell =
                        document.createElement("td");


                    const actions =
                        document.createElement("div");

                    actions.className =
                        "table-actions";


                    const editLink =
                        document.createElement("a");

                    editLink.href =
                        registration.editUrl;

                    editLink.className =
                        "btn btn-warning btn-sm";

                    editLink.textContent =
                        "Edit";


                    const deleteLink =
                        document.createElement("a");

                    deleteLink.href =
                        registration.deleteUrl;

                    deleteLink.className =
                        "btn btn-danger btn-sm";

                    deleteLink.textContent =
                        "Delete";


                    actions.appendChild(
                        editLink
                    );

                    actions.appendChild(
                        deleteLink
                    );

                    actionsCell.appendChild(
                        actions
                    );


                    row.appendChild(
                        yearCell
                    );

                    row.appendChild(
                        semesterCell
                    );

                    row.appendChild(
                        unitCell
                    );

                    row.appendChild(
                        dateCell
                    );

                    row.appendChild(
                        actionsCell
                    );


                    historyBody.appendChild(
                        row
                    );

                }
            );


            historyTable.appendChild(
                historyBody
            );

            detailsCell.appendChild(
                historyTable
            );

            detailsRow.appendChild(
                detailsCell
            );

            studentTable.appendChild(
                detailsRow
            );


            /*
             * VIEW / HIDE UNITS
             */

            viewButton.addEventListener(
                "click",
                function () {

                    if (
                        detailsRow.style.display ===
                        "none"
                    ) {

                        detailsRow.style.display =
                            "table-row";

                        viewButton.textContent =
                            "Hide Units";

                    } else {

                        detailsRow.style.display =
                            "none";

                        viewButton.textContent =
                            "View Units";

                    }

                }
            );

        });

    }


    /*
     * =====================================================
     * FILTER BUTTON
     * =====================================================
     */

    filterForm.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();

            filterRegistrations();

        }
    );


    /*
     * =====================================================
     * INITIAL DISPLAY
     * =====================================================
     */

    filterRegistrations();

});