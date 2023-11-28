import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import re
import csv

def connect_to_mongodb():
    try:
        global vocabulary_collection
        client = MongoClient('localhost', 11451, serverSelectionTimeoutMS=5000)
        db = client['vocabulary_db']
        vocabulary_collection = db['vocabulary']
        update_listbox()
        status_label.config(text="Connected to MongoDB", fg="green")
    except ServerSelectionTimeoutError:
        status_label.config(text="Connection Timeout", fg="red")

def update_listbox(search_term=None):
    query = {} if search_term is None else {"word": re.compile(f"{search_term}", re.IGNORECASE)}
    all_vocab = vocabulary_collection.find(query)
    vocab_listbox.delete(0, tk.END)
    for vocab in all_vocab:
        info = f"{vocab['word']} - {vocab['definition']} - {vocab.get('part_of_speech', '')} - {vocab.get('category', '')}"
        vocab_listbox.insert(tk.END, info)

def update_listbox_by_category(selected_category):
    query = {} if selected_category == "All Categories" else {"category": selected_category}
    all_vocab = vocabulary_collection.find(query)
    vocab_listbox.delete(0, tk.END)
    for vocab in all_vocab:
        info = f"{vocab['word']} - {vocab['definition']} - {vocab.get('part_of_speech', '')} - {vocab.get('category', '')}"
        vocab_listbox.insert(tk.END, info)

def insert_vocab():
    new_word = entry_word.get().strip()
    new_definition = entry_definition.get().strip()
    new_part_of_speech = entry_part_of_speech.get().strip()
    new_category = category_variable.get().strip()

    if new_word and new_definition and new_part_of_speech and new_category:
        existing_word = vocabulary_collection.find_one({"word": new_word})
        if existing_word:
            vocabulary_collection.update_one(
                {"word": new_word},
                {
                    "$set": {
                        "definition": new_definition,
                        "part_of_speech": new_part_of_speech,
                        "category": new_category
                    }
                }
            )
        else:
            vocabulary_collection.insert_one({
                "word": new_word,
                "definition": new_definition,
                "part_of_speech": new_part_of_speech,
                "category": new_category
            })
        update_listbox()
    else:
        messagebox.showwarning("Empty Fields", "Please fill in all fields.")

def delete_selected():
    selected_indices = vocab_listbox.curselection()
    for index in selected_indices:
        selected_word = vocab_listbox.get(index)
        word_to_delete = selected_word.split(' - ')[0]
        vocabulary_collection.delete_one({"word": word_to_delete})
    update_listbox()

def search():
    search_term = entry_search.get()
    update_listbox(search_term)

def show_all():
    entry_search.delete(0, tk.END)
    update_listbox()

def show_category_vocabulary():
    selected_category = category_variable.get()
    if selected_category == "All Categories":
        update_listbox()
    else:
        update_listbox_by_category(selected_category)

def import_from_csv(file_path):
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                existing_word = vocabulary_collection.find_one({"word": row['en']})
                if existing_word:
                    vocabulary_collection.update_one(
                        {"word": row['en']},
                        {
                            "$set": {
                                "definition": row['cn'],
                                "part_of_speech": row['enfeature'],
                                "category": row['category']
                            }
                        }
                    )
                else:
                    vocabulary_collection.insert_one({
                        "word": row['en'],
                        "definition": row['cn'],
                        "part_of_speech": row['enfeature'],
                        "category": row['category']
                    })
        update_listbox()  # 更新词汇列表显示
        messagebox.showinfo("Success", "CSV data imported successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Error importing CSV data: {str(e)}")

# 添加一个按钮来触发导入操作
def import_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        import_from_csv(file_path)

root = tk.Tk()
root.title("Vocabulary DB GUI")
root.resizable(False, False)

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

status_label = tk.Label(frame, text="")
status_label.grid(row=0, column=1, padx=5, pady=5)

connect_button = tk.Button(frame, text="Connect to MongoDB", command=connect_to_mongodb)
connect_button.grid(row=0, column=0, padx=5, pady=5)

label_word = tk.Label(frame, text="Word:")
label_word.grid(row=1, column=0, padx=5, pady=5)

entry_word = tk.Entry(frame)
entry_word.grid(row=1, column=1, padx=5, pady=5)

label_definition = tk.Label(frame, text="Definition:")
label_definition.grid(row=2, column=0, padx=5, pady=5)

entry_definition = tk.Entry(frame)
entry_definition.grid(row=2, column=1, padx=5, pady=5)

label_part_of_speech = tk.Label(frame, text="Part of Speech:")
label_part_of_speech.grid(row=3, column=0, padx=5, pady=5)

entry_part_of_speech = tk.Entry(frame)
entry_part_of_speech.grid(row=3, column=1, padx=5, pady=5)

label_category = tk.Label(frame, text="Category:")
label_category.grid(row=4, column=0, padx=5, pady=5)

categories = ["All Categories", "Category1", "Category2", "Category3"]  # Replace with your actual categories
category_variable = tk.StringVar(frame)
category_variable.set(categories[0])

category_dropdown = tk.OptionMenu(frame, category_variable, *categories)
category_dropdown.grid(row=4, column=1, padx=5, pady=5)

insert_button = tk.Button(frame, text="Insert Vocabulary", command=insert_vocab)
insert_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

search_frame = tk.Frame(frame)
search_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

label_search = tk.Label(search_frame, text="Search:")
label_search.grid(row=0, column=0, padx=5, pady=5)

entry_search = tk.Entry(search_frame)
entry_search.grid(row=0, column=1, padx=5, pady=5)

search_button = tk.Button(search_frame, text="Search", command=search)
search_button.grid(row=0, column=2, padx=5, pady=5)

show_all_button = tk.Button(search_frame, text="Show All", command=show_all)
show_all_button.grid(row=0, column=3, padx=5, pady=5)

show_category_button = tk.Button(frame, text="Show Category", command=show_category_vocabulary)
show_category_button.grid(row=4, column=2, padx=5, pady=5)

vocab_listbox = tk.Listbox(frame, width=60, height=10, selectmode=tk.MULTIPLE)
vocab_listbox.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

delete_button = tk.Button(frame, text="Delete Selected", command=delete_selected)
delete_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

import_csv_button = tk.Button(frame, text="Import from CSV", command=import_csv)
import_csv_button.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

connect_to_mongodb()

root.mainloop()
