def procesar_url(url):
    """
    Procesa la URL para generar su representación en formato NDEF.
    """
    # Mapear protocolos a identificadores
    protocols = {
        "https://www.": "02", "http://www.": "01",
        "https://": "04", "http://": "03",
        "tel:": "05", "mailto:": "06"
    }

    # Identificar el protocolo y calcular el contenido restante
    uri_identifier = next((id for proto, id in protocols.items() if url.startswith(proto)), "00")
    resto = url.split("://")[-1] if "://" in url else url
    resto_hex = ''.join(format(byte, '02X') for byte in resto.encode('utf-8'))

    # Construir el mensaje NDEF
    longitud_resto = len(resto) + 1
    return f"D1 01 {longitud_resto:02X} 55 {uri_identifier} {resto_hex}"


def dividir_en_filas(hex_string, longitud_fila=32):
    """
    Divide una cadena hexadecimal en filas de una longitud fija.
    """
    bytes_separados = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
    return [
        ' '.join(bytes_separados[i:i + (longitud_fila // 2)])
        for i in range(0, len(bytes_separados), longitud_fila // 2)
    ]


def ajustar_bloques(filas, bloque_inicial=4):
    """
    Ajusta las filas para que sean múltiplos de 4, agrega relleno y numera los bloques.
    """
    # Rellenar filas individuales para que tengan 16 bytes (32 caracteres)
    filas_rellenas = [fila.ljust(47, ' ') + "00 " * ((32 - len(fila.replace(' ', '')) // 2)) for fila in filas]

    # Calcular cuántas filas faltan para completar un múltiplo de 4
    filas_faltantes = (4 - len(filas_rellenas) % 4) % 4
    filas_rellenas.extend(["00 " * 16] * filas_faltantes)

    # Numerar los bloques
    return [f"Block {bloque_inicial + i}: {fila}" for i, fila in enumerate(filas_rellenas)]


def generar_archivo_flipper(url, uid="1E 0A 23 3F"):
    """
    Genera un archivo compatible con Flipper para una URL dada.
    """
    contenido_ndef = procesar_url(url)
    mensaje_completo = f"03 {len(contenido_ndef.split()):02X} {contenido_ndef} FE"
    filas = dividir_en_filas(mensaje_completo)
    bloques_numerados = ajustar_bloques(filas, bloque_inicial=4)

    # Cabecera del archivo
    cabecera = f"""
Filetype: Flipper NFC device
Version: 4
Device type: Mifare Classic
UID: {uid}
ATQA: 00 04
SAK: 08
Mifare Classic type: 1K
Data format version: 2
"""
    return cabecera + '\n'.join(bloques_numerados)


# Ejemplo de uso
url = input("Introduce la URL: ")
archivo_flipper = generar_archivo_flipper(url)

# Mostrar el contenido generado
print("=== Archivo NFC generado ===")
print(archivo_flipper)
