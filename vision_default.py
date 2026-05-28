import cv2
import os
import time
from ultralytics import YOLO

# ==========================================
# 1. CARICAMENTO MODELLO STANDARD COCO
# ==========================================
CARTELLA_CORRENTE = os.path.dirname(os.path.abspath(__file__))
PESO_STANDARD_PATH = os.path.join(CARTELLA_CORRENTE, "yolov8n.pt")

try:
    modello = YOLO(PESO_STANDARD_PATH)
    print(f"[+] Modello Standard COCO caricato con successo da {PESO_STANDARD_PATH}!")
except Exception as e:
    print(f"[-] Errore nel caricamento del file yolov8n.pt: {e}")
    exit()

# ==========================================
# 2. INIZIALIZZAZIONE WEBCAM (DIRECTSHOW)
# ==========================================
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print(f"\n[+] AVVIATO MONITOR DI SOLA VISIONE GLOBALE COSTYCNC!")
print("[*] Inizializzazione DirectShow della webcam...")

# Piccolo riscaldamento per stabilizzare il sensore video
for i in range(5):
    cap.read()
    time.sleep(0.05)

print("[*] Premi 'q' sulla finestra video per chiudere.\n")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        time.sleep(0.01)
        continue

    altezza, larghezza, _ = frame.shape
    centro_x = int(larghezza / 2)

    # Analisi in tempo reale degli 80 oggetti standard con soglia di confidenza al 25%
    risultati = modello(frame, conf=0.25, verbose=False)
    
    oggetti_trovati_nel_frame = 0

    for r in risultati:
        if r.boxes is not None:
            for box in r.boxes:
                cls_id = int(box.cls.item())
                nome_oggetto = modello.names[cls_id]
                confidenza = box.conf.item() # Livello di certezza del rilevamento
                
                # Estrazione delle coordinate spaziali del rettangolo
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                
                # 🟢 DISEGNA IL QUADRATO SU OGNI OGGETTO IDENTIFICATO
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Stampa il nome dell'oggetto e la percentuale di precisione sopra il quadrato
                testo_etichetta = f"{nome_oggetto.upper()} {confidenza:.2f}"
                cv2.putText(frame, testo_etichetta, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                oggetti_trovati_nel_frame += 1

    # Disegno della mezzeria centrale fissa gialla di riferimento visivo
    cv2.line(frame, (centro_x, 0), (centro_x, altezza), (0, 255, 255), 2)

    # Mostra lo stato generale nel monitor video
    if oggetti_trovati_nel_frame > 0:
        cv2.putText(frame, f"OGGETTI RILEVATI: {oggetti_trovati_nel_frame}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "STATO: SCANSIONE IN CORSO (NESSUN OGGETTO)", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Mostra a video il flusso grafico finale elaborato
    cv2.imshow("CostyCNC Labs - Pure AI Vision Monitor", frame)

    # Chiude la finestra se premi il tasto 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("[+] Programma di visione terminato.")

