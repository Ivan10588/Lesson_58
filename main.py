import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json

class JSONParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сервис парсинга JSON")
        self.root.geometry("800x600")
        self.api_url = "http://localhost:5000"
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        title_label = ttk.Label(main_frame, text="Управление товарами (JSON + API)", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W))
        ttk.Button(button_frame, text="Загрузить JSON", command=self.load_json_file).pack(side=tk.LEFT, padx=(0, 5))

        list_frame = ttk.LabelFrame(main_frame, text="Список элементов", padding="5")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=1)

        columns = ('ID', 'Name', 'Description', 'Price')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        form_frame = ttk.LabelFrame(main_frame, text="Форма элемента", padding="10")
        form_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.price_var = tk.DoubleVar()

        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.id_entry = ttk.Entry(form_frame, textvariable=self.id_var, state='readonly')
        self.id_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var)
        name_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        form_frame.columnconfigure(3, weight=1)

        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.NE)
        desc_entry = ttk.Entry(form_frame, textvariable=self.desc_var)
        desc_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(form_frame, text="Price:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        price_entry = ttk.Entry(form_frame, textvariable=self.price_var)
        price_entry.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        form_button_frame = ttk.Frame(form_frame)
        form_button_frame.grid(row=4, column=0, columnspan=4, pady=(10, 0), sticky=tk.E)

        self.add_button = ttk.Button(form_button_frame, text="Добавить", command=self.create_item)
        self.add_button.pack(side=tk.LEFT, padx=(0, 5))

        self.update_button = ttk.Button(form_button_frame, text="Обновить", command=self.update_item, state='disabled')
        self.update_button.pack(side=tk.LEFT, padx=(0, 5))

        self.delete_button = ttk.Button(form_button_frame, text="Удалить", command=self.delete_item, state='disabled')
        self.delete_button.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_button = ttk.Button(form_button_frame, text="Очистить", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.refresh_list()

    def load_json_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите JSON-файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                with open('data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Успех", "JSON-файл успешно загружен!")
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def refresh_list(self):
        try:
            response = requests.get(f"{self.api_url}/items")
            if response.status_code == 200:
                items = response.json()
                for item in self.tree.get_children():
                    self.tree.delete(item)
                for item in items:
                    self.tree.insert('', tk.END, values=(
                        item['id'], item['name'], item['description'], item['price']
                    ))
            else:
                messagebox.showerror(
                    "Ошибка API",
                    f"Не удалось получить данные: статус {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось подключиться к API:\n{str(e)}")

    def clear_form(self):
        self.id_var.set("")
        self.name_var.set("")
        self.desc_var.set("")
        self.price_var.set(0.0)
        self.update_button.config(state='disabled')
        self.delete_button.config(state='disabled')

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item[0])['values']
            self.id_var.set(item_values[0])
            self.name_var.set(item_values[1])
            self.desc_var.set(item_values[2])
            self.price_var.set(item_values[3])
            self.update_button.config(state='normal')
            self.delete_button.config(state='normal')

    def create_item(self):
        if not self.validate_inputs():
            return
        try:
            new_item = {
                'name': self.name_var.get(),
                'description': self.desc_var.get(),
                'price': float(self.price_var.get())
            }
            response = requests.post(f"{self.api_url}/items", json=new_item)
            if response.status_code == 201:
                messagebox.showinfo("Успех", "Элемент успешно добавлен!")
                self.clear_form()
                self.refresh_list()
            else:
                error_text = response.json().get('error', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка API", f"Ошибка при добавлении: {error_text}")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Цена должна быть числом!")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось подключиться к API:\n{str(e)}")

    def update_item(self):
        if not self.validate_inputs():
            return
        try:
            item_id = int(self.id_var.get())
            updated_item = {
                'name': self.name_var.get(),
                'description': self.desc_var.get(),
                'price': float(self.price_var.get())
            }
            response = requests.put(f"{self.api_url}/items/{item_id}", json=updated_item)
            if response.status_code == 200:
                messagebox.showinfo("Успех", "Элемент успешно обновлён!")
                self.clear_form()
                self.refresh_list()
            elif response.status_code == 404:
                messagebox.showwarning("Внимание", "Элемент не найден (возможно, был удалён)")
                self.clear_form()
                self.refresh_list()
            else:
                error_text = response.json().get('error', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка API", f"Ошибка при обновлении: {error_text}")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "ID и цена должны быть числами!")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось подключиться к API:\n{str(e)}")

    def delete_item(self):
        item_id = self.id_var.get()
        if not item_id:
            messagebox.showwarning("Внимание", "Нет ID для удаления. Выберите элемент в списке.")
            return

        confirm = messagebox.askyesno("Подтверждение удаления", f"Вы уверены, что хотите удалить элемент с ID {item_id}?")
        if not confirm:
            return

        try:
            response = requests.delete(f"{self.api_url}/items/{item_id}")
            if response.status_code == 204:
                messagebox.showinfo("Успех", "Элемент успешно удалён!")
                self.clear_form()
                self.refresh_list()
            elif response.status_code == 404:
                messagebox.showwarning("Внимание", "Элемент не найден (возможно, уже удалён)")
                self.clear_form()
                self.refresh_list()
            else:
                error_text = response.json().get('error', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка API", f"Ошибка при удалении: {error_text}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось подключиться к API:\n{str(e)}")

    def validate_inputs(self):
        if not self.name_var.get().strip():
            messagebox.showerror("Ошибка валидации", "Поле 'Name' обязательно для заполнения.")
            return False
        if not self.desc_var.get().strip():
            messagebox.showerror("Ошибка валидации", "Поле 'Description' обязательно для заполнения.")
            return False
        try:
            float(self.price_var.get())
        except ValueError:
            messagebox.showerror("Ошибка валидации", "Поле 'Price' должно быть числом.")
            return False
        return True

def main():
    root = tk.Tk()
    app = JSONParserApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()