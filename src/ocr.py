import os
from paddleocr import PaddleOCR
import cv2
import numpy as np

class OCR:
    def __init__(self, lang='en', use_gpu=False):
        # Set environment variables
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
        os.environ['OMP_NUM_THREADS'] = '1'

        # Define model directories
        base_dir = os.path.dirname(os.path.abspath(__file__))
        det_model_dir = os.path.join(base_dir, 'models', 'det')
        rec_model_dir = os.path.join(base_dir, 'models', 'rec')
        cls_model_dir = os.path.join(base_dir, 'models', 'cls')

        self.ocr = PaddleOCR(use_angle_cls=True, 
                             lang=lang,
                             use_gpu=use_gpu,
                             det_model_dir=det_model_dir,
                             rec_model_dir=rec_model_dir,
                             cls_model_dir=cls_model_dir)

    def get_receipt_info(self, image):
        if isinstance(image, str):
            image = cv2.imread(image)
        elif isinstance(image, np.ndarray):
            pass
        else:
            raise ValueError("Unsupported image type. Please provide either a file path or a numpy array.")

        result = self.ocr.ocr(image, cls=True)
        
        extracted_text = []
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                extracted_text.append(line[1][0])  # Append the text content

        return ' '.join(extracted_text)  # Join all text into a single string

    def visualize(self, image, result):
        boxes = [line[0] for line in result]
        txts = [line[1][0] for line in result]
        scores = [line[1][1] for line in result]
        im_show = image.copy()
        
        for box, txt, score in zip(boxes, txts, scores):
            box = np.array(box).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(im_show, [box], True, color=(255, 0, 0), thickness=2)
            cv2.putText(im_show, f'{txt}', (int(box[0, 0, 0]), int(box[0, 0, 1])), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
        
        return im_show