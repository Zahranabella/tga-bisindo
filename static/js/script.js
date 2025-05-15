// document.addEventListener("DOMContentLoaded", function () {
//     const uploadForm = document.getElementById("uploadForm");
//     const videoInput = document.getElementById("videoInput");
//     const messageDiv = document.getElementById("message");
//     const videoContainer = document.getElementById("videoContainer");
//     const videoElement = document.getElementById("uploadedVideo");

//     // Buat elemen loading
//     const loadingDiv = document.createElement("div");
//     loadingDiv.id = "loading";
//     loadingDiv.textContent = "Uploading...";
//     loadingDiv.style.display = "none";
//     loadingDiv.style.marginTop = "10px";
//     loadingDiv.style.fontWeight = "bold";
//     uploadForm.appendChild(loadingDiv);

//     uploadForm.addEventListener("submit", function (event) {
//         event.preventDefault();

//         const file = videoInput.files[0];
//         if (!file) {
//             messageDiv.textContent = "Please select a video file to upload.";
//             return;
//         }

//         const formData = new FormData();
//         formData.append("video", file);

//         // Tampilkan loading
//         loadingDiv.style.display = "block";
//         messageDiv.textContent = "";

//         fetch("/", {
//             method: "POST",
//             body: formData
//         })
//             .then(response => response.json())
//             .then(data => {
//                 loadingDiv.style.display = "none"; // Sembunyikan loading setelah upload selesai
//                 if (data.video_path) {
//                     messageDiv.textContent = "Upload berhasil! Berikut hasil deteksi:";
//                     messageDiv.style.color = "#FFDAB3";
//                     loadingDiv.style.fontWeight = "bold";
//                     videoElement.src = data.video_path;
//                     videoContainer.style.display = "block";
//                 } else {
//                     messageDiv.textContent = "Gagal mengunggah video.";
//                     messageDiv.style.color = "#FFDAB3";
//                     loadingDiv.style.fontWeight = "bold";
//                 }
//             })
//             .catch(error => {
//                 loadingDiv.style.display = "none";
//                 messageDiv.textContent = "Terjadi kesalahan saat mengunggah file.";
//                 messageDiv.style.color = "#FFDAB3";
//                 loadingDiv.style.fontWeight = "bold";
//                 console.error("Upload error:", error);
//             });
//     });
// });


//PEMISAHNYA DISINI!!!
document.addEventListener("DOMContentLoaded", function () {
    const uploadForm = document.getElementById("uploadForm");
    const videoInput = document.getElementById("videoInput");
    const messageDiv = document.getElementById("message");
    const videoContainer = document.getElementById("videoContainer");
    const videoElement = document.getElementById("uploadedVideo");
    const labelResult = document.getElementById("labelResult");
    const videoSource = videoElement.querySelector("source");

    // 🔹 Buat elemen loading
    const loadingDiv = document.createElement("div");
    loadingDiv.id = "loading";
    loadingDiv.textContent = "Uploading...";
    loadingDiv.style.display = "none";
    loadingDiv.style.marginTop = "10px";
    loadingDiv.style.fontWeight = "bold";
    uploadForm.appendChild(loadingDiv);

    // 🔹 Event listener untuk upload video
    uploadForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const file = videoInput.files[0];
        if (!file) {
            messageDiv.textContent = "Please select a video file to upload.";
            return;
        }

        const formData = new FormData();
        formData.append("video", file);

        // Tampilkan loading
        loadingDiv.style.display = "block";
        messageDiv.textContent = "";

        fetch(window.location.pathname, {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            loadingDiv.style.display = "none";

            if (data.success) {
                // Pastikan <source> di dalam video di-set, lalu .load()
                videoSource.src = data.video_url + "?t=" + new Date().getTime(); // Hindari cache
                videoElement.load(); // Reload video
                videoContainer.style.display = "block";

                messageDiv.textContent = "Upload berhasil!";
                messageDiv.style.color = "#FFDAB3";

                // Tampilkan label hasil deteksi
                labelResult.innerHTML = `<strong>Versi Teks:</strong> ${data.hasil}`;
                labelResult.style.display = "block";
            } else {
                messageDiv.textContent = "Gagal mengunggah video.";
                messageDiv.style.color = "#FFDAB3";
            }
        })
        .catch(error => {
            loadingDiv.style.display = "none";
            messageDiv.textContent = "Terjadi kesalahan saat mengunggah file.";
            messageDiv.style.color = "#FFDAB3";
            console.error("Upload error:", error);
        });
    });
});


