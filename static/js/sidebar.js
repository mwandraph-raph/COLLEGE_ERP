/* =========================================================
   XORADEX EDUCORE ERP
   SIDEBAR JAVASCRIPT
   ---------------------------------------------------------
   Desktop / Tablet : collapsible sidebar
   Mobile           : off-canvas sidebar
   Breakpoint       : 768px
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
       RESPONSIVE BREAKPOINT
       ===================================================== */

    const MOBILE_QUERY = window.matchMedia(
        "(max-width: 767.98px)"
    );


    function isMobile() {
        return MOBILE_QUERY.matches;
    }


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
       ARIA STATE
       ===================================================== */

    function updateToggleState() {

        if (!toggle) {
            return;
        }

        if (isMobile()) {

            toggle.setAttribute(
                "aria-expanded",
                sidebar.classList.contains("mobile-open")
                    ? "true"
                    : "false"
            );

        } else {

            toggle.setAttribute(
                "aria-expanded",
                sidebar.classList.contains("collapsed")
                    ? "false"
                    : "true"
            );
        }
    }


    /* =====================================================
       OPEN MOBILE SIDEBAR
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

        updateToggleState();
    }


    /* =====================================================
       CLOSE MOBILE SIDEBAR
       ===================================================== */

    function closeMobileSidebar() {

        sidebar.classList.remove("mobile-open");

        overlay.classList.remove("active");

        document.body.classList.remove(
            "sidebar-mobile-open"
        );

        updateToggleState();
    }


    /* =====================================================
       TOGGLE BUTTON
       ===================================================== */

    if (toggle) {

        toggle.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

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


                /* -----------------------------------------
                   DESKTOP / TABLET
                   ----------------------------------------- */

                sidebar.classList.toggle(
                    "collapsed"
                );

                updateToggleState();
            }
        );
    }


    /* =====================================================
       OVERLAY
       ===================================================== */

    overlay.addEventListener(
        "click",
        function () {

            closeMobileSidebar();

        }
    );


    /* =====================================================
       ESC KEY
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
       =====================================================

       IMPORTANT:
       We NEVER prevent normal Django navigation.

       Examples:

           /students/
           /applicants/
           /courses/
           /exam/dashboard/

       are allowed to navigate normally.

       Only Bootstrap submenu links beginning with "#"
       are ignored.
       ===================================================== */

    sidebar.addEventListener(
        "click",
        function (event) {

            const link =
                event.target.closest("a[href]");

            if (!link || !sidebar.contains(link)) {
                return;
            }


            const href =
                link.getAttribute("href");


            /* ---------------------------------------------
               Ignore Bootstrap submenu links
               --------------------------------------------- */

            if (
                !href ||
                href === "#" ||
                href.startsWith("#")
            ) {
                return;
            }


            /* ---------------------------------------------
               Real Django navigation link
               --------------------------------------------- */

            if (isMobile()) {

                /*
                 * Close the drawer.
                 *
                 * We deliberately DO NOT call
                 * event.preventDefault().
                 *
                 * The browser therefore continues
                 * to the Django URL normally.
                 */

                closeMobileSidebar();
            }

        }
    );


    /* =====================================================
       ACTIVE MENU
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
                        currentPath.startsWith(linkPath)
                    ) {

                        active = true;

                        link.classList.add("active");
                    }

                } catch (error) {

                    /* Ignore invalid URLs */

                }

            });


            /* ---------------------------------------------
               Open parent submenu for active page
               --------------------------------------------- */

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
       SCREEN SIZE CHANGE
       ===================================================== */

    function handleBreakpointChange() {

        closeMobileSidebar();


        if (isMobile()) {

            sidebar.classList.remove(
                "collapsed"
            );
        }


        updateToggleState();
    }


    if (MOBILE_QUERY.addEventListener) {

        MOBILE_QUERY.addEventListener(
            "change",
            handleBreakpointChange
        );

    } else {

        MOBILE_QUERY.addListener(
            handleBreakpointChange
        );
    }


    /* =====================================================
       INITIAL STATE
       ===================================================== */

    if (isMobile()) {

        sidebar.classList.remove(
            "collapsed"
        );

        closeMobileSidebar();
    }


    updateToggleState();

});