document.addEventListener("DOMContentLoaded", function () {

    console.log("Programme Levels JS loaded");

    const detailButtons = document.querySelectorAll(
        ".programme-details-btn"
    );

    detailButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const targetId = button.getAttribute("data-target");
            const detailsRow = document.getElementById(targetId);

            if (!detailsRow) {
                return;
            }

            const isHidden =
                detailsRow.style.display === "none" ||
                detailsRow.style.display === "";

            if (isHidden) {

                // Show details
                detailsRow.style.display = "table-row";

                button.innerHTML =
                    '<i class="bi bi-eye-slash"></i> Hide Details';

                button.classList.remove("btn-primary");
                button.classList.add("btn-secondary");

            } else {

                // Hide details
                detailsRow.style.display = "none";

                button.innerHTML =
                    '<i class="bi bi-eye"></i> View Details';

                button.classList.remove("btn-secondary");
                button.classList.add("btn-primary");

            }

        });

    });

});