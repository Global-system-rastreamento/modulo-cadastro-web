from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_border(cell, **kwargs):
    """
    Aplica bordas a uma célula específica
    Uso: set_cell_border(cell, top={"sz": 12, "color": "#FF0000", "val": "single"})
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    
    # Remove bordas existentes
    tcBorders = tcPr.find(qn('w:tcBorders'))
    if tcBorders is not None:
        tcPr.remove(tcBorders)
    
    # Adiciona novas bordas
    tcBorders = OxmlElement('w:tcBorders')
    
    for edge in ('left', 'top', 'right', 'bottom', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f'w:{edge}'
            element = OxmlElement(tag)
            element.set(qn('w:val'), edge_data.get('val', 'single'))
            element.set(qn('w:sz'), str(edge_data.get('sz', 4)))
            element.set(qn('w:space'), str(edge_data.get('space', 0)))
            element.set(qn('w:color'), edge_data.get('color', 'auto'))
            tcBorders.append(element)
    
    tcPr.append(tcBorders)

def set_table_borders(table, border_style=None):
    """
    Aplica bordas a toda a tabela
    """
    if border_style is None:
        border_style = {
            'val': 'single',
            'sz': 4,
            'color': 'auto',
            'space': 0
        }
    
    for row in table.rows:
        for cell in row.cells:
            set_cell_border(
                cell,
                top=border_style,
                bottom=border_style,
                left=border_style,
                right=border_style
            )