document.addEventListener("DOMContentLoaded", function () {

    /* =========================================================
       SIDEBAR COLLAPSE / EXPAND
    ========================================================= */

    const sidebar = document.getElementById("erpSidebar");
    const toggle = document.getElementById("sidebarToggle");

    if (toggle && sidebar) {

        toggle.addEventListener("click", function () {
            sidebar.classList.toggle("collapsed");
        });

    }


    /* =========================================================
       KEEP ACTIVE SIDEBAR MENU OPEN
    ========================================================= */

    const currentPath = window.location.pathname;

    document.querySelectorAll("#erpSidebar .collapse").forEach(function (menu) {

        const links = menu.querySelectorAll("a[href]");
        let active = false;

        links.forEach(function (link) {

            const href = link.getAttribute("href");

            if (!href || href === "#") {
                return;
            }

            try {

                const linkPath =
                    new URL(
                        href,
                        window.location.origin
                    ).pathname;

                if (
                    currentPath === linkPath ||
                    currentPath.startsWith(linkPath)
                ) {
                    active = true;
                    link.classList.add("active");
                }

            } catch (error) {
                // Ignore invalid links
            }

        });


        /* ---------------------------------------------------------
           OPEN THE MENU CONTAINING THE CURRENT PAGE
        --------------------------------------------------------- */

        if (active) {

            menu.classList.add("show");

            const trigger = document.querySelector(
                '[href="#' + menu.id + '"]'
            );

            if (trigger) {

                trigger.setAttribute(
                    "aria-expanded",
                    "true"
                );

            }

        }

    });

});