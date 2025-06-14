# 🧪 EpiClim: Climate-Linked Disease Outbreaks in India (2009–2023)

This repository explores the intricate relationship between **climate variables** and **epidemic outbreaks** in India using the publicly available **EpiClim dataset**. The project integrates epidemiological surveillance data with environmental indicators to uncover patterns, thresholds, and potential early warning signals for disease spread.

---

## 📦 About the Dataset

The **EpiClim dataset** provides **district-level, weekly data** on epidemic outbreaks across India from **2009 to 2023**, curated for **climate-health modeling and geospatial analysis**. It combines:

- 📍 **Geographical info**: District/state names, latitude & longitude  
- 🦠 **Disease data**: Weekly case & death counts across diseases like acute diarrhoeal disease, malaria, dengue, etc.  
- 🌧️ **Climatic indicators**:  
  - Precipitation (mm/day)  
  - Average temperature (Kelvin)  
  - Leaf Area Index (vegetation density proxy)

**Structure**: 8,985 rows × 14 columns  
**Granularity**: Weekly records by district

---

## 📊 Analysis Overview

The core analysis was conducted in a Jupyter Notebook (`EpiClim_dataset_analysis.ipynb`), covering:

- 🔹 Data cleaning, and exploratory statistics  
- 🔹 Temporal trends of outbreaks across years and seasons  
- 🔹 Disease-specific profiling (ADD, Dengue, Cholera, etc.)  
- 🔹 Regression analysis & t-tests to detect climate thresholds  
- 🔹 Climate segmentation for precipitation-based risk zones  

📌 **Bonus**: An infographic summarizing key insights is included in [Quick_breakdown.pdf](Quick_breakdown.pdf).

---

## 🧠 Key Findings (At a Glance)

- **Precipitation** emerged as the strongest predictor of outbreaks  
- Clear seasonal peaks aligned with the **monsoon cycle**  
- **West Bengal**, **Delhi**, and **UP** reported the highest disease burdens  
- Statistically significant outbreak thresholds detected for rainfall > 30 mm/week  
- India has seen a **notable decline in outbreak cases** post-2018

📉 Read the full notebook or see the infographic for detailed plots and statistical models.

---

## 📁 Repository Contents

| File | Description |
|------|-------------|
| `EpiClim_dataset_analysis.ipynb` | Full Python notebook with data cleaning, EDA, modeling, and plots |
| `Quick_breakdown.pdf` | Quick infographic summary of the analysis |
| `monthly_disease_outbreak.csv` | *(Expected)* Raw dataset used for the analysis |

---

## 🚀 How to Use

1. Clone this repositorys
2. Open `EpiClim_dataset_analysis.ipynb` in Jupyter or VS Code
3. Run all cells to reproduce the full analysis
4. Use or adapt plots and insights in your own research or public health projects

---

## 📚 Citation & Attribution

This project is built on the **EpiClim** dataset curated for GeoHealth research. If you use this repository or visualizations in academic or applied work, please consider citing the dataset source and crediting this repository.

---

## 📬 Contact

For questions, collaborations, or feedback, feel free to reach out via GitHub Issues.

---

**Let data and climate guide public health.**
