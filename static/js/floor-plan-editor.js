document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('floor-canvas');
    let activeTable = null;
    let offsetX = 0;
    let offsetY = 0;

    fetch('/tables/floor-plan-data/')
        .then(res => res.json())
        .then(tables => tables.forEach(renderTable));

    function renderTable(table) {
        const el = document.createElement('div');
        el.className = table.is_fixed
            ? 'absolute flex items-center justify-center text-xs font-body bg-ink/60 text-paper border border-ink/20 rounded cursor-not-allowed'
            : 'absolute flex items-center justify-center text-xs font-body cursor-move bg-maple text-ink border border-ink/20 rounded';
        el.style.left = `${table.position_x}px`;
        el.style.top = `${table.position_y}px`;
        el.style.width = `${table.width}px`;
        el.style.height = `${table.height}px`;
        el.dataset.id = table.id;
        el.dataset.lastX = table.position_x;
        el.dataset.lastY = table.position_y;
        el.textContent = table.name;

        if (!table.is_fixed) {
            el.addEventListener('mousedown', (e) => {
                activeTable = el;
                offsetX = e.clientX - el.offsetLeft;
                offsetY = e.clientY - el.offsetTop;
            });
        }

        canvas.appendChild(el);
    }

    document.addEventListener('mousemove', (e) => {
        if (!activeTable) return;
        const canvasRect = canvas.getBoundingClientRect();
        let newX = e.clientX - offsetX;
        let newY = e.clientY - offsetY;

        newX = Math.max(0, Math.min(newX, canvasRect.width - activeTable.offsetWidth));
        newY = Math.max(0, Math.min(newY, canvasRect.height - activeTable.offsetHeight));

        activeTable.style.left = `${newX}px`;
        activeTable.style.top = `${newY}px`;
    });

    document.addEventListener('mouseup', () => {
        if (!activeTable) return;

        const snappedX = snapToGrid(parseFloat(activeTable.style.left));
        const snappedY = snapToGrid(parseFloat(activeTable.style.top));
        const allTables = Array.from(canvas.children);

        if (checkOverlap(activeTable, snappedX, snappedY, allTables)) {
            activeTable.style.left = `${activeTable.dataset.lastX}px`;
            activeTable.style.top = `${activeTable.dataset.lastY}px`;
        } else {
            activeTable.style.left = `${snappedX}px`;
            activeTable.style.top = `${snappedY}px`;
            activeTable.dataset.lastX = snappedX;
            activeTable.dataset.lastY = snappedY;
            savePosition(activeTable);
        }

        activeTable = null;
    });

    function checkOverlap(el, newX, newY, allTables) {
        const w = el.offsetWidth;
        const h = el.offsetHeight;
        return allTables.some(other => {
            if (other === el) return false;
            const ox = parseFloat(other.style.left);
            const oy = parseFloat(other.style.top);
            const ow = other.offsetWidth;
            const oh = other.offsetHeight;
            return newX < ox + ow && newX + w > ox && newY < oy + oh && newY + h > oy;
        });
    }

    function snapToGrid(value, gridSize = 10) {
        return Math.round(value / gridSize) * gridSize;
    }

    function savePosition(el) {
        fetch(`/tables/${el.dataset.id}/update-position/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                position_x: parseFloat(el.style.left),
                position_y: parseFloat(el.style.top),
            }),
        });
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});