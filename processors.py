# processors.py
import numpy as np
import cv2

def remove_bg_grabcut(bgr):
    """Tách nền bằng OpenCV GrabCut, trả về PNG bytes (RGBA)."""
    if bgr is None:
        raise ValueError("Ảnh đầu vào rỗng")

    h, w = bgr.shape[:2]
    pad = max(4, int(0.03 * min(h, w)))
    rect = (pad, pad, max(1, w - 2 * pad), max(1, h - 2 * pad))

    mask = np.zeros((h, w), np.uint8)
    bgModel = np.zeros((1, 65), np.float64)
    fgModel = np.zeros((1, 65), np.float64)

    cv2.grabCut(bgr, mask, rect, bgModel, fgModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 0) | (mask == 2), 0, 1).astype("uint8")

    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = mask2 * 255

    ok, buf = cv2.imencode(".png", rgba)
    if not ok:
        raise RuntimeError("Không encode được PNG")
    return buf.tobytes()

def remove_bg_rembg(img_bytes):
    """
    Tách nền bằng rembg (U^2-Net). Trả về PNG bytes (RGBA).
    Import tại chỗ để không bắt buộc cài rembg nếu chỉ dùng GrabCut.
    """
    from rembg import remove  # sẽ lỗi ImportError nếu chưa cài
    return remove(img_bytes)
