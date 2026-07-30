document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("erpSidebar");

    const toggle = document.getElementById("sidebarToggle");

    if(toggle){

        toggle.addEventListener("click", function(){

            sidebar.classList.toggle("collapsed");

        });

    }

});