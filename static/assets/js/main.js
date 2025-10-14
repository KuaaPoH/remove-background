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
 * ===== HERO DROPZONE + BACKEND CALL (POPUP + LOADING) =====
 * - Bấm "Bắt đầu từ một ảnh" => mở chọn file thiết bị
 * - Chọn/kéo-thả ảnh => gửi /remove-bg
 * - Trong lúc chờ: mở modal + spinner
 * - Xong: hiện 2 ảnh + nút Tải
 * ========================================================== */
function initHeroDropzone() {
  const dz        = document.querySelector('.pr-dropzone');
  if (!dz) return;

  const inner     = dz.querySelector('.pr-drop-inner');
  const btn       = dz.querySelector('.pr-cta');
  let   fileInput = document.getElementById('fileInput');

  // === Modal so sánh (đã thêm trong index.html) ===
  const compareModalEl = document.getElementById('compareModal');
  const modalOrig      = document.getElementById('modalOrig');
  const modalRes       = document.getElementById('modalRes');
  const modalDownload  = document.getElementById('modalDownload');
  // holder để cắm spinner (nếu bạn bọc bằng div#origHolder/#resHolder thì giữ id đó;
  // nếu không có, spinner vẫn cắm vào cha của ảnh)
  const origHolder     = document.getElementById('origHolder') || modalOrig?.parentElement;
  const resHolder      = document.getElementById('resHolder')  || modalRes?.parentElement;

  let compareModal; // khởi tạo khi cần
  let spinner;      // spinner Bootstrap

  // Config engine
  const { ENGINE } = window.APP_CONFIG || { ENGINE: "rembg" };

  // ===== Helpers =====
  function showMainPreview(src) {
    inner.innerHTML = "";
    const img = document.createElement('img');
    img.src = src;
    img.alt = 'preview';
    img.style.maxWidth   = '100%';
    img.style.maxHeight  = '360px';
    img.style.borderRadius = '12px';
    img.style.boxShadow  = '0 8px 24px rgba(17,24,39,.14)';
    inner.appendChild(img);

    const actions = document.createElement('div');
    actions.className = 'mt-3';
    actions.innerHTML = `<button class="btn btn-sm btn-secondary" id="pr-change">Chọn ảnh khác</button>`;
    inner.appendChild(actions);
    inner.querySelector('#pr-change')?.addEventListener('click', () => fileInput.click());

    dz.style.height = 'auto';
    dz.style.minHeight = '300px';
  }

  // Tạo spinner (Bootstrap) gắn vào holder
  function attachSpinner(holder) {
    if (!holder) return;
    // xóa spinner cũ nếu có
    holder.querySelector('.rb-spinner-wrap')?.remove();
    const wrap = document.createElement('div');
    wrap.className = 'rb-spinner-wrap d-flex justify-content-center align-items-center';
    wrap.style.minHeight = '220px';
    wrap.innerHTML = `
      <div class="spinner-border" role="status" style="width:3rem;height:3rem;">
        <span class="visually-hidden">Loading...</span>
      </div>
    `;
    holder.appendChild(wrap);
    return wrap;
  }
  function detachSpinner(holder) {
    holder?.querySelector('.rb-spinner-wrap')?.remove();
  }

  // Bật modal + loading
  function startLoading(origURL) {
    // gán ảnh gốc vào modal (nếu có)
    if (origURL) modalOrig.src = origURL;

    // modal
    if (!compareModal) {
      compareModal = new bootstrap.Modal(compareModalEl, { backdrop: 'static' });
    }
    compareModal.show();

    // spinner ở cột kết quả
    spinner = attachSpinner(resHolder);

    // tạm thời clear ảnh kết quả + vô hiệu nút tải
    modalRes.removeAttribute('src');
    modalDownload.removeAttribute('href');
  }

  // Tắt loading + hiển thị ảnh kết quả
  function stopLoading(resultURL) {
    detachSpinner(resHolder);
    if (resultURL) {
      modalRes.src = resultURL;
      modalDownload.href = resultURL;
    }
  }

  async function processImageFile(file) {
    const fd = new FormData();
    fd.append("image", file);
    const res = await fetch(`/remove-bg?engine=${encodeURIComponent(ENGINE)}`, {
      method: "POST",
      body: fd
    });
    if (!res.ok) throw new Error(await res.text() || "Xử lý thất bại");
    const blob = await res.blob();
    return URL.createObjectURL(blob); // resultURL
  }

  // ===== Nút "Bắt đầu từ một ảnh" => mở hộp chọn file =====
  btn?.addEventListener('click', (e) => {
    e.preventDefault();
    fileInput?.click();
  });

  // ===== Input ẩn =====
  if (!fileInput) {
    fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.hidden = true;
    fileInput.id = 'fileInput';
    dz.appendChild(fileInput);
  }

  // Click vùng trống dropzone => mở chọn file
  dz.addEventListener('click', (e) => {
    if (e.target === dz || e.target === inner) fileInput.click();
  });

  // Chọn file từ thiết bị
  fileInput.addEventListener('change', async () => {
    const f = fileInput.files && fileInput.files[0];
    if (!f || !f.type.startsWith('image/')) return;

    const origURL = URL.createObjectURL(f);
    showMainPreview(origURL);

    try {
      startLoading(origURL);                         // mở modal + spinner
      const resultURL = await processImageFile(f);  // gọi backend
      stopLoading(resultURL);                       // hiển thị kết quả
    } catch (err) {
      stopLoading();                                // đảm bảo tắt spinner
      console.error(err);
      alert("Xử lý thất bại: " + err.message);
    }
  });

  // Drag & drop
  ['dragenter','dragover'].forEach(ev =>
    dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.add('dragging'); })
  );
  ['dragleave','drop'].forEach(ev =>
    dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.remove('dragging'); })
  );
  dz.addEventListener('drop', async (e) => {
    const f = e.dataTransfer?.files?.[0];
    if (!f || !f.type.startsWith('image/')) return;

    const origURL = URL.createObjectURL(f);
    showMainPreview(origURL);

    try {
      startLoading(origURL);
      const resultURL = await processImageFile(f);
      stopLoading(resultURL);
    } catch (err) {
      stopLoading();
      console.error(err);
      alert("Xử lý thất bại: " + err.message);
    }
  });

  // Ảnh ví dụ trong HTML
  window.showExampleImage = async function (src) {
    try {
      const resp = await fetch(src);
      const blob = await resp.blob();
      const file = new File([blob], "example.jpg", { type: blob.type || "image/jpeg" });

      const origURL = URL.createObjectURL(file);
      showMainPreview(origURL);

      startLoading(origURL);
      const resultURL = await processImageFile(file);
      stopLoading(resultURL);
    } catch (err) {
      stopLoading();
      console.error(err);
      alert("Không xử lý được ảnh ví dụ: " + err.message);
    }
  };
}

// Khởi tạo sau khi DOM sẵn sàng
window.addEventListener('load', initHeroDropzone);
})(); // đóng IIFE

