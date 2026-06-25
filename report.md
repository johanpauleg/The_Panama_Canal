# Planificador de eventos del Canal de Panamá

**Autor:** Johan Paul Echevarría González  
**Perfil de GitHub:** johanpauleg  
**Repositorio:** The_Panama_Canal

## 1. Introducción

Este proyecto consiste en una aplicación web desarrollada con Streamlit para planificar eventos vinculados al funcionamiento del Canal de Panamá. La idea principal no es solamente permitir que el usuario registre eventos, sino imponer una serie de reglas que eviten combinaciones incoherentes, conflictos de recursos y solapamientos de tiempo. En otras palabras, el sistema intenta comportarse como un planificador con restricciones reales, donde cada decisión tiene consecuencias y donde no todo evento es válido únicamente por haber sido introducido en la interfaz.

La motivación detrás del proyecto fue construir una herramienta que unifique interfaz, validación y persistencia de datos en una solución pequeña pero completa. Para ello se organizaron los datos del sistema en archivos JSON y la lógica principal en dos módulos de Python: `app.py`, encargado de la experiencia de usuario, y `scheduler.py`, encargado de las reglas del dominio. Esa separación permite entender con claridad qué parte del código se relaciona con la presentación y cuál controla el comportamiento del sistema.

## 2. Objetivo del proyecto

El objetivo general del proyecto es simular la programación de eventos del Canal de Panamá bajo restricciones concretas de tiempo, duración, tipo de evento y disponibilidad de recursos. La aplicación permite crear eventos únicos y eventos recurrentes, pero antes de aceptarlos verifica que cumplan condiciones específicas. Si un evento no puede ejecutarse en el horario escogido, el sistema analiza si existe una fecha posterior compatible dentro de una ventana máxima de 60 días.

Con esta idea, el proyecto representa un problema clásico de planificación: no basta con guardar información, también es necesario validar que esa información tenga sentido dentro de las reglas del sistema. Por eso el diseño no se centra únicamente en la interfaz, sino en el conjunto completo de validaciones que sostienen la funcionalidad.

## 3. Descripción general del sistema

La aplicación está pensada para que el usuario pueda administrar dos tipos principales de eventos:

- Evento único.
- Evento recurrente.

Cada uno de estos eventos puede corresponder a dos clases de operación:

- Mantenimiento de una esclusa.
- Tránsito de una embarcación por el canal.

En el caso de los tránsitos, además, el usuario debe indicar el tamaño de la embarcación. Esa decisión es importante porque el tamaño determina la duración esperada del evento, la cantidad de remolcadores necesarios y el tipo de piloto requerido. El sistema trabaja entonces con una combinación de reglas temporales y reglas de recursos que deben cumplirse simultáneamente.

El comportamiento de la aplicación refleja un principio básico de programación de recursos: los eventos no existen de forma aislada, sino dentro de un contexto donde otros eventos también consumen capacidad. Por esa razón, el sistema no solo comprueba si una combinación es válida en abstracto, sino también si es viable respecto a los eventos ya programados.

## 4. Recursos del sistema

El proyecto distingue dos categorías de recursos: recursos específicos y recursos cuantitativos.

Los recursos específicos corresponden a las esclusas disponibles en el sistema. Estas son A1, A2, A3, C1, C2, C3, P1, P2 y P3. Su uso es excluyente: si una esclusa está ocupada por un evento, no puede ser usada simultáneamente por otro evento en el mismo intervalo.

Los recursos por cantidad son los siguientes:

- 2 pilotos junior.
- 2 pilotos senior.
- 6 remolcadores.
- 3 equipos de mantenimiento.

Este enfoque refleja dos formas distintas de disponibilidad. En unos casos se trata de recursos discretos que pueden estar ocupados o libres; en otros, de recursos acumulativos que deben contarse para asegurar que la suma total no sobrepase la capacidad disponible. La diferencia entre ambos tipos de recursos hizo necesario implementar reglas de validación ligeramente distintas, tanto en `scheduler.py` como en el proceso de programación del evento.

## 5. Diseño de los eventos

### 5.1 Evento único

