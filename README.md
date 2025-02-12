# Letters Promptotype

**A Flask-based prototype for letter editions, employing DH Craft’s [Promptotyping](https://github.com/DigitalHumanitiesCraft/excellence/tree/v1.0.0/promptotyping) methodology.**

This project serves as a **promptotype**—a prototype developed using AI-assisted prompt engineering—designed to facilitate the exploration and visualization of **letter corpora** in a structured **XML TEI** format.

---

## Overview
The app provides:
- a **list of letters** with status labels.
- access to a **single-letter view** with multiple tabs:
  - **Original text**
  - **Translation** (if available)
  - **TEI/XML Code view**
  - **Basic metadata**
- a **timeline** showing when letters were sent.

---

## Data Sources
Currently, the prototype is based on letters from the **Joseph von Hammer-Purgstall** digital letter edition (coming soon on [http://gams.uni-graz.at/hpe](http://gams.uni-graz.at/hpe). However, the data can be replaced with letters from the **Hugo Schuchardt Archive** [https://gams.uni-graz.at/hsa](https://gams.uni-graz.at/hsa) (available in the `baissac` folder). Simply replace the dataset in the `data/` folder and restart the app.

**License:**  
The letter data and the app is licensed under **[Creative Commons BY-NC 4.0](http://creativecommons.org/licenses/by-nc/4.0/)**.

---

## Technical Details
- **Framework:** Flask (Python)
- **Hosting:** Render.com
- **Frontend:** HTML, Bootstrap5
- **Data Storage:** JSON-based
- **Dynamic Data Sources:** Can be adapted to different letter collections with similar structure.
- **Scalability:** Successfully tested with ~500 letters.

---

## How to Run Locally
### Clone the Repository
```sh
git clone https://github.com/martinascholger/promptotype-letters.git
cd promptotype-letters/letters
```
### Install Dependencies
```sh
pip install -r requirements.txt
```
### Run the Flask App
```sh
python app.py
```
By default, the app runs at **`http://127.0.0.1:5000/`**.

---

## Live Deployment
The app is deployed on **Render.com**, and the latest version can be accessed at:  **[Live App URL](https://promptotype-letters.onrender.com/)**

---

## 🔧 Development Process
The app was developed using **Promptotyping**, following these stages:
1. **Prompt Engineering**  
   - Designed structured prompts for **AI-assisted** interface generation using Claude 3.5 Sonnet & ChatGPT o1. See more on DH Craft’s [Promptotyping Process](https://github.com/DigitalHumanitiesCraft/excellence/tree/v1.0.0/promptotyping) Guidelines. 
2. **Setup & Environment**  
   - Flask backend with JSON data storage.
3. **Refinement**  
   - Improved individual views (list view, letter detail, metadata, timeline).

---

## Extending the Prototype
- Replace the **data folder** with other TEI-structured letters (e.g., from the **Hugo Schuchardt Archive**).
- Modify the **Flask routes** to adjust views.
- Implement additional **filters** for letter sorting and search.

---

## Citation
To cite this project in your research, please refer to the [CITATION.cff](https://github.com/martinascholger/promptotype-letters/CITATION.cff) file. You can also use GitHub's citation feature by clicking on the "Cite this repository" button on our GitHub page.


