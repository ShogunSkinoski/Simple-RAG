from ultralytics import YOLO
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCR:
    def __init__(self, weights):
        self.model = YOLO(weights)

    def get_image_position(self, image) -> list:
        position_list = []
        results = self.model.track(image, persist=True)
        for box in results[0].boxes:
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = xyxy
            obj_id = box.id[0].cpu().numpy().astype(int) if box.id is not None else -1
            position_list.append((obj_id, x1, y1, x2, y2))
        return position_list

    def _xyxy_to_xywh(self, x1, y1, x2, y2):
        return x1, y1, x2 - x1, y2 - y1
    
    def get_receipt_info(self, image) -> list:
        receipt_positions = self.get_image_position(image)
        receipt_info = []
        for position in receipt_positions:
            pos = position[1:]
            pos = self._xyxy_to_xywh(*pos)
            x, y, w, h = pos
            roi = image[y:y+h, x:x+w]
            text = pytesseract.image_to_string(roi, lang='tur')
            receipt_info.append(text)
        return receipt_info