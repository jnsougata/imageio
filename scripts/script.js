let button = document.getElementById("upload");
let hiddenInput = document.getElementById("files");
let image = document.getElementById("placeholder");
let copyButtom = document.getElementById("copy");
let matrix = document.getElementById("matrix");


function handleFile(file) {
    let reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = function() {
        button.disabled = true;
        let canvas = document.createElement("canvas");
            let ctx = canvas.getContext("2d");
            let img = new Image();
            img.src = reader.result;
            img.onload = function() {
                let width = img.width;
                let height = img.height;
                if (height > 400) {
                    width = width * (500 / height);
                    height = 400;
                }
                canvas.width = width;
                canvas.height = height;
                ctx.drawImage(img, 0, 0, width, height);
                image.src = canvas.toDataURL();
            }
            image.style.width = "100%";
            image.style.height = "auto";
        let data = {"data": reader.result}
        fetch(`/upload/${file.name}`, {method: "POST", body: JSON.stringify(data)})
        .then(response => response.json())
        .then(json_resp => {
            let resolved = window.location.href + json_resp.hash;
            let urlView = document.getElementById("url");
            urlView.value = resolved;
            matrix.style.display = "flex";
        })
    }
}

button.addEventListener("click", function() {
    hiddenInput.click();
}); 

hiddenInput.addEventListener("change", function() {
    let file = hiddenInput.files[0]
    if (file) {
        handleFile(file);
    }
})

copyButtom.addEventListener("click", function() {
    navigator.clipboard.writeText(document.getElementById("url").value);
    let prompt = document.getElementById("prompt");
    prompt.innerHTML = "URL copied to clipboard!";
    setTimeout(function() {
        prompt.innerHTML = "Drop - Paste - Upload";
        matrix.style.display = "none";
        image.src = "/assets/upload.png";
        image.style.width = "200px";
        image.style.height = "200px";
        button.disabled = false;
    }, 1000);
}); 

// file drop callback
function dropHandler(ev) {
    ev.preventDefault();
    if (ev.dataTransfer.items) {
        let file = ev.dataTransfer.items[0].getAsFile();
        if (file.type.startsWith("image/")) {
            handleFile(file);
        }
    }
}

// overrided default file drop event
function dragOverHandler(ev) {
    ev.preventDefault();
}

// detect file paste
document.addEventListener("paste", function(e) {
    let file = e.clipboardData.files[0];
    if (file && file.type.startsWith("image/")) {
        handleFile(file);
    }
});