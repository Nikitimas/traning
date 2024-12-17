import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pdfplumber
import pytesseract
import pandas as pd



# ===== Функция для извлечения текста из PDF =====
def extract_text_from_pdf(file_path, is_scanned=False):
    data = []
    if is_scanned:
        # Если PDF сканирован, используем OCR через pytesseract
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Если PDF содержит изображение
                image = page.to_image(resolution=300).original
                text = pytesseract.image_to_string(image, lang="rus+eng")
                data.append(text)
    else:
        # Если PDF текстовый
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                data.append(page.extract_text())
    return "".join(data)


# ===== Функция для извлечения полей из текста =====
def extract_fields(text):
    import re
    invoice_number = re.search(r'Счёт[-\s]?фактура.*?№\s*(\S+)', text, re.IGNORECASE)
    date = re.search(r'Дата.*?(\d{2}\.\d{2}\.\д{4})', text, re.IGNORECASE)
    vat = re.search(r'НДС.*?(\d+,\d+)', text, re.IGNORECASE)
    total_amount = re.search(r'Сумма.*?([\d\s]+,\d+)', text, re.IGNORECASE)

    return {
        "Счёт-фактура": invoice_number.group(1) if invoice_number else None,
        "Дата": date.group(1) if date else None,
        "НДС": vat.group(1) if vat else None,
        "Сумма": total_amount.group(1) if total_amount else None
    }


# ===== Основная обработка PDF =====
def process_pdfs(folder_path, is_scanned=False):
    pdf_data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            text = extract_text_from_pdf(file_path, is_scanned)
            fields = extract_fields(text)
            fields["Файл"] = file_name
            pdf_data.append(fields)
    return pdf_data


# ===== Сравнение данных с таблицей 1С =====
def compare_data(pdf_data, onec_data):
    pdf_df = pd.DataFrame(pdf_data)
    onec_df = pd.DataFrame(onec_data)

    # Слияние таблиц
    merged = pd.merge(pdf_df, onec_df, how="outer", on=["Счёт-фактура", "Дата", "НДС", "Сумма"], indicator=True)

    # Разделяем на совпадения и несовпадения
    matches = merged[merged["_merge"] == "both"]
    mismatches = merged[merged["_merge"] != "both"]

    return matches, mismatches


# ===== Класс для окна GUI =====
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Настройки окна
        self.title("Сравнение PDF и 1С данных")
        self.geometry("900x700")
        self.folder_path = None
        self.onec_file_path = None

        # Создание элементов интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Выбор папки с PDF
        ttk.Label(self, text="Папка с PDF-файлами:").pack(pady=5)
        ttk.Button(self, text="Выбрать папку", command=self.select_folder).pack(pady=5)

        # Выбор файла 1С
        ttk.Label(self, text="Файл 1С (Excel):").pack(pady=5)
        ttk.Button(self, text="Выбрать файл", command=self.select_onec_file).pack(pady=5)

        # Переключатель: сканированные PDF или текстовые
        self.is_scanned = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Обрабатывать как сканированные PDF (OCR)", variable=self.is_scanned).pack(pady=5)

        # Кнопка для запуска обработки
        ttk.Button(self, text="Начать обработку", command=self.start_processing).pack(pady=10)

        # Пустая область для вывода результатов
        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            messagebox.showinfo("Папка выбрана", f"Вы выбрали папку: {folder}")

    def select_onec_file(self):
        filetypes = [("Excel files", "*.xlsx"), ("Excel files", "*.xls")]
        file = filedialog.askopenfilename(filetypes=filetypes)
        if file:
            self.onec_file_path = file
            messagebox.showinfo("Файл выбран", f"Вы выбрали файл: {file}")

    def start_processing(self):
        if not self.folder_path or not self.onec_file_path:
            messagebox.showerror("Ошибка", "Сначала выберите папку с PDF-файлами и файл данных 1С!")
            return

        # Загрузка данных
        onec_data = pd.read_excel(self.onec_file_path).to_dict(orient="records")
        pdf_data = process_pdfs(self.folder_path, self.is_scanned.get())

        # Сравнение данных
        matches, mismatches = compare_data(pdf_data, onec_data)

        # Отображение результатов
        self.show_results(matches, mismatches)

    def show_results(self, matches, mismatches):
        # Очистка старых результатов
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Вывод совпадений
        ttk.Label(self.results_frame, text="Совпадения:").pack()
        matches_text = tk.Text(self.results_frame, height=10, wrap="word")
        matches_text.pack(fill="both", expand=True)
        matches_text.insert("1.0", matches.to_string(index=False))

        # Вывод несовпадений
        ttk.Label(self.results_frame, text="Несовпадения:").pack()
        mismatches_text = tk.Text(self.results_frame, height=10, wrap="word")
        mismatches_text.pack(fill="both", expand=True)
        mismatches_text.insert("1.0", mismatches.to_string(index=False))


# ===== Запуск приложения =====
if __name__ == "__main__":
    app = App()
    app.mainloop()