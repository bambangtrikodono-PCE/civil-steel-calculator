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

## Dependencies

- `customtkinter`: Modern GUI framework.
- `reportlab`: PDF generation.
- `matplotlib`: Section visualization.
- `pandas` (optional): For database handling.

## License

MIT License. See `LICENSE` for details.
