from tkinterdnd2 import TkinterDnD
import ttkbootstrap as ttk
from upload_screen import UploadScreen

def main():
    root = TkinterDnD.Tk()
    root.style = ttk.Style(theme="cosmo")
    app = UploadScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main() 