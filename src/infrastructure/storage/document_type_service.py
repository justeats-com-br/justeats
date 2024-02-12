import imghdr
from io import BytesIO
from typing import Optional


class DocumentTypeService:
    def load_image_type(self, image: bytes) -> Optional[str]:
        with BytesIO(image) as f:
            image_type = imghdr.what(f)
            if not image_type:
                return None

            return f"image/{image_type}"
