# Planificador de eventos del Canal de Panamá

**Autor:** Johan Paul Echevarría González  
**Perfil de GitHub:** johanpauleg  
**Repositorio:** The_Panama_Canal

## Descripción

Este proyecto es una aplicación desarrollada con Streamlit para planificar eventos relacionados con el funcionamiento del Canal de Panamá. Su objetivo es evitar la creación de eventos ilógicos o inválidos y prevenir que un mismo recurso se asigne a más de un evento al mismo tiempo.

## Recursos del sistema

El sistema trabaja con dos tipos de recursos:

- Recursos específicos: esclusas A1, A2, A3, C1, C2, C3, P1, P2 y P3.
- Recursos por cantidad: 2 pilotos junior, 2 pilotos senior, 6 remolcadores y 3 equipos de mantenimiento.

## Tipos de eventos

La aplicación permite crear dos tipos de eventos:

- Evento único.
- Evento recurrente, donde se define cuántas veces se repite y el intervalo de días entre cada repetición.

En ambos casos, el usuario puede seleccionar entre dos clases de evento:

- Mantenimiento de una esclusa.
- Tránsito de una embarcación por el canal.

Cuando se trata de un tránsito, también es necesario indicar el tamaño de la embarcación, ya que cada tamaño requiere recursos distintos.

## Validaciones

Antes de agendar un evento, el sistema aplica varias validaciones:

### Validaciones de tiempo

Se comprueba que la fecha y la hora de inicio sean coherentes con la fecha y la hora de finalización. En particular, el inicio no puede quedar en el pasado, la finalización debe ser posterior al inicio y ambos extremos deben ubicarse dentro de los próximos 60 días.

### Validaciones de duración

Cada tipo de evento debe cumplir una duración específica:

- Mantenimiento de una esclusa: entre 4 y 5 horas.
- Tránsito de embarcación pequeña: entre 6 y 8 horas.
- Tránsito de embarcación mediana: entre 8 y 11 horas.
- Tránsito de embarcación grande: entre 10 y 14 horas.

### Validaciones de recursos y restricciones

El sistema verifica que la combinación de recursos seleccionada sea válida para el tipo de evento elegido. Por ejemplo:

- Un mantenimiento de esclusa requiere una esclusa y un equipo de mantenimiento, sin pilotos ni remolcadores.
- Un tránsito requiere tres esclusas alineadas, como A1, C1 y P1.
- Un tránsito de embarcación pequeña requiere un piloto junior.
- Un tránsito de embarcación mediana o grande requiere un piloto senior.
- La cantidad de remolcadores aumenta según el tamaño de la embarcación: 1, 2 o 3.
- Los tránsitos no pueden incluir equipos de mantenimiento.

### Validaciones de recurrencia

En los eventos recurrentes, el sistema comprueba que la serie completa de repeticiones no supere el límite de 60 días.

### Validaciones de disponibilidad

La aplicación revisa si ya existen eventos en el mismo intervalo de tiempo y si alguno consume los mismos recursos. Esto se aplica tanto a eventos únicos como a eventos recurrentes. Si no hay disponibilidad, el sistema busca el próximo horario posible en el que el evento pueda ejecutarse con la misma duración y los mismos recursos.

## Estructura del proyecto

- `app.py`: interfaz principal de Streamlit y lógica de interacción con el usuario.
- `scheduler.py`: reglas de validación y manejo de eventos.
- `events.json`: almacenamiento de los eventos programados.
- `resources.json`: inventario de recursos disponibles.
- `restrictions.json`: reglas y restricciones del sistema.
- `.streamlit/config.toml`: configuración visual de Streamlit.

## Cómo ejecutar el proyecto

1. Instalar las dependencias:

	```bash
	pip install -r requirements.txt
	```

2. Ejecutar la aplicación:

	```bash
	streamlit run app.py
	```

## Requisitos mínimos

- Python 3.10 o superior.
- Streamlit 1.36.0.

## Observación final

Este proyecto fue diseñado para simular, de forma ordenada, la planificación de eventos dentro del Canal de Panamá y para impedir conflictos de recursos, duración o tiempo.
