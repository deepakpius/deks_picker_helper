import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
import tempfile
from fpdf import FPDF
import types

# --- ADD: Latin-1 sanitizer for FPDF (minimal, no logic change) ---
def latin1(s):
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    return s.encode("latin-1", "replace").decode("latin-1")

# Custom sort list
custom_pick_order = [
    '1705', '1716', '1717', '1728', '1729', '1740', '1741', '1752', '1753', '1764', '1765', '1776',
    '1777', '1788', '1789', '1800', '1801', '1812', '1813', '1824', '1825', '1836', '1837', '1848',
    '1849', '1860', '1704', '1693', '1548', '1537', '1692', '1681', '1536', '1525', '1680', '1669',
    '1524', '1513', '1668', '1657', '1512', '1501', '1656', '1645', '1500', '1489', '1644', '1633',
    '1488', '1477', '1632', '1621', '1476', '1465', '1620', '1609', '1464', '1453', '1608', '1597',
    '1452', '1441', '1596', '1585', '1440', '1429', '1584', '1573', '1428', '1417', '1572', '1561',
    '1416', '1405', '1560', '1549', '1404', '1393', '1392', '1381', '1380', '1369', '997', '1008',
    '1189', '1200', '1009', '1020', '1201', '1212', '1021', '1032', '1213', '1224', '1033', '1044',
    '1225', '1236', '1045', '1056', '1237', '1248', '1057', '1068', '1249', '1260', '1069', '1080',
    '1261', '1272', '1081', '1092', '1273', '1285', '1093', '1104', '1284', '1296', '1105', '1116',
    '1297', '1308', '1117', '1128', '1309', '1320', '1129', '1140', '1321', '1332', '1141', '1152',
    '1333', '1344', '1153', '1164', '1345', '1356', '1165', '1176', '1357', '1368', '117', '1188',
    '804', '793', '792', '781', '996', '985', '780', '769', '984', '973', '768', '757', '972', '961',
    '756', '745', '960', '949', '744', '733', '948', '937', '732', '721', '936', '925', '720', '709',
    '924', '913', '708', '697', '912', '901', '698', '685', '900', '889', '684', '673', '888', '877',
    '672', '661', '409', '420', '145', '156', '157', '421', '432', '168', '169', '433', '444', '180',
    '181', '445', '456', '192', '193', '457', '468', '204', '205', '469', '480', '216', '217', '481',
    '492', '228', '229', '493', '504', '240', '241', '505', '516', '252', '253', '517', '528', '264',
    '265', '529', '540', '276', '277', '541', '552', '288', '289', '300', '660', '649', '876', '865',
    '648', '637', '864', '853', '636', '625', '852', '841', '624', '613', '840', '829', '828', '817', 
    '612', '601', '600', '589', '816', '805', '588', '577', '576', '565', '564', '553', '001', '012', '013',
    '024', '025','301', '312', '036', '037', '313', '324', '048', '049', '325', '336', '061', '072', '337', '348', 
    '073','084', '349', '360', '085', '096', '361', '372', '097', '108', '373', '384', '109', '120', '385',
    '396', '121', '132', '397', '408', '133', '144'
]
custom_pick_order_2 = ['564', '553','001', '012', '013','024', '025','301', '312', '036', '037', '313', '324', '048', '049', '325', '336', '061', '072', 
                       '337', '348','073','084', '349', '360', '085', '096', '361', '372', '097', '108', '373', '384', '109', '120', '385','396', 
                       '121', '132', '397', '408', '133', '144',  '409', '420', '145', '156', '157', '421', '432', '168', '169', '433', '444', 
                       '180','181', '445', '456', '192', '193', '457', '468', '204', '205', '469', '480', '216', '217', '481','492', '228', 
                       '229', '493', '504', '240', '241', '505', '516', '252', '253', '517', '528', '264','265', '529', '540', '276', '277', 
                       '541', '552', '288', '289', '300', '804', '793', '792', '781', '996', '985', '780', '769', '984', '973', '768', '757', 
                       '972', '961','756', '745', '960', '949', '744', '733', '948', '937', '732', '721', '936', '925', '720', '709',
                       '924', '913', '708', '697', '912', '901', '698', '685', '900', '889', '684', '673', '888', '877', '672', '661', '660', 
                       '649', '876', '865', '648', '637', '864', '853', '636', '625', '852', '841', '624', '613', '840', '829', '612', '601', 
                       '828', '817', '600', '589', '816', '805', '588', '577', '576', '565',  '997', '1008',
                       '1189', '1200', '1009', '1020', '1201', '1212', '1021', '1032', '1213', '1224', '1033', '1044',
                       '1225', '1236', '1045', '1056', '1237', '1248', '1057', '1068', '1249', '1260', '1069', '1080',
                       '1261', '1272', '1081', '1092', '1273', '1285', '1093', '1104', '1284', '1296', '1105', '1116',
                       '1297', '1308', '1117', '1128', '1309', '1320', '1129', '1140', '1321', '1332', '1141', '1152',
                       '1333', '1344', '1153', '1164', '1345', '1356', '1165', '1176', '1357', '1368', '117', '1188',  
                       '1548', '1537', '1692', '1681', '1536', '1525', '1680', '1669','1524', '1513', '1668', '1657', 
                       '1512', '1501', '1656', '1645', '1500', '1489', '1644', '1633','1488', '1477', '1632', '1621', 
                       '1476', '1465', '1620', '1609', '1464', '1453', '1608', '1597','1452', '1441', '1596', '1585', 
                       '1440', '1429', '1584', '1573', '1428', '1417', '1572', '1561','1416', '1405', '1560', '1549', 
                       '1404', '1393', '1392', '1381', '1380', '1369', '1693', '1704', '1860', '1849', '1848', '1837', 
                       '1836', '1825', '1824', '1813', '1812', '1801', '1800', '1789', '1788', '1777', '1776', '1765', 
                       '1764', '1753', '1752', '1741', '1740', '1729', '1728', '1717', '1716', '1705']
