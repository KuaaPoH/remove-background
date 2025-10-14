# api.py
from flask import Blueprint, request, send_file, abort
import io
import numpy as np
import cv2
from processors import remove_bg_grabcut, remove_bg_rembg

api_bp = Blueprint("api", __name__)

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
