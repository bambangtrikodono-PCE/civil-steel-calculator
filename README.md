# Civil Engineering Steel Calculator (SNI 1729)

A comprehensive Python-based desktop application for steel structure analysis and design, compliant with **SNI 1729:2015 / AISC 360-10**.

## Features

- **Tension Member Analysis**: Yielding and Rupture checks.
- **Compression Member Analysis**: Flexural Buckling capacity.
- **Flexural Member (Beam) Analysis**: Moment capacity ($M_n$) considering Yielding and Lateral-Torsional Buckling (LTB).
- **Beam-Column Interaction**: Interaction equations H1-1a/b.
- **Connection Design**:
    - **Bolted Connections**: Shear capacity.
    - **Welded Connections**: Fillet and Groove weld strength.
    - **Base Plate Design**: Concrete bearing and plate thickness.
    - **Moment End Plate**: Advanced connection check (Flush).
- **Profile Database**: Built-in library for WF, H-Beam, and HSS (Box) sections.
- **Visualization**: Cross-section plotter using Matplotlib.
- **Reporting**: Professional PDF calculation reports.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/civil-steel-calculator.git
    cd civil-steel-calculator
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the main application:
```bash
python main.py
```

## Structure

- `core/`: Core calculation logic, database handling, and report generation.
- `gui/`: User Interface built with `customtkinter`.
- `data/`: CSV database of steel profiles (`profiles.csv`).
- `tests/`: Verification scripts (`verify_logic.py`, etc.).

## Project Portfolio Context (STAR Method)

**Situation:**
Structural engineers often face a gap between manual calculations, which are prone to human error and time-consuming, and expensive commercial software that can be overkill for individual component checks. There was a need for a lightweight, verifiable, and standard-compliant tool for Indonesian civil engineers working with SNI 1729 / AISC 360 standards.

**Task:**
The objective was to develop a custom desktop application capable of performing rigorous structural steel analysis (Tension, Compression, Flexure, Beam-Column, and Connections). The tool required a modern, user-friendly interface, instant visual feedback, and the ability to generate professional PDF calculation reports for design documentation.

**Action:**
- **Architecture**: Designed a modular Python application separating core engineering logic from the GUI.
- **Implementation**: Coded complex structural algorithms including Lateral-Torsional Buckling (LTB) and Interaction Equations (H1-1a/b).
- **Interface**: Built a responsive dark-mode GUI using `customtkinter` with a scrollable dashboard layout.
- **Visualization**: Integrated `matplotlib` to dynamically render cross-sections (WF, H-Beam, HSS) based on user selection.
- **Reporting**: Developed a PDF engine using `reportlab` to automatically generate calculation notes.
- **Verification**: Wrote comprehensive unit tests (`unittest`) to validate calculations against hand-solved examples.

**Result:**
"Civil Engineering" is a fully functional, verifiable structural calculator that reduces component design time by significantly automating repetitive checks. It delivers accurate results compliant with national standards, provides immediate visual confirmation of profiles, and produces ready-to-print reports, demonstrating a strong command of both Structural Engineering principles and Python Software Development.

## Dependencies

- `customtkinter`: Modern GUI framework.
- `reportlab`: PDF generation.
- `matplotlib`: Section visualization.
- `pandas` (optional): For database handling.

## License

MIT License. See `LICENSE` for details.