Un evento único representa una operación que ocurre una sola vez en una franja temporal determinada. Este tipo de evento es útil cuando el usuario desea registrar una tarea puntual, como una reparación específica o un tránsito aislado de una embarcación. La validación de este evento analiza su duración, sus recursos requeridos y la disponibilidad del canal durante el intervalo escogido.

### 5.2 Evento recurrente

Un evento recurrente representa una operación que se repite varias veces con un intervalo fijo en días. En la interfaz, el usuario define cuántas repeticiones habrá y cuántos días separan una ejecución de la siguiente. El sistema genera cada repetición como un evento independiente para que pueda ser comprobado contra la disponibilidad general.

Este diseño fue importante porque permitió tratar la recurrencia no como una excepción, sino como una serie de eventos individuales relacionados entre sí. Desde el punto de vista de la validación, esto es más robusto que asumir que toda la serie ocupa un único bloque fijo; cada repetición puede entrar o no en conflicto con otros eventos, y por eso debe verificarse por separado.

## 6. Reglas de validación

Las validaciones constituyen el núcleo del proyecto. Se implementaron para asegurar que la información ingresada por el usuario no solo esté bien formada, sino que respete las restricciones del problema.

### 6.1 Validaciones de tiempo

La primera verificación temporal comprueba que la fecha y hora de inicio no estén en el pasado y que la fecha y hora de finalización sean posteriores al inicio. También se impone una ventana de 60 días hacia adelante. Esta restricción ayuda a limitar el horizonte de planificación y evita que el sistema tenga que trabajar con un rango excesivamente grande de fechas.

La decisión de limitar el calendario a 60 días responde a un criterio práctico. Por una parte, facilita la evaluación de conflictos dentro de un periodo razonable; por otra, hace más manejable el proceso de búsqueda de disponibilidad futura cuando un evento no puede programarse de inmediato.

### 6.2 Validaciones de duración

Cada tipo de evento posee una duración admitida. En el caso del mantenimiento de una esclusa, la duración debe estar entre 4 y 5 horas. Para los tránsitos, la duración depende del tamaño de la embarcación:

- Embarcación pequeña: entre 6 y 8 horas.
- Embarcación mediana: entre 8 y 11 horas.
- Embarcación grande: entre 10 y 14 horas.

Estas duraciones no son arbitrarias desde el punto de vista del modelo. Se usaron para dar coherencia al problema y para que la validación fuera más estricta, obligando al usuario a respetar tiempos realistas dentro del contexto del canal.

### 6.3 Validaciones de recursos y restricciones

Además del tiempo, cada evento debe respetar una composición válida de recursos. Por ejemplo, un mantenimiento de una esclusa requiere una esclusa concreta y un equipo de mantenimiento, mientras que los pilotos y los remolcadores no forman parte de esa operación. En cambio, un tránsito requiere tres esclusas alineadas y una combinación específica de personal y remolcadores.

En el caso de los tránsitos, el tamaño de la embarcación modifica la lógica del evento. Una embarcación pequeña requiere un piloto junior, mientras que una mediana o grande requiere un piloto senior. Además, a medida que crece el tamaño de la embarcación, aumenta el número de remolcadores necesarios. Este enfoque hace que el sistema se comporte de forma diferenciada según el tipo de evento, en lugar de aplicar una validación genérica para todos los casos.

### 6.4 Validaciones de recurrencia

Para los eventos recurrentes se añadió una validación adicional que comprueba que la serie completa no exceda la ventana de 60 días. Esto evita que una recurrencia definida por el usuario termine generando eventos fuera del horizonte permitido. En la práctica, esta regla protege la consistencia del calendario y mantiene el comportamiento del sistema alineado con el resto de las validaciones temporales.

### 6.5 Validaciones de disponibilidad

La parte más importante del sistema es la comprobación de disponibilidad. Aunque un evento sea correcto desde el punto de vista lógico, puede no ser posible si coincide con otro evento que ya consume los mismos recursos. Para resolver esto, la aplicación revisa todos los eventos ya almacenados en `events.json` y detecta si hay solapamientos en el tiempo.

