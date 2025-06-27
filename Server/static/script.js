document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const imgElement = document.getElementById('live-image');
    const logContainer = document.getElementById('log-container');
    let lastUpdateTime = 0;

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
        if (now - lastUpdateTime > 10) {
            imgElement.src = '/get_image?' + now;
            lastUpdateTime = now;
        }
    }

    function updateValues(values) {
        document.getElementById('conf-value').textContent = values.conf || '-';
        document.querySelector('.confidence-fill').style.width = (values.conf*100 || 0) + '%';
        document.getElementById('x-value').textContent = values.x || '-';
        document.getElementById('y-value').textContent = values.y || '-';
        document.getElementById('x-angle-value').textContent = values.x_angle || '-';
        document.getElementById('y-angle-value').textContent = values.y_angle || '-';
        const line = document.getElementById('y-angle-line');
        if (line) {
            line.style.transform = `rotate(${values.y_angle}deg)`;
        }
    }

    socket.on('update', (data) => {
        if (data.image_updated) {
            updateImage();
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