/**
* Template Name: Landio
* Template URL: https://bootstrapmade.com/landio-bootstrap-landing-page-template/
* Updated: Sep 06 2025 with Bootstrap v5.3.8
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function() {
  "use strict";

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');
    if (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top')) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  /**
   * Mobile nav toggle
   */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');

  function mobileNavToogle() {
    document.querySelector('body').classList.toggle('mobile-nav-active');
    mobileNavToggleBtn.classList.toggle('bi-list');
    mobileNavToggleBtn.classList.toggle('bi-x');
  }
  if (mobileNavToggleBtn) {
    mobileNavToggleBtn.addEventListener('click', mobileNavToogle);
  }

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll('#navmenu a').forEach(navmenu => {
    navmenu.addEventListener('click', () => {
      if (document.querySelector('.mobile-nav-active')) {
        mobileNavToogle();
      }
    });

  });

  /**
   * Toggle mobile nav dropdowns
   */
  document.querySelectorAll('.navmenu .toggle-dropdown').forEach(navmenu => {
    navmenu.addEventListener('click', function(e) {
      e.preventDefault();
      this.parentNode.classList.toggle('active');
      this.parentNode.nextElementSibling.classList.toggle('dropdown-active');
      e.stopImmediatePropagation();
    });
  });

  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
  }
  scrollTop?.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  /**
   * Animation on scroll function and init
   */
  function aosInit() {
    if (window.AOS) {
      AOS.init({
        duration: 600,
        easing: 'ease-in-out',
        once: true,
        mirror: false
      });
    }
  }
  window.addEventListener('load', aosInit);

  /**
   * Init swiper sliders
   */
  function initSwiper() {
    if (typeof Swiper === 'undefined') return;
    document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
      let config = JSON.parse(
        swiperElement.querySelector(".swiper-config").innerHTML.trim()
      );

      if (swiperElement.classList.contains("swiper-tab")) {
        initSwiperWithCustomPagination(swiperElement, config);
      } else {
        new Swiper(swiperElement, config);
      }
    });
  }

  window.addEventListener("load", initSwiper);

  /**
   * Frequently Asked Questions Toggle
   */
  document.querySelectorAll('.faq-item h3, .faq-item .faq-toggle, .faq-item .faq-header').forEach((faqItem) => {
    faqItem.addEventListener('click', () => {
      faqItem.parentNode.classList.toggle('faq-active');
    });
  });

  /**
   * Correct scrolling position upon page load for URLs containing hash links.
   */
  window.addEventListener('load', function(e) {
    if (window.location.hash) {
      if (document.querySelector(window.location.hash)) {
        setTimeout(() => {
          let section = document.querySelector(window.location.hash);
          let scrollMarginTop = getComputedStyle(section).scrollMarginTop;
          window.scrollTo({
            top: section.offsetTop - parseInt(scrollMarginTop),
            behavior: 'smooth'
          });
        }, 100);
      }
    }
  });

  /**
   * Navmenu Scrollspy
   */
  let navmenulinks = document.querySelectorAll('.navmenu a');

  function navmenuScrollspy() {
    navmenulinks.forEach(navmenulink => {
      if (!navmenulink.hash) return;
      let section = document.querySelector(navmenulink.hash);
      if (!section) return;
      let position = window.scrollY + 200;
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        document.querySelectorAll('.navmenu a.active').forEach(link => link.classList.remove('active'));
        navmenulink.classList.add('active');
      } else {
        navmenulink.classList.remove('active');
      }
    })
  }
  window.addEventListener('load', navmenuScrollspy);
  document.addEventListener('scroll', navmenuScrollspy);

  /* ==========================================================
   * ===== HERO DROPZONE (PhotoRoom-like) =====================
   * - Hỗ trợ click chọn ảnh, kéo-thả
   * - Hiển thị ảnh preview ngay trong khung caro
   * - Không phụ thuộc backend
   * ========================================================== */
  function initHeroDropzone() {
    const dz = document.querySelector('.pr-dropzone');
    if (!dz) return;

    const inner = dz.querySelector('.pr-drop-inner');
    const btn = dz.querySelector('.pr-cta');
    let fileInput = document.getElementById('fileInput');

    // nếu thiếu input ẩn, tạo luôn
    if (!fileInput) {
      fileInput = document.createElement('input');
      fileInput.type = 'file';
      fileInput.accept = 'image/*';
      fileInput.hidden = true;
      fileInput.id = 'fileInput';
      dz.appendChild(fileInput);
    }

    // click nút tím / click vùng dropzone -> mở chọn file
    btn?.addEventListener('click', (e) => {
      e.preventDefault();
      fileInput.click();
    });
    dz.addEventListener('click', (e) => {
      // chỉ khi click vào nền trống mới mở file (tránh click vào link)
      if (e.target === dz || e.target === inner) fileInput.click();
    });

    // xử lý file đã chọn
    fileInput.addEventListener('change', () => {
      if (fileInput.files && fileInput.files[0]) {
        previewImage(fileInput.files[0]);
      }
    });

    // drag & drop highlight
    ['dragenter','dragover'].forEach(ev =>
      dz.addEventListener(ev, e => {
        e.preventDefault();
        dz.classList.add('dragging');
      })
    );
    ['dragleave','drop'].forEach(ev =>
      dz.addEventListener(ev, e => {
        e.preventDefault();
        dz.classList.remove('dragging');
      })
    );

    dz.addEventListener('drop', (e) => {
      const files = e.dataTransfer?.files;
      if (files && files[0]) {
        previewImage(files[0]);
      }
    });

    // tạo/hiển thị preview
    function previewImage(file) {
      if (!file.type.startsWith('image/')) return;

      const reader = new FileReader();
      reader.onload = function(ev) {
        // xoá nội dung cũ (nút + hint) và render preview
        inner.innerHTML = '';
        const img = document.createElement('img');
        img.src = ev.target.result;
        img.alt = 'preview';
        img.style.maxWidth = '100%';
        img.style.maxHeight = '360px';
        img.style.borderRadius = '12px';
        img.style.boxShadow = '0 8px 24px rgba(17,24,39,.14)';
        inner.appendChild(img);

        // thêm dải nút phụ (chọn lại)
        const actions = document.createElement('div');
        actions.className = 'mt-3';
        actions.innerHTML = `
          <button class="btn btn-sm btn-secondary" id="pr-change">Chọn ảnh khác</button>
        `;
        inner.appendChild(actions);

        inner.querySelector('#pr-change')?.addEventListener('click', () => fileInput.click());
      };
      reader.readAsDataURL(file);
    }
  }

  // Khởi tạo sau khi DOM sẵn sàng
  window.addEventListener('load', initHeroDropzone);

})();
