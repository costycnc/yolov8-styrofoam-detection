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
        └── 📁 labels/                  # Put your annotation files here (.txt)
```

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

