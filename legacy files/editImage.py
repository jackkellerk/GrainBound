import Tkinter as tk

root = tk.Tk()
tk.Label(root, text="this is the root window").pack()
root.geometry("200x200")
for i in range(4):
    window = tk.Toplevel()
    window.geometry("200x200")

    tk.Label(window, text="this is window %s" % i).pack()

window.mainloop()
root.mainloop()