document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('floor-canvas');
    const REFRESH_INTERVAL_MS = 15000;

    const statusColors = {
        free: 'var(--color-concrete)',
        turning_soon: 'var(--color-maple)',
        seated: 'var(--color-vermillion)',
    };

    const statusTextColors = {
        free: 'var(--color-ink)',
        turning_soon: 'var(--color-ink)',
        seated: 'var(--color-paper)',
    };

    function loadFloorStatus() {
        fetch('/tables/floor-status-data/')
            .then(res => res.json())
            .then(tables => {
                canvas.innerHTML = '';
                tables.forEach(renderTable);
            });
    }

    function renderTable(table) {
        const el = document.createElement('div');
        el.className = 'absolute flex items-center justify-center text-xs font-body rounded border border-ink/10 transition-colors';
        el.style.left = `${table.position_x}px`;
        el.style.top = `${table.position_y}px`;
        el.style.width = `${table.width}px`;
        el.style.height = `${table.height}px`;
        el.style.backgroundColor = statusColors[table.status] || statusColors.free;
        el.style.color = statusTextColors[table.status] || statusTextColors.free;
        el.textContent = table.name;
        canvas.appendChild(el);
    }

    loadFloorStatus();
    setInterval(loadFloorStatus, REFRESH_INTERVAL_MS);
});