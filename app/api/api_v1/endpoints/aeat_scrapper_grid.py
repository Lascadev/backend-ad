from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import time
import subprocess
import ctypes
import pyautogui  # Importamos PyAutoGUI
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

router = APIRouter()

# Configurar la carpeta de descargas
download_folder = os.path.abspath("downloads")
os.makedirs(download_folder, exist_ok=True)  # Crear la carpeta si no existe

def install_certificate(cert_path, password):
    """
    Instala el certificado .p12 en el almacén de certificados de Windows usando PowerShell.
    """
    try:
        print(f"Instalando certificado desde {cert_path}...")
        # Ruta al script de PowerShell
        ps_script = os.path.abspath("install_certificate.ps1")

        # Ejecutar el script de PowerShell
        command = f'powershell -ExecutionPolicy Bypass -File "{ps_script}" -certPath "{cert_path}" -password "{password}"'
        subprocess.run(command, shell=True, check=True)
        print("Certificado instalado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar el certificado: {e}")
        raise HTTPException(status_code=500, detail="Error al instalar el certificado.")

def remove_certificate(cert_name):
    """
    Elimina el certificado del almacén de certificados de Windows.
    """
    try:
        print(f"Eliminando certificado {cert_name}...")
        command = f'certutil -delstore -user My "{cert_name}"'
        subprocess.run(command, shell=True, check=True)
        print("Certificado eliminado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al eliminar el certificado: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar el certificado.")


@router.post("/upload-certificate/")
async def upload_certificate(certificate: UploadFile = File(...), password: str = Form(...)):
    try:
        print("Iniciando el proceso de carga del certificado...")

        # Guardar el certificado subido
        cert_path = f"certificates/{certificate.filename}"
        os.makedirs("certificates", exist_ok=True)
        with open(cert_path, "wb") as buffer:
            shutil.copyfileobj(certificate.file, buffer)

        # Instalar el certificado en el servidor
        install_certificate(cert_path, password)

        # Configurar Firefox con Selenium
        options = Options()
        options.set_preference("browser.download.folderList", 2)  # Usar una carpeta personalizada
        options.set_preference("browser.download.dir", download_folder)  # Especificar la carpeta de descargas
        options.set_preference("browser.download.useDownloadDir", True)  # Usar la carpeta especificada
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")  # Descargar PDF automáticamente
        options.set_preference("pdfjs.disabled", True)  # Deshabilitar el visor de PDF integrado

        driver = webdriver.Firefox(options=options)

        # Navegar a la página de la AEAT
        aeat_url = "https://sede.agenciatributaria.gob.es/static_files/common/html/selector_acceso/SelectorAccesos.html?ref=%2Fwlpl%2FEMCE-JDIT%2FECOTInternetCiudadanosServlet&aut=CP"
        driver.get(aeat_url)
        print("Navegando a la página de la AEAT...")

        try:
            autoriza_c_button = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.NAME, "autoriza-C"))
            )
            autoriza_c_button.click()
            pyautogui.press("enter")
            print("Botón 'autoriza-C' presionado correctamente.")
        except Exception as e:
            print(f"Error al presionar el botón 'autoriza-C' o interactuar con el modal: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al presionar el botón 'autoriza-C' o interactuar con el modal: {str(e)}")
        time.sleep(8)
        try:
            tipo_certificado_input = driver.find_element(By.ID, "fTipoCertificado4")
            tipo_certificado_input.click()
            print("Input 'fTipoCertificado4' seleccionado correctamente.")
        except Exception as e:
            print(f"Error al seleccionar el input 'fTipoCertificado4': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al seleccionar el input 'fTipoCertificado4': {str(e)}")

        try:
            validar_solicitud_button = driver.find_element(By.ID, "validarSolicitud")
            validar_solicitud_button.click()
            print("Botón 'validarSolicitud' presionado correctamente.")
        except Exception as e:
            print(f"Error al presionar el botón 'validarSolicitud': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al presionar el botón 'validarSolicitud': {str(e)}")
        time.sleep(5)
        try:
            # Localizar el botón por su valor (value) "Firmar Enviar"
            firmay_envia_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@value='Firmar Enviar']"))
            )
            firmay_envia_button.click()
            print("Botón 'Firmar Enviar' presionado correctamente.")
        except Exception as e:
            print(f"Error al presionar el botón 'Firmar Enviar': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al presionar el botón 'Firmar Enviar': {str(e)}")

        try:
            # Obtener todas las ventanas abiertas
            windows = driver.window_handles
            # Cambiar el enfoque a la última ventana abierta (la nueva ventana)
            driver.switch_to.window(windows[-1])
            print("Enfoque cambiado a la nueva ventana.")
        except Exception as e:
            print(f"Error al cambiar el enfoque a la nueva ventana: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al cambiar el enfoque a la nueva ventana: {str(e)}")
        time.sleep(5)
        # Hacer clic en el checkbox "Conforme"
        try:
            conforme_checkbox = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, "Conforme"))
            )
            conforme_checkbox.click()
            print("Checkbox 'Conforme' seleccionado correctamente.")
        except Exception as e:
            print(f"Error al seleccionar el checkbox 'Conforme': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al seleccionar el checkbox 'Conforme': {str(e)}")

        try:
            firmar_button = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.ID, "Firmar"))
            )
            firmar_button.click()
            print("Botón 'Firmar y Enviar' presionado correctamente.")
        except Exception as e:
            print(f"Error al presionar el botón 'Firmar y Enviar': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al presionar el botón 'Firmar y Enviar': {str(e)}")

        time.sleep(3)
        try:
            windows = driver.window_handles
            driver.switch_to.window(windows[0])
            print("Enfoque cambiado a la ventana principal.")
        except Exception as e:
            print(f"Error al cambiar el enfoque a la ventana principal: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al cambiar el enfoque a la ventana principal: {str(e)}")
    
        try:
            descargar_button = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.ID, "descarga"))
            )
            descargar_button.click()
            print("Botón 'Descargar documento' presionado correctamente.")
            
            # Esperar un tiempo para la descarga
            time.sleep(5)  # Ajusta el tiempo según sea necesario

            # Eliminar el certificado
            remove_certificate(certificate.filename)
            os.remove(cert_path)
            print("Certificado eliminado correctamente.")

            # Cerrar el navegador
            driver.quit()
            print("Navegador cerrado correctamente.")

        except Exception as e:
            print(f"Error en la descarga o eliminación del certificado: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error en la descarga o eliminación del certificado: {str(e)}")
        
    except Exception as e:
        # Asegurarse de eliminar el certificado en caso de error
        try:
            if os.path.exists(cert_path):
                remove_certificate(certificate.filename)
                os.remove(cert_path)
        except Exception as cleanup_error:
            print(f"Error al limpiar el certificado: {cleanup_error}")
        
        raise HTTPException(status_code=500, detail=str(e))
