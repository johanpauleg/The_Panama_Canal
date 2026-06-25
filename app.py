import streamlit as st
from datetime import datetime, timedelta, date, time
from scheduler import Event
import json
from pathlib import Path

def load_json(filename):
    return json.loads(Path(filename).read_text())

def save_to_json(filename, data): 
    Path(filename).write_text(json.dumps(data))
    
def save_event(data):
    events_data = load_json("events.json")
    if len(events_data) == 0:
        events_data.append("1")
        save_to_json("events.json", events_data)
    events_data = load_json("events.json")
    next_id = int(events_data[-1])
    events_data.pop()
    if data["type"] == "One-time event":
        data["id"] = str(next_id)
        events_data.append(data)
        next_id += 1
        events_data.append(str(next_id))
    else:
        base_start = datetime.fromisoformat(data["start_datetime"])
        base_end = datetime.fromisoformat(data["end_datetime"])
        
        for i in range(data["repeats"]):
            event_copy = data.copy()
            event_copy["id"] = str(next_id + i)
            event_copy["start_datetime"] = (base_start + timedelta(days=i * data["interval"])).isoformat()
            event_copy["end_datetime"] = (base_end + timedelta(days=i * data["interval"])).isoformat()
            events_data.append(event_copy)
        next_id += data["repeats"]
        events_data.append(str(next_id))
    save_to_json("events.json", events_data)
    
def delete_event(event_id): 
    events_data = load_json("events.json")
    for i in range(len(events_data)):
        if type(events_data[i]) == str:
            pass
        else:
            if str(events_data[i].get("id")) == str(event_id):
                events_data.pop(i)
                break
    save_to_json("events.json", events_data)

def home():
    st.title("Home page")
    st.subheader("Welcome to The Panama Canal.")
    st.write("You can two main actions:")
    create, see_and_delete = st.columns(2)
    with create:
        with st.container(border=True):
            st.write("Create a new event.")
            
    with see_and_delete:
        with st.container(border=True):
            st.write("See scheduled events and delete them.")
    
    with st.container(border=True):
        st.write("When creating a new event:")
        st.write("- You can chose between two types of events: One-time event or Recurring Event.")
        st.write("-- If you choose to create a Recurring Event, you have to select how many repeats do you want there to be and the interval of time (in days) between those repeats.")
        st.write("- You can chose what date and time you want your event to start and end.")
        st.write("- You can chose between two events: Transit or Lock maintenance.")
        st.write("-- If you choose to create a Transit, you have to select the size of the vessel that is going to sail trough the canal.")
        st.write("- Then you can chose how many Junior pilots, Senior pilots, Maintenance teams and Tugboats, and which Locks, you are going to use at your event.")
        st.write("- Then, you can press a button to Schedule the event, and the program I made is going to tell you if your event is valid, if it is not valid and if your event requires resources that are unavailable, and in that case, it will suggest to you the closest date in which your event resources are available and your event can be scheduled (of course, if there is not a date in which your event can happen, it will tell you so).")

