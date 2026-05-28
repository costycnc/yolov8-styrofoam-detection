import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ValidatoreYolo:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO Automatic Viewer")
        self.root.geometry("1000x650")

        self.img_obj = None
        self.boxes = []
        self.name_base = ""
        self.real_w = 1
        self.real_h = 1
        self.draw = False
        
        # Dimensioni di fallback più stabili per evitare bug di rendering iniziali
        self.dw = 700
        self.dh = 500

        # UI Layout
        top = tk.Frame(root, pady=10)
        top.pack(fill=tk.X)
        
        tk.Button(top, text="Seleziona Immagine", command=self.carica_immagine, font=("Arial", 10, "bold"), bg="#007bff", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Label(top, text="Classe:").pack(side=tk.LEFT, padx=5)
        self.cls_ent = tk.Entry(top, width=4)
        self.cls_ent.insert(0, "0") # Cambiato a 0 per combaciare con 'polistirolo'
        self.cls_ent.pack(side=tk.LEFT)
        self.lbl_info = tk.Label(top, text="Nessun file", font=("Arial", 10))
        self.lbl_info.pack(side=tk.LEFT, padx=20)

        # Workspace
        self.cvs = tk.Canvas(root, bg="white", cursor="crosshair")
        self.cvs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.cvs.bind("<ButtonPress-1>", self.mousedown)
        self.cvs.bind("<B1-Motion>", self.mousemove)
        self.cvs.bind("<ButtonRelease-1>", self.mouseup)

        right = tk.Frame(root, width=220, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        right.pack_propagate(False)

        tk.Label(right, text="Dati YOLO:").pack(anchor=tk.W)
        self.txt_out = tk.Text(right, height=15, width=25, font=("Courier", 9))
        self.txt_out.pack(fill=tk.X, pady=5)

        tk.Button(right, text="Salva .txt", command=self.salva_txt, bg="#28a745", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=5)
        tk.Button(right, text="Svuota", command=self.svuota, bg="#dc3545", fg="white").pack(fill=tk.X, pady=5)

    def carica_immagine(self):
        f_path = filedialog.askopenfilename(filetypes=[("Immagini", "*.jpg *.jpeg *.png *.bmp *.webp")])
        if not f_path: return

        self.boxes = []
        folder_corrente = os.path.dirname(f_path)
        cartella_principale = os.path.dirname(folder_corrente) 
        
        nome_file = os.path.basename(f_path)
        self.name_base = os.path.splitext(nome_file)[0]
        
        txt_path = os.path.join(cartella_principale, "labels", self.name_base + ".txt")

        if os.path.exists(txt_path):
            with open(txt_path, 'r') as f:
                for riga in f:
                    p = riga.strip().split()
                    # 🛠️ CORREZIONE 1: Pulizia profonda e validazione rigorosa dei 5 parametri YOLO
                    if len(p) >= 5:
                        try:
                            c = int(p[0])
                            x = float(p[1])
                            y = float(p[2])
                            w = float(p[3])
                            h = float(p[4])
                            if h > 0: # Salva il box solo se l'altezza è valida
                                self.boxes.append({'c': c, 'x': x, 'y': y, 'w': w, 'h': h})
                        except ValueError:
                            continue
            self.lbl_info.config(text=f"{nome_file} (TXT Trovato!)", fg="green")
        else:
            self.lbl_info.config(text=f"{nome_file} (Nessun TXT)", fg="red")

        self.pil_img = Image.open(f_path)
        self.real_w, self.real_h = self.pil_img.size
        
        # Forza Tkinter ad aggiornare la finestra per leggere le dimensioni reali del Canvas
        self.root.update_idletasks()
        self.rendering()

    def rendering(self):
        if not hasattr(self, 'pil_img'): return
        cw, ch = self.cvs.winfo_width(), self.cvs.winfo_height()
        if cw < 10: cw, ch = 700, 500

        ratio = min(cw / self.real_w, ch / self.real_h)
        self.dw, self.dh = int(self.real_w * ratio), int(self.real_h * ratio)
        
        img_resized = self.pil_img.resize((self.dw, self.dh), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img_resized)
        
        self.cvs.delete("all")
        self.ox, self.oy = (cw - self.dw) // 2, (ch - self.dh) // 2
        self.cvs.create_image(self.ox, self.oy, anchor=tk.NW, image=self.tk_img)

        for b in self.boxes:
            w, h = b['w'] * self.dw, b['h'] * self.dh
            x = (b['x'] * self.dw) - (w / 2) + self.ox
            y = (b['y'] * self.dh) - (h / 2) + self.oy
            self.cvs.create_rectangle(x, y, x + w, y + h, outline="red", width=2)
            self.cvs.create_text(x + 5, y - 10, text=f"Cls: {b['c']}", fill="red", anchor=tk.NW, font=("Arial", 9, "bold"))
        
        self.aggiorna_testo()

    def aggiorna_testo(self):
        self.txt_out.delete("1.0", tk.END)
        testo = ""
        for b in self.boxes:
            testo += f"{b['c']} {b['x']:.6f} {b['y']:.6f} {b['w']:.6f} {b['h']:.6f}\n"
        # 🛠️ CORREZIONE 2: strip() pulisce i ritorni a capo vuoti alla fine del box di testo
        self.txt_out.insert(tk.END, testo.strip())

    def mousedown(self, e):
        if not hasattr(self, 'pil_img'): return
        self.sx, self.sy = e.x, e.y
        self.draw = True
        self.rect_id = self.cvs.create_rectangle(e.x, e.y, e.x, e.y, outline="green", width=2)

    def mousemove(self, e):
        if self.draw and hasattr(self, 'rect_id'):
            self.cvs.coords(self.rect_id, self.sx, self.sy, e.x, e.y)

    def mouseup(self, e):
        if not self.draw: return
        self.draw = False
        
        # Rileva le coordinate relative all'immagine ritagliata
        x1, y1 = max(0, min(self.sx, e.x) - self.ox), max(0, min(self.sy, e.y) - self.oy)
        x2, y2 = min(self.dw, max(self.sx, e.x) - self.ox), min(self.dh, max(self.sy, e.y) - self.oy)
        
        pw, ph = x2 - x1, y2 - y1
        if pw < 5 or ph < 5:
            self.cvs.delete(self.rect_id)
            return
            
        try: c_val = int(self.cls_ent.get())
        except: c_val = 0

        # 🛠️ CORREZIONE 3: Blocco matematico di sicurezza per impedire coordinate a zero o negative
        norm_w = max(0.001, pw / self.dw)
        norm_h = max(0.001, ph / self.dh)

        self.boxes.append({
            'c': c_val,
            'x': (x1 + (pw / 2)) / self.dw,
            'y': (y1 + (ph / 2)) / self.dh,
            'w': norm_w,
            'h': norm_h
        })
        self.rendering()

    def salva_txt(self):
        if not self.name_base: return
        f_dir = filedialog.askdirectory(title="Seleziona la cartella /labels/ dove salvare")
        if not f_dir: return
        p_salvataggio = os.path.join(f_dir, self.name_base + ".txt")
        
        # 🛠️ CORREZIONE 4: Salvataggio pulito senza righe vuote spurie finali
        contenuto_pulito = self.txt_out.get("1.0", tk.END).strip()
        with open(p_salvataggio, 'w') as f:
            f.write(contenuto_pulito)
            
        messagebox.showinfo("Salvato", f"File scritto in:\n{p_salvataggio}")

    def svuota(self):
        if messagebox.askyesno("Svuota", "Cancello i riquadri?"):
            self.boxes = []
            self.rendering()

if __name__ == "__main__":
    root = tk.Tk()
    app = ValidatoreYolo(root)
    root.mainloop()
