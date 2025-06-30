document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const imgElement = document.getElementById('live-image');
    const maskElement = document.getElementById('live-mask');
    const logContainer = document.getElementById('log-container');
    let lastUpdateTime_img = 0;
    let lastUpdateTime_mask = 0;

    function addLog(message) {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.innerHTML = `<span class="log-time">[${timeString}]</span> <span class="log-message">${message}</span>`;
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    function updateImage() {
        const now = Date.now();
        if (now - lastUpdateTime_img > 10) {
            imgElement.src = '/get_image?' + now;
            lastUpdateTime_img = now;
        }
    }

    function updateBothImages() {
        const now = Date.now();
        if (now - lastUpdateTime_img > 10) {
            imgElement.src = '/get_image?' + now;
            lastUpdateTime_img = now;
        }
        if (now - lastUpdateTime_mask > 10) {
            maskElement.src = '/get_mask?' + now;
            lastUpdateTime_mask = now;
        }
    }

    function updateValues(values) {
        document.getElementById('conf-value').textContent = values.conf || '-';
        document.querySelector('.confidence-fill').style.width = (values.conf*100 || 0) + '%';
        document.getElementById('x-value').textContent = values.x || '-';
        document.getElementById('y-value').textContent = values.y || '-';
        document.getElementById('relative-x-angle-value').textContent = values.relative_x_angle || '-';
        document.getElementById('relative-y-angle-value').textContent = values.relative_y_angle || '-';
        document.getElementById('absolut-x-angle-value').textContent = values.absolut_x_angle || '-';
        document.getElementById('absolut-y-angle-value').textContent = values.absolut_y_angle || '-';
        const relative_y_line = document.getElementById('relative-y-angle-line');
        if (relative_y_line) {
            relative_y_line.style.transform = `rotate(${values.relative_y_angle}deg)`;
        }
        const relative_x_line = document.getElementById('relative-x-angle-line');
        if (relative_x_line) {
            relative_x_line.style.transform = `rotate(${values.relative_x_angle}deg)`;
        }
        const absolut_y_line = document.getElementById('absolut-y-angle-line');
        if (absolut_y_line) {
            absolut_y_line.style.transform = `rotate(${values.absolut_y_angle-90}deg)`;
        }
        const absolut_x_line = document.getElementById('absolut-x-angle-line');
        if (absolut_x_line) {
            absolut_x_line.style.transform = `rotate(${values.absolut_x_angle-90}deg)`;
        }
    }

    socket.on('updateObjectDetection', (data) => {
        if (data.image_updated) {
            updateImage();
        }
        if (data.values) {
            updateValues(data.values);
        }
    });

    socket.on('updateColorDetection', (data) => {
        if (data.both_image_updated) {
            updateBothImages();
        }
        if (data.values) {
            updateValues(data.values);
        }
    });

    socket.on('log', (message) => {
        addLog(message)
    })

    addLog('System running');
    addLog('Waiting for data...');
});