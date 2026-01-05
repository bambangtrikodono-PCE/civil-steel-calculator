from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

class PDFReport:
    @staticmethod
    def generate(filepath, title, inputs, results):
        """
        Generate a PDF report.
        
        Args:
            filepath (str): Output path.
            title (str): Report title (e.g., "Tension Member Check")
            inputs (dict): Dictionary of input parameters.
            results (dict): Dictionary of calculation results.
        """
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Custom Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor("#1f538d"),
            spaceAfter=20
        )
        
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor("#2b2b2b"),
            spaceBefore=15,
            spaceAfter=10
        )

        # 1. Header
        elements.append(Paragraph("Civil Engineering - Calculation Report", title_style))
        elements.append(Paragraph(f"<b>Type:</b> {title}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        # 2. Inputs
        elements.append(Paragraph("Input Parameters", header_style))
        
        input_data = [["Parameter", "Value"]]
        for k, v in inputs.items():
            input_data.append([k, str(v)])
            
        t_input = Table(input_data, colWidths=[200, 200])
        t_input.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#e1e1e1")),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#dcdcdc")),
        ]))
        elements.append(t_input)
        elements.append(Spacer(1, 20))

        # 3. Results
        elements.append(Paragraph("Calculation Results", header_style))
        
        res_data = [["Item", "Result"]]
        status = "UNKNOWN"
        
        for k, v in results.items():
            if k == "status":
                status = v
                continue
            # Format numbers if possible
            val_str = str(v)
            if isinstance(v, float):
                val_str = f"{v:.3f}"
            res_data.append([k, val_str])
            
        t_res = Table(res_data, colWidths=[200, 200])
        t_res.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#e1e1e1")),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#dcdcdc")),
        ]))
        elements.append(t_res)
        elements.append(Spacer(1, 20))

        # 4. Status Box
        status_color = colors.green if "SAFE" in status or "OK" in status else colors.red
        status_text = f"<b>STATUS: {status}</b>"
        
        p_status = Paragraph(status_text, ParagraphStyle(
            'Status', parent=styles['Normal'], fontSize=14, textColor=status_color, alignment=1
        ))
        elements.append(p_status)

        # Build PDF
        doc.build(elements)
