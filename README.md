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
   <img width="1384" height="794" alt="image" src="https://github.com/user-attachments/assets/81918ac5-b2cd-438c-8892-02febc406efd" />

   ---

## 🎯 Advanced Usage: Tracking Standard Objects (No Training Required)

You can run the system immediately using standard real-world objects without any custom training. The system natively leverages the pre-trained COCO dataset embedded inside `yolov8n.pt`. 

### 🛠️ How to Modify Your Original Script
To switch from your custom styrofoam model to standard objects, make these 3 quick updates in your code:

1. **Change the model initialization:**
   ```python
   # Replace your best.pt path with the stock weights
   modello = YOLO("yolov8n.pt") 
   ```
2. **Define the target ID at the top of your parameters:**
   ```python
   CLASSE_DA_INSEGUIRE = 39  # Example: 39 for a bottle
   ```
3. **Update the class filter condition inside the loop:**
   ```python
   # Change this: if cls_id == 0:
   # Into this:
   if cls_id == CLASSE_DA_INSEGUIRE:
   ```

*Note: The system will only draw the red bounding box and send G-code commands for the **selected object ID**. All other detected objects will be safely ignored.*

### 📊 Complete COCO Dataset Object ID Reference Table


| ID | Object Name | ID | Object Name | ID | Object Name | ID | Object Name |
| :---: | :--- | :---: | :--- | :---: | :--- | :---: | :--- |
| **0** | person | **20** | sheep | **40** | wine glass | **60** | dining table |
| **1** | bicycle | **21** | cow | **41** | cup | **61** | toilet |
| **2** | car | **22** | elephant | **42** | fork | **62** | tv |
| **3** | motorcycle | **23** | bear | **43** | knife | **63** | laptop |
| **4** | airplane | **24** | zebra | **44** | spoon | **64** | mouse |
| **5** | bus | **25** | giraffe | **45** | bowl | **65** | remote |
| **6** | train | **26** | backpack | **46** | banana | **66** | keyboard |
| **7** | truck | **27** | umbrella | **47** | apple | **67** | cell phone |
| **8** | boat | **28** | handbag | **48** | sandwich | **68** | microwave |
| **9** | traffic light | **29** | tie | **49** | orange | **69** | oven |
| **10** | fire hydrant | **30** | suitcase | **50** | broccoli | **70** | toaster |
| **11** | stop sign | **31** | frisbee | **51** | carrot | **71** | sink |
| **12** | parking meter | **32** | skis | **52** | hot dog | **72** | refrigerator |
| **13** | bench | **33** | snowboard | **53** | pizza | **73** | book |
| **14** | bird | **34** | sports ball | **54** | donut | **74** | clock |
| **15** | cat | **35** | kite | **55** | cake | **75** | vase |
| **16** | dog | **36** | baseball bat | **56** | chair | **76** | scissors |
| **17** | horse | **37** | baseball glove | **57** | couch | **77** | teddy bear |
| **18** | sheep | **38** | skateboard | **58** | potted plant | **78** | hair drier |
| **19** | cow | **39** | bottle | **59** | bed | **79** | toothbrush |

---

## 📚 Official Documentation & References

For deeper technical documentation regarding YOLOv8 settings, training arguments, and model prediction formats, refer to the following official resources:

* **Official Ultralytics Docs:** [https://ultralytics.com](https://ultralytics.com) - Comprehensive guides on custom training, datasets, and hyperparameters.
* **YOLOv8 Predict Mode Guide:** [https://ultralytics.commodes/predict/](https://ultralytics.commodes/predict/) - Technical layout of how bounding box coordinates (`xyxy`), labels, and confidence thresholds are handled in real-time streams.
* **YOLOv8 GitHub Repository:** [https://github.com](https://github.com) - Source code, official issue tracking, and community discussions.






```

