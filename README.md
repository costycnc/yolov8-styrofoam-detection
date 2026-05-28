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
├── 📄 3_controllo_robot.py             # The robot control logic script
├── 📄 python_editor.py                 # The Tkinter dataset validator script
├── 📄 yolov8n.pt                       # Pre-trained weights file (6.4 MB)
│
└── 📁 dataset/
    ├── 📄 data.yaml                    # Generated automatically by the scripts
    └── 📁 train/
        ├── 📁 images/                  # Put your images here (.jpg, .png)
        │   ├── 📷 1.jpg
        │   ├── 📷 2.jpg
        │   └── ...
        └── 📁 labels/                  # Put your annotation files here (.txt)
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

## 🚀 How to Run

### 1. Dataset Annotation
Run the UI validator tool to draw bounding boxes around styrofoam pieces. Make sure to set the class to `0`.
```bash
python python_editor.py
```

### 2. Model Training
Run the training script to start training YOLOv8 on your dataset using the pre-trained model.
```bash
python 3_adestra_robot_preadestrato.py
```

---

## 💡 Post-Training Operations & Workflow

Once the `data.yaml` file exists and you have successfully obtained the `best.pt` and `last.pt` weights from the training process, **the hardest part of the work is done!** 

You no longer need to modify the AI scripts or repeat the training process. The `best.pt` and `last.pt` files will remain saved on your PC as standard program assets, ready for deployment.

Depending on your current goal, here is how the system behaves and what you should do:

### 1. Daily Production (Running the Robot)
You do not need to launch the training script anymore. Start the final camera vision script directly (e.g., `test_visione.py` utilizing Multithreading at 5 FPS).
* The script will automatically load the optimized `best.pt` weights.
* The camera feed will initialize, and the robot will start tracking the foam blocks on the rail smoothly and synchronously with the GRBL controller while reading the `Idle` state.

### 2. Accidental Re-runs of the Training Script
If you accidentally execute the script containing `model.train()` again, YOLO will respond as follows:
* It will overwrite the contents of `data.yaml` with the same configuration paths (no critical damage done).
* **Warning**: It will generate a completely new results folder (e.g., `addestramento_zero2` or `train2`). It will not overwrite your previous `best.pt` weights, but it will restart calculating the training epochs from scratch, costing you unnecessary computation time.

### 3. Expanding the Dataset in the Future (Adding New Images)
If you capture new photos of the blocks later and want to improve the robot's accuracy:
1. Leave `data.yaml` exactly as it is (since paths and the `polistirolo` class name remain unchanged).
2. Modify the training script to load your previously generated `best.pt` file instead of the stock `yolov8n.pt`.
3. Launch the training process: the AI will not start learning from scratch; instead, it will resume training using the new photos by building on top of its existing knowledge (Fine-tuning)!

```

