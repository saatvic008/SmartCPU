# 🖥️ SmartCPU: Interactive Architecture Simulator

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white)

**SmartCPU** is a high-fidelity, interactive software simulator designed to visualize the internal workings of a modern processor. It bridges the gap between theoretical Computer Organization concepts and practical visualization.

## 🌟 Key Features

*   **5-Stage Instruction Pipeline:** Visualizes Fetch, Decode, Execute, Memory, and Write-Back stages in real-time.
*   **Advanced Cache Memory:** Simulates a Direct-Mapped Cache with **LRU (Least Recently Used)** replacement policy.
*   **Hazard Detection & Resolution:** Automatically detects RAW data hazards and Control hazards, implementing **Data Forwarding (Bypassing)** to minimize pipeline stalls.
*   **Interactive Dashboard:** A Streamlit-based UI with Plotly Gantt charts for pipeline analysis.

## 🏗️ System Architecture

The simulator is built on a modular architecture:
1.  **Core Engine:** Handles Registers (R0-R7), ALU operations, and Instruction Parsing.
2.  **Memory Subsystem:** Manages RAM and Cache hierarchy.
3.  **Pipeline Controller:** Orchestrates the flow of instructions and manages cycle counting.

## 🚀 Getting Started

### Prerequisites
*   Python 3.8+
*   pip

### Installation
1.  Clone the repository:
    ```bash
    git clone https://github.com/saatvic008/SmartCPU.git
    cd SmartCPU
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    streamlit run app.py
    ```

## 👥 Team & Contributions

This project was developed using an **AI-Augmented Workflow**, where human engineers focused on complex logic while autonomous agents handled scaffolding and version control.

| Role | Name | Responsibility |
| :--- | :--- | :--- |
| **Team Lead** | Chetan Saatvic | System Architecture, Pipeline Engine, Bot Orchestration |
| **Memory Specialist** | Mathin | Cache Logic (LRU), Main Memory Simulation |
| **Pipeline Specialist** | Srivignesh | Hazard Detection, Data Forwarding Logic |
| **CoreDev Bot** | AI Agent | Automated Core Module Generation |
| **UI/Test Bot** | AI Agent | Automated Dashboard & Test Scaffolding |

## 📄 License
This project is for educational purposes as part of the Computer Organization and Architecture course.
