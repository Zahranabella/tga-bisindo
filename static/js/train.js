document.getElementById('trainForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const epochs = document.getElementById('epochs').value;
    const batchSize = document.getElementById('batchSize').value;

    document.getElementById('trainStatus').textContent = 'Model sedang dilatih...';

    try {
        const response = await fetch('/train', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ epochs, batchSize })
        });

        const result = await response.json();
        document.getElementById('trainStatus').textContent = result.message;
    } catch (error) {
        document.getElementById('trainStatus').textContent = 'Gagal memulai pelatihan.';
    }
});
