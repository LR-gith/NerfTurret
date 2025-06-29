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