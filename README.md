# Los_alfas(Integrantes del equipo)
Adrian_Reig,Carlos Juan Battistini,Rodrigo_Yamill

## Tema de los alfas.
Queremos hacer una aplicacion que se dedique a ver el mercado en tiempo real pudiendo asi ayudar a que producto es mas recomendable invertir si en lo seguro(etf(sp500)) o a lo ariesgado comprando acciones de empresas mundiales(nvidia). Para esos datos, esta aplicacion recopilara periodicos munidales, para que cuando se produzca una subida o bajada de las acciones, se vendan o compren(saltara una alerta en el movil).

### Deberes
########Dockerfile instrucciones
Porque usarlo: Usamos Docker para que nuestra app de mercado financiero funcione igual en Windows, Mac o Linux, reduciendo el esfuerzo de desarrollo.
🏗️ Arquitectura:  
1º Contenedor Único: Ejecuta una aplicación interactiva utilizando la imagen oficial de Python 3.9-slim, es mucho más ligero que una máquina virtual, ya que no incluye un sistema operativo completo innecesario.
2º Gestión de Archivos: El contenedor integra las carpetas src/ (lógica del programa), data/ (fuentes JSON y CSV) y web/ (interfaz de usuario).  
3ºOrden de Ejecución:
    3.1º Se establece el directorio de trabajo en /app.
    3.2º Se instalan las dependencias externas desde el archivo requirements.txt.  
    3.3º Se copia el código fuente al contenedor.  
    3.4º Se lanza la interfaz web mediante streamlit_app.py.  
🛠️ Instrucciones:
Ejecuta los siguientes comandos en tu terminal instalada con Docker Desktop:  
Construir la imagen: docker build -t los-alfa-app .
Ejecutar el contenedor: docker run -p 8501:8501 los-alfa-app.
#### Notas
usamos solo un conenedor porque todos los archivos son rapidos y accesibles en la misma carpeta del proyecto y pertenecen al mismo entorno virtual.