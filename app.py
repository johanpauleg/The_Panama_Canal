import streamlit as st
from datetime import time, datetime, timedelta
from something import events, loadSchedule, saveSchedule


def home():
    st.title("Página principal")


def add():
    st.title("Añadir evento")

    ahora = datetime.now()
    proxima_hora = ahora.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    hora_default_inicio = proxima_hora.time()
    hora_default_culminación = (proxima_hora + timedelta(hours=1)).time()

    if "fecha_inicio" not in st.session_state:
        st.session_state["fecha_inicio"] = ahora.date()
    if "hora_inicio" not in st.session_state:
        st.session_state["hora_inicio"] = hora_default_inicio
    if "fecha_culminación" not in st.session_state:
        st.session_state["fecha_culminación"] = ahora.date()
    if "hora_culminación" not in st.session_state:
        st.session_state["hora_culminación"] = hora_default_culminación
    if "defaults" not in st.session_state:
        st.session_state["defaults"] = {
            "fecha_inicio": ahora.date(),
            "hora_inicio": hora_default_inicio,
            "fecha_culminación": ahora.date(),
            "hora_culminación": hora_default_culminación,
        }
    if "pending_reubicacion" in st.session_state:
        pending = st.session_state.pop("pending_reubicacion")
        st.session_state["fecha_inicio"] = pending["start"].date()
        st.session_state["hora_inicio"] = pending["start"].time()
        st.session_state["fecha_culminación"] = pending["end"].date()
        st.session_state["hora_culminación"] = pending["end"].time()
    if "reubicacion" not in st.session_state:
        st.session_state["reubicacion"] = None
    if "reubicacion_data" not in st.session_state:
        st.session_state["reubicacion_data"] = None
    if "reubicacion_tipo" not in st.session_state:
        st.session_state["reubicacion_tipo"] = None

    st.subheader("Selecciona el tipo de evento:")
    tipo = st.pills(
        "",
        ["Evento único", "Evento recurrente"],
        selection_mode="single",
        label_visibility="collapsed",
    )
    repeticiones = None
    intervalo = None
    embarcación = None

    if tipo == "Evento único":
        st.write("---")
        col_fec_ini, col_hor_ini = st.columns(2)
        with col_fec_ini:
            fecha_inicio = st.date_input(
                ":material/calendar_today: Fecha de inicio del evento",
                value=st.session_state["fecha_inicio"],
                key="fecha_inicio",
            )
        with col_hor_ini:
            hora_inicio = st.time_input(
                ":material/schedule: Hora de inicio del evento",
                value=st.session_state["hora_inicio"],
                step=3600,
                key="hora_inicio",
            )
        col_fec_cul, col_hor_cul = st.columns(2)
        with col_fec_cul:
            fecha_culminación = st.date_input(
                ":material/calendar_today: Fecha de culminación del evento",
                value=st.session_state["fecha_culminación"],
                key="fecha_culminación",
            )
        with col_hor_cul:
            hora_culminación = st.time_input(
                ":material/schedule: Hora de culminación del evento",
                value=st.session_state["hora_culminación"],
                step=3600,
                key="hora_culminación",
            )

        dt_inicio = datetime.combine(fecha_inicio, hora_inicio)
        dt_culminación = datetime.combine(fecha_culminación, hora_culminación)
        duración = int((dt_culminación - dt_inicio).total_seconds() // 3600)

    elif tipo == "Evento recurrente":
        st.write("---")
        col_rep, col_int = st.columns(2)
        with col_rep:
            repeticiones = st.number_input(
                ":material/repeat: Cantidad de repeticiones",
                min_value=2,
                max_value=60,
                value=2,
                step=1,
            )
        with col_int:
            intervalo = st.number_input(
                ":material/calendar_view_day: Intervalo entre repeticiones (días)",
                min_value=1,
                max_value=59,
                value=1,
                step=1,
            )
        col_fec_ini, col_hor_ini = st.columns(2)
        with col_fec_ini:
            fecha_inicio = st.date_input(
                ":material/calendar_today: Fecha de inicio del primer evento de la serie",
                value=st.session_state["fecha_inicio"],
                key="fecha_inicio",
            )
        with col_hor_ini:
            hora_inicio = st.time_input(
                ":material/schedule: Hora de inicio del primer evento de la serie",
                value=st.session_state["hora_inicio"],
                step=3600,
                key="hora_inicio",
            )
        col_fec_cul, col_hor_cul = st.columns(2)
        with col_fec_cul:
            fecha_culminación = st.date_input(
                ":material/calendar_today: Fecha de culminación del primer evento de la serie",
                value=st.session_state["fecha_culminación"],
                key="fecha_culminación",
            )
        with col_hor_cul:
            hora_culminación = st.time_input(
                ":material/schedule: Hora de culminación del primer evento de la serie",
                value=st.session_state["hora_culminación"],
                step=3600,
                key="hora_culminación",
            )

        dt_inicio = datetime.combine(fecha_inicio, hora_inicio)
        dt_culminación = datetime.combine(fecha_culminación, hora_culminación)
        duración = int((dt_culminación - dt_inicio).total_seconds() // 3600)

    else:
        pass

    if tipo:
        st.write("---")
        st.subheader("Selecciona el evento:")
        subtipo = st.pills(
            "",
            ["Tránsito", "Mantenimiento a una esclusa"],
            selection_mode="single",
            label_visibility="collapsed",
        )
        if subtipo:
            st.write("---")
            st.subheader("Recursos a utilizar en el evento:")
            st.markdown(":material/person: Personal")
            col_jr, col_sr, col_eqm = st.columns(3)
            with col_jr:
                pilotos_jr = st.number_input(
                    ":material/person: Pilotos junior",
                    min_value=0,
                    max_value=10,
                    value=0,
                    step=1,
                )
            with col_sr:
                pilotos_sr = st.number_input(
                    ":material/person: Pilotos senior",
                    min_value=0,
                    max_value=10,
                    value=0,
                    step=1,
                )
            with col_eqm:
                equipos_m = st.number_input(
                    ":material/group: Equipos de mantenimiento",
                    min_value=0,
                    max_value=10,
                    value=0,
                    step=1,
                )
            st.markdown(":material/directions_boat:  Remolcadores")
            remolcadores = st.number_input(
                "",
                min_value=0,
                max_value=10,
                value=0,
                step=1,
                label_visibility="collapsed",
            )
            st.markdown(":material/grid_view: Esclusas")
            esclusas = st.multiselect(
                "",
                ["A1", "A2", "A3", "C1", "C2", "C3", "P1", "P2", "P3"],
                label_visibility="collapsed",
            )
            if subtipo == "Tránsito":
                st.write("---")
                st.subheader("Detalles del tránsito:")
                embarcación = st.selectbox(
                    ":material/sailing: Tipo de embarcación",
                    ["Pequeña", "Mediana", "Grande"],
                )
            st.write("---")
            submit = st.button("Añadir evento al calendario")
            if submit:
                datos_evento = {
                    "type": tipo,
                    "reps": repeticiones if tipo == "Evento recurrente" else None,
                    "step": intervalo if tipo == "Evento recurrente" else None,
                    "startDate": fecha_inicio,
                    "startTime": hora_inicio,
                    "endDate": fecha_culminación,
                    "endTime": hora_culminación,
                    "subType": subtipo,
                    "jrPilots": pilotos_jr,
                    "srPilots": pilotos_sr,
                    "maintTeams": equipos_m,
                    "tugboats": remolcadores,
                    "locks": esclusas,
                    "shipSize": embarcación if subtipo == "Tránsito" else None,
                    "direction": None,
                    "priority": None,
                }
                c1 = events(datos_evento)
                ok, message, suggestion = c1.validateAndAdd()
                if not ok:
                    st.error(f"Error: {message}")
                    if suggestion:
                        st.session_state["reubicacion"] = suggestion
                        st.session_state["reubicacion_data"] = dict(datos_evento)
                        st.session_state["reubicacion_tipo"] = tipo
                else:
                    st.success(message)
                    st.session_state["reubicacion"] = None
                    st.session_state["reubicacion_data"] = None
                    st.session_state["reubicacion_tipo"] = None
                    st.session_state["show_reubicar"] = False

            if (
                st.session_state.get("reubicacion")
                and st.session_state.get("reubicacion_data")
                and st.session_state.get("reubicacion_tipo")
            ):
                st.session_state["show_reubicar"] = True

            if st.session_state.get("show_reubicar"):
                if st.button("Reubicar a la proxima disponibilidad"):
                    suggestion = st.session_state["reubicacion"]
                    datos_evento_reubicado = dict(st.session_state["reubicacion_data"])
                    datos_evento_reubicado["startDate"] = suggestion["start"].date()
                    datos_evento_reubicado["startTime"] = suggestion["start"].time()
                    datos_evento_reubicado["endDate"] = suggestion["end"].date()
                    datos_evento_reubicado["endTime"] = suggestion["end"].time()
                    c2 = events(datos_evento_reubicado)
                    ok2, message2, _ = c2.validateAndAdd()
                    if ok2:
                        if st.session_state["reubicacion_tipo"] == "Evento recurrente":
                            st.success("Serie reubicada con éxito.")
                        else:
                            st.success("Evento reubicado con éxito.")
                        st.session_state["reubicacion"] = None
                        st.session_state["reubicacion_data"] = None
                        st.session_state["reubicacion_tipo"] = None
                        st.session_state["show_reubicar"] = False
                    else:
                        st.error(f"Error: {message2}")


# ---------------------------------------------------------------------------------------------------------
def view():
    st.title("Ver Agenda")
    schedule = loadSchedule()
    if not schedule:
        st.info("La agenda esta vacia.")
        return

    def sort_key(record: dict):
        return (
            record.get("startDate", ""),
            record.get("startTime", ""),
            record.get("id", ""),
        )

    ordered = sorted(schedule, key=sort_key)
    st.dataframe(ordered, use_container_width=True)


def delete():
    st.title("Eliminar eventos")
    schedule = loadSchedule()
    if not schedule:
        st.info("No hay eventos para eliminar.")
        return

    options = []
    indexByLabel = {}
    for idx, record in enumerate(schedule):
        label = (
            f"{record.get('id', '??')} | {record.get('subType', '')} | "
            f"{record.get('startDate', '')} {record.get('startTime', '')}"
        )
        options.append(label)
        indexByLabel[label] = idx

    selected = st.multiselect(
        "Selecciona eventos para eliminar",
        options,
        label_visibility="visible",
    )

    if st.button("Eliminar seleccionados"):
        if not selected:
            st.warning("Selecciona al menos un evento.")
            return
        remaining = [
            record
            for idx, record in enumerate(schedule)
            if idx not in {indexByLabel[label] for label in selected}
        ]
        saveSchedule(remaining)
        st.success("Eventos eliminados con exito.")


pg_home = st.Page(home, title="Página principal", icon=":material/home:")
pg_add = st.Page(add, title="Añadir evento", icon=":material/add:")
pg_view = st.Page(view, title="Ver agenda", icon=":material/list:")
pg_delete = st.Page(delete, title="Eliminar eventos", icon=":material/delete:")

pg = st.navigation({"": [pg_home, pg_add, pg_view, pg_delete]})

pg.run()
