document.addEventListener("DOMContentLoaded", function () {

    /*
     * =========================================================
     * RECEIPT HISTORY TOGGLE
     * =========================================================
     */

    const buttons = document.querySelectorAll(
        ".receipt-history-toggle"
    );

    buttons.forEach(function (button) {

        button.addEventListener("click", function () {

            const targetId = button.getAttribute(
                "data-target"
            );

            const target = document.getElementById(
                targetId
            );

            if (!target) {
                return;
            }

            const icon = button.querySelector("i");

            const text = button.querySelector(
                ".receipt-toggle-text"
            );

            const isHidden =
                target.classList.contains("d-none");


            if (isHidden) {

                target.classList.remove("d-none");

                button.setAttribute(
                    "aria-expanded",
                    "true"
                );

                if (text) {
                    text.textContent =
                        "Hide Receipts";
                }

                if (icon) {

                    icon.classList.remove(
                        "fa-eye"
                    );

                    icon.classList.add(
                        "fa-eye-slash"
                    );

                }

            } else {

                target.classList.add("d-none");

                button.setAttribute(
                    "aria-expanded",
                    "false"
                );

                if (text) {
                    text.textContent =
                        "View Receipts";
                }

                if (icon) {

                    icon.classList.remove(
                        "fa-eye-slash"
                    );

                    icon.classList.add(
                        "fa-eye"
                    );

                }

            }

        });

    });


    /*
     * =========================================================
     * LIVE RECEIPT SEARCH
     * =========================================================
     */

    const searchInput = document.getElementById(
        "receiptSearch"
    );

    const receiptRegister = document.getElementById(
        "receiptRegister"
    );

    const noResults = document.getElementById(
        "receiptNoResults"
    );


    if (!searchInput || !receiptRegister) {
        return;
    }


    const studentGroups = Array.from(
        receiptRegister.querySelectorAll(
            ".receipt-student-group"
        )
    );


    searchInput.addEventListener(
        "input",
        function () {

            const searchTerm =
                searchInput.value
                    .trim()
                    .toLowerCase();

            let visibleStudents = 0;


            studentGroups.forEach(function (group) {

                const studentName =
                    (
                        group.dataset.studentName || ""
                    ).toLowerCase();

                const admissionNo =
                    (
                        group.dataset.admissionNo || ""
                    ).toLowerCase();

                const groupText =
                    (
                        group.textContent || ""
                    ).toLowerCase();


                const matches =
                    searchTerm === "" ||
                    studentName.includes(searchTerm) ||
                    admissionNo.includes(searchTerm) ||
                    groupText.includes(searchTerm);


                if (matches) {

                    group.classList.remove(
                        "d-none"
                    );

                    visibleStudents++;

                } else {

                    group.classList.add(
                        "d-none"
                    );


                    /*
                     * Close receipt history when
                     * the student is hidden.
                     */

                    const history =
                        group.querySelector(
                            ".receipt-history"
                        );

                    const button =
                        group.querySelector(
                            ".receipt-history-toggle"
                        );

                    const text =
                        group.querySelector(
                            ".receipt-toggle-text"
                        );

                    const icon =
                        button
                            ? button.querySelector("i")
                            : null;


                    if (history) {

                        history.classList.add(
                            "d-none"
                        );

                    }


                    if (button) {

                        button.setAttribute(
                            "aria-expanded",
                            "false"
                        );

                    }


                    if (text) {

                        text.textContent =
                            "View Receipts";

                    }


                    if (icon) {

                        icon.classList.remove(
                            "fa-eye-slash"
                        );

                        icon.classList.add(
                            "fa-eye"
                        );

                    }

                }

            });


            /*
             * SEARCH EMPTY STATE
             */

            if (noResults) {

                if (
                    searchTerm !== "" &&
                    visibleStudents === 0
                ) {

                    noResults.classList.remove(
                        "d-none"
                    );

                } else {

                    noResults.classList.add(
                        "d-none"
                    );

                }

            }

        }
    );

});