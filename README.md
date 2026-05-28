# YOLOv8 Styrofoam Detection System

This repository contains the dataset validator script and the custom training pipeline using YOLOv8 to detect styrofoam pieces on a conveyor belt system.

---

## 🛠️ Requirements & Installation

Before running the scripts, you need to set up your Python environment and install the required dependencies.

### 1. Prerequisites
* **Python 3.8** or higher installed on your system.

### 2. Install Dependencies
Open your terminal or command prompt and run the following command to install the necessary packages (`ultralytics` for YOLOv8 and `Pillow` for the UI images):

```bash
pip install ultralytics pillow
```

*Note: Tkinter comes pre-installed with standard Python installations on Windows.*

---

## 📁 Project Structure

To avoid path errors or permission issues, please organize your local folder exactly like this:

```text
📁 robot-project/
│
├── 📄 3_adestra_robot_preadestrato.py  # The pre-trained weights training script
├── 📄 3_controllo_robot.py             # The main robot control logic script (5 FPS Multithreading)
├── 📄 python_editor.py                 # The Tkinter dataset validator script
├── 📄 yolov8n.pt                       # Pre-trained weights file (6.4 MB)
│
└── 📁 dataset/
    ├── 📄 data.yaml                    # Generated automatically by the scripts
    └── 📁 train/
        ├── 📁 images/                  # Contains 4 pre-compiled sample images
        │   ├── 📷 1.jpg
        │   ├── 📷 2.jpg
        │   └── ...
        └── 📁 labels/                  # Contains the corresponding .txt annotation files
            ├── 📄 1.txt
            ├── 📄 2.txt
            └── ...
```

### ⚠️ Critical Rules to Check
* **Identical Names**: The image `1.jpg` in `images/` and its annotation file `1.txt` in `labels/` must have the exact same filename.
* **Lowercase Folder Names**: The folders `images` and `labels` must be strictly lowercase. YOLO looks for these exact names.
* **Location of `yolov8n.pt`**: It must be placed in the exact same directory as your Python scripts, otherwise the program will halt with a path error.

If this structure is followed, YOLO will automatically create a `runs/` folder inside your project directory to store results without triggering Windows permission errors.

---

## 🚀 How to Run & Project Status

### 📦 Out-of-the-Box Setup & Real-Time Operation
The repository comes **pre-compiled with 4 sample images** already placed inside the `images/` folder.
* **Reviewing Annotations**: You can run `python_editor.py` immediately, open any of the 4 images, and instantly see the red bounding boxes (labels) generated during testing.
* **Instant Deployment**: Since the dataset is ready, you can run the main script directly. If you place real styrofoam pieces under the camera and connect your GRBL-compatible machine, the system will immediately start tracking and streaming **G-code commands** to the hardware!

### 1. Dataset Annotation (Optional)
If you want to view, modify, or add new bounding boxes around styrofoam pieces, run the UI tool. Make sure to keep the class set to `0`.
```bash
python python_editor.py
```

### 2. Model Training (Training from Scratch or Fine-Tuning)
* **To train from scratch**: Delete the existing 4 images/labels, insert your new custom dataset into the folders, and run the script.
* **To fine-tune**: Keep the current files, append your new images, and launch the pipeline:
```bash
python 3_adestra_robot_preadestrato.py
```

---

## 💡 Post-Training Operations & Workflow

Once the `data.yaml` file exists and you have successfully obtained the `best.pt` and `last.pt` weights from the training process, **the hardest part of the work is done!** 

You no longer need to modify the AI scripts or repeat the training process. The `best.pt` and `last.pt` files will remain saved on your PC as standard program assets, ready for deployment.

Depending on your current goal, here is how the system behaves and what you should do:

### 1. Daily Production (Running the Robot)
You do not need to launch the training script anymore. Start the final camera vision script directly (`3_controllo_robot.py` utilizing Multithreading at 5 FPS).
* The script will automatically load the optimized `best.pt` weights.
* The camera feed will initialize, and the robot will start tracking the foam blocks on the rail smoothly and synchronously with the GRBL controller while reading the `Idle` state.

### 2. Accidental Re-runs of the Training Script
If you accidentally execute the script containing `model.train()` again, YOLO will respond as follows:
* It will overwrite the contents of `data.yaml` with the same configuration paths (no critical damage done).
* **Warning**: It will generate a completely new results folder (e.g., `runs/` variations). It will not overwrite your previous `best.pt` weights, but it will restart calculating the training epochs from scratch, costing you unnecessary computation time.

### 3. Expanding the Dataset in the Future (Adding New Images)
If you capture new photos of the blocks later and want to improve the robot's accuracy:
1. Leave `data.yaml` exactly as it is (since paths and the `polistirolo` class name remain unchanged).
2. Modify the training script to load your previously generated `best.pt` file instead of the stock `yolov8n.pt`.
3. Launch the training process: the AI will not start learning from scratch; instead, it will resume training using the new photos by building on top of its existing knowledge (Fine-tuning)!

## python_editor.py

   <img width="1268" height="765" alt="image" src="https://github.com/user-attachments/assets/771f3d2b-0de5-4bce-869b-61ae525ababf" />

## 3_controllo_robot.py
   

   <img width="1350" height="809" alt="image" src="https://github.com/user-attachments/assets/f124ebe1-b0ba-407e-9c88-0647574c5f2e" />




```

