import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import csv

def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",           
            password="Root3328.",
            database="deliveryservice"
        )
        return connection
    except Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось подключиться: {e}")
        return None

class DatabaseApp:
    def __init__(self, root, table_name, columns):
        
        self.root = root
        self.table_name = table_name
        self.columns = columns
        self.add_search()
        self.export_to_csv()
        
        self.root.title(f"Управление таблицей: {table_name}")
        self.root.geometry("800x500")
        
        self.create_widgets()
        
        self.refresh_table()
    
    def create_widgets(self):

        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)
        
        self.entries = {}
        
        for i, col in enumerate(self.columns):

            if col.get('pk') and col.get('auto_increment'):
                continue
            
            label = tk.Label(input_frame, text=f"{col['label']}:")
            label.grid(row=0, column=i*2, padx=5, pady=5, sticky="e")
            
            entry = tk.Entry(input_frame, width=25)
            entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            self.entries[col['name']] = entry
        
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="➕ Добавить", command=self.add_record, 
                  bg="#97EA97", width=12).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="✏️ Обновить", command=self.update_record, 
                  bg="#FFD700", width=12).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="🗑️ Удалить", command=self.delete_record, 
                  bg="#FF6347", width=12).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="🧹 Очистить", command=self.clear_entries, 
                  width=12).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="🔄 Показать всех", command=self.refresh_table, 
                  width=15).grid(row=0, column=4, padx=5)
        
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns_display = [col['name'] for col in self.columns]
        self.tree = ttk.Treeview(tree_frame, columns=columns_display, show="headings",
                                 yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree.yview)
        
        for col in self.columns:
            self.tree.heading(col['name'], text=col['label'])
            self.tree.column(col['name'], width=100, anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT {', '.join(columns_names)} FROM {self.table_name}"
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        
        for i, col in enumerate(self.columns):
            col_name = col['name']
            if col_name in self.entries:
                self.entries[col_name].delete(0, tk.END)
                self.entries[col_name].insert(0, str(values[i]) if values[i] is not None else "")
    
    def get_pk_name(self):
        for col in self.columns:
            if col.get('pk'):
                return col['name']
        return None
    
    def add_record(self):
        values = {}
        for col_name, entry in self.entries.items():
            values[col_name] = entry.get().strip()
        
        for col in self.columns:
            col_name = col['name']
            if col.get('required') and col_name in self.entries and not values[col_name]:
                messagebox.showwarning("Ошибка", f"Поле '{col['label']}' обязательно для заполнения")
                return
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        columns_names = list(values.keys())
        placeholders = ", ".join(["%s"] * len(columns_names))
        query = f"INSERT INTO {self.table_name} ({', '.join(columns_names)}) VALUES ({placeholders})"
        
        try:
            cursor.execute(query, list(values.values()))
            conn.commit()
            messagebox.showinfo("Успех", "Запись добавлена")
            self.clear_entries()
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def update_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для обновления")
            return
        
        pk_name = self.get_pk_name()
        if not pk_name:
            return
        
        values_current = self.tree.item(selected[0])['values']
        pk_index = [col['name'] for col in self.columns].index(pk_name)
        pk_value = values_current[pk_index]
        
        new_values = {}
        for col_name, entry in self.entries.items():
            new_values[col_name] = entry.get().strip()
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{col} = %s" for col in new_values.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {pk_name} = %s"
        
        try:
            params = list(new_values.values()) + [pk_value]
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Успех", "Запись обновлена")
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить запись?"):
            return
        
        pk_name = self.get_pk_name()
        if not pk_name:
            return
        
        values = self.tree.item(selected[0])['values']
        pk_index = [col['name'] for col in self.columns].index(pk_name)
        pk_value = values[pk_index]
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        query = f"DELETE FROM {self.table_name} WHERE {pk_name} = %s"
        
        try:
            cursor.execute(query, (pk_value,))
            conn.commit()
            messagebox.showinfo("Успех", "Запись удалена")
            self.clear_entries()
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def add_search(self):
        """Добавить строку поиска"""
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5)
    
        tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="🔍 Найти", command=self.search).pack(side=tk.LEFT)

    def search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return
    
        # Ищем по всем текстовым полям
        conn = connect_db()
        if not conn:
            return
    
        cursor = conn.cursor()
    
        # Формируем условие LIKE для всех текстовых колонок
        text_columns = [col['name'] for col in self.columns 
                if col.get('required') is not None and not col.get('pk')]
    
        if not text_columns:
            return
    
        conditions = " OR ".join([f"{col} LIKE %s" for col in text_columns])
        query = f"SELECT * FROM {self.table_name} WHERE {conditions}"
    
        try:
            cursor.execute(query, tuple([f"%{keyword}%"] * len(text_columns)))
            rows = cursor.fetchall()
        
            # Очищаем таблицу
            for row in self.tree.get_children():
                self.tree.delete(row)
        
            # Заполняем результатами поиска
            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except Error as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def export_to_csv(self):
        filename = f"{self.table_name}_export.csv"
    
        conn = connect_db()
        if not conn:
            return
    
        cursor = conn.cursor()
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT * FROM {self.table_name}"
    
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
        
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([col['label'] for col in self.columns])
                writer.writerows(rows)
        
            messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()


def main():
    root = tk.Tk()
    
    columns = [
        {"name": "id", "label": "ID", "pk": True, "auto_increment": True},
        {"name": "full_name", "label": "ФИО", "required": True},
        {"name": "phone", "label": "Телефон", "required": True},
        {"name": "status", "label": "Статус", "required": True},
    ]
    
    app = DatabaseApp(root, table_name="couriers", columns=columns)
    root.mainloop()

if __name__ == "__main__":
    main()
