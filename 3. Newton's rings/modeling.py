import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk


def wavelength_to_rgb(wavelength):
    wl = wavelength * 1e9
    if wl < 380:
        return 0, 0, 0
    elif wl < 440:
        attenuation = 0.3 + 0.7 * (wl - 380) / (60)
        return attenuation * (440 - wl) / 60, 0, attenuation
    elif wl < 490:
        return 0, (wl - 440) / 50, 1
    elif wl < 510:
        return 0, 1, (510 - wl) / 20
    elif wl < 580:
        return (wl - 510) / 70, 1, 0
    elif wl < 645:
        return 1, (645 - wl) / 65, 0
    elif wl <= 700:
        attenuation = 0.3 + 0.7 * (700 - wl) / 55
        return attenuation, 0, 0
    else:
        return 0, 0, 0


class NewtonRingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Кольца Ньютона")

        # Параметры по умолчанию
        self.R = 1.0  # Радиус кривизны (м)
        self.lambda0 = 500e-9  # Длина волны (м)
        self.delta_lambda = 10e-9  # Ширина спектра (м)
        self.size = 400  # Размер изображения
        self.mode = tk.StringVar(value="quasi")  # Режим освещения

        # Создание элементов интерфейса
        self.create_widgets()

        # Инициализация изображения
        self.update_image()

    def create_widgets(self):
        param_frame = ttk.Frame(self.root, padding=10)
        param_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(param_frame, text="Радиус кривизны (м):").pack()
        self.R_entry = ttk.Entry(param_frame)
        self.R_entry.insert(0, "1.0")
        self.R_entry.pack()

        ttk.Label(param_frame, text="Длина волны (нм):").pack()
        self.lambda_entry = ttk.Entry(param_frame)
        self.lambda_entry.insert(0, "500")
        self.lambda_entry.pack()

        ttk.Label(param_frame, text="Ширина спектра (нм):").pack()
        self.dlambda_entry = ttk.Entry(param_frame)
        self.dlambda_entry.insert(0, "10")
        self.dlambda_entry.pack()

        # Выбор режима освещения
        ttk.Label(param_frame, text="Режим освещения:").pack(pady=(10, 0))
        ttk.Radiobutton(param_frame, text="Монохроматический", variable=self.mode, value="mono").pack(anchor=tk.W)
        ttk.Radiobutton(param_frame, text="Квазимонохроматический", variable=self.mode, value="quasi").pack(anchor=tk.W)
        ttk.Radiobutton(param_frame, text="Белый свет", variable=self.mode, value="white").pack(anchor=tk.W)

        ttk.Button(param_frame, text="Обновить", command=self.update_image).pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=self.size, height=self.size)
        self.canvas.pack(side=tk.RIGHT, padx=10, pady=10)

    def intensity_mono(self, r, wavelength):
        return 0.5 * (1 - np.cos(2 * np.pi * r ** 2 / (wavelength * self.R)))

    def spectral_density(self, wavelength):
        sigma = self.delta_lambda / (2 * np.sqrt(2 * np.log(2)))
        return np.exp(-((wavelength - self.lambda0) ** 2) / (2 * sigma ** 2))

    def intensity_quasi(self, r):
        wavelengths = np.linspace(self.lambda0 - self.delta_lambda / 2,
                                  self.lambda0 + self.delta_lambda / 2, 20)
        weights = np.array([self.spectral_density(wl) for wl in wavelengths])
        weights /= np.sum(weights)

        image = np.zeros((r.shape[0], r.shape[1], 3))
        for wl, weight in zip(wavelengths, weights):
            I = self.intensity_mono(r, wl)
            rgb = wavelength_to_rgb(wl)
            for i in range(3):
                image[:, :, i] += weight * I * rgb[i]
        image /= np.max(image)
        return (image * 255).astype(np.uint8)

    def intensity_white_light(self, r):
        wavelengths = np.linspace(400e-9, 700e-9, 30)
        image = np.zeros((r.shape[0], r.shape[1], 3))
        for wl in wavelengths:
            I = self.intensity_mono(r, wl)
            rgb = wavelength_to_rgb(wl)
            for i in range(3):
                image[:, :, i] += I * rgb[i]
        image /= np.max(image)  # Нормализация
        return (image * 255).astype(np.uint8)

    def update_image(self):
        try:
            self.R = float(self.R_entry.get())
            self.lambda0 = float(self.lambda_entry.get()) * 1e-9
            self.delta_lambda = float(self.dlambda_entry.get()) * 1e-9
        except:
            return

        x = np.linspace(-0.01, 0.01, self.size)
        y = np.linspace(-0.01, 0.01, self.size)
        xx, yy = np.meshgrid(x, y)
        r = np.sqrt(xx ** 2 + yy ** 2)

        if self.mode.get() == "mono":
            I = self.intensity_mono(r, self.lambda0)
            I = (I * 255).astype(np.uint8)
            img = Image.fromarray(I, mode='L').convert("RGB")
            rgb = wavelength_to_rgb(self.lambda0)
            pixels = img.load()
            for i in range(img.size[0]):
                for j in range(img.size[1]):
                    intensity = pixels[i, j][0] / 255
                    pixels[i, j] = tuple(int(255 * intensity * c) for c in rgb)

        elif self.mode.get() == "quasi":
            I = self.intensity_quasi(r)
            img = Image.fromarray(I, mode='RGB')

        elif self.mode.get() == "white":
            I = self.intensity_white_light(r)
            img = Image.fromarray(I, mode='RGB')

        self.tkimg = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tkimg)


if __name__ == "__main__":
    root = tk.Tk()
    app = NewtonRingsApp(root)
    root.mainloop()
