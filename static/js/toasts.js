document.querySelectorAll('[data-toast]').forEach((toast) => {
    setTimeout(() => dismissToast(toast), 5000);
});

document.querySelectorAll('[data-toast] button').forEach((btn) => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        dismissToast(btn.closest('[data-toast]'));
    });
});

function dismissToast(toast) {
    toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(12px)';
    setTimeout(() => toast.remove(), 300);
}