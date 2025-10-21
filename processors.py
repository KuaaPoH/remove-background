# processors.py  --- SAFE MINIMAL VERSION (ASCII only)

import numpy as np
import cv2


def remove_bg_grabcut(bgr):
    """
    Remove background using OpenCV GrabCut.
    Input:  BGR ndarray
    Output: PNG bytes (RGBA)
    """
    if bgr is None:
        raise ValueError("Empty input image")

    h, w = bgr.shape[:2]
    pad = max(4, int(0.03 * min(h, w)))
    rect = (pad, pad, max(1, w - 2 * pad), max(1, h - 2 * pad))

    mask = np.zeros((h, w), np.uint8)
    bg_model = np.zeros((1, 65), np.float64)
    fg_model = np.zeros((1, 65), np.float64)

    # 5 iterations are usually enough
    cv2.grabCut(bgr, mask, rect, bg_model, fg_model, 5, cv2.GC_INIT_WITH_RECT)
    alpha = np.where((mask == 0) | (mask == 2), 0, 1).astype("uint8") * 255

    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = alpha

    ok, buf = cv2.imencode(".png", rgba)
    if not ok:
        raise RuntimeError("Failed to encode PNG")
    return buf.tobytes()


def remove_bg_rembg(img_bytes: bytes) -> bytes:
    """
    Remove background using rembg (ONNX).
    Import is done lazily here so the module can be imported even if rembg is not installed.
    Returns PNG bytes (RGBA).
    """
    try:
        # lazy import; raises ModuleNotFoundError if rembg/onnxruntime not installed
        from rembg import remove
    except Exception as e:
        raise RuntimeError(
            "rembg/onnxruntime is not installed. "
            "Install with: pip install -U rembg onnxruntime==1.18.1 "
            "(or onnxruntime-gpu==1.18.1 if you have CUDA)"
        ) from e

    # simplest call; no session cache to avoid import-time issues
    return remove(img_bytes)
