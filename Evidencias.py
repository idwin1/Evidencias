import os
import sys
import subprocess
import json
import shutil
import platform
from pathlib import Path
# python -m PyInstaller --onefile --noconsole app.py
# Lista de librerías requeridas
LIBRERIAS_REQUERIDAS = {
    "colorama": "colorama",
    "tkinter": "tkinter",
    "platform": "platform"
}

def verificar_e_instalar_librerias():
    for import_name, pip_name in LIBRERIAS_REQUERIDAS.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"[!] La librería '{import_name}' no está instalada.")
            print(f"[+] Instalando '{pip_name}'...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            except Exception as e:
                print(f"[❌] Error crítico al instalar {pip_name}: {e}")
                sys.exit(1)

verificar_e_instalar_librerias()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from colorama import init, Fore

init(autoreset=True)

CONFIG_FILE = "config.json"

def cargar_configuracion():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(Fore.RED + f"[❌] Error al cargar config: {e}")
        return {}

class AplicacionOrganizador:

    def __init__(self, ventana_principal):
        self.root = ventana_principal
        self.root.title("Organizador de Evidencias Pro")
        self.root.geometry("650x500")
        self.root.resizable(False, False)
        
        # Paleta de colores oscura
        self.bg_color = "#121212"
        self.panel_color = "#1E1E1E"
        self.text_color = "#FFFFFF"
        self.btn_blue = "#5865F2"
        self.btn_purple = "#9C27B0"
        self.btn_orange = "#FF9800"
        self.btn_red = "#E91E63"
        self.btn_teal = "#00BCD4"
        
        self.root.configure(bg=self.bg_color)
        self.root.withdraw()

        # Cargar rutas desde config
        datos_config = cargar_configuracion()
        self.ruta_guardado = self.obtener_ruta_inicial(datos_config)
        self.ruta_salida_guardada = datos_config.get("Ruta_Salida", {}).get("ruta", "")

        self.root.deiconify()
        self.construir_interfaz()
        self.cargar_carpetas()

    def construir_interfaz(self):
        # Header
        frame_header = tk.Frame(self.root, bg=self.bg_color)
        frame_header.pack(fill="x", pady=20, padx=20)
        
        tk.Label(
            frame_header, text="📁 Organizador de Evidencias", 
            font=("Segoe UI", 18, "bold"), bg=self.bg_color, fg=self.text_color
        ).pack(side="left")

        # Acciones
        frame_acciones = tk.Frame(self.root, bg=self.panel_color, padx=10, pady=10)
        frame_acciones.pack(fill="x", padx=20)
        
        tk.Label(
            frame_acciones, text="⚡ ACCIONES", font=("Segoe UI", 8, "bold"), 
            bg=self.panel_color, fg="#888888"
        ).pack(anchor="w", pady=(0, 10))

        frame_botones = tk.Frame(frame_acciones, bg=self.panel_color)
        frame_botones.pack(fill="x")

        btn_opts = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "padx": 10, "pady": 5, "cursor": "hand2"}

        tk.Button(frame_botones, text="📁 Ruta Base", bg=self.btn_blue, command=self.cambiar_carpeta_base, **btn_opts).pack(side="left", padx=(0, 5))
        tk.Button(frame_botones, text="📂 Ruta Destino", bg=self.btn_orange, command=self.cambiar_ruta_salida, **btn_opts).pack(side="left", padx=5)
        tk.Button(frame_botones, text="🔄 Recargar", bg=self.btn_purple, command=self.cargar_carpetas, **btn_opts).pack(side="left", padx=5)
        tk.Button(frame_botones, text="⚙️ Procesar Caso", bg=self.btn_teal, command=self.procesar_evidencias, **btn_opts).pack(side="right")

        # Panel principal
        frame_seleccion = tk.Frame(self.root, bg=self.panel_color, padx=20, pady=20)
        frame_seleccion.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_ruta_base = tk.Label(frame_seleccion, text=f"Ruta Base: {self.ruta_guardado}", font=("Segoe UI", 9, "italic"), bg=self.panel_color, fg="#AAAAAA")
        self.lbl_ruta_base.pack(anchor="w", pady=(0, 5))

        texto_destino = self.ruta_salida_guardada if self.ruta_salida_guardada else "Por defecto (Dentro del proyecto)"
        self.lbl_ruta_salida = tk.Label(frame_seleccion, text=f"Ruta Destino: {texto_destino}", font=("Segoe UI", 9, "italic"), bg=self.panel_color, fg="#FFB74D")
        self.lbl_ruta_salida.pack(anchor="w", pady=(0, 15))

        tk.Label(frame_seleccion, text="Selecciona el proyecto a procesar:", font=("Segoe UI", 10), bg=self.panel_color, fg=self.text_color).pack(anchor="w", pady=(0, 5))
        self.combo_carpetas = ttk.Combobox(frame_seleccion, width=50, state="readonly", font=("Segoe UI", 10))
        self.combo_carpetas.pack(anchor="w", ipady=3)

        self.lbl_estado = tk.Label(frame_seleccion, text="", font=("Segoe UI", 9), bg=self.panel_color, justify="left")
        self.lbl_estado.pack(anchor="w", pady=15)

    def obtener_ruta_inicial(self, datos):
        ruta_data = datos.get("Ruta_Data", {}).get("ruta", "")
        if ruta_data and os.path.exists(ruta_data):
            return os.path.abspath(ruta_data)
    
        messagebox.showinfo("Configuración", "Selecciona la carpeta base donde están los proyectos.")
        ruta_sel = filedialog.askdirectory(title="Selecciona la carpeta base")
        if ruta_sel:
            ruta_abs = os.path.abspath(ruta_sel)
            self.guardar_en_config("Ruta_Data", ruta_abs)
            return ruta_abs
        else:
            self.root.destroy()
            sys.exit()
    
    def guardar_en_config(self, clave, ruta):
        try:
            datos = cargar_configuracion()
            if clave not in datos or not isinstance(datos[clave], dict):
                datos[clave] = {}
            datos[clave]["ruta"] = ruta
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[❌] Error al guardar config: {e}")

    def cambiar_carpeta_base(self):
        nueva = filedialog.askdirectory(title="Selecciona la ruta base")
        if nueva:
            self.ruta_guardado = os.path.abspath(nueva)
            self.guardar_en_config("Ruta_Data", self.ruta_guardado)
            self.lbl_ruta_base.config(text=f"Ruta Base: {self.ruta_guardado}")
            self.cargar_carpetas()

    def cambiar_ruta_salida(self):
        nueva = filedialog.askdirectory(title="Selecciona dónde guardar las carpetas generadas")
        if nueva:
            self.ruta_salida_guardada = os.path.abspath(nueva)
            self.guardar_en_config("Ruta_Salida", self.ruta_salida_guardada)
            self.lbl_ruta_salida.config(text=f"Ruta Destino: {self.ruta_salida_guardada}")

    def cargar_carpetas(self):
        ruta = self.ruta_guardado
        if os.path.exists(ruta) and os.path.isdir(ruta):
            carpetas = [d for d in os.listdir(ruta) if os.path.isdir(os.path.join(ruta, d))]
            self.combo_carpetas['values'] = carpetas
            if carpetas:
                self.combo_carpetas.current(0)
                self.mostrar_mensaje(f"Se encontraron {len(carpetas)} carpetas de proyectos.", "#4CAF50")
            else:
                self.combo_carpetas.set('')
                self.mostrar_mensaje("La ruta base no contiene subcarpetas.", "#FF9800")
        else:
            self.mostrar_mensaje("La ruta base no existe.", self.btn_red)

    def procesar_evidencias(self):
        carpeta_seleccionada = self.combo_carpetas.get()
        if not carpeta_seleccionada:
            self.mostrar_mensaje("Debes seleccionar una carpeta primero.", self.btn_red)
            return

        ruta_proyecto = os.path.join(self.ruta_guardado, carpeta_seleccionada)
        ruta_casos_js = os.path.join(ruta_proyecto, "casos.json")
        ruta_evidencias = os.path.join(ruta_proyecto, "evidencias")

        if not os.path.exists(ruta_casos_js):
            self.mostrar_mensaje(f"Falta 'casos.json' en {carpeta_seleccionada}.", self.btn_red)
            return
        if not os.path.exists(ruta_evidencias):
            self.mostrar_mensaje(f"Falta la carpeta 'evidencias' en {carpeta_seleccionada}.", self.btn_red)
            return

        try:
            with open(ruta_casos_js, "r", encoding="utf-8") as f:
                casos_data = json.load(f)

            # Definir dónde se guardarán las carpetas CP_001, CP_002...
            if self.ruta_salida_guardada and os.path.exists(self.ruta_salida_guardada):
                ruta_destino_base = os.path.join(self.ruta_salida_guardada, f"Resultados_{carpeta_seleccionada}")
            else:
                ruta_destino_base = os.path.join(ruta_proyecto, "Evidencias_Procesadas")
            
            os.makedirs(ruta_destino_base, exist_ok=True)
            imagenes_procesadas = 0

            for caso in casos_data:
                num_cp = caso.get("num_cp", "Desconocido")
                carpeta_caso = os.path.join(ruta_destino_base, f"CP_{num_cp}")
                os.makedirs(carpeta_caso, exist_ok=True)

                # CORRECCIÓN 1: La clave en tu JSON es "pasos" en minúscula
                pasos = caso.get("pasos", [])
                if isinstance(pasos, dict): 
                    pasos = [pasos]

                for paso in pasos:
                    # CORRECCIÓN 2: La clave en tu JSON es "evidencia" (singular)
                    evidencias_lista = paso.get("evidencia", [])
                    
                    for ruta_imagen_json in evidencias_lista:
                        # CORRECCIÓN 3: Normalizar las barras invertidas para extraer bien el nombre
                        ruta_limpia = ruta_imagen_json.replace("\\", "/")
                        nombre_archivo = os.path.basename(ruta_limpia)
                        
                        ruta_origen = os.path.join(ruta_evidencias, nombre_archivo)
                        ruta_destino = os.path.join(carpeta_caso, nombre_archivo)

                        if os.path.exists(ruta_origen):
                            shutil.copy2(ruta_origen, ruta_destino)
                            imagenes_procesadas += 1
                        else:
                            print(Fore.YELLOW + f"[!] No se encontró la imagen: {nombre_archivo}")
                            print(Fore.RED + f"    Buscada en: {ruta_origen}")

            self.mostrar_mensaje(f"¡Éxito! Se copiaron {imagenes_procesadas} imágenes a {ruta_destino_base}", self.btn_teal)

        except json.JSONDecodeError:
            self.mostrar_mensaje("Error: 'casos.js' no es un JSON válido.", self.btn_red)
        except Exception as e:
            self.mostrar_mensaje(f"Ocurrió un error al procesar: {str(e)}", self.btn_red)

    def mostrar_mensaje(self, texto, color):
        self.lbl_estado.config(text=texto, fg=color)

if __name__ == "__main__":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    
    ventana = tk.Tk()
    ventana.configure(bg="#121212")
    app = AplicacionOrganizador(ventana)
    ventana.mainloop()