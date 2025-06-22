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
    loadingDiv.style.color = "#FFDAB3";
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

                    if (document.body.id === "home-page") {
                        messageDiv.textContent = "Upload berhasil! Login untuk menyimpan riwayat deteksi.";
                    } else if (document.body.id === "dashboard-page") {
                        messageDiv.textContent = "Upload berhasil!";
                    }

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