document.addEventListener('readystatechange', () => {
    const img = document.getElementById("image");
    const src = img.getAttribute("data-og-src");
    const loader = new Image();

    loader.addEventListener("load", () => {
        img.src = loader.src;
        img.classList.remove("loading");
    });
    loader.src = src;
});

/*function refreshImage() {
    const xhr = new XMLHttpRequest();
    const img = document.getElementById("image");
    const cont = document.getElementById("image-container");

    img.classList.add("loading");

    xhr.addEventListener("load", () => {
        if (xhr.status === 200) {
            const res = JSON.parse(xhr.responseText);

            img["data-danbooru-id"] = res.id;
            img["data-og-src"] = res.image;
            img.src = res.image_preview;

            cont.href = res.source_type !== "other" && res.source ? res.source : `https://danbooru.donmai.us/posts/${res.id}`;
            cont["data-source-type"] = res.source_type;

            var loader = new Image();

            loader.addEventListener("load", () => {
                img.src = loader.src;
                img.classList.remove("loading");
            })
            loader.src = res.image;
        }
    });

    xhr.open("GET", "/api/random", true);
    xhr.send();
}*/

function hCaptchaLoad() {
    Array.from(document.querySelectorAll(".h-captcha"))
        .flatMap(x => Array.from(x.querySelectorAll("textarea")))
        .forEach(x => {x.required = true; console.log(x)});
}

// TODO: clean up the following , very ugly

let showReportForm = false;

function toggleReport() {
    const reportModal = document.getElementById("report-form");
    const reportButton = document.getElementById("report-button");

    function reposReportForm() {
        const btnBounds = reportButton.getBoundingClientRect();

        reportModal.style.right = (document.body.clientWidth - btnBounds.right).toString() + "px";
        reportModal.style.top = (btnBounds.top + btnBounds.height + 10).toString() + "px";
    }

    if (showReportForm) {
        showReportForm = !showReportForm;

        reportModal.style.display = "none";
        window.removeEventListener("resize", reposReportForm);

        return;
    }

    showReportForm = !showReportForm;

    reposReportForm();
    reportModal.style.display = "initial";
    window.addEventListener("resize", reposReportForm);
}

function submitForm(form) {
    const submitBtn = form.querySelector("button[role=\"submit\"]")
    const xhr = new XMLHttpRequest();

    if (!form.elements["h-captcha-response"].value) {
        alert("Please complete the captcha");
        return;
    }

    xhr.addEventListener("load", () => {
        submitBtn.disabled = false;

        if (xhr.status === 200) {
            alert("Report sent! Thank you!")

            if (showReportForm) {
                toggleReport();
            }
        } else {
            const { errors } = JSON.parse(xhr.responseText);

            console.log(errors);

            if ("hcaptcha" in errors) {
                alert("hCaptcha error");
                return;
            }

            const fmt = errors.map(x => `[${x}]: ${errors[x]}`).join('\n')
            alert(`There was an error while submitting your report:\n${fmt}`)
        }
    });

    submitBtn.disabled = true;

    xhr.open("POST", form.action, true)
    xhr.send(new FormData(form));
}


