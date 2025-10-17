from flask import Blueprint, request, send_file, abort, render_template_string, current_app
import io, base64, os

import numpy as np
import cv2
from processors import remove_bg_grabcut, remove_bg_rembg

api_bp = Blueprint("api", __name__)

# ===============================================
# 1) API trả file PNG: POST /remove-bg
#    - Dùng cho JS fetch/truyền thống (trả bytes ảnh)
# ===============================================
@api_bp.post("/remove-bg")
def remove_bg():
    # kiểm tra file
    if "image" not in request.files:
        abort(400, "Thiếu file ảnh 'image'")
    img_bytes = request.files["image"].read()

    # chọn engine: rembg (mặc định) hoặc grabcut
    engine = (request.args.get("engine") or "rembg").lower()

    try:
        if engine == "grabcut":
            arr = np.frombuffer(img_bytes, np.uint8)
            bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if bgr is None:
                abort(400, "Không đọc được ảnh")
            out_bytes = remove_bg_grabcut(bgr)
        else:
            # mặc định: rembg
            out_bytes = remove_bg_rembg(img_bytes)
    except Exception as e:
        # fallback sang GrabCut nếu AI lỗi
        try:
            arr = np.frombuffer(img_bytes, np.uint8)
            bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if bgr is None:
                abort(400, f"Lỗi xử lý ảnh: {e}")
            out_bytes = remove_bg_grabcut(bgr)
        except Exception as e2:
            abort(500, f"Xử lý thất bại: {e2}")

    return send_file(io.BytesIO(out_bytes), mimetype="image/png", download_name="removed.png")


# =========================================================
# 2) API trả HTML fragment: POST /remove-bg-frag
#    - Dùng với HTMX (hx-post) để Python “điều khiển” UX
#    - Flask render sẵn UI Before/After + nút Tải
# =========================================================
@api_bp.post("/remove-bg-frag")
def remove_bg_frag():
    if "image" not in request.files:
        abort(400, "Thiếu file ảnh 'image'")
    img_bytes = request.files["image"].read()

    engine = (request.form.get("engine") or request.args.get("engine") or "rembg").lower()


    try:
        if engine == "grabcut":
            arr = np.frombuffer(img_bytes, np.uint8)
            bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if bgr is None:
                abort(400, "Không đọc được ảnh")
            out_bytes = remove_bg_grabcut(bgr)
        else:
            out_bytes = remove_bg_rembg(img_bytes)
    except Exception:
        # fallback GrabCut
        arr = np.frombuffer(img_bytes, np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if bgr is None:
            abort(500, "Xử lý thất bại")
        out_bytes = remove_bg_grabcut(bgr)

    # Base64 cho <img>
    result_b64 = base64.b64encode(out_bytes).decode("ascii")
    orig_b64   = base64.b64encode(img_bytes).decode("ascii")

    # LƯU Ý: KHÔNG đặt tiền tố f trước chuỗi! (không dùng f""" ... """)
    html = '''
<div class="row g-4 align-items-start">
  <!-- Ảnh gốc: không nền caro -->
  <div class="col-md-6">
    <h6 class="mb-2">Ảnh gốc</h6>
    <div class="rb-fit">
      <img alt="Original"
           src="data:image/*;base64,{{ orig_b64 }}"
           class="img-fluid rb-img">
    </div>
  </div>

  <!-- Ảnh đã tách nền: có nền caro ở phía sau -->
  <div class="col-md-6">
    <div class="d-flex align-items-center justify-content-between mb-2">
      <h6 class="m-0">Ảnh đã tách nền</h6>
      <a class="btn btn-sm btn-success" download="removed.png"
         href="data:image/png;base64,{{ result_b64 }}">Tải ảnh</a>
    </div>

    <!-- NỀN CARO chỉ bọc riêng ảnh kết quả -->
    <div class="rb-fit bg-checker rounded">
      <img alt="Result"
           src="data:image/png;base64,{{ result_b64 }}"
           class="img-fluid rb-img">
    </div>
  </div>
</div>
'''

    return render_template_string(html, orig_b64=orig_b64, result_b64=result_b64)

@api_bp.post("/remove-bg-example")
def remove_bg_example():
    # nhận đường dẫn tương đối trong static
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

    try:
        if engine == "grabcut":
            arr = np.frombuffer(img_bytes, np.uint8)
            bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if bgr is None:
                abort(400, "Không đọc được ảnh")
            out_bytes = remove_bg_grabcut(bgr)
        else:
            out_bytes = remove_bg_rembg(img_bytes)
    except Exception:
        arr = np.frombuffer(img_bytes, np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if bgr is None:
            abort(500, "Xử lý thất bại")
        out_bytes = remove_bg_grabcut(bgr)

    result_b64 = base64.b64encode(out_bytes).decode("ascii")
    orig_b64   = base64.b64encode(img_bytes).decode("ascii")

    html = '''
<div class="row g-4 align-items-start">
  <div class="col-md-6">
    <h6 class="mb-2">Ảnh gốc</h6>
    <div class="rb-fit">
      <img alt="Original" src="data:image/*;base64,{{ orig_b64 }}" class="img-fluid rb-img">
    </div>
  </div>
  <div class="col-md-6">
    <div class="d-flex align-items-center justify-content-between mb-2">
      <h6 class="m-0">Ảnh đã tách nền</h6>
      <a class="btn btn-sm btn-success" download="removed.png" href="data:image/png;base64,{{ result_b64 }}">Tải ảnh</a>
    </div>
    <div class="rb-fit bg-checker rounded">
      <img alt="Result" src="data:image/png;base64,{{ result_b64 }}" class="img-fluid rb-img">
    </div>
  </div>
</div>
'''
    return render_template_string(html, orig_b64=orig_b64, result_b64=result_b64)