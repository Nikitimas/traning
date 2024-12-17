from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_to_pdf():
    # Открыть диалог выбора файлов
    files = filedialog.askopenfilenames(
        title="Выберите файлы JPEG для конвертации",
        filetypes=[("JPEG files", "*.jpg"), ("JPEG files", "*.jpeg"), ("All files", "*.*")]
    )

    if not files:
        messagebox.showinfo("Информация", "Вы не выбрали файлы.")
        return

    # Открыть диалог для сохранения файла
    save_path = filedialog.asksaveasfilename(
        title="Сохранить PDF как",
        filetypes=[("PDF files", "*.pdf")],
        defaultextension=".pdf"
    )

    if not save_path:
        messagebox.showinfo("Информация", "Вы не выбрали путь для сохранения.")
        return

    try:
        # Открыть изображения
        image_list = []
        for file in files:
            img = Image.open(file).convert("RGB")  # Конвертируем изображение в RGB
            image_list.append(img)

        # Если несколько изображений — все кроме первого добавляются как страницы
        image_list[0].save(save_path, save_all=True, append_images=image_list[1:])

        messagebox.showinfo("Успех", f"Файлы успешно конвертированы в {save_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# Создание простого интерфейса
def main():
    root = tk.Tk()
    root.title("Конвертация JPEG в PDF")
    root.geometry("400x200")

    label = tk.Label(root, text="Конвертер JPEG в PDF", font=("Arial", 14))
    label.pack(pady=20)

    button = tk.Button(root, text="Выбрать файлы JPEG и преобразовать в PDF", command=convert_to_pdf, font=("Arial", 12))
    button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()