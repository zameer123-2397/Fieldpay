// mobile menu toggle
function toggleMenu(){
  const menu = document.getElementById('mobileMenu');
  const btn = document.getElementById('hamburgerBtn');
  const isOpen = menu.classList.toggle('open');
  btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
}
function closeMenu(){
  document.getElementById('mobileMenu').classList.remove('open');
  document.getElementById('hamburgerBtn').setAttribute('aria-expanded','false');
}

// scroll-reveal animation (used by any page with .reveal elements)
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in'); });
}, { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

// message toasts — auto slide-out after a few seconds
document.querySelectorAll('.toast').forEach((toast, i) => {
  setTimeout(() => {
    toast.classList.add('out');
    toast.addEventListener('animationend', () => toast.remove());
  }, 3200 + i * 300);
});
