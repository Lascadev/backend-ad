from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

router = APIRouter()

# Configurar la carpeta de descargas
download_folder = os.path.abspath("downloads")
os.makedirs(download_folder, exist_ok=True)  # Crear la carpeta si no existe

@router.post("/upload-certificate/")
async def upload_certificate(certificate: UploadFile = File(...), password: str = Form(...)):
    try:
        # Guardar el certificado subido
        cert_path = f"certificates/{certificate.filename}"
        os.makedirs("certificates", exist_ok=True)
        with open(cert_path, "wb") as buffer:
            shutil.copyfileobj(certificate.file, buffer)

        # Configurar Firefox con Selenium para descargar automáticamente
        options = Options()
        options.set_preference("browser.download.folderList", 2)  # Usar una carpeta personalizada
        options.set_preference("browser.download.dir", download_folder)  # Especificar la carpeta de descargas
        options.set_preference("browser.download.useDownloadDir", True)  # Usar la carpeta especificada
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")  # Descargar PDF automáticamente
        options.set_preference("pdfjs.disabled", True)  # Deshabilitar el visor de PDF integrado

        driver = webdriver.Firefox(options=options)

        # Navegar a la página de certificados de Firefox
        driver.get("about:preferences#privacy")
        time.sleep(2)  # Esperar a que la página cargue

        # Hacer clic en "Ver certificados"
        try:
            view_certificates_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "viewCertificatesButton"))
            )
            view_certificates_button.click()
            print("Clic en 'Ver certificados' realizado correctamente.")
        except Exception as e:
            print(f"Error al hacer clic en 'Ver certificados': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al hacer clic en 'Ver certificados': {str(e)}")

        # Localizar el <stack id="dialogStack">
        try:
            dialog_stack = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "dialogStack"))
            )
            print("Elemento <stack id='dialogStack'> encontrado correctamente.")
        except Exception as e:
            print(f"Error al localizar el <stack id='dialogStack'>: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al localizar el <stack id='dialogStack'>: {str(e)}")

        # Localizar el <vbox id="dialogTemplate"> dentro de <stack id="dialogStack">
        try:
            dialog_template = dialog_stack.find_element(By.ID, "dialogTemplate")
            print("Elemento <vbox id='dialogTemplate'> encontrado correctamente.")
        except Exception as e:
            print(f"Error al localizar el <vbox id='dialogTemplate'>: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al localizar el <vbox id='dialogTemplate'>: {str(e)}")

        # Localizar el <vbox class="dialogBox"> dentro de <vbox id="dialogTemplate">
        try:
            dialog_box = dialog_template.find_element(By.CSS_SELECTOR, "vbox.dialogBox")
            print("Elemento <vbox class='dialogBox'> encontrado correctamente.")
        except Exception as e:
            print(f"Error al localizar el <vbox class='dialogBox'>: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al localizar el <vbox class='dialogBox'>: {str(e)}")

        # Localizar el <browser name="dialogFrame-16"> dentro de <vbox class="dialogBox">
        try:
            dialog_frame = dialog_box.find_element(By.CSS_SELECTOR, "browser[class='dialogFrame']")
            print("Elemento <browser name='dialogFrame'> encontrado correctamente.")
            print("¡Llegamos aquí! Acceso al contenido interno confirmado.")
        except Exception as e:
            print(f"Error al localizar el <browser name='dialogFrame'>: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al localizar el <browser name='dialogFrame'>: {str(e)}")

        # Cambiar al contexto del <browser name="dialogFrame-16">
        try:
            driver.switch_to.frame(dialog_frame)
            print("Cambio al contexto del <browser name='dialogFrame'> realizado correctamente.")
        except Exception as e:
            print(f"Error al cambiar al contexto del <browser name='dialogFrame'>: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al cambiar al contexto del <browser name='dialogFrame'>: {str(e)}")

        # Localizar el <window windowtype="mozilla:certmanager"> dentro del #document
        try:
            window_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "window[windowtype='mozilla:certmanager']"))
            )
            print("Elemento <window windowtype='mozilla:certmanager'> encontrado correctamente.")
        except Exception as e:
            print(f"Error al localizar el <window windowtype='mozilla:certmanager'>: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al localizar el <window windowtype='mozilla:certmanager'>: {str(e)}")

        # Localizar el <dialog id="certmanager"> dentro del <window windowtype="mozilla:certmanager">
        try:
            certmanager_dialog = window_element.find_element(By.ID, "certmanager")
            print("Elemento <dialog id='certmanager'> encontrado correctamente.")
        except Exception as e:
            print(f"Error al localizar el <dialog id='certmanager'>: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al localizar el <dialog id='certmanager'>: {str(e)}")

        # Localizar el <tabbox id="certmanagertabs"> dentro del <dialog id="certmanager">
        try:
            certmanagertabs = certmanager_dialog.find_element(By.ID, "certmanagertabs")
            print("Elemento <tabbox id='certmanagertabs'> encontrado correctamente.")
        except Exception as e:
            print(f"Error al localizar el <tabbox id='certmanagertabs'>: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al localizar el <tabbox id='certmanagertabs'>: {str(e)}")

        # Localizar el <tabs id="certMgrTabbox"> dentro del <tabbox id="certmanagertabs">
        try:
            certMgrTabbox = certmanagertabs.find_element(By.ID, "certMgrTabbox")
            print("Elemento <tabs id='certMgrTabbox'> encontrado correctamente.")
        except Exception as e:
            print(f"Error al localizar el <tabs id='certMgrTabbox'>: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al localizar el <tabs id='certMgrTabbox'>: {str(e)}")

        # Localizar el botón "Importar…" dentro del <dialog id="certmanager">
        try:
            import_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "mine_restoreButton"))
            )
            print("Botón 'Importar…' encontrado correctamente.")
        except Exception as e:
            print(f"Error al localizar el botón 'Importar…': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al localizar el botón 'Importar…': {str(e)}")

        # Hacer clic en el botón "Importar…"
        try:
            import_button.click()
            print("Clic en el botón 'Importar…' realizado correctamente.")
        except Exception as e:
            print(f"Error al hacer clic en el botón 'Importar…': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al hacer clic en el botón 'Importar…': {str(e)}")

        # Esperar a que aparezca el diálogo del explorador de archivos
        time.sleep(2)  # Esperar 2 segundos para que el diálogo aparezca

        # Usar pyautogui para seleccionar el archivo del certificado
        try:
            # Escribir la ruta completa del certificado
            pyautogui.write(os.path.abspath(cert_path))
            time.sleep(1)  # Esperar 1 segundo para que se escriba la ruta

            # Presionar Enter para seleccionar el archivo
            pyautogui.press("enter")
            print("Certificado seleccionado correctamente.")
        except Exception as e:
            print(f"Error al seleccionar el certificado: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al seleccionar el certificado: {str(e)}")

        # Esperar a que aparezca la ventana de introducción de contraseña
        time.sleep(2)  # Esperar 2 segundos para que la ventana aparezca

        # Usar pyautogui para escribir la contraseña (respetando mayúsculas y minúsculas)
        try:
            for char in password:
                if char.isupper():
                    # Simular la pulsación de la tecla Shift para mayúsculas
                    pyautogui.keyDown("shift")
                    pyautogui.press(char.lower())  # Escribir la letra en minúscula (Shift la convierte en mayúscula)
                    pyautogui.keyUp("shift")
                else:
                    # Escribir la letra en minúscula directamente
                    pyautogui.press(char)
            time.sleep(1)  # Esperar 1 segundo para que se escriba la contraseña

            # Presionar Enter para confirmar la contraseña
            pyautogui.press("enter")
            print("Contraseña introducida correctamente.")
        except Exception as e:
            print(f"Error al introducir la contraseña: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al introducir la contraseña: {str(e)}")

        # Esperar a que se complete la importación del certificado
        time.sleep(5)  # Esperar 5 segundos para asegurarnos de que el certificado se haya importado

        # Navegar a la página de la AEAT
        aeat_url = "https://sede.agenciatributaria.gob.es/static_files/common/html/selector_acceso/SelectorAccesos.html?ref=%2Fwlpl%2FEMCE-JDIT%2FECOTInternetCiudadanosServlet&aut=CP"
        driver.get(aeat_url)
        print("Navegando a la página de la AEAT...")

        # Localizar el botón "autoriza-C"
        try:
            autoriza_c_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "autoriza-C"))
            )
            print("Botón 'autoriza-C' encontrado correctamente.")
        except Exception as e:
            print(f"Error al localizar el botón 'autoriza-C': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al localizar el botón 'autoriza-C': {str(e)}")

        # Hacer clic en el botón "autoriza-C"
        try:
            autoriza_c_button.click()
            print("Clic en el botón 'autoriza-C' realizado correctamente.")
        except Exception as e:
            print(f"Error al hacer clic en el botón 'autoriza-C': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al hacer clic en el botón 'autoriza-C': {str(e)}")

        # Esperar a que aparezca el diálogo emergente
        time.sleep(2)  # Esperar 2 segundos para que el diálogo aparezca

        # Simular la pulsación de la tecla Enter para aceptar el diálogo
        try:
            pyautogui.press("enter")
            print("Tecla Enter presionada para aceptar el diálogo.")
        except Exception as e:
            print(f"Error al presionar Enter: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al presionar Enter: {str(e)}")

        # Esperar 25 segundos para que la página cargue completamente
        time.sleep(25)

        # Buscar el input con el ID "fTipoCertificado4" y marcarlo (seleccionarlo)
        try:
            tipo_certificado_input = driver.find_element(By.ID, "fTipoCertificado4")
            tipo_certificado_input.click()
            print("Input 'fTipoCertificado4' seleccionado correctamente.")
        except Exception as e:
            print(f"Error al seleccionar el input 'fTipoCertificado4': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al seleccionar el input 'fTipoCertificado4': {str(e)}")

        # Presionar el botón de validar solicitud con el ID "validarSolicitud"
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

        # Esperar a que se abra la nueva ventana
        time.sleep(5)  # Esperar 5 segundos para que la nueva ventana se abra

        # Cambiar el enfoque a la nueva ventana
        try:
            # Obtener todas las ventanas abiertas
            windows = driver.window_handles
            # Cambiar el enfoque a la última ventana abierta (la nueva ventana)
            driver.switch_to.window(windows[-1])
            print("Enfoque cambiado a la nueva ventana.")
        except Exception as e:
            print(f"Error al cambiar el enfoque a la nueva ventana: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al cambiar el enfoque a la nueva ventana: {str(e)}")

        # Hacer clic en el checkbox "Conforme"
        try:
            conforme_checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "Conforme"))
            )
            conforme_checkbox.click()
            print("Checkbox 'Conforme' seleccionado correctamente.")
        except Exception as e:
            print(f"Error al seleccionar el checkbox 'Conforme': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al seleccionar el checkbox 'Conforme': {str(e)}")

        # Esperar 25 segundos
        time.sleep(25)

        # Hacer clic en el botón "Firmar y Enviar" en la nueva ventana
        try:
            firmar_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "Firmar"))
            )
            firmar_button.click()
            print("Botón 'Firmar y Enviar' presionado correctamente.")
        except Exception as e:
            print(f"Error al presionar el botón 'Firmar y Enviar': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al presionar el botón 'Firmar y Enviar': {str(e)}")

        # Esperar a que la nueva ventana se cierre y volver a la ventana anterior
        time.sleep(5)  # Esperar 5 segundos para que la nueva ventana se cierre

        # Cambiar el enfoque a la ventana principal
        try:
            windows = driver.window_handles
            driver.switch_to.window(windows[0])
            print("Enfoque cambiado a la ventana principal.")
        except Exception as e:
            print(f"Error al cambiar el enfoque a la ventana principal: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al cambiar el enfoque a la ventana principal: {str(e)}")

        # Hacer clic en el botón "Descargar documento"
        try:
            descargar_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "descarga"))
            )
            descargar_button.click()
            print("Botón 'Descargar documento' presionado correctamente.")
        except Exception as e:
            print(f"Error al presionar el botón 'Descargar documento': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al presionar el botón 'Descargar documento': {str(e)}")

        # Esperar a que el archivo PDF se descargue
        time.sleep(10)  # Esperar 10 segundos para que la descarga se complete

        # Verificar si el archivo PDF se descargó correctamente
        pdf_files = [f for f in os.listdir(download_folder) if f.endswith(".pdf")]
        if pdf_files:
            print(f"Archivo PDF descargado correctamente: {pdf_files[0]}")
        else:
            print("No se encontró ningún archivo PDF descargado.")
            raise HTTPException(status_code=500, detail="No se encontró ningún archivo PDF descargado.")

        # Cerrar el navegador
        driver.quit()

        # Eliminar archivos temporales
        os.remove(cert_path)

        return JSONResponse(content={
            "message": "Proceso completado",
            "resultado": "¡Llegamos aquí! Certificado importado, acceso a la AEAT realizado, proceso de firma completado y documento descargado correctamente.",
            "archivo_descargado": pdf_files[0] if pdf_files else None
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))