import os
from ultralytics import YOLO

# Trova la cartella dove si trova questo script e il file yolov8n.pt da 6MB
CARTELLA_CORRENTE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(CARTELLA_CORRENTE, "dataset")
YAML_PATH = os.path.join(BASE_DIR, "data.yaml")
LOCAL_PT_PATH = os.path.join(CARTELLA_CORRENTE, "yolov8n.pt")

# Definiamo dove salvare i risultati dell'addestramento (nella tua cartella)
CARTELLA_RISULTATI = os.path.join(CARTELLA_CORRENTE, "runs")

print(f"[*] Lavoro nella cartella locale: {CARTELLA_CORRENTE}")

if not os.path.exists(LOCAL_PT_PATH):
    print(f"[-] Errore: Metti il file 'yolov8n.pt' da 6MB qui: {LOCAL_PT_PATH}")
    exit()

# Crea il file data.yaml
yaml_content = f"""
path: {BASE_DIR}
train: train/images
val: train/images
names:
  0: polistirolo
"""

os.makedirs(BASE_DIR, exist_ok=True)
with open(YAML_PATH, "w") as f: 
    f.write(yaml_content.strip())

# Carica il modello locale
model = YOLO(LOCAL_PT_PATH) 

print("[*] Avvio addestramento sicuro...")
#results = model.train(data=YAML_PATH,epochs=60,imgsz=640,device="cpu",workers=2,project=CARTELLA_RISULTATI)

results = model.train(
    data=YAML_PATH,
    epochs=60,       
    imgsz=640,
    device="cpu",
    project=CARTELLA_RISULTATI,  # <--- FONDAMENTALE: Evita l'errore di accesso negato in System32!
    workers=8,                  # <--- VELOCE: Usa tutti i core della tua CPU
    plots=False,                # <--- VELOCE: Non perde tempo a disegnare grafici pesanti
    verbose=False               # <--- VELOCE: Riduce le scritte a schermo per non rallentare il terminale
)


