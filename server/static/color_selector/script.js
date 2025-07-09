document.addEventListener('DOMContentLoaded', () => {
    const image = document.getElementById('image');
    const removeAllButton = document.getElementById('remove-all-button');
    const buttonUpdateImg = document.getElementById('button-update-image');
    const confirmButton = document.getElementById('confirm-button');
    const selectionContainer = document.getElementById('color-selection-container')
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    let colorCount = 1;
    let lastUpdateTime_img = 0;

    image.onload = () => {
        canvas.width = image.width;
        canvas.height = image.height;
        ctx.drawImage(image, 0, 0);
    };

    function updateImage() {
        const now = Date.now();
        if (now - lastUpdateTime_img > 10) {
            image.src = '/get_image?' + now;
            lastUpdateTime_img = now;
        }
    }

    function removeAllEntries(){
        const colorEntries = selectionContainer.querySelectorAll('.color-entry');
        colorEntries.forEach((entry) => {entry.remove();});
        colorCount = 1;
    }

    function addColorEntry(hexCode) {
        const colorEntry = document.createElement('div');
        colorEntry.className = 'color-entry';
        colorEntry.innerHTML = `<span class="color-count">${colorCount}.</span> <span class="color">${hexCode}</span>
                                <div class="color-display" style="background-color: ${hexCode}"></div>
                                <button class="del-color-entry" type="button"><i class="fas fa-trash"></i></button>`;
        selectionContainer.appendChild(colorEntry);
        selectionContainer.scrollTop = selectionContainer.scrollHeight;

        const deleteButton = colorEntry.querySelector('.del-color-entry');
        deleteButton.addEventListener('click', () => {
            colorEntry.remove();
            updateColorCounts()
            colorCount-=1;
        });

        colorCount+=1;
    }

    function updateColorCounts() {
    const colorEntries = selectionContainer.querySelectorAll('.color-entry');
    colorEntries.forEach((entry, index) => {
        const countSpan = entry.querySelector('.color-count');
        countSpan.textContent = `${index + 1}.`;
    });
}

    buttonUpdateImg.addEventListener('click', updateImage)
    removeAllButton.addEventListener('click', removeAllEntries)
    image.addEventListener('click', (e) => {
        const rect = image.getBoundingClientRect();
        const x = Math.floor(e.clientX - rect.left);
        const y = Math.floor(e.clientY - rect.top);

        ctx.drawImage(image, 0, 0);

        const pixel = ctx.getImageData(x, y, 1, 1).data;
        const hexColor = rgbToHex(pixel[0], pixel[1], pixel[2]);

        addColorEntry(hexColor);
    });

    function rgbToHex(r, g, b) {
        return "#" + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('');
    }

    confirmButton.addEventListener('click', async () => {
        const colors = [];
        const colorEntries = selectionContainer.querySelectorAll('.color-entry');
        colorEntries.forEach((entry) => {
            colors.push(entry.querySelector('.color').textContent);
        });
        const response = await fetch('/updateColorSelections', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({colors: colors})
        });

        if (!response.ok) {
            alert('Failed to send');
        } else {
            window.location.assign("/");
        }
    });
});