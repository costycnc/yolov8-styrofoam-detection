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
SOGLIA_VICINO = 25  # Sotto i 25 pixel di errore, passa alla precisione (1mm)
ZONA_MORTA = 6      # Sotto i 6 pixel di errore, il robot è al Punto 0 (si ferma)

in_movimento = False
passo_attuale = "FERMO"
ultimo_controllo_stato = 0

cap = cv2.VideoCapture(0)
print("\n[+] AVVIATO SISTEMA PASSO-PASSO COSTYCNC CON BLOCCO DI SICUREZZA VUOTO!")
print("[*] Premi 'q' sulla finestra video per chiudere.\n")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    altezza, larghezza, _ = frame.shape
    centro_x = int(larghezza / 2)

    # ==================================================
    # 4. CONTROLLO DELLO STATO REALE (RUN / IDLE) DI GRBL
    # ==================================================
    if robot and robot.is_open and in_movimento:
        ora_attuale = time.time()
        if ora_attuale - ultimo_controllo_stato > 0.2:
            robot.write(b"?")
            ultimo_controllo_stato = ora_attuale
        
        if robot.in_waiting > 0:
            linea_ricevuta = robot.readline().decode('utf-8', errors='ignore').strip()
            if "Idle" in linea_ricevuta:
                print(f"[ROBOT] Rilevato stato 'Idle'. Asse fermo. Sblocco la telecamera.")
                in_movimento = False
                passo_attuale = "FERMO"
                robot.reset_input_buffer()

    # Se il robot è fermo, l'IA analizza lo spazio
    if not in_movimento:
        risultati = modello(frame, conf=0.15, verbose=False)
        cubetto_rilevato = False
        errore_x = 0

        for r in risultati:
            if r.boxes is not None:
                for box in r.boxes:
                    cls_id = int(box.cls.item())
                    
                    if cls_id == 0:
                        # CORREZIONE BLINDATA: Estrazione esatta ad indice [0] per avere la lista piatta di numeri
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        
                        cubetto_centro_x = int((x1 + x2) / 2)
                        cubetto_centro_y = int((y1 + y2) / 2)
                        errore_x = cubetto_centro_x - centro_x
                        cubetto_rilevato = True

                        # Disegno degli elementi grafici sul monitor video
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.circle(frame, (cubetto_centro_x, cubetto_centro_y), 5, (255, 255, 0), -1)
                        cv2.line(frame, (centro_x, cubetto_centro_y), (cubetto_centro_x, cubetto_centro_y), (0, 255, 0), 2)
                        cv2.putText(frame, f"Polistirolo: Err {errore_x}px", (x1, y1 - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        break
                if cubetto_rilevato:
                    break

        # ==========================================
        # LOGICA HARDWARE CON CONTROLLO DI RILEVAMENTO
        # ==========================================
        if cubetto_rilevato:
            abs_errore = abs(errore_x)
            segno = 1 if errore_x > 0 else -1

            if abs_errore > ZONA_MORTA:
                if abs_errore > SOGLIA_VICINO:
                    mm_da_fare = 10 * segno
                    passo_attuale = "10mm"
                    comando_gcode = f"G91 G01 X{mm_da_fare} F1000\r"
                    print(f"[IA LONTANO] Err: {errore_x}px. Invio {passo_attuale} -> {comando_gcode.strip()}")
                else:
                    mm_da_fare = 1 * segno
                    passo_attuale = "1mm"
                    comando_gcode = f"G91 G01 X{mm_da_fare} F500\r"
                    print(f"[IA VICINO] Err: {errore_x}px. Invio {passo_attuale} -> {comando_gcode.strip()}")

                if robot and robot.is_open:
                    robot.write(comando_gcode.encode('utf-8'))
                    in_movimento = True  
            else:
                print("[PUNTO 0] Allineato al centro!")
                cv2.putText(frame, "STATO: CENTRATO (PUNTO 0)", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            # Se l'IA non vede nulla, i motori rimangono spenti e l'asse immobile
            cv2.putText(frame, "STATO: NESSUN PEZZO RILEVATO (MOTORI FERMI)", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    else:
        cv2.putText(frame, f"MOTORI IN MOVIMENTO FISICO: {passo_attuale}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Disegno della mezzeria centrale fissa gialla (Asse del robot)
    cv2.line(frame, (centro_x, 0), (centro_x, altezza), (0, 255, 255), 2)
    cv2.imshow("CostyCNC Labs - Monitor Visione AI & Hardware Link", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if robot:
    robot.close()
cap.release()
cv2.destroyAllWindows()
print("[+] Programma terminato.")
