import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile
import os
from datetime import datetime

# 1. Configuración visual de la interfaz
st.set_page_config(page_title="Generador de Informes de Planta", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size:32px; font-weight:bold; color:#1f2937; margin-bottom:5px; }
    .subtitle { font-size:16px; color:#4B5563; margin-bottom:25px; }
    .card-ingreso { background-color: #f0fdf4; padding: 10px; border-radius: 8px; border-left: 5px solid #22c55e; margin-bottom: 10px;}
    .card-despacho { background-color: #eff6ff; padding: 10px; border-radius: 8px; border-left: 5px solid #1e3a8a; margin-bottom: 10px;}
    .card-vehiculos { background-color: #fff7ed; padding: 10px; border-radius: 8px; border-left: 5px solid #f97316; margin-bottom: 10px;}
    .card-mermas { background-color: #fef2f2; padding: 10px; border-radius: 8px; border-left: 5px solid #dc2626; margin-bottom: 10px;}
    .card-humedad { background-color: #f0fdfa; padding: 10px; border-radius: 8px; border-left: 5px solid #0d9488; margin-bottom: 10px;}
    .card-temp { background-color: #eef2ff; padding: 10px; border-radius: 8px; border-left: 5px solid #4f46e5; margin-bottom: 10px;}
    .card-limpieza { background-color: #fdf2f8; padding: 10px; border-radius: 8px; border-left: 5px solid #ec4899; margin-bottom: 10px;}
    .card-inventario { background-color: #fffbeb; padding: 10px; border-radius: 8px; border-left: 5px solid #f59e0b; margin-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO PRINCIPAL ---
st.markdown('<div class="main-title">📋 Sistema de Informes de Planta</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Sube tus fotos para generar el reporte oficial. El diseño corporativo se aplica automáticamente.</div>', unsafe_allow_html=True)

# --- PANEL DE PERSONALIZACIÓN (OPCIONAL) ---
with st.expander("🎨 1. Personalización del Informe (Opcional - Solo si deseas cambiar el diseño por defecto)"):
    st.info("💡 La aplicación ya cuenta con un membrete y logo predeterminados. Solo sube archivos aquí si necesitas usar un diseño diferente para este informe específico.")
    col_mem, col_log = st.columns(2)
    
    with col_mem:
        hoja_membrete = st.file_uploader("Cambiar Hoja de Membrete", type=['png', 'jpg', 'jpeg'])
        if hoja_membrete:
            st.success("✅ Nuevo membrete temporal cargado.")
            
    with col_log:
        logo_empresa = st.file_uploader("Cambiar Logo de la Empresa", type=['png', 'jpg', 'jpeg'])
        if logo_empresa:
            st.success("✅ Nuevo logo temporal cargado.")
            
    usar_franja = st.checkbox("Mostrar la franja superior de colores por cada categoría", 
                              value=False, 
                              help="Si tu membrete ya tiene un diseño en la parte superior, mantén esto desmarcado.")

st.markdown("---")
st.markdown("### 📸 2. Carga de Fotografías por Categoría")

# 2. Zonas de carga de archivos (Organizadas en 3 filas)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card-ingreso"><b>📥 INGRESO</b></div>', unsafe_allow_html=True)
    fotos_ingreso = st.file_uploader("Ingreso de Mercancía", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="ingreso")

with col2:
    st.markdown('<div class="card-despacho"><b>📦 DESPACHO</b></div>', unsafe_allow_html=True)
    fotos_despacho = st.file_uploader("Despacho de Mercancía", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="despacho")

with col3:
    st.markdown('<div class="card-vehiculos"><b>🚚 VEHÍCULOS</b></div>', unsafe_allow_html=True)
    fotos_vehiculos = st.file_uploader("Preparación de Vehículos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="vehiculos")

st.write("") 

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown('<div class="card-mermas"><b>📉 MERMAS</b></div>', unsafe_allow_html=True)
    fotos_mermas = st.file_uploader("Relación de Mermas", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="mermas")

with col5:
    st.markdown('<div class="card-humedad"><b>💧 HUMEDAD</b></div>', unsafe_allow_html=True)
    fotos_humedad = st.file_uploader("Sala de Procesos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="humedad")

with col6:
    st.markdown('<div class="card-temp"><b>❄️ TEMPERATURA</b></div>', unsafe_allow_html=True)
    fotos_temp = st.file_uploader("Temperatura de Cuarto", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="temperatura")

st.write("") 

col7, col8, col9 = st.columns(3)

with col7:
    st.markdown('<div class="card-limpieza"><b>🧹 LIMPIEZA</b></div>', unsafe_allow_html=True)
    fotos_limpieza = st.file_uploader("Limpieza y Desinfección", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="limpieza")

with col8:
    st.markdown('<div class="card-inventario"><b>📋 INVENTARIO</b></div>', unsafe_allow_html=True)
    fotos_inventario = st.file_uploader("Inventario Físico", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key="inventario")


# 3. Motor de generación de PDF
def procesar_y_ajustar_pdf(ingresos, despachos, vehiculos, mermas, humedades, temperaturas, limpiezas, inventarios, ruta_membrete, ruta_logo, usar_franja, tmpdir):
    pdf = FPDF()
    
    # Se agregaron las dos nuevas categorías con sus colores (Rosa y Ámbar)
    categorias = [
        ("INGRESO DE MERCANCÍA", ingresos, (34, 197, 94)),       
        ("DESPACHO DE MERCANCÍA", despachos, (30, 58, 138)),     
        ("PREPARACIÓN DE VEHÍCULOS", vehiculos, (249, 115, 22)), 
        ("MERMAS", mermas, (220, 38, 38)),                       
        ("HUMEDAD SALA DE PROCESOS", humedades, (13, 148, 136)), 
        ("TEMPERATURA DE CUARTO", temperaturas, (79, 70, 229)),
        ("LIMPIEZA Y DESINFECCIÓN DE ÁREAS", limpiezas, (236, 72, 153)),
        ("INVENTARIO", inventarios, (245, 158, 11))
    ]
    
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    page_w, page_h = 210, 297 
    
    for titulo_oficial, archivos, color_rgb in categorias:
        if archivos:  
            for archivo in archivos:
                img_path = os.path.join(tmpdir, archivo.name)
                with open(img_path, "wb") as f:
                    f.write(archivo.getbuffer())
                
                img = Image.open(img_path)
                img_w, img_h = img.size
                
                if img_w > img_h:
                    pdf.add_page(orientation='L')
                    page_w, page_h = 297, 210
                else:
                    pdf.add_page(orientation='P')
                    page_w, page_h = 210, 297
                
                # --- APLICAR MEMBRETE ---
                if ruta_membrete and os.path.exists(ruta_membrete):
                    pdf.image(ruta_membrete, x=0, y=0, w=page_w, h=page_h)
                
                # --- ENCABEZADO Y TÍTULOS ---
                r, g, b = color_rgb
                
                if usar_franja:
                    pdf.set_fill_color(r, g, b) 
                    pdf.rect(0, 0, page_w, 25, 'F')
                    pdf.set_text_color(255, 255, 255)
                else:
                    pdf.set_text_color(r, g, b) 
                
                pdf.set_xy(0, 8)
                pdf.set_font("helvetica", "B", 16)
                pdf.cell(0, 8, "INFORME DIARIO DE PLANTA", align="C")
                pdf.ln(7)
                
                pdf.set_font("helvetica", "B", 11)
                pdf.cell(0, 8, f"[{titulo_oficial}]", align="C")
                
                # --- INSERTAR LOGO ---
                if ruta_logo and os.path.exists(ruta_logo):
                    pdf.image(ruta_logo, x=page_w - 35, y=5, h=18)
                
                # --- IMAGEN DEL FORMATO ---
                max_w = page_w - 30
                max_h = page_h - 70 
                
                img_aspect = img_w / img_h
                page_aspect = max_w / max_h
                
                if img_aspect > page_aspect:
                    w = max_w
                    h = w / img_aspect
                else:
                    h = max_h
                    w = h * img_aspect
                
                x = (page_w - w) / 2
                y = 40 + (max_h - h) / 2
                
                pdf.image(img_path, x=x, y=y, w=w, h=h)
                
    # --- FIRMA Y FECHA ---
    if pdf.page_no() > 0:
        pdf.set_xy(0, page_h - 25)
        
        pdf.set_draw_color(30, 58, 138)
        pdf.line(x1=page_w/2 - 60, y1=page_h - 26, x2=page_w/2 + 60, y2=page_h - 26)
        
        pdf.set_text_color(50, 50, 50)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 8, "REALIZADO POR: ING NAZLY LUNA RODRIGUEZ JEFE DE CALIDAD", align="C", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", "", 9)
        pdf.cell(0, 5, f"Fecha de generación del informe: {fecha_actual}", align="C")
                
    return pdf

# 4. Zona de ejecución
st.markdown("---")
st.markdown("### ⚙️ 3. Generación de Documento")

if st.button("🚀 COMPILAR INFORME OFICIAL PDF", type="primary"):
    # Se agregaron las nuevas variables a la validación
    if not (fotos_ingreso or fotos_despacho or fotos_vehiculos or fotos_mermas or fotos_humedad or fotos_temp or fotos_limpieza or fotos_inventario):
        st.error("⚠️ Operación cancelada: Debes anexar al menos una fotografía para generar el informe.")
    else:
        with st.spinner("Construyendo informe corporativo..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                
                ruta_membrete_final = None
                if hoja_membrete:
                    ruta_membrete_final = os.path.join(tmpdir, "membrete_custom.png")
                    with open(ruta_membrete_final, "wb") as f:
                        f.write(hoja_membrete.getbuffer())
                else:
                    if os.path.exists("membrete_default.png"):
                        ruta_membrete_final = "membrete_default.png"
                    elif os.path.exists("membrete_default.jpg"):
                        ruta_membrete_final = "membrete_default.jpg"

                ruta_logo_final = None
                if logo_empresa:
                    ruta_logo_final = os.path.join(tmpdir, "logo_custom.png")
                    with open(ruta_logo_final, "wb") as f:
                        f.write(logo_empresa.getbuffer())
                else:
                    if os.path.exists("logo_default.png"):
                        ruta_logo_final = "logo_default.png"
                    elif os.path.exists("logo_default.jpg"):
                        ruta_logo_final = "logo_default.jpg"
                
                pdf = procesar_y_ajustar_pdf(
                    fotos_ingreso,
                    fotos_despacho, 
                    fotos_vehiculos, 
                    fotos_mermas, 
                    fotos_humedad,
                    fotos_temp,
                    fotos_limpieza,    # Nueva categoría
                    fotos_inventario,  # Nueva categoría
                    ruta_membrete_final,
                    ruta_logo_final,
                    usar_franja,
                    tmpdir
                )
                pdf_salida = os.path.join(tmpdir, "Informe_Planta_Oficial.pdf")
                
                pdf.output(pdf_salida)
                
                with open(pdf_salida, "rb") as pdf_file:
                    st.success("✨ ¡El informe está listo para descargar!")
                    st.download_button(
                        label="📥 DESCARGAR INFORME PDF",
                        data=pdf_file,
                        file_name="Informe_Diario_Planta.pdf",
                        mime="application/pdf"
                    )