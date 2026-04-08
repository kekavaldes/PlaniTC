# PlaniTC — Simulador Educativo de Tomografía Computada

Creado por TM Angélica Valdés y TM Evelyn Oyarzún  
Versión web desarrollada en Python + Streamlit

## Instalación

### Opción A: Ejecutar en tu computador (local)

1. Instalar Python 3.9 o superior desde https://python.org

2. Instalar dependencias:
```bash
pip install streamlit numpy
```

3. Ejecutar la app:
```bash
streamlit run PlaniTC_app.py
```

4. Se abrirá automáticamente en tu navegador en http://localhost:8501

---

### Opción B: Publicar en la nube GRATIS (Streamlit Community Cloud)

Para que tus estudiantes accedan sin instalar nada:

1. Crear cuenta gratis en https://github.com
2. Subir los archivos `PlaniTC_app.py` y `requirements.txt` a un repositorio
3. Ir a https://share.streamlit.io
4. Conectar el repositorio y hacer deploy
5. ¡Listo! Obtienes una URL pública como `https://tu-app.streamlit.app`

---

## Módulos de la aplicación

| Pestaña | Contenido |
|---------|-----------|
| 👤 Ingreso y Topograma | Datos paciente, región anatómica, 2 topogramas configurables |
| ⚡ Adquisición | Tipo exploración, kVp, mAs/modulación, detectores, pitch, rango |
| 🔄 Reconstrucción | Fase, kernel, grosor, ventana WW/WL, algoritmos iterativos |
| 💉 Jeringa Inyectora | Protocolo de contraste IV, fases, caudal, VVP |
| 🖼️ Imagen Simulada | Cortes CT simulados en tiempo real + resumen de protocolo |

## Próximas mejoras sugeridas

- Agregar imágenes DICOM reales por región anatómica
- Quiz educativo al final de cada módulo
- Comparación lado a lado de dos protocolos distintos
- Exportar protocolo completo como PDF
- Guardar y cargar protocolos de estudiantes