def add():
    st.title("Add events")
    now = datetime.now()
    if now.hour == 23:
        default_start_date = (now + timedelta(days=1)).date()
        default_end_date = (now + timedelta(days=1)).date()
    elif now.hour == 22:
        default_start_date = now.date()
        default_end_date = (now + timedelta(days=1)).date()
    else:
        default_start_date = now.date()
        default_end_date = now.date()
    next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    default_start_time = next_hour.time()
    default_end_time = (next_hour + timedelta(hours=1)).time()
    
    if "scheduled_successfully" not in st.session_state:
        st.session_state.scheduled_successfully = False
    if "next_available_datetime" not in st.session_state:
        st.session_state.next_available_datetime = None
    if "just_scheduled" not in st.session_state:
        st.session_state.just_scheduled = False
    if "conflict_errors" not in st.session_state:
        st.session_state.conflict_errors = None
    if "not_next_available_datetime" not in st.session_state:
        st.session_state.not_next_available_datetime = None

    def reset_success_state():
        st.session_state.scheduled_successfully = False

    st.subheader("Select the type of event:")
    type = st.pills(
        "",
        ["One-time event", "Recurring event"],
        selection_mode="single",
        label_visibility="collapsed",
        on_change=reset_success_state
    )
    if type == "One-time event":
        st.write("---")
        start_date_column, start_time_column = st.columns(2)
        with start_date_column:
            start_date = st.date_input(
                ":material/calendar_today: Start date of the event",
                value=default_start_date,
                on_change=reset_success_state
            )
        with start_time_column:
            start_time = st.time_input(
                ":material/schedule: Start time of the event",
                value=default_start_time,
                step=3600,
                on_change=reset_success_state
            )
        end_date_column, end_time_column = st.columns(2)
        with end_date_column:
            end_date = st.date_input(
                ":material/calendar_today: End date of the event",
                value=default_end_date,
                on_change=reset_success_state
            )
        with end_time_column:
            end_time = st.time_input(
                ":material/schedule: End time of the event",
                value=default_end_time,
                step=3600,
                on_change=reset_success_state
            )

        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)

    elif type == "Recurring event":
        st.write("---")
        repeats_column, interval_column = st.columns(2)
        with repeats_column:
            repeats = st.number_input(
                ":material/repeat: Amount of repeats",
                min_value=2,
                max_value=60,
                value=2,
                step=1,
                on_change=reset_success_state
            )
        with interval_column:
            interval = st.number_input(
                ":material/calendar_view_day: Interval between repeats (days)",
                min_value=1,
                max_value=59,
                value=1,
                step=1,
                on_change=reset_success_state
            )
        start_date_column, start_time_column = st.columns(2)
        with start_date_column:
            start_date = st.date_input(
                ":material/calendar_today: Start date of the first event in the series  ",
                value=default_start_date,
                on_change=reset_success_state
            )
        with start_time_column:
            start_time = st.time_input(
                ":material/schedule: Start time of the first event in the series",
                value=default_start_time,
                step=3600,
                on_change=reset_success_state
            )
        end_date_column, end_time_column = st.columns(2)
        with end_date_column:
            end_date = st.date_input(
                ":material/calendar_today: End date of the first event in the series",
                value=default_end_date,
                on_change=reset_success_state
            )
        with end_time_column:
            end_time = st.time_input(
                ":material/schedule: End time of the first event in the series",
                value=default_end_time,
                step=3600,
                on_change=reset_success_state
            )

        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)

    if type:
        st.write("---")
        st.subheader("Select the event:")
        subtype = st.pills(
            "",
            ["Transit", "Lock maintenance"],
            selection_mode="single",
            label_visibility="collapsed",
            on_change=reset_success_state
        )
        if subtype:
            st.write("---")
            st.subheader("Resources:")
            st.markdown(":material/person: Human resources")
            junior_pilots_column, senior_pilots_column, maintenance_teams_column = st.columns(3)
            with junior_pilots_column:
                junior_pilots = st.number_input(
                    ":material/person: Junior pilots",
                    min_value=0,
                    max_value=10,
                    value=0,
                    step=1,
                    on_change=reset_success_state
                )
            with senior_pilots_column:
                senior_pilots = st.number_input(
                    ":material/person: Senior pilots",
                    min_value=0,
                    max_value=10,
                    value=0,
                    step=1,
                    on_change=reset_success_state
                )
            with maintenance_teams_column:
                maintenance_teams = st.number_input(
                    ":material/group: Maintenance teams",
                    min_value=0,
                    max_value=10,
                    value=0,
                    step=1,
                    on_change=reset_success_state
                )
            st.markdown(":material/directions_boat:  Tugboats")
            tugboats = st.number_input(
                "",
                min_value=0,
                max_value=10,
                value=0,
                step=1,
                label_visibility="collapsed",
                on_change=reset_success_state
            )
            st.markdown(":material/grid_view: Locks")
            locks = st.multiselect(
                "",
                ["A1", "A2", "A3", "C1", "C2", "C3", "P1", "P2", "P3"],
                label_visibility="collapsed",
                on_change=reset_success_state
            )
            if subtype == "Transit":
                st.write("---")
                st.markdown(":material/sailing: Vessel size")
                vessel_size = st.selectbox(
                    "",
                    ["Small", "Medium", "Large"],
                    label_visibility="collapsed",
                    on_change=reset_success_state
                )
            
            st.write("---")
            
            if st.session_state.just_scheduled:
                st.success("Event scheduled successfully.")
                st.session_state.just_scheduled = False
                
            data = {
                    "id": None,
                    "type": type,
                    "start_datetime": start_datetime.isoformat(),
                    "end_datetime": end_datetime.isoformat(),
                    "repeats": repeats if type == "Recurring event" else None,
                    "interval": interval if type == "Recurring event" else None,
                    "subtype": subtype,
                    "vessel_size": vessel_size if subtype == "Transit" else None,
                    "junior_pilots": junior_pilots,
                    "senior_pilots": senior_pilots,
                    "maintenance_teams": maintenance_teams,
                    "tugboats": tugboats,
                    "locks": locks,
                }
          
            if st.session_state.scheduled_successfully:
                st.success("Event scheduled successfully.")
                if st.button("Schedule another event"):
                    st.session_state.scheduled_successfully = False
                    st.session_state.just_scheduled = False
                    st.session_state.next_available_datetime = None
                    st.session_state.conflict_errors = None
                    st.rerun()
            elif st.session_state.not_next_available_datetime is not None:
                st.error(f"{st.session_state.not_next_available_datetime}")
                if st.button("Schedule another event"):
                    st.session_state.not_next_available_datetime = None
                    st.session_state.scheduled_successfully = False
                    st.session_state.just_scheduled = False
                    st.session_state.next_available_datetime = None
                    st.session_state.conflict_errors = None
                    st.rerun()
            elif st.session_state.next_available_datetime is not None:
                if st.session_state.conflict_errors:
                    st.error(st.session_state.conflict_errors)
                suggestion = st.session_state.next_available_datetime
                start = str(suggestion['start_datetime']).replace("T", " ")
                end = str(suggestion['end_datetime']).replace("T", " ")
                    
                st.info(f"💡 **Suggested next available time:**\nFrom `{start}` to `{end}`")              
                    
                reschedule, cancel = st.columns(2)
                with reschedule:
                    if st.button("Reschedule at suggested time", type="primary"):
                        suggestion_data = suggestion["data"]
                        suggestion_data["start_datetime"] = suggestion["start_datetime"]
                        suggestion_data["end_datetime"] = suggestion["end_datetime"]
                        save_event(suggestion_data)
                        st.session_state.next_available_datetime = None
                        st.session_state.conflict_errors = None
                        st.session_state.scheduled_successfully = True
                        st.rerun()
                with cancel:
                    if st.button("Cancel and edit manually"):
                        st.session_state.next_available_datetime = None
                        st.session_state.conflict_errors = None
                        st.rerun()
                        
            else:
                if st.button("Schedule event", type="primary"):
                    event = Event(data)
                        
                    if type == "One-time event":
                        if not event.static_validations():
                            error_message = "Error: The one-time event is not valid, because:"
                            for error in event.error_messages:
                                error_message += (f"\n + {error}")
                            st.error(error_message)
                        else:
                            is_valid, error_messages = event.validate_resources_availability()
                            if not is_valid:
                                error_message = "Resource conflict. The event cannot be scheduled, because:"
                                for error in error_messages:
                                    error_message += (f"\n + {error}")
                                st.session_state.conflict_errors = error_message
                                    
                                has_next, message, start, end = event.one_time_event_next_available_datetime()
                                if not has_next:
                                    st.session_state.not_next_available_datetime = message
                                else:
                                    st.session_state.next_available_datetime = {
                                        "data": data,
                                        "start_datetime": start.isoformat(),
                                        "end_datetime": end.isoformat()
                                    }
                                    st.rerun()
                            else:
                                save_event(data)
                                st.session_state.scheduled_successfully = True
                                st.rerun()
                    else:
                        if not event.static_validations_recurrences():
                            error_message = "Error: The recurring event is not valid, because:"
                            for error in event.error_messages:
                                error_message += (f"\n + {error}")
                            st.error(error_message)
                        else:
                            is_valid, error_messages = event.validate_recurrences()
                            if not is_valid:
                                error_message = "Resource conflict. The recurring event cannot be scheduled, because:"
                                for error in error_messages:
                                    error_message += (f"\n + {error}")
                                st.session_state.conflict_errors = error_message
                                    
                                has_next, message, start, end = event.recurring_event_next_available_datetime()
                                if not has_next:
                                    st.session_state.not_next_available_datetime = message
                                else:
                                    st.session_state.next_available_datetime = {
                                        "data": data,
                                        "start_datetime": start.isoformat(),
                                        "end_datetime": end.isoformat()
                                    }
                                    st.rerun()
                            else:
                                save_event(data)
                                st.session_state.scheduled_successfully = True
                                st.rerun()
                           