Si el evento propuesto entra en conflicto con otros, el sistema analiza hora por hora la franja temporal para detectar el siguiente momento en el que los recursos vuelven a estar disponibles. Esta búsqueda también se aplica a los eventos recurrentes, ya que cada repetición debe ser viable por sí misma. El resultado es un mecanismo de planificación que no se limita a decir “sí” o “no”, sino que intenta encontrar una alternativa concreta cuando la primera opción no funciona.

## 7. Estructura del proyecto

La organización de archivos es simple y funcional, lo cual facilita entender el proyecto y mantenerlo:

- `app.py`: contiene la interfaz principal de Streamlit y la lógica de interacción con el usuario.
- `scheduler.py`: concentra las reglas de validación y la clase `Event`.
- `events.json`: almacena los eventos programados y los identificadores utilizados por el sistema.
- `resources.json`: define la capacidad total de recursos disponibles.
- `restrictions.json`: guarda las restricciones específicas para cada tipo de evento.
- `requirements.txt`: declara la dependencia externa del proyecto.
- `report.md`: contiene la descripción general y el informe del proyecto.
- `.streamlit/config.toml`: define la apariencia visual de la aplicación.

Esta estructura fue elegida porque separa claramente la lógica de negocio de los datos persistentes y de la interfaz. Aunque el proyecto es pequeño, mantener esa separación lo vuelve más entendible y reduce la probabilidad de errores al modificar una parte sin afectar las otras.

## 8. Diseño de la interfaz

La interfaz fue construida con Streamlit para aprovechar su simplicidad y rapidez de desarrollo. La aplicación muestra una página de inicio con información general, una sección para agregar eventos y otra para consultar y eliminar eventos existentes. La navegación se organiza en páginas, lo cual mejora la claridad de la experiencia de usuario.

En la página de creación de eventos se emplean controles como selectores de fecha, hora, números, listas desplegables y selección múltiple. Estos componentes permiten construir una interfaz accesible sin necesidad de programar una capa web compleja desde cero. Streamlit fue una elección adecuada porque ofrecía un equilibrio entre velocidad de desarrollo y facilidad de mantenimiento.

Además, la aplicación intenta guiar al usuario paso a paso. Primero se selecciona el tipo de evento, luego la clase de operación y después los recursos. Esto evita que la persona introduzca datos sin contexto y hace que el flujo de uso sea más natural.

## 9. Persistencia de datos

El proyecto guarda su información en archivos JSON. Esta elección tiene varias ventajas para un proyecto de este tamaño: la estructura es simple, el contenido es legible y no se necesita una base de datos externa para probar el sistema. Los eventos se cargan y se actualizan directamente desde `events.json`, mientras que los recursos y restricciones se leen desde sus respectivos archivos de configuración.

El uso de archivos JSON también facilitó la depuración, porque permite inspeccionar el contenido almacenado de forma directa. Aunque en un proyecto más grande sería razonable usar una base de datos relacional o un sistema más sofisticado, en este caso JSON era suficiente para representar el estado de la aplicación.

## 10. Cómo se usa el programa

Para ejecutar el proyecto, primero es necesario instalar las dependencias indicadas en `requirements.txt`:

```bash
pip install -r requirements.txt
```

Después, la aplicación se inicia con:

```bash
streamlit run app.py
```

Una vez abierta la interfaz, el usuario puede seguir un flujo básico:

1. Entrar en la página de inicio y leer la descripción general.
2. Ir a la sección de creación de eventos.
3. Elegir entre evento único o recurrente.
4. Seleccionar si el evento corresponde a mantenimiento o tránsito.
5. Definir fechas, horas y recursos.
6. Enviar la solicitud para que el sistema valide la propuesta.
7. Revisar si el evento fue aceptado o si se sugirió un horario alternativo.

Un ejemplo sencillo sería crear un tránsito de embarcación pequeña en una franja de seis horas, con un piloto junior, un remolcador y tres esclusas alineadas. Si otra operación ya utiliza esos recursos en ese intervalo, el sistema detectará el conflicto y buscará una alternativa compatible.

