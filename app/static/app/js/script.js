document.addEventListener('DOMContentLoaded', function () {
  // ===== 1. Smooth Scrolling for Anchor Links =====
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const target = document.querySelector(targetId);
      if (target) {
        window.scrollTo({
          top: target.offsetTop - 20,
          behavior: 'smooth'
        });
      }
    });
  });

  // ===== 2. Sticky Navigation with Scroll Detection =====
  const nav = document.querySelector('.nav');
  let lastScrollTop = 0;

  window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Add/remove 'scrolled' class for shadow
    if (scrollTop > 10) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }

    // Optional: hide nav on scroll down, show on scroll up (advanced)
    // if (scrollTop > lastScrollTop && scrollTop > 100) {
    //   nav.style.transform = 'translateY(-100%)';
    // } else {
    //   nav.style.transform = 'translateY(0)';
    // }
    lastScrollTop = scrollTop;
  });

  // ===== 3. Form Enhancements =====
  // Auto-focus first input in forms
  const firstInput = document.querySelector('form input, form textarea, form select');
  if (firstInput && !firstInput.hasAttribute('noautofocus')) {
    // Small delay to ensure DOM is ready
    setTimeout(() => firstInput.focus(), 100);
  }

  // Prevent accidental double-submission
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function () {
      const submitBtn = this.querySelector('[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
      }
    });
  });

  // ===== 4. Page Load Animation =====
  const pageContent = document.querySelector('.content');
  if (pageContent) {
    // Fade in content after small delay for perceived performance
    setTimeout(() => {
      pageContent.classList.add('page-enter-active');
    }, 50);
  }

  // ===== 5. Accessibility: Skip to Content Link =====
  const skipLink = document.createElement('a');
  skipLink.href = '#main-content';
  skipLink.textContent = 'Skip to main content';
  skipLink.className = 'skip-link';
  skipLink.style.cssText = `
    position: absolute;
    top: -40px;
    left: 6px;
    background: #000;
    color: #fff;
    padding: 8px;
    text-decoration: none;
    z-index: 1000;
    border-radius: 4px;
  `;
  skipLink.addEventListener('focus', () => {
    skipLink.style.top = '6px';
  });
  skipLink.addEventListener('blur', () => {
    skipLink.style.top = '-40px';
  });
  document.body.prepend(skipLink);

  // Add ID to main content if missing
  const mainContent = document.querySelector('main');
  if (mainContent && !mainContent.id) {
    mainContent.id = 'main-content';
  }

  // ===== 6. Radio Button Enhancement (Quiz UI) =====
  // Ensure keyboard navigation works smoothly for radio groups
  document.querySelectorAll('.radio-group').forEach(group => {
    const radios = group.querySelectorAll('.radio-input');
    if (radios.length > 0) {
      // Arrow key navigation
      group.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
          e.preventDefault();
          const currentIndex = Array.from(radios).findIndex(r => r === document.activeElement);
          let newIndex;
          if (e.key === 'ArrowDown') {
            newIndex = (currentIndex + 1) % radios.length;
          } else {
            newIndex = (currentIndex - 1 + radios.length) % radios.length;
          }
          radios[newIndex].focus();
        }
      });
    }
  });
});

// ===== Performance: Defer non-critical JS =====
// Optional: Load heavy scripts after page load
// window.addEventListener('load', () => {
//   // e.g., analytics, non-critical widgets
// });