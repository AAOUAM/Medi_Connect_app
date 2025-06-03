document.addEventListener('DOMContentLoaded', () => {
  const links = document.querySelectorAll('.sidebar-nav li a');
  links.forEach(link => {
    if (link.href === window.location.href) {
      link.parentElement.classList.add('active');
    }
  });
});
