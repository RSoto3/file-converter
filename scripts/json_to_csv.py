import csv
import json
import os
import html
from datetime import datetime
import re

def reemplazar_entidades_especiales_automatico(texto):
    """Reemplaza automáticamente las entidades HTML con sus caracteres Unicode.
    Args:
        texto (str): El texto de entrada que puede contener entidades HTML.
    Returns:
        str: El texto con las entidades HTML reemplazadas.
    """
    if isinstance(texto, str):
        return html.unescape(texto)
    return texto

def formatear_fecha_directus(fecha_str):
    """
    Formatea una cadena de fecha en el formato de fecha de Directus (YYYY-MM-DD).
    Args:
        fecha_str (str): La cadena de fecha a formatear.
    Returns:
        str: La fecha formateada en 'YYYY-MM-DD', o una cadena vacía si la entrada no es válida.
    """
    if not fecha_str or fecha_str.lower() == "sin definir":
        return ""
    formatos_entrada = ["%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d", "%d.%m.%Y", "%Y.%m.%d"]
    for fmt in formatos_entrada:
        try:
            fecha_obj = datetime.strptime(fecha_str, fmt)
            fecha_formateada = fecha_obj.strftime("%Y-%m-%d")
            return fecha_formateada
        except ValueError:
            continue
    return ""

def json_a_csv_desde_array(ruta_archivo_json, ruta_archivo_csv_base, columnas_deseadas, total_registros):
    """
    Convierte registros de un archivo JSON a CSV, dividiéndolos en varios archivos,
    reemplazando entidades HTML, asegurando codificación UTF-8,
    guardando el 'run' como string y tipo general, eliminando espacios,
    maneando correctamente RUNs de un solo dígito, y escribiendo RUNs entre comillas en el CSV.
    Args:
        ruta_archivo_json (str): Ruta al archivo JSON de entrada.
        ruta_archivo_csv_base (str): Ruta base para los archivos CSV de salida.
        columnas_deseadas (list): Lista de nombres de columna deseados.
        total_registros (int): Cantidad total de registros a procesar.
    """
    try:
        with open(ruta_archivo_json, 'r', encoding='utf-8') as archivo_json:
            datos_json = json.load(archivo_json)

        if "data" in datos_json and isinstance(datos_json["data"], list):
            data_array = datos_json["data"]
            fecha_nacimiento_index = -1
            run_index = -1
            if "fecha_nacimiento" in [col.lower().replace(' ', '_') for col in columnas_deseadas]:
                fecha_nacimiento_index = [col.lower().replace(' ', '_') for col in columnas_deseadas].index("fecha_nacimiento")
            if "run" in [col.lower().replace(' ', '_') for col in columnas_deseadas]:
                run_index = [col.lower().replace(' ', '_') for col in columnas_deseadas].index("run")

            # Definir el numero maximo de registros por archivo
            registros_por_archivo = 6000  
            num_archivos = (total_registros + registros_por_archivo - 1) // registros_por_archivo

            for i in range(num_archivos):
                ruta_archivo_csv = f"{ruta_archivo_csv_base}_{i + 1}.csv"
                with open(ruta_archivo_csv, 'w', newline='', encoding='utf-8') as archivo_csv:
                    escritor_csv = csv.writer(archivo_csv, quoting=csv.QUOTE_MINIMAL)
                    escritor_csv.writerow(columnas_deseadas)

                    contador_registros_archivo = 0
                    runs_vistos = set()
                    inicio_archivo = i * registros_por_archivo
                    fin_archivo = min((i + 1) * registros_por_archivo, total_registros)

                    for j in range(inicio_archivo, fin_archivo):
                        registro = data_array[j]
                        if contador_registros_archivo < registros_por_archivo:
                            if isinstance(registro, list) and len(registro) >= len(columnas_deseadas):
                                fila_corregida = []
                                for k, valor in enumerate(registro[:len(columnas_deseadas)]):
                                    valor_str = re.sub(r'^\s+|\s+$', '', str(valor))
                                    if k == run_index:
                                        fila_corregida.append(valor_str)
                                    else:
                                        try:
                                            valor_num = int(valor_str)
                                            fila_corregida.append(valor_num)
                                        except ValueError:
                                            try:
                                                valor_num = float(valor_str)
                                                fila_corregida.append(valor_num)
                                            except ValueError:
                                                fila_corregida.append(valor_str)
                                if fecha_nacimiento_index != -1:
                                    fila_corregida[fecha_nacimiento_index] = formatear_fecha_directus(fila_corregida[fecha_nacimiento_index])
                                if run_index != -1:
                                    run_sin_formato = fila_corregida[run_index]
                                    if run_sin_formato in runs_vistos:
                                        print(f"RUN duplicado encontrado en el registro: {registro}")
                                    else:
                                        runs_vistos.add(run_sin_formato)
                                escritor_csv.writerow(fila_corregida)
                                contador_registros_archivo += 1
                            else:
                                print(f"Advertencia: Registro incompleto o con formato incorrecto en {ruta_archivo_json}: {registro}")
                        else:
                            break
                print(f"Archivo convertido (registros {inicio_archivo + 1}-{fin_archivo}): {ruta_archivo_json} -> {ruta_archivo_csv}")
        else:
            print(f"Advertencia: El archivo {ruta_archivo_json} no contiene una clave 'data' con una lista.")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_archivo_json}")
    except json.JSONDecodeError:
        print(f"Error: El archivo {ruta_archivo_json} no es un JSON válido.")
    except Exception as e:
        print(f"Ocurrió un error al procesar {ruta_archivo_json}: {e}")

