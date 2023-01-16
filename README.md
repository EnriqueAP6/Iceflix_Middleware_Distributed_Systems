This repository is a Python project template.
It contains the following files and directories:

- `configs` has the authenticator configuration file.
- `iceflix` is the main Python package.

- `iceflix/__init__.py` is an empty file needed by Python to
  recognise the `iceflix` directory as a Python module.
- `iceflix/cli.py` contains several functions to handle the basic console entry points
  defined in `python.cfg`.
  The name of the submodule and the functions can be modified if you need.
- `iceflix/iceflix.ice` contains the Slice interface definition for the lab.
- `pyproject.toml` defines the build system used in the project.
- `run_service` should be a script that can be run directly from the
  repository root directory. It should be able to run all the services
  in background in order to test the whole system.
- `setup.cfg` is a Python distribution configuration file for Setuptools.
  It needs to be modified in order to adeccuate to the package name and
  console handler functions.

# **UTILIZACIÓN (entrega parcial)**

  Para llevar a cabo la ejecución del authenticator, lo primero que debes hacer es escribir el proxy del servicio main al que quieras que se conecte dentro del archivo **configs/authenticator.config** (en la propiedad "MainProxy", tras borrar el valor previamente escrito).

  Una vez realizado lo anterior, simplemente debes escribir por terminal (estando dentro del directorio del repositorio) lo siguiente:
    ./run_service
  
  A partir de ese momento, el servicio main con el que se esté probando mi programa podrá interactuar con él utilizando cualesquiera de los 6 métodos definidos en la interfaz y que debe ofrecer todo servicio authenticator. 
  Mi código generará mensajes por pantalla a raíz de la conexión con el servicio main, su desconexión (se manejan errores), envío de mensajes newService y announce; y del registro/eliminación de credenciales de usuario tanto en la lista de tokens temporales como en la base de datos.

# **UTILIZACIÓN (entrega final)**

Llegados a la última entrega, el programa presentado únicamente requerirá el empleo de la sentencia **./run_service** para comenzar su ejecución. Esta iniciará con un algoritmo de arranque que a lo sumo* se prolongará por 12 segundos y cuyo objetivo es recibir obligatoriamente el anunciamiento de algún servicio Main (en caso negativo se aborta), además del de otro servicio Authenticator. Esto último permitirá hacerle consciente de si su base de datos es la primera en ponerse en marcha y por tanto la vigente, o si es necesario recibir las credenciales de aquella que está siendo usada por los otros servicios del mismo tipo (mediante el método bulkUpdate()). 

Una vez ocurrido lo anterior, comenzarán los anunciamientos propios cada 8 segundos y podrán recibirse los de otros servicios. Por último, a las funcionalidades de la primera entrega (las invocaciones a los 6 métodos de la versión 1 del archivo ice) se le sumarán ciertos métodos que permitirán sincronizar la base de datos usada con la de los demás Authenticator activos (avisos de tokens/usuarios insertados o borrados).

*Puede terminar antes incluso si ya se ha detectado tanto un servicio Main como uno Authenticator

**IMPORTANTE: Debido a las consultas realizadas a profesores de la asignatura, el código supone que el token de administración recibido desde clientes estará codificado (no viajará en claro). En mi caso se ha utilizado la codificación sha256.**

# **BASE DE DATOS USADA**

  A la hora de registrar todos los nombres de usuario y contreña que se desee por el servicio main, empleo un archivo de texto llamado **resources/bbddCredenciales.txt** (situado como puede verse en la carpeta "resources"). En él he dejado colocados ciertas credenciales completas para que quien pruebe mi código pueda realizar todo tipo de comprobaciones. Será creado en tiempo de ejecución en caso de haberse borrado.

# **CALIFICACIÓN PYLINT**

  Tras realizar las mejoras apropiadas y eliminando avisos que conscientemente sé que no son necesarios, la herramienta pylint devuelve una nota de 10.00. 

  
