# APIUniSabana
## Integrantes del Proyecto
| Nombre | Correo Electrónico |
|---|---|
| Valentina Alejandra López Romero | valentinalopro@unisabana.edu.co |
| Mariana Valle Moreno | marianavamo@unisabana.edu.co |

# Circuit Breaker API

Este trabajo implementa el patrón de diseño **Circuit Breaker** en una API REST, utilizando Python y Flask, para mejorar la resiliencia de un servicio que depende de un buró externo. La API principal (UniSabana) se protege de los fallos continuos del buró primario, redirigiendo el tráfico a un buró secundario (fallback) cuando es necesario.

## Características Principales

- **Patrón Circuit Breaker**: La lógica principal controla el flujo de las solicitudes basándose en el estado de un servicio externo.
- **Estados del Circuito**: Implementa los estados **Closed**, **Open** y **Half-open** para una gestión de fallos inteligente.
- **Ventana Deslizante**: Evalúa la tasa de fallos dentro de una ventana de 10 solicitudes recientes.
- **Umbral de Fallos**: El circuito se abre si el 50% o más de las solicitudes en la ventana fallan.
- **Mecanismo de Fallback**: Cuando el circuito está abierto, las solicitudes se desvían automáticamente a un servicio de respaldo (buró secundario).
- **Recuperación Automática**: Después de 30 segundos en el estado `Open`, el circuito pasa a `Half-open` para probar si el servicio primario se ha recuperado.

## Estructura del Proyecto

El proyecto está organizado en un solo archivo principal que contiene la lógica de la API y las implementaciones de los servicios externos simulados.

- `unisabana_api.py`: Contiene el código de la API de UniSabana y la lógica del Circuit Breaker.
- `primary.py`: Simula el servicio del buró primario, que es propenso a fallos.
- `secondary.py`: Simula el servicio del buró secundario, que actúa como fallback.
- `load_test.py`: Script utilizado para simular múltiples solicitudes a la API y probar los estados del circuito.

## Cómo Usarlo

  **Ejecutar los servicios**: Se deben ejecutar los servicios simulados en terminales separadas.
    - **Buró Secundario (siempre encendido):**
      `python secondary.py`
    - **API UniSabana:**
      `python unisabana_api.py`
    - **Buró Primario (apagar para forzar fallos):**
      `python primary.py`
      (Para ver el circuito abrirse, apaga este servicio con `Ctrl+C`.)
  **Realizar pruebas de carga**: Usa el script `load_test.py` para enviar múltiples solicitudes a la API de UniSabana.
    ```bash
    python load_test.py
    ```

## Flujo de Demostración

- **Estado `Closed` a `Open`**: Al apagar `primary.py`, las solicitudes fallarán, y el circuito cambiará a `Open` después de que 5 de las 10 solicitudes fallen.
- **Estado `Open` y `Fallback`**: Todas las solicitudes subsecuentes serán redirigidas a `secondary.py`, y la API principal responderá con el resultado del buró secundario.
- **Estado `Half-open`**: Al volver a encender `primary.py` y esperar 30 segundos, la próxima solicitud de `load_test.py` será una "prueba" en el estado `Half-open`. Si tiene éxito, el circuito se cerrará.

---
El video "[A Quick Guide to Writing a Great Readme](https://www.youtube.com/watch?v=0h8-C-tq-o4)" proporciona consejos útiles sobre cómo estructurar un archivo README de manera efectiva para proyectos de software.