if __name__ == "__main__":
    carpeta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    carpeta_data = os.path.join(carpeta_base, "data")
    carpeta_tmp = os.path.join(carpeta_base, "tmp")
    nombre_archivo_json = "persona.json"
    nombre_archivo_csv_base = os.path.join(carpeta_tmp, "persona")
    ruta_archivo_json = os.path.join(carpeta_data, nombre_archivo_json)
    columnas_deseadas = ["run", "nombres", "apellidos", "telefono", "direccion", "numero", "sector_villa", "fecha_nacimiento"]

    if not os.path.exists(carpeta_data):
        os.makedirs(carpeta_data)
        print(f"Carpeta de datos creada: {carpeta_data}. Por favor, coloca tu archivo {nombre_archivo_json} aquí.")
    elif not os.path.exists(ruta_archivo_json):
        print(f"Por favor, coloca tu archivo {nombre_archivo_json} en la carpeta: {carpeta_data}")

    if not os.path.exists(carpeta_tmp):
        os.makedirs(carpeta_tmp)
        print(f"Carpeta temporal creada: {carpeta_tmp}.")

    if os.path.exists(ruta_archivo_json):
        try:
            with open(ruta_archivo_json, 'r', encoding='utf-8') as archivo_json:
                data_json = json.load(archivo_json)
                if isinstance(data_json, dict) and 'recordsTotal' in data_json:
                    total_registros = data_json['recordsTotal']
                    print(f"Se encontraron {total_registros} registros totales en el archivo JSON.")
                    json_a_csv_desde_array(ruta_archivo_json, nombre_archivo_csv_base, columnas_deseadas, total_registros)
                    print("Proceso de conversión completado.")
                else:
                    print("Error: El archivo JSON no tiene la clave 'recordsTotal' esperada.")
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo JSON en {ruta_archivo_json}")
        except json.JSONDecodeError:
            print(f"Error: El archivo JSON en {ruta_archivo_json} no es válido.")
        except Exception as e:
            print(f"Ocurrió un error al leer el archivo JSON: {e}")
    else:
        print("No se encontró el archivo JSON. Asegúrate de que esté en la ubicación correcta.")
