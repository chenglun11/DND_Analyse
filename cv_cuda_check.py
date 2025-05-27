import cv2

if hasattr(cv2, 'cuda'):
    print("✅ OpenCV CUDA is available.")
else:
    print("❌ OpenCV CUDA is not available.")