# <-- Replace this as needed / Trained model

st.set_page_config(page_title="Deks Industries", layout="wide")

# Header with logo
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://d1hbpr09pwz0sk.cloudfront.net/logo_url/deks-industries-australasia-405aec84", width=80)
with col2:
    st.title("📄 Picking Ticket Sorter")

uploaded_file = st.file_uploader("Upload your PICKING TICKET PDF", type="pdf")

# Sorting method selection
sort_option = st.radio("Choose Sorting Method:", ("Sort by Ascending", "Sort by Model I", "Sort by Model II"))

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        pdf_path = tmp_file.name

    doc = fitz.open(pdf_path)
    lines = []
    for page in doc:
        lines += page.get_text().splitlines()
        
    # Extract Order Number from the document text
    full_text = "\n".join(lines) 
    m = re.search(r"Order\s*Number\s*:\s*([A-Za-z0-9\-_/]+)", full_text, re.IGNORECASE)  
    order_number = m.group(1).strip() if m else "UNKNOWN"  
    st.info(f"**Order Number:** {order_number}") 
    
    entries = []
    part_number_pattern = re.compile(r'^[A-Z0-9\-/]+$')

    for i in range(6, len(lines)):
        if lines[i].strip() == "EA":
            committed_qty = lines[i + 2].strip() if i + 2 < len(lines) else ""

            part_number = ""
            part_candidate_1 = lines[i - 2].strip()
            part_candidate_2 = lines[i - 3].strip()

            if part_number_pattern.match(part_candidate_1):
                part_number = part_candidate_1
            elif part_number_pattern.match(part_candidate_2):
                part_number = part_candidate_2

            bin_value = ""
            for j in range(i - 1, i - 10, -1):
                if "PICK" in lines[j]:
                    pick_line = lines[j].strip()
                    if pick_line.startswith("PICK ") and len(pick_line.split()) > 1:
                        bin_text = pick_line.split(" ", 1)[1]
                        bin_value = bin_text.split(',')[0].split()[0]
                    elif pick_line.strip() == "PICK" and j + 1 < len(lines):
                        bin_line = lines[j + 1].strip()
                        bin_value = bin_line.split(',')[0].split()[0]
                    elif pick_line.startswith("PICK") and len(pick_line) > 4 and j + 1 < len(lines):
                        pick_suffix = pick_line[4:].strip()
                        next_line = lines[j + 1].strip()
                        bin_value = (pick_suffix + next_line).split(',')[0].split()[0]
                    break

            if bin_value and part_number:
                entries.append({
                    "PICK": bin_value,
                    "Part #": part_number,
                    "Qty Committed": committed_qty
                })

    def sort_key(entry):
        try:
            return int(entry["PICK"])
        except:
            return entry["PICK"]

    def custom_sort_key(entry):
        try:
            return custom_pick_order.index(entry["PICK"])
        except:
            return float('inf')

    def custom_sort_key2(entry):
        try:
            return custom_pick_order_2.index(entry["PICK"])
        except:
            return float('inf')

    if sort_option == "Sort by Ascending":
        sorted_entries = sorted(entries, key=sort_key)
    elif sort_option == "Sort by Model II":
        sorted_entries = sorted(entries, key=custom_sort_key2)
    else:
        sorted_entries = sorted(entries, key=custom_sort_key)

    if sorted_entries:
        df = pd.DataFrame(sorted_entries)
        st.success("Sorted successfully!")
        st.dataframe(df, use_container_width=True)

        class PDFTable(FPDF):
            def header(self):
                self.set_font("Arial", "B", 12)
                # sanitize to Latin-1
                self.cell(0, 10, latin1("Picking Ticket Summary"), 0, 1, "C")

            def table(self, data):
                self.set_font("Arial", "B", 10)
                col_widths = [30, 80, 40]
                headers = ["PICK", "Part #", "Qty Committed"]
                for i, header in enumerate(headers):
                    self.cell(col_widths[i], 10, latin1(header), border=1)
                self.ln()
                self.set_font("Arial", "", 10)
                for _, row in data.iterrows():
                    self.cell(col_widths[0], 10, latin1(str(row["PICK"])), border=1)
                    self.cell(col_widths[1], 10, latin1(str(row["Part #"])), border=1)
                    self.cell(col_widths[2], 10, latin1(str(row["Qty Committed"])), border=1)
                    self.ln()

        pdf = PDFTable()

        # Override header to include Order Number (use ASCII hyphen, sanitize)
        def custom_header(self):
            self.set_font("Arial", "B", 12)
            title = "Picking Ticket Summary"
            if getattr(self, "_order_number", None):
                title += f" - Order {self._order_number}"  # hyphen, not en dash
            self.cell(0, 10, latin1(title), 0, 1, "C")
        pdf._order_number = order_number
        pdf.header = types.MethodType(custom_header, pdf)

        pdf.add_page()
        pdf.table(df)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            pdf.output(tmpfile.name)
            with open(tmpfile.name, "rb") as f:
                st.download_button("📥 Download Results as PDF", f.read(), file_name="pick_ticket_summary.pdf", mime="application/pdf")

    else:
        st.warning("No valid entries found in the PDF.")