Otro ejemplo sería programar un mantenimiento de esclusa de cuatro horas con una esclusa específica y un equipo de mantenimiento. Si el horario seleccionado coincide con otro evento que ocupa la misma esclusa, el sistema rechazará la propuesta y sugerirá una fecha conveniente.

## 11. Dificultades encontradas

Durante el desarrollo surgieron varias dificultades que obligaron a ajustar tanto la estructura del código como la forma de validar ciertos datos.

Una de las primeras dificultades fue organizar correctamente las reglas de validación. El sistema no solo debía comprobar si un dato era correcto de forma aislada, sino también cómo interactuaba con otros datos. Esa necesidad llevó a separar el código en funciones con responsabilidades más concretas, especialmente dentro de `scheduler.py`.

Otra dificultad importante fue manejar la disponibilidad de recursos a lo largo del tiempo. Verificar conflictos entre eventos no es tan simple como revisar una fecha de inicio y una de fin; fue necesario recorrer la franja horaria de hora en hora para detectar solapamientos reales. Esta parte del proyecto exigió pensar el problema desde el punto de vista de intervalos y no solo desde el de formularios.

También resultó útil revisar cómo almacenar los eventos de forma persistente sin introducir complejidad innecesaria. La solución con JSON fue suficiente, pero exigió un tratamiento cuidadoso para no mezclar identificadores con eventos y para conservar una estructura coherente al guardar y eliminar registros.

## 12. Aprendizajes obtenidos

Este proyecto dejó varios aprendizajes técnicos y de diseño. El primero fue la importancia de separar responsabilidades: la interfaz no debe contener toda la lógica, y la lógica no debe depender por completo de la forma visual de los datos. Al dividir el sistema en capas más pequeñas, el código se volvió más comprensible.

El segundo aprendizaje fue el valor de las validaciones. En un sistema de planificación, aceptar datos sin control genera resultados incorrectos muy rápido. Por eso cada regla de negocio debe reflejarse en una comprobación explícita.

El tercer aprendizaje fue que un problema aparentemente pequeño puede esconder muchas dependencias. El tipo de evento, su duración, los recursos requeridos y la disponibilidad general forman parte de un mismo sistema, así que cualquier cambio en una sección puede afectar otras partes.

Finalmente, también se reforzó la importancia de escribir código pensando en el mantenimiento futuro. Aunque el proyecto está hecho a escala académica, el diseño elegido intenta que sea más fácil entenderlo, ampliarlo o corregirlo después.

## 13. Posibles mejoras futuras

Aunque el proyecto cumple su función principal, todavía podría mejorarse en varios aspectos. Una posible mejora sería sustituir el almacenamiento JSON por una base de datos ligera para manejar mejor la persistencia y las consultas. Otra mejora sería refactorizar más la clase `Event` para reducir duplicación de lógica entre validaciones similares.

También sería posible añadir pruebas automatizadas para verificar las reglas de validación, algo especialmente útil en una aplicación con tantas restricciones. Además, la interfaz podría enriquecerse con mensajes más visuales, tablas de eventos programados y un resumen de recursos ocupados en tiempo real.

Otra mejora interesante sería permitir exportar o importar calendarios completos, así como incorporar filtros para consultar eventos por tipo, por esclusa o por rango de fechas. Todas estas ampliaciones mantendrían la idea central del proyecto, pero lo harían más robusto y más cercano a una herramienta de planificación real.

## 14. Conclusión

El proyecto demuestra cómo una aplicación relativamente pequeña puede resolver un problema de planificación con varias restricciones simultáneas. A partir de Streamlit, archivos JSON y reglas bien definidas, fue posible construir un sistema que organiza eventos, controla recursos y evita conflictos de forma automática.

Más allá de la interfaz, el valor principal del proyecto está en la lógica que sostiene la validación. Cada evento debe cumplir condiciones de tiempo, duración, recursos y disponibilidad, y solo cuando todas esas condiciones se satisfacen el sistema lo acepta. Eso convierte al proyecto en una simulación útil de planificación estructurada dentro del contexto del Canal de Panamá.

En resumen, este trabajo integra interfaz, persistencia y validación en una solución coherente, con una organización clara y una base suficiente para seguir creciendo en futuras versiones.
