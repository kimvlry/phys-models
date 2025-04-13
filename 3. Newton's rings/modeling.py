import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk


class NewtonRingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Кольца Ньютона")

        # Параметры по умолчанию
        self.R = 1.0  # Радиус кривизны (м)
        self.lambda0 = 500e-9  # Длина волны (м)
        self.delta_lambda = 10e-9  # Ширина спектра (м)
        self.size = 400  # Размер изображения

        # Создание элементов интерфейса
        self.create_widgets()

        # Инициализация изображения
        self.update_image()

    def create_widgets(self):
        # Фрейм для параметров
        param_frame = ttk.Frame(self.root, padding=10)
        param_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Поля ввода
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

        # Кнопка обновления
        ttk.Button(param_frame, text="Обновить", command=self.update_image).pack(pady=10)

        # Холст для изображения
        self.canvas = tk.Canvas(self.root, width=self.size, height=self.size)
        self.canvas.pack(side=tk.RIGHT, padx=10, pady=10)

    def intensity_mono(self, r, wavelength):
        """Интенсивность для монохроматического света"""
        return 0.5 * (1 - np.cos(2 * np.pi * r ** 2 / (wavelength * self.R)))

    # Вычисление спектральной плотности для каждой дискретной точки
    def spectral_density(self, wavelength):
        sigma = self.delta_lambda / (2 * np.sqrt(2 * np.log(2)))
        return np.exp(-((wavelength - self.lambda0) ** 2) / (2 * sigma ** 2))

    def intensity_quasi(self, r):
        wavelengths = np.linspace(self.lambda0 - self.delta_lambda / 2,
                                  self.lambda0 + self.delta_lambda / 2, 20)
        total = np.zeros_like(r)
        weights = np.zeros_like(wavelengths)
        # Вычисление вклада каждой длины волны
        for i, wl in enumerate(wavelengths):
            weights[i] = self.spectral_density(wl)
        # Нормировка весов так, чтобы их сумма была равна 1
        # (чтобы итоговое усреднение не зависело от количества дискретных точек)
        weights /= np.sum(weights)

        for wl, weight in zip(wavelengths, weights):
            total += weight * self.intensity_mono(r, wl)
        return total

    def wavelength_to_rgb(self, wavelength):
        """Приблизительное преобразование длины волны в RGB"""
        if wavelength < 380e-9:
            return (0, 0, 0)
        elif wavelength < 440e-9:
            attenuation = 0.3 + 0.7 * (wavelength - 380e-9) / (440e-9 - 380e-9)
            return (attenuation * (440e-9 - wavelength) / (440e-9 - 380e-9), 0, attenuation)
        elif wavelength < 490e-9:
            return (0, (wavelength - 440e-9) / (490e-9 - 440e-9), 1)
        elif wavelength < 510e-9:
            return (0, 1, (510e-9 - wavelength) / (510e-9 - 490e-9))
        elif wavelength < 580e-9:
            return ((wavelength - 510e-9) / (580e-9 - 510e-9), 1, 0)
        elif wavelength < 645e-9:
            return (1, (645e-9 - wavelength) / (645e-9 - 580e-9), 0)
        else:
            attenuation = 0.3 + 0.7 * (700e-9 - wavelength) / (700e-9 - 645e-9)
            return (attenuation, 0, 0)

    def update_image(self):
        # Обновление параметров
        try:
            self.R = float(self.R_entry.get())
            self.lambda0 = float(self.lambda_entry.get()) * 1e-9
            self.delta_lambda = float(self.dlambda_entry.get()) * 1e-9
        except:
            return

        # Создание координатной сетки
        x = np.linspace(-0.01, 0.01, self.size)  # 2 см область
        y = np.linspace(-0.01, 0.01, self.size)
        xx, yy = np.meshgrid(x, y)
        r = np.sqrt(xx ** 2 + yy ** 2)

        # Расчёт интенсивности
        if self.delta_lambda == 0:
            I = self.intensity_mono(r, self.lambda0)
        else:
            I = self.intensity_quasi(r)

        # Нормализация и преобразование в цвет
        I_normalized = (I * 255).astype(np.uint8)

        # Создание изображения

        img = Image.fromarray(I_normalized, mode='L')
        if self.delta_lambda == 0:
            # Применение цвета для монохроматического случая
            rgb = self.wavelength_to_rgb(self.lambda0)
            img = img.convert("RGB")
            pixels = img.load()
            for i in range(img.size[0]):
                for j in range(img.size[1]):
                    intensity = pixels[i, j][0] / 255
                    pixels[i, j] = tuple(int(255 * intensity * c) for c in rgb)

        self.tkimg = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tkimg)


if __name__ == "__main__":
    root = tk.Tk()
    app = NewtonRingsApp(root)
    root.mainloop()