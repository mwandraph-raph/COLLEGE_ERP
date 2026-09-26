document.addEventListener("DOMContentLoaded", function () {


    /* =========================================================
       LOAD EXISTING DATA
       ========================================================= */

    const dataElements =
        document.querySelectorAll(".enrollment-data");

    const enrollments = [];


    dataElements.forEach(function (element) {

        enrollments.push({

            id: element.dataset.id,

            studentId: element.dataset.studentId,

            admission: element.dataset.admission,

            student: element.dataset.student,

            programme: element.dataset.programme,

            level: element.dataset.level,

            year: element.dataset.year,

            semester: element.dataset.semester,

            status: element.dataset.status,

            statusDisplay: element.dataset.statusDisplay,

            detailUrl: element.dataset.detailUrl,

            registerUrl: element.dataset.registerUrl,

            editUrl: element.dataset.editUrl,

            deleteUrl: element.dataset.deleteUrl

        });

    });



    /* =========================================================
       PAGE ELEMENTS
       ========================================================= */

    const filters =
        document.querySelectorAll(".status-filter");

    const tableBody =
        document.getElementById("studentTableBody");

    const tableTitle =
        document.getElementById("tableTitle");

    const tableDescription =
        document.getElementById("tableDescription");

    const searchInput =
        document.getElementById("studentSearch");

    const searchButton =
        document.getElementById("searchButton");



    /* =========================================================
       CURRENT SEARCH
       ========================================================= */

    let currentSearch = "";



    /* =========================================================
       DETERMINE SEMESTER ORDER
       ========================================================= */

    function getSemesterOrder(semester) {

        const value =
            String(semester).toLowerCase();


        if (
            value.includes("jan") ||
            value.includes("january")
        ) {

            return 1;

        }


        if (
            value.includes("apr") ||
            value.includes("april")
        ) {

            return 2;

        }


        if (
            value.includes("jul") ||
            value.includes("july")
        ) {

            return 3;

        }


        if (
            value.includes("oct") ||
            value.includes("october")
        ) {

            return 4;

        }


        return 0;

    }



    /* =========================================================
       ACADEMIC RECORD ORDER
       ========================================================= */

    function getRecordOrder(record) {

        const yearMatch =
            String(record.year).match(/\d{4}/);

        const year =
            yearMatch
                ? parseInt(yearMatch[0], 10)
                : 0;


        const semesterOrder =
            getSemesterOrder(record.semester);


        return (
            year * 100 +
            semesterOrder
        );

    }



    /* =========================================================
       SORT RECORDS
       ========================================================= */

    function sortRecordsLatestFirst(records) {

        return records.slice().sort(function (a, b) {

            const orderA =
                getRecordOrder(a);

            const orderB =
                getRecordOrder(b);


            if (orderA !== orderB) {

                return orderB - orderA;

            }


            return Number(b.id) - Number(a.id);

        });

    }



    /* =========================================================
       GROUP ALL RECORDS BY STUDENT
       ========================================================= */

    function groupByStudent(records) {

        const grouped = {};


        records.forEach(function (record) {

            const key =
                record.studentId ||
                record.admission;


            if (!grouped[key]) {

                grouped[key] = [];

            }


            grouped[key].push(record);

        });


        return grouped;

    }



    /* =========================================================
       SEARCH MATCH
       ========================================================= */

    function matchesSearch(record) {

        if (!currentSearch) {

            return true;

        }


        const searchableText = [

            record.admission,

            record.student,

            record.programme,

            record.level,

            record.year,

            record.semester,

            record.status,

            record.statusDisplay

        ]

        .join(" ")
        .toLowerCase();


        return searchableText.includes(
            currentSearch
        );

    }



    /* =========================================================
       GET ONE REPRESENTATIVE RECORD PER STUDENT
       ========================================================= */

    function getStudentRecords(status) {

        let sourceRecords =
            enrollments;


        if (status !== "ALL") {

            sourceRecords =
                enrollments.filter(function (record) {

                    return record.status === status;

                });

        }


        const grouped =
            groupByStudent(sourceRecords);


        const students = [];


        Object.keys(grouped).forEach(function (key) {

            const records =
                sortRecordsLatestFirst(
                    grouped[key]
                );


            const studentMatchesSearch =
                records.some(function (record) {

                    return matchesSearch(record);

                });


            if (!studentMatchesSearch) {

                return;

            }


            students.push({

                representative: records[0],

                matchingRecords: records

            });

        });


        students.sort(function (a, b) {

            return (
                getRecordOrder(
                    b.representative
                ) -
                getRecordOrder(
                    a.representative
                )
            );

        });


        return students;

    }



    /* =========================================================
       STATUS BADGE
       ========================================================= */

    function statusBadge(status, display) {

        let badgeClass =
            "bg-danger";


        if (status === "ENROLLED") {

            badgeClass =
                "bg-success";

        }

        else if (status === "PROGRESSED") {

            badgeClass =
                "bg-primary";

        }

        else if (status === "COMPLETED") {

            badgeClass =
                "bg-dark";

        }

        else if (status === "DEFERRED") {

            badgeClass =
                "bg-warning text-dark";

        }


        return `

            <span class="badge ${badgeClass}">

                ${display}

            </span>

        `;

    }



    /* =========================================================
       CREATE RECORDS CONTENT
       ========================================================= */

    function createHistoryHTML(allStudentRecords) {

        const sortedHistory =
            sortRecordsLatestFirst(
                allStudentRecords
            );


        if (!sortedHistory.length) {

            return `

                <div class="text-muted">

                    No semester records available.

                </div>

            `;

        }


        const first =
            sortedHistory[0];


        let html = `

            <div class="p-2">

                <div class="mb-3">

                    <strong>
                        ${first.student}
                    </strong>

                    <span class="text-muted">

                        — ${first.admission}

                    </span>

                </div>


                <table class="table table-striped table-hover">

                    <thead>

                        <tr>

                            <th>Academic Year</th>

                            <th>Semester</th>

                            <th>Programme Level</th>

                            <th>Status</th>

                            <th>Actions</th>

                        </tr>

                    </thead>

                    <tbody>

        `;


        sortedHistory.forEach(function (record) {

            html += `

                <tr>

                    <td>
                        ${record.year}
                    </td>

                    <td>
                        ${record.semester}
                    </td>

                    <td>
                        ${record.level}
                    </td>

                    <td>

                        ${statusBadge(
                            record.status,
                            record.statusDisplay
                        )}

                    </td>

                    <td>

                        <div class="table-actions">

                            <a href="${record.detailUrl}"
                               class="btn btn-info btn-sm">

                                View

                            </a>

                            <a href="${record.registerUrl}"
                               class="btn btn-success btn-sm">

                                Register Units

                            </a>

                            <a href="${record.editUrl}"
                               class="btn btn-warning btn-sm">

                                Edit

                            </a>

                            <a href="${record.deleteUrl}"
                               class="btn btn-danger btn-sm">

                                Delete

                            </a>

                        </div>

                    </td>

                </tr>

            `;

        });


        html += `

                    </tbody>

                </table>

            </div>

        `;


        return html;

    }



    /* =========================================================
       CREATE STUDENT ROW
       ========================================================= */

    function createStudentRows(student) {

        const record =
            student.representative;


        const allStudentRecords =
            enrollments.filter(function (enrollment) {

                return (
                    enrollment.studentId ===
                    record.studentId
                );

            });


        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>
                ${record.admission}
            </td>

            <td>

                <strong>
                    ${record.student}
                </strong>

            </td>

            <td>
                ${record.programme}
            </td>

            <td>
                ${record.level}
            </td>

            <td>
                ${record.year}
            </td>

            <td>
                ${record.semester}
            </td>

            <td>

                ${statusBadge(
                    record.status,
                    record.statusDisplay
                )}

            </td>

            <td>

                <div class="table-actions">

                    <button type="button"
                            class="btn btn-info btn-sm history-button">

                        View Records

                    </button>

                </div>

            </td>

        `;


        const historyRow =
            document.createElement("tr");


        historyRow.style.display =
            "none";


        const historyCell =
            document.createElement("td");


        historyCell.colSpan = 8;


        historyCell.className =
            "p-3";


        historyCell.innerHTML =
            createHistoryHTML(
                allStudentRecords
            );


        historyRow.appendChild(
            historyCell
        );


        const historyButton =
            row.querySelector(
                ".history-button"
            );


        historyButton.addEventListener(
            "click",
            function () {

                if (
                    historyRow.style.display ===
                    "none"
                ) {

                    historyRow.style.display =
                        "";

                    historyButton.textContent =
                        "Hide Records";

                }

                else {

                    historyRow.style.display =
                        "none";

                    historyButton.textContent =
                        "View Records";

                }

            }
        );


        return [
            row,
            historyRow
        ];

    }



    /* =========================================================
       RENDER STUDENTS
       ========================================================= */

    function renderStudents(status) {

        tableBody.innerHTML = "";


        const students =
            getStudentRecords(status);


        if (status === "ALL") {

            tableTitle.textContent =
                "All Students";

            tableDescription.textContent =
                "One record per student. View Records shows the complete semester history.";

        }

        else if (status === "ENROLLED") {

            tableTitle.textContent =
                "Enrolled Students";

            tableDescription.textContent =
                "One record per currently enrolled student.";

        }

        else if (status === "PROGRESSED") {

            tableTitle.textContent =
                "Progressed Students";

            tableDescription.textContent =
                "One record per progressed student. View Records shows the complete academic history.";

        }

        else if (status === "COMPLETED") {

            tableTitle.textContent =
                "Completed Students";

            tableDescription.textContent =
                "One record per completed student.";

        }


        if (!students.length) {

            const emptyRow =
                document.createElement("tr");


            emptyRow.innerHTML = `

                <td colspan="8"
                    class="table-empty">

                    <strong>
                        No students found.
                    </strong>

                </td>

            `;


            tableBody.appendChild(
                emptyRow
            );


            return;

        }


        students.forEach(function (student) {

            const rows =
                createStudentRows(
                    student
                );


            rows.forEach(function (row) {

                tableBody.appendChild(
                    row
                );

            });

        });

    }



    /* =========================================================
       UNIQUE STUDENT COUNTS
       ========================================================= */

    function uniqueStudentCount(status) {

        const students =
            new Set();


        enrollments.forEach(function (record) {

            if (record.status === status) {

                students.add(
                    record.studentId ||
                    record.admission
                );

            }

        });


        return students.size;

    }



    /* =========================================================
       COUNTS
       ========================================================= */

    const allStudents =
        new Set();


    enrollments.forEach(function (record) {

        allStudents.add(
            record.studentId ||
            record.admission
        );

    });


    document.getElementById(
        "allCount"
    ).textContent =
        allStudents.size;


    document.getElementById(
        "enrolledCount"
    ).textContent =
        uniqueStudentCount("ENROLLED");


    document.getElementById(
        "progressedCount"
    ).textContent =
        uniqueStudentCount("PROGRESSED");


    document.getElementById(
        "completedCount"
    ).textContent =
        uniqueStudentCount("COMPLETED");



    /* =========================================================
       SEARCH BUTTON
       ========================================================= */

    function performSearch() {

        currentSearch =
            searchInput.value
                .trim()
                .toLowerCase();


        const activeFilter =
            document.querySelector(
                ".status-filter.active"
            );


        const activeStatus =
            activeFilter
                ? activeFilter.dataset.status
                : "ALL";


        renderStudents(
            activeStatus
        );

    }


    searchButton.addEventListener(
        "click",
        performSearch
    );


    /* =========================================================
       SEARCH WITH ENTER KEY
       ========================================================= */

    searchInput.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                performSearch();

            }

        }
    );



    /* =========================================================
       FILTER BUTTONS
       ========================================================= */

    filters.forEach(function (filter) {

        filter.addEventListener(
            "click",
            function () {

                filters.forEach(
                    function (button) {

                        button.classList.remove(
                            "active"
                        );

                    }
                );


                this.classList.add(
                    "active"
                );


                renderStudents(
                    this.dataset.status
                );

            }
        );

    });



    /* =========================================================
       INITIAL VIEW
       ========================================================= */

    renderStudents("ALL");

});