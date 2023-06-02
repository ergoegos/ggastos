# Tutorial de ejecución

Instalar las dependencias en un entorno de python utilizando el comando.

Crear un entorno python

````
python -m venv venv
source venv/bin/activate
````


```
pip install -r requirements.txt
```


Ejecutar el Postgres:

````
docker compose up
````

Iniciar el servidor de streamlit

````
streamlit run gestor_gastos/app.py
````

Acceder a la web en la siguiente dirección
`````
http://localhost:8501
`````

Para que funcione correctamente se necesitan las credenciales de Google Auth, que no se adjuntan por cuestiones de seguridad y que se incluyen en la raiz de "gestor_gastos" en forma de json. 