def schedule():
    st.title("Scheduled events")
    events_data = load_json("events.json")
    if len(events_data) == 0:
        st.info("There are no scheduled events.")
    else:
        for event in events_data:
            if type(event) == str:
                pass
            else:
                
                with st.container(border=True):
                    if event.get("subtype") == "Lock maintenance":
                        st.write(f"{event.get("id")} - Lock maintenance :material/grid_view:")
                        start_datetime, end_datetime = st.columns(2)
                        with start_datetime:
                            st.write(f"Start: {event.get("start_datetime")}")
                        with end_datetime:
                            st.write(f"End: {event.get("end_datetime")}")
                        maintenance_teams, locks = st.columns(2)
                        with maintenance_teams:
                            st.write(f"Maintenance teams: {event.get("maintenance_teams")}")
                        with locks:
                            locks = ""
                            for lock in event.get("locks"):
                                locks += f"{lock}, "
                            st.write(f"Locks: {locks[:-2]}")
                    else:
                        st.write(f"{event.get("id")} - {event.get("vessel_size")} vessel transit :material/sailing:")
                        start_datetime, end_datetime = st.columns(2)
                        with start_datetime:
                            st.write(f"Start: {event.get("start_datetime")}")
                        with end_datetime:
                            st.write(f"End: {event.get("end_datetime")}")
                        if event.get("vessel_size") == "Small":
                            junior_pilots, tugboat, locks = st.columns(3)
                            with junior_pilots:
                                st.write(f"Junior pilots: {event.get("junior_pilots")}")
                            with tugboat:
                                st.write(f"Tugboats: {event.get("tugboat")}")
                            with locks:
                                locks = ""
                                for lock in event.get("locks"):
                                    locks += f"{lock}, "
                                st.write(f"Locks: {locks[:-2]}")
                        else:
                            senior_pilots, tugboat, locks = st.columns(3)
                            with senior_pilots:
                                st.write(f"Senior pilots: {event.get("senior_pilots")}")
                            with tugboat:
                                st.write(f"Tugboats: {event.get("tugboat")}")
                            with locks:
                                locks = ""
                                for lock in event.get("locks"):
                                    locks += f"{lock}, "
                                st.write(f"Locks: {locks[:-2]}")
                    if st.button("Delete event", key=f"delete_{event.get("id")}"):
                        delete_event(event.get("id"))
                        st.rerun()

pg_home = st.Page(home, title="Home page", icon=":material/home:")
pg_add = st.Page(add, title="Add events", icon=":material/add:")
pg_schedule = st.Page(schedule, title="Scheduled events", icon=":material/list:")

pg = st.navigation({"": [pg_home, pg_add, pg_schedule]})

pg.run()