// document.addEventListener("DOMContentLoaded", function () {
//     const uploadDetectForm = document.getElementById("uploadDetectForm");
//     const uploadDatasetForm = document.getElementById("uploadDatasetForm");

//     const videoInput = document.getElementById("videoInput");
//     const fileInput = document.getElementById("fileInput");
//     const labelInput = document.getElementById("labelInput");

//     const messageDiv = document.getElementById("message");
//     const videoContainer = document.getElementById("videoContainer");
//     const videoElement = document.getElementById("uploadedVideo");
//     const datasetList = document.getElementById("datasetList");

//     // 🔄 Buat elemen loading
//     const loadingDiv = document.createElement("div");
//     loadingDiv.id = "loading";
//     loadingDiv.textContent = "⏳ Uploading...";
//     loadingDiv.style.display = "none";
//     loadingDiv.style.marginTop = "10px";
//     loadingDiv.style.fontWeight = "bold";
//     messageDiv.appendChild(loadingDiv);

//     // 🚀 Form Upload dan Deteksi
//     uploadDetectForm.addEventListener("submit", function (event) {
//         event.preventDefault();

//         const file = videoInput.files[0];
//         if (!file) {
//             messageDiv.textContent = "📁 Silakan pilih file video atau gambar.";
//             return;
//         }

//         const formData = new FormData();
//         formData.append("video", file);

//         loadingDiv.style.display = "block";
//         messageDiv.textContent = "";

//         fetch("/", {
//             method: "POST",
//             body: formData
//         })
//             .then(response => response.json())
//             .then(data => {
//                 loadingDiv.style.display = "none";
//                 if (data.video_path) {
//                     messageDiv.textContent = "Upload berhasil! Hasil deteksi: " + data.detected_labels.join(", ");
//                     videoElement.src = data.video_path;
//                     videoContainer.style.display = "block";
//                 } else {
//                     messageDiv.textContent = "Gagal mengunggah video.";
//                 }
//             })
            
//             .catch(error => {
//                 loadingDiv.style.display = "none";
//                 messageDiv.textContent = "Terjadi kesalahan saat mengunggah.";
//                 console.error("Upload error:", error);
//             });
//     });

//     // 🧠 Form Upload Dataset dengan Label
//     uploadDatasetForm.addEventListener("submit", function (event) {
//         event.preventDefault();

//         const file = fileInput.files[0];
//         const label = labelInput.value.trim();

//         if (!file || label === "") {
//             messageDiv.textContent = "📁 File dan label harus diisi!";
//             messageDiv.style.color = "red";
//             return;
//         }

//         const formData = new FormData();
//         formData.append("file", file);
//         formData.append("label", label);

//         loadingDiv.style.display = "block";
//         messageDiv.textContent = "";

//         fetch("/upload", {
//             method: "POST",
//             body: formData
//         })
//             .then(response => response.json())
//             .then(data => {
//                 loadingDiv.style.display = "none";

//                 if (data.error) {
//                     messageDiv.textContent = `Error: ${data.error}`;
//                 } else {
//                     messageDiv.textContent = `📦 File ${data.filename} berhasil diunggah dengan label "${data.label}"`;
//                     const listItem = document.createElement("li");
//                     listItem.textContent = `${data.filename} - Label: ${data.label}`;
//                     datasetList.appendChild(listItem);

//                     fileInput.value = "";
//                     labelInput.value = "";
//                 }
//             });
//     });

//     // 📂 Load Dataset yang Sudah Ada
//     function loadDataset() {
//         fetch("/dataset")
//             .then(response => response.json())
//             .then(data => {
//                 datasetList.innerHTML = "";
//                 for (let [filename, label] of Object.entries(data)) {
//                     let listItem = document.createElement("li");
//                     listItem.textContent = `${filename} - Label: ${label}`;
//                     datasetList.appendChild(listItem);
//                 }
//             });
//     }

//     // ⏬ Panggil saat halaman selesai dimuat
//     loadDataset();
// });
