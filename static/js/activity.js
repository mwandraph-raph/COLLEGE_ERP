document.addEventListener(
    "DOMContentLoaded",
    function () {


        // ==================================================
        // ACTIVITY DETAIL MODAL
        // ==================================================

        const modal = document.getElementById(
            "activityModal"
        );


        if (modal) {


            modal.addEventListener(
                "show.bs.modal",
                function (event) {


                    const row =
                        event.relatedTarget;



                    // BASIC DETAILS

                    setText(
                        "modalUser",
                        row.dataset.user
                    );


                    setText(
                        "modalDate",
                        row.dataset.date
                    );


                    setText(
                        "modalModule",
                        row.dataset.module
                    );


                    setText(
                        "modalObject",
                        row.dataset.object
                    );


                    setText(
                        "modalIP",
                        row.dataset.ip
                    );


                    setText(
                        "modalDescription",
                        row.dataset.description
                    );


                    setText(
                        "modalAgent",
                        row.dataset.agent
                    );



                    // SECURITY DETAILS


                    setText(
                        "modalRecordId",
                        row.dataset.id
                    );


                    setText(
                        "modalVerifiedAt",
                        row.dataset.verifiedAt
                    );


                    setText(
                        "modalHash",
                        row.dataset.hash
                    );



                    // BADGES

                    updateActionBadge(
                        "modalAction",
                        row.dataset.action
                    );


                    updateSeverityBadge(
                        "modalSeverity",
                        row.dataset.severity
                    );



                    // INTEGRITY CHECK


                    const integrity =
                        document.getElementById(
                            "modalIntegrity"
                        );


                    if (integrity) {


                        if (
                            row.dataset.verified === "true"
                        ) {


                            integrity.className =
                                "badge rounded-pill bg-success activity-badge";


                            integrity.innerHTML =
                                `
                                <i class="bi bi-shield-check"></i>
                                Verified
                                `;


                        }

                        else {


                            integrity.className =
                                "badge rounded-pill bg-danger activity-badge";


                            integrity.innerHTML =
                                `
                                <i class="bi bi-shield-exclamation"></i>
                                Tampered
                                `;

                        }

                    }


                }

            );

        }




        // ==================================================
        // COPY HASH BUTTON
        // ==================================================


        const copyBtn =
            document.getElementById(
                "copyHashBtn"
            );


        if (copyBtn) {


            copyBtn.addEventListener(
                "click",
                function () {


                    const hash =
                        document.getElementById(
                            "modalHash"
                        ).innerText;



                    navigator.clipboard.writeText(
                        hash
                    );


                    copyBtn.innerHTML =
                    `
                    <i class="bi bi-check-circle"></i>
                    Copied
                    `;



                    setTimeout(
                        function () {


                            copyBtn.innerHTML =
                            `
                            <i class="bi bi-clipboard"></i>
                            Copy Hash
                            `;


                        },
                        2000
                    );


                }

            );

        }





        // ==================================================
        // ENTERPRISE AUDIT CHARTS
        // ==================================================


        if (
            typeof Chart !== "undefined"
        ) {


            createChart(
                "actionChart",
                actionData,
                "action"
            );


            createChart(
                "moduleChart",
                moduleData,
                "module"
            );


            createChart(
                "severityChart",
                severityData,
                "severity"
            );


        }





        // ==================================================
        // HELPER FUNCTIONS
        // ==================================================


        function setText(
            id,
            value
        ){


            const element =
                document.getElementById(id);


            if(element){

                element.innerText =
                    value || "-";

            }

        }





        function updateActionBadge(
            id,
            value
        ){


            const badge =
                document.getElementById(id);



            if(!badge)
                return;



            badge.innerText =
                value || "-";


            badge.className =
                "badge rounded-pill activity-badge";



            switch(value){


                case "Delete":

                    badge.classList.add(
                        "bg-danger"
                    );

                    break;



                case "Update":

                    badge.classList.add(
                        "bg-warning",
                        "text-dark"
                    );

                    break;



                case "Create":

                    badge.classList.add(
                        "bg-success"
                    );

                    break;



                case "Login":

                    badge.classList.add(
                        "bg-primary"
                    );

                    break;



                case "Logout":

                    badge.classList.add(
                        "bg-dark"
                    );

                    break;



                default:

                    badge.classList.add(
                        "bg-secondary"
                    );

            }


        }





        function updateSeverityBadge(
            id,
            value
        ){


            const badge =
                document.getElementById(id);



            if(!badge)
                return;



            badge.innerText =
                value || "-";



            badge.className =
                "badge rounded-pill activity-badge";



            if(value === "Critical"){


                badge.classList.add(
                    "bg-danger"
                );


            }

            else if(value === "Warning"){


                badge.classList.add(
                    "bg-warning",
                    "text-dark"
                );


            }

            else {


                badge.classList.add(
                    "bg-success"
                );


            }


        }






        function createChart(
            element,
            data,
            field
        ){


            const canvas =
                document.getElementById(
                    element
                );



            if(
                !canvas ||
                !data
            ){

                return;

            }



            new Chart(
                canvas,
                {


                    type:"doughnut",



                    data:{


                        labels:
                            data.map(
                                item =>
                                item[field]
                            ),



                        datasets:[{


                            data:
                                data.map(
                                    item =>
                                    item.total
                                )


                        }]


                    },



                    options:{


                        responsive:true,


                        maintainAspectRatio:false,


                        plugins:{


                            legend:{


                                position:"bottom"


                            }


                        }


                    }


                }

            );


        }



    }
);