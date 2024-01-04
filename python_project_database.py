import tkinter as tk
from tkinter import messagebox
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Bhahkmbb1"
)

mycursor = mydb.cursor()

# Veritabanını kontrol et ve yoksa oluştur
database_name = "pythonproje"
mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")

mycursor.close()
mydb.close()

# Yeni veritabanına özel bağlantı
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Bhahkmbb1",
  database=database_name  # Oluşturduğunuz veritabanını burada belirtin
)

mycursor = mydb.cursor()

# Tabloyu kontrol et ve yoksa oluştur
table_name = "tasks"
mycursor.execute(f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task VARCHAR(255),
    priority INT,
    details TEXT
)
""")

mycursor.execute("SELECT * FROM tasks")
rows = mycursor.fetchall()





# Görevleri dosyadan yükleme
def load_tasks():
    tasks = {}
    try:
        mycursor.execute("SELECT * FROM tasks")
        result = mycursor.fetchall()  # Tüm görevleri al
        for row in result:
            task_id, task_detail, priority, details = row
            tasks[task_detail] = (priority, details)  # Görevleri sözlüğe ekle
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
    return tasks

tasks = load_tasks()

def add_task():
    global text_task_details
    
    task = task_entry.get()
    priority = int(priority_entry.get())
    details = text_task_details.get("1.0", tk.END).strip()  # .strip() sonundaki boşlukları temizler
    
    if task != "" and priority >= 0:
        # Veritabanına görevi ekle
        try:
            sql = "INSERT INTO tasks (task, priority, details) VALUES (%s, %s, %s)"
            val = (task, priority, details)
            mycursor.execute(sql, val)
            mydb.commit()  # Değişiklikleri kaydet
            print(mycursor.rowcount, "record inserted.")
            
            update_listbox()  # Görev listesini güncelle
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            messagebox.showwarning("Uyarı", "Veritabanı hatası: Görev eklenemedi!")
    else:
        messagebox.showwarning("Uyarı", "Boş görev veya negatif önem derecesi eklenemez!")
    
    # Giriş alanlarını temizle
    task_entry.delete(0, tk.END)
    priority_entry.delete(0, tk.END)
    text_task_details.delete("1.0", tk.END)


def update_listbox():
    clear_listbox()
    for task, (priority, details) in sorted(tasks.items(), key=lambda item: item[1]):
        lb_tasks.insert(tk.END, f"{task} (Önem Derecesi: {priority}) (Detaylar: {details})")


def clear_listbox():
    lb_tasks.delete(0, tk.END)

def delete_task():
    task_info = lb_tasks.get("active")
    task = task_info.split(" (")[0]
    if task in tasks:
        del tasks[task]
        update_listbox()
        

def refresh_list():
    update_listbox()
    
def update_task():
    global edit_window
    global entry_task_title
    global entry_task_priority
    global text_task_details

    task_info = lb_tasks.get("active")
    task_detail = task_info.split(" (")[0]
    


    if task_detail in tasks:
        edit_window = tk.Tk()
        edit_window.title("Görevi Güncelle")
        
        edit_window.configure(bg='lightblue')

        tk.Label(edit_window, text="Görev Başlığı:",bg="lightblue").pack()
        entry_task_title = tk.Entry(edit_window,bg="white",fg="black", borderwidth=0, relief="flat")
        entry_task_title.insert(0, task_detail)  # Mevcut görevi kutuya yerleştir
        entry_task_title.pack()

        tk.Label(edit_window, text="Öncelik Sırası:",bg="lightblue").pack()
        entry_task_priority = tk.Entry(edit_window,bg="white",fg="black", borderwidth=0, relief="flat")
        
        priority, details = tasks[task_detail]
        entry_task_priority.insert(0, priority)  
        entry_task_priority.pack()

        tk.Label(edit_window, text="Ayrıntılar:",bg="lightblue").pack()
        text_task_details = tk.Text(edit_window, height=10, width=50,bg="white",fg="black", borderwidth=0, relief="flat")
        text_task_details.insert(tk.END, details)  # Mevcut detayları kutuya yerleştir
        text_task_details.pack()

        save_button = tk.Button(edit_window, text="Kaydet", command=save_updated_task,bg="lightblue",highlightbackground='lightblue', highlightcolor='lightblue', highlightthickness=2)
        save_button.pack()

def save_updated_task():
    global edit_window
    task_info = lb_tasks.get("active")
    old_task_detail = task_info.split(" (")[0]

    new_task_detail = entry_task_title.get()
    new_task_priority = int(entry_task_priority.get())
    new_task_details = text_task_details.get("1.0", tk.END).strip()

    # Veritabanında güncelleme yap
    try:
        # Önceki görev detayına göre güncelleme yapmak için SQL sorgusu
        sql = "UPDATE tasks SET task=%s, priority=%s, details=%s WHERE task=%s"
        val = (new_task_detail, new_task_priority, new_task_details, old_task_detail)
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "record(s) affected")

        # Eğer görev adı değiştiyse, eski görevi sil ve yeni görevi ekle
        if old_task_detail in tasks:
            del tasks[old_task_detail]
        tasks[new_task_detail] = (new_task_priority, new_task_details)

        update_listbox()
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        messagebox.showwarning("Uyarı", "Veritabanı hatası: Görev güncellenemedi!")

    edit_window.destroy()


def main_window():
    global task_entry
    global priority_entry
    global lb_tasks
    global text_task_details
    
    
    root = tk.Tk()
    root.title("Python To-Do List Uygulaması")
    root.configure(bg='lightblue')

    frame_left = tk.Frame(root, bg='lightblue')
    frame_left.pack(side=tk.LEFT, padx=10)
    tk.Label(frame_left, text="Önem Derecesi (Sayı olarak):", bg='lightblue').pack()
    priority_entry = tk.Entry(frame_left, width=20,bg="white",fg="black", borderwidth=0, relief="flat")
    priority_entry.pack()

    frame_center = tk.Frame(root, bg='lightblue')
    frame_center.pack(side=tk.LEFT, padx=10)
    tk.Label(frame_center, text="Görev Girin", bg='lightblue',highlightbackground='lightblue', highlightcolor='lightblue', highlightthickness=2).pack()
    task_entry = tk.Entry(frame_center, width=50,bg="white",fg="black", borderwidth=0, relief="flat")
    task_entry.pack()
    add_button = tk.Button(frame_center, text="Görev Ekle", command=add_task,bg="lightblue",highlightbackground='lightblue', highlightcolor='lightblue', highlightthickness=2)
    add_button.pack()
    text_task_details = tk.Text(frame_center, height=10, width=50,bg="white",fg="black", borderwidth=0, relief="flat")
    text_task_details.pack()
    
    frame_right = tk.Frame(root, bg='lightblue')
    frame_right.pack(side=tk.LEFT, padx=10)
    tk.Label(frame_right, text="Görevler (Önem Derecesine Göre Sıralı)", bg='lightblue').pack()
    lb_tasks = tk.Listbox(frame_right, width=50,bg="white",fg="black", borderwidth=0, relief="flat")
    lb_tasks.pack()
    delete_button = tk.Button(frame_right, text="Görevi Sil", command=delete_task,bg="lightblue",highlightbackground='lightblue', highlightcolor='lightblue', highlightthickness=2)
    delete_button.pack()
    refresh_button = tk.Button(frame_right, text="Listeyi Yenile", command=refresh_list,bg="lightblue",highlightbackground='lightblue', highlightcolor='lightblue', highlightthickness=2)
    refresh_button.pack()
    
    
    
    edit_button = tk.Button(frame_right, text="Görevi Düzenle", command=update_task, bg="lightblue",highlightbackground='lightblue', highlightcolor='lightblue', highlightthickness=2)
    edit_button.pack()

    update_listbox()
    root.mainloop()


def login():
    if entry_username.get() == "admin" and entry_password.get() == "password":
        messagebox.showinfo("Bilgi", "Giriş başarılı!")
        login_window.destroy()
        main_window()
    else:
        messagebox.showwarning("Uyarı", "Yanlış kullanıcı adı veya şifre!")


def login_screen():
    global entry_username
    global entry_password
    global login_window

    login_window = tk.Tk()
    login_window.title("Giriş Ekranı")
    login_window.configure(bg='lightblue')

    tk.Label(login_window, text="Kullanıcı Adı:",bg="lightblue").pack()
    entry_username = tk.Entry(login_window,bg="white",fg="black", borderwidth=0, relief="flat")
    entry_username.pack()

    tk.Label(login_window, text="Şifre:",bg="lightblue").pack()
    entry_password = tk.Entry(login_window, show="*",bg="white",fg="black", borderwidth=0, relief="flat")
    entry_password.pack()

    login_button = tk.Button(login_window, text="Giriş Yap", command=login, bg="lightblue",highlightbackground='lightblue', highlightcolor='lightblue', highlightthickness=2)
    login_button.pack()

    login_window.mainloop()



tasks = load_tasks()
login_screen()