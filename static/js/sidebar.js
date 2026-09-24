/* =========================================================
   XORADEX EDUCORE ERP
   SIDEBAR JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       ELEMENTS
       ===================================================== */

    const sidebar = document.getElementById("erpSidebar");
    const toggle = document.getElementById("sidebarToggle");

    if (!sidebar) {
        return;
    }


    /* =====================================================
       CONFIGURATION
       ===================================================== */

    const MOBILE_BREAKPOINT = 768;


    /* =====================================================
       MOBILE OVERLAY
       ===================================================== */

    let overlay = document.querySelector(
        ".erp-sidebar-overlay"
    );

    if (!overlay) {

        overlay = document.createElement("div");

        overlay.className = "erp-sidebar-overlay";

        document.body.appendChild(overlay);

    }


    /* =====================================================
       DEVICE CHECK
       ===================================================== */

    function isMobile() {

        return window.innerWidth <= MOBILE_BREAKPOINT;

    }


    /* =====================================================
       OPEN MOBILE NAVIGATION
       ===================================================== */

    function openMobileSidebar() {

        if (!isMobile()) {
            return;
        }

        sidebar.classList.add("mobile-open");

        overlay.classList.add("active");

        document.body.classList.add(
            "sidebar-mobile-open"
        );

        if (toggle) {

            toggle.setAttribute(
                "aria-expanded",
                "true"
            );

        }

    }


    /* =====================================================
       CLOSE MOBILE NAVIGATION
       ===================================================== */

    function closeMobileSidebar() {

        sidebar.classList.remove("mobile-open");

        overlay.classList.remove("active");

        document.body.classList.remove(
            "sidebar-mobile-open"
        );

        if (toggle) {

            toggle.setAttribute(
                "aria-expanded",
                "false"
            );

        }

    }


    /* =====================================================
       SIDEBAR TOGGLE
       ===================================================== */

    if (toggle) {

        toggle.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                /* ---------------------------------------------
                   MOBILE
                   --------------------------------------------- */

                if (isMobile()) {

                    if (
                        sidebar.classList.contains(
                            "mobile-open"
                        )
                    ) {

                        closeMobileSidebar();

                    } else {

                        openMobileSidebar();

                    }

                    return;
                }


                /* ---------------------------------------------
                   DESKTOP / TABLET
                   --------------------------------------------- */

                sidebar.classList.toggle(
                    "collapsed"
                );


                const collapsed =
                    sidebar.classList.contains(
                        "collapsed"
                    );


                toggle.setAttribute(
                    "aria-expanded",
                    String(!collapsed)
                );

            }
        );

    }


    /* =====================================================
       OVERLAY CLOSE
       ===================================================== */

    overlay.addEventListener(
        "click",
        function () {

            closeMobileSidebar();

        }
    );


    /* =====================================================
       ESCAPE KEY
       ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                isMobile() &&
                sidebar.classList.contains(
                    "mobile-open"
                )
            ) {

                closeMobileSidebar();

            }

        }
    );


    /* =====================================================
       SIDEBAR LINKS
       ===================================================== */

    sidebar
        .querySelectorAll("a[href]")
        .forEach(function (link) {

            link.addEventListener(
                "click",
                function () {

                    if (!isMobile()) {
                        return;
                    }


                    const href =
                        link.getAttribute("href");


                    /*
                     * Bootstrap submenu triggers use "#menu".
                     *
                     * Do NOT close the full-screen sidebar when
                     * clicking these. Bootstrap needs the click
                     * to open/close the submenu.
                     */

                    if (
                        !href ||
                        href === "#" ||
                        href.startsWith("#")
                    ) {

                        return;

                    }


                    /*
                     * Real navigation link.
                     */

                    closeMobileSidebar();

                }
            );

        });


    /* =====================================================
       KEEP ACTIVE MENU OPEN
       ===================================================== */

    const currentPath =
        window.location.pathname;


    document
        .querySelectorAll(
            "#erpSidebar .collapse"
        )
        .forEach(function (menu) {

            const links =
                menu.querySelectorAll("a[href]");

            let active = false;


            /* -------------------------------------------------
               CHECK LINKS
               ------------------------------------------------- */

            links.forEach(function (link) {

                const href =
                    link.getAttribute("href");


                if (
                    !href ||
                    href === "#" ||
                    href.startsWith("#")
                ) {

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
                        currentPath.startsWith(
                            linkPath
                        )
                    ) {

                        active = true;

                        link.classList.add(
                            "active"
                        );

                    }

                } catch (error) {

                    /*
                     * Ignore malformed URLs.
                     */

                }

            });


            /* -------------------------------------------------
               OPEN PARENT MENU
               ------------------------------------------------- */

            if (active) {

                menu.classList.add("show");


                const trigger =
                    document.querySelector(
                        '[href="#' +
                        menu.id +
                        '"]'
                    );


                if (trigger) {

                    trigger.setAttribute(
                        "aria-expanded",
                        "true"
                    );

                }

            }

        });


    /* =====================================================
       RESPONSIVE RESIZE
       ===================================================== */

    let wasMobile = isMobile();


    window.addEventListener(
        "resize",
        function () {

            const nowMobile = isMobile();


            /*
             * Desktop/tablet → mobile
             */

            if (
                !wasMobile &&
                nowMobile
            ) {

                closeMobileSidebar();

            }


            /*
             * Mobile → desktop/tablet
             */

            if (
                wasMobile &&
                !nowMobile
            ) {

                closeMobileSidebar();

            }


            wasMobile = nowMobile;

        }
    );


    /* =====================================================
       INITIAL STATE
       ===================================================== */

    if (isMobile()) {

        closeMobileSidebar();

    }


    /* =====================================================
       ACCESSIBILITY
       ===================================================== */

    if (toggle) {

        toggle.setAttribute(
            "aria-expanded",
            "false"
        );

    }

});