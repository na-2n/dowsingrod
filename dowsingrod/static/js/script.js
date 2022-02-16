document.addEventListener('readystatechange', () => {
    const img = document.getElementById("image");
    const src = img.getAttribute("data-og-src");
    const loader = new Image();

    loader.addEventListener('load', () => {
        img.src = loader.src;
        img.classList.remove('loading');
    });
    loader.src = src;
});

// TODO: clean up the following , very ugly

let showReportForm = false;

function showReport() {
    const reportModal = document.getElementById("report-form");
    const reportButton = document.getElementById("report-button");

    function reposReportForm() {
        const btnBounds = reportButton.getBoundingClientRect();

        reportModal.style.right = (document.body.clientWidth - btnBounds.right - 10).toString() + "px";
        reportModal.style.top = (btnBounds.top + btnBounds.height + 10).toString() + "px";
    }

    if (showReportForm) {
        showReportForm = !showReportForm;

        reportModal.style.display = "none";
        window.removeEventListener("resize", reposReportForm());

        return;
    }

    showReportForm = !showReportForm;

    reposReportForm();
    reportModal.style.display = "initial";
    window.addEventListener("resize", reposReportForm);
}

