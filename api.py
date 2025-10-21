# -*- coding: utf-8 -*-
from flask import Blueprint, request, send_file, abort, render_template_string, current_app
import io, base64, os, logging, traceback
import numpy as np
import cv2

from processors import remove_bg_grabcut, remove_bg_rembg

api_bp = Blueprint("api", __name__)
log = logging.getLogger(__name__)

# ----------------------------
# Helpers
# ----------------------------
def _decode_bgr(img_bytes: bytes):
    """Decode bytes -> BGR(A) bằng OpenCV. Raise 400 nếu lỗi."""
    arr = np.frombuffer(img_bytes, np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    if bgr is None:
        abort(400, "Khong doc duoc anh")  # tránh unicode nếu bạn lưu ANSI
    return bgr

def _process_image(img_bytes: bytes, engine: str):
    """
    Xoa nen theo engine: 'rembg' (mac dinh) hoac 'grabcut'.
    Co fallback sang grabcut neu AI loi.

    Tra ve: (out_bytes, used_engine, (w0,h0), (w1,h1), fallback)
    """
    engine = (engine or "rembg").lower()

    # Kich thuoc anh goc
    bgr0 = _decode_bgr(img_bytes)
    h0, w0 = bgr0.shape[:2]

    used_engine = engine
    fallback = False

    try:
        if engine == "grabcut":
            out_bytes = remove_bg_grabcut(bgr0)
        else:
            out_bytes = remove_bg_rembg(img_bytes)  # rembg dung bytes
    except Exception as e:
        # Ghi log & fallback
        log.error("Engine '%s' failed: %s\n%s", engine, e, traceback.format_exc())
        out_bytes = remove_bg_grabcut(bgr0)
        used_engine = f"{engine} -> grabcut"
        fallback = True

    # Kich thuoc anh ket qua (phong khi khac)
    try:
        bgr1 = _decode_bgr(out_bytes)
        h1, w1 = bgr1.shape[:2]
    except Exception:
        h1, w1 = h0, w0

    return out_bytes, used_engine, (w0, h0), (w1, h1), fallback

def _badge_class(used_engine: str, fallback: bool) -> str:
    return "badge bg-warning text-dark" if fallback or "->" in used_engine else "badge bg-secondary"


# ===============================================
# 1) Tra file PNG: POST /remove-bg
# ===============================================
@api_bp.post("/remove-bg")
def remove_bg():
    if "image" not in request.files:
        abort(400, "Thiếu file ảnh 'image'")
    img_bytes = request.files["image"].read()

    engine = (request.form.get("engine") or request.args.get("engine") or "rembg").lower()
    out_bytes, used_engine, _, _, _ = _process_image(img_bytes, engine)

    resp = send_file(io.BytesIO(out_bytes), mimetype="image/png", download_name="removed.png")
    resp.headers["X-Engine-Used"] = used_engine
    return resp


# =========================================================
# 2) Tra HTML fragment (HTMX): POST /remove-bg-frag
# =========================================================
@api_bp.post("/remove-bg-frag")
def remove_bg_frag():
    if "image" not in request.files:
        abort(400, "Thiếu file ảnh 'image'")
    img_bytes = request.files["image"].read()

    engine = (request.form.get("engine") or request.args.get("engine") or "rembg").lower()
    out_bytes, used_engine, (w0, h0), (w1, h1), fallback = _process_image(img_bytes, engine)

    result_b64 = base64.b64encode(out_bytes).decode("ascii")
    orig_b64   = base64.b64encode(img_bytes).decode("ascii")
    badge_cls  = _badge_class(used_engine, fallback)

    html = '''
<div class="row g-4 align-items-start">
  <!-- Anh goc -->
  <div class="col-lg-6">
    <h6 class="mb-2 text-muted">Ảnh gốc <span class="small text-secondary">({{ w0 }}×{{ h0 }})</span></h6>
    <div class="rb-box">
      <img src="data:image/*;base64,{{ orig_b64 }}" alt="Original" class="rb-img">
    </div>
  </div>

  <!-- Anh da tach nen -->
  <div class="col-lg-6">
    <div class="d-flex align-items-center justify-content-between mb-2">
      <h6 class="m-0 text-muted">Ảnh đã tách nền <span class="small text-secondary">({{ w1 }}×{{ h1 }})</span></h6>
      <div class="d-flex align-items-center gap-2">
        <span class="{{ badge_cls }}">Engine: {{ used_engine }}</span>
        <a class="btn btn-sm btn-success" download="removed.png" href="data:image/png;base64,{{ result_b64 }}">Tải ảnh</a>
      </div>
    </div>
    <div class="rb-box bg-checker">
      <img src="data:image/png;base64,{{ result_b64 }}" alt="Result" class="rb-img">
    </div>
  </div>
</div>
'''
    return render_template_string(
        html,
        orig_b64=orig_b64, result_b64=result_b64,
        w0=w0, h0=h0, w1=w1, h1=h1,
        used_engine=used_engine, badge_cls=badge_cls
    )


# =========================================================
# 3) Anh vi du (HTMX): POST /remove-bg-example
# =========================================================
@api_bp.post("/remove-bg-example")
def remove_bg_example():
    rel_path = (request.form.get("path") or "").strip()
    if not rel_path:
        abort(400, "Thiếu đường dẫn ảnh 'path'")
    if not rel_path.startswith("assets/img/examples/"):
        abort(400, "Đường dẫn không hợp lệ")

    static_root = current_app.static_folder
    abs_path = os.path.normpath(os.path.join(static_root, rel_path))
    if not abs_path.startswith(static_root) or not os.path.isfile(abs_path):
        abort(404, "Không tìm thấy ảnh ví dụ")

    with open(abs_path, "rb") as f:
        img_bytes = f.read()

    engine = (request.form.get("engine") or request.args.get("engine") or "rembg").lower()
    out_bytes, used_engine, (w0, h0), (w1, h1), fallback = _process_image(img_bytes, engine)

    result_b64 = base64.b64encode(out_bytes).decode("ascii")
    orig_b64   = base64.b64encode(img_bytes).decode("ascii")
    badge_cls  = _badge_class(used_engine, fallback)

    html = '''
<div class="row g-4 align-items-start">
  <div class="col-lg-6">
    <h6 class="mb-2 text-muted">Ảnh gốc <span class="small text-secondary">({{ w0 }}×{{ h0 }})</span></h6>
    <div class="rb-box">
      <img alt="Original" src="data:image/*;base64,{{ orig_b64 }}" class="rb-img">
    </div>
  </div>
  <div class="col-lg-6">
    <div class="d-flex align-items-center justify-content-between mb-2">
      <h6 class="m-0 text-muted">Ảnh đã tách nền <span class="small text-secondary">({{ w1 }}×{{ h1 }})</span></h6>
      <div class="d-flex align-items-center gap-2">
        <span class="{{ badge_cls }}">Engine: {{ used_engine }}</span>
        <a class="btn btn-sm btn-success" download="removed.png" href="data:image/png;base64,{{ result_b64 }}">Tải ảnh</a>
      </div>
    </div>
    <div class="rb-box bg-checker">
      <img alt="Result" src="data:image/png;base64,{{ result_b64 }}" class="rb-img">
    </div>
  </div>
</div>
'''
    return render_template_string(
        html,
        orig_b64=orig_b64, result_b64=result_b64,
        w0=w0, h0=h0, w1=w1, h1=h1,
        used_engine=used_engine, badge_cls=badge_cls
    )
# Thêm vào cuối api.py

@api_bp.errorhandler(400)
def _h400(e):
    html = '<div class="alert alert-danger">Lỗi 400: {{msg}}</div>'
    return render_template_string(html, msg=str(e)), 400

@api_bp.errorhandler(500)
def _h500(e):
    html = '<div class="alert alert-danger">Lỗi 500: {{msg}}</div>'
    return render_template_string(html, msg=str(e)), 500
