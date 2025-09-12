import tkinter as tk
import time

def update_time():
    current_time = time.strftime('%H:%M:%S')
    label.config(text=current_time)
    root.after(1000, update_time)  

root = tk.Tk()
root.title("Always on Top Clock")

root.attributes("-topmost", True)
root.overrideredirect(True)  

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"+{screen_width-250}+20")  

root.wm_attributes("-transparentcolor", "black")

label = tk.Label(root, 
                font=('Arial', 30), 
                bg='black',  
                fg='white',
                padx=10,
                pady=5)
label.pack()

root.update_idletasks()
root.update()

update_time()
root.mainloop()