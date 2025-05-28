import customtkinter as ctk
from PIL import Image
import os
import random

class ImageWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.base_dir = os.path.join(os.path.dirname(__file__), "Resources", "ads")
        image_path = self._get_random_image_path()

        image = Image.open(image_path)
        ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(image.width, image.height))

        self.geometry(f"{image.width}x{image.height}")
        self.title(f"Random Ad – {os.path.basename(image_path)}")

        label = ctk.CTkLabel(self, image=ctk_image, text="")
        label.image = ctk_image
        label.pack()

    def _get_random_image_path(self):
        if not os.path.isdir(self.base_dir):
            raise FileNotFoundError(f"[!] Ads folder not found at {self.base_dir}")

        images = [f for f in os.listdir(self.base_dir)
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if not images:
            raise ValueError(f"[!] No images found in folder: {self.base_dir}")

        return os.path.join(self.base_dir, random.choice(images))

if __name__ == "__main__":
    app = ImageWindow()
    app.mainloop()
