from PIL import Image, ImageEnhance, ImageSequence

# Ruta de entrada y salida
ruta_imagen = r"C:\Users\Andres\Desktop\portafolio\backup\Alystarpedia\assets\icons\machine.gif"
ruta_salida = r"C:\Users\Andres\Desktop\portafolio\backup\Alystarpedia\assets\icons\machine_mejorado.gif"

try:
    gif = Image.open(ruta_imagen)
except Exception as e:
    print(f"❌ Error al cargar el GIF: {e}")
    exit()

frames_mejorados = []

# Ajustes: modifica estos factores según el resultado deseado
factor_color = 1.1   # 1.0 es sin cambio; >1 para más saturación
factor_contraste = 1.1  # Para ajustar el contraste

# Procesar cada frame
for frame in ImageSequence.Iterator(gif):
    # Convertir a modo RGBA para preservar transparencia
    frame = frame.convert("RGBA")
    
    # Mejorar la saturación
    enhancer_color = ImageEnhance.Color(frame)
    frame_mejorado = enhancer_color.enhance(factor_color)
    
    # Mejorar el contraste
    enhancer_contraste = ImageEnhance.Contrast(frame_mejorado)
    frame_mejorado = enhancer_contraste.enhance(factor_contraste)
    
    frames_mejorados.append(frame_mejorado)

# Guardar el GIF mejorado
# Si el GIF es animado, se guarda con todos los frames y se mantienen la transparencia y la duración original
frames_mejorados[0].save(
    ruta_salida,
    save_all=True,
    append_images=frames_mejorados[1:],
    loop=0,
    duration=gif.info.get("duration", 100),
    disposal=2,
    transparency=0
)

print(f"✅ GIF mejorado guardado como: {ruta_salida}")
