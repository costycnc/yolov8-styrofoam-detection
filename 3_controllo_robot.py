import cv2
import os
import serial
import time
from ultralytics import YOLO

# ==========================================
# 1. CONFIGURAZIONE HARDWARE E PORTA SERIALE
# ==========================================
PORTA_SERIALE = 'COM3'  # Cambiala con la COM reale del tuo robot
BAUD_RATE = 115200

try:
    robot = serial.Serial(PORTA_SERIALE, BAUD_RATE, timeout=0.05)
    time.sleep(2) 
    robot.reset_input_buffer()
    robot.reset_output_buffer()
    print(f"[+] Connesso con successo al robot su {PORTA_SERIALE}!")
except Exception as e:
    print(f"[-] Errore di connessione seriale: {e}")
    print("[*] Esecuzione in modalità DEMO (senza invio comandi reali).")
    robot = None

# ==========================================
# 2. CONFIGURAZIONE PERCORSI IA
# ==========================================
CARTELLA_CORRENTE = os.path.dirname(os.path.abspath(__file__))
PESO_PATH = os.path.join(CARTELLA_CORRENTE, "addestramento_da_zero", "weights", "best.pt")

if not os.path.exists(PESO_PATH):
    PESO_PATH = r"C:\test\robot_project\addestramento_da_zero\weights\best.pt"

try:
    modello = YOLO(PESO_PATH)
    print("[+] Modello 'polistirolo' caricato con successo!")
except Exception as e:
    print(f"[-] Errore nel caricamento del file dei pesi: {e}")
    exit()

# ==========================================
# 3. PARAMETRI DI ALLINEAMENTO PASSO-PASSO
# ==========================================
SOGLIA_VICINO = 25  
ZONA_MORTA = 6      

# 🛠️ CORREZIONE DEFINITIVA PER WINDOWS: Usiamo cv2.CAP_DSHOW per evitare il bug MSMF
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

print("\n[+] AVVIATO SISTEMA SCATTO SINGOLO COSTYCNC!")
print("[*] Inizializzazione DirectShow della webcam...")

# Piccolo warm-up per stabilizzare l'hardware
for i in range(5):
    cap.read()
    time.sleep(0.05)

print("[*] Premi 'q' sulla finestra video per chiudere.\n")

while cap.isOpened():
    # Scatto del fotogramma statico a motore fermo
    success, frame = cap.read()
    
    # Se fallisce un singolo frame per interferenza, riprova senza bloccarsi
    if not success:
        time.sleep(0.01)
        continue

    altezza, larghezza, _ = frame.shape
    centro_x = int(larghezza / 2)

    # Passa l'immagine statica a YOLO
    risultati = modello(frame, conf=0.15, verbose=False)
    cubetto_rilevato = False
    errore_x = 0
    x1, y1, x2, y2 = 0, 0, 0, 0
    cubetto_centro_x, cubetto_centro_y = 0, 0

    for r in risultati:
        if r.boxes is not None:
            for box in r.boxes:
                if int(box.cls.item()) == 0:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist()) 
                    cubetto_centro_x = int((x1 + x2) / 2)
                    cubetto_centro_y = int((y1 + y2) / 2)
                    errore_x = cubetto_centro_x - centro_x
                    cubetto_rilevato = True
                    break
            if cubetto_rilevato:
                break

    # ==================================================
    # 4. DISEGNO GRAFICO SULLO SCATTO FISSO ATTUALE
    # ==================================================
    if cubetto_rilevato:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.circle(frame, (cubetto_centro_x, cubetto_centro_y), 5, (255, 255, 0), -1)
        cv2.line(frame, (centro_x, cubetto_centro_y), (cubetto_centro_x, cubetto_centro_y), (0, 255, 0), 2)
        cv2.putText(frame, f"Polistirolo: Err {errore_x}px", (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.line(frame, (centro_x, 0), (centro_x, altezza), (0, 255, 255), 2)

    # ==================================================
    # 5. LOGICA HARDWARE E ATTESA BLOCCANTE DEL MOVIMENTO
    # ==================================================
    if cubetto_rilevato:
        abs_errore = abs(errore_x)
        segno = 1 if errore_x > 0 else -1

        if abs_errore > ZONA_MORTA:
            if abs_errore > SOGLIA_VICINO:
                mm_da_fare = 10 * segno
                passo_attuale = "10mm"
                comando_gcode = f"G91 G01 X{mm_da_fare} F1000\r"
            else:
                mm_da_fare = 1 * segno
                passo_attuale = "1mm"
                comando_gcode = f"G91 G01 X{mm_da_fare} F500\r"

            print(f"[FOTO ELABORATA] Err: {errore_x}px. Invio -> {comando_gcode.strip()}")
            cv2.putText(frame, f"Esecuzione asse: {passo_attuale}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.imshow("CostyCNC Labs - Monitor Visione AI & Hardware Link", frame)
            cv2.waitKey(1)

            # Invia il comando al robot
            if robot and robot.is_open:
                robot.write(comando_gcode.encode('utf-8'))
                time.sleep(0.15) 
                
                # Ciclo di attesa basato sullo stato Idle
                mentre_muove = True
                while mentre_muove:
                    robot.write(b"?")
                    time.sleep(0.1)
                    if robot.in_waiting > 0:
                        risposta = robot.readline().decode('utf-8', errors='ignore').strip()
                        if "Idle" in risposta:
                            print("[ROBOT] Movimento completato con successo. Sblocco per prossima foto.")
                            mentre_muove = False
                robot.reset_input_buffer()
        else:
            print("[PUNTO 0] Allineato al centro!")
            cv2.putText(frame, "STATO: CENTRATO (PUNTO 0)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imshow("CostyCNC Labs - Monitor Visione AI & Hardware Link", frame)
    else:
        cv2.putText(frame, "STATO: VUOTO - ATTESA PEZZO", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.imshow("CostyCNC Labs - Monitor Visione AI & Hardware Link", frame)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

if robot:
    robot.close()
cap.release()
cv2.destroyAllWindows()
print("[+] Programma terminato.")
