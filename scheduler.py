from datetime import datetime, timedelta
import json
from pathlib import Path

def load_json(filename):
    return json.loads(Path(filename).read_text())

resources_data = load_json("resources.json")
restrictions_data = load_json("restrictions.json")

class Event:
    def __init__(self, data):
        self.type = data.get("type")
        if self.type == "Recurring event":
            self.repeats = data.get("repeats")
            self.interval = data.get("interval")
        self.start_datetime = datetime.fromisoformat(data.get("start_datetime"))
        self.end_datetime = datetime.fromisoformat(data.get("end_datetime"))
        self.duration_hours = (self.end_datetime - self.start_datetime).total_seconds() / 3600
        self.subtype = data.get("subtype")
        if self.subtype == "Transit":
            self.vessel_size = data.get("vessel_size")
        self.junior_pilots = data.get("junior_pilots")
        self.senior_pilots = data.get("senior_pilots")
        self.tugboats = data.get("tugboats")
        self.maintenance_teams = data.get("maintenance_teams")
        self.locks = data.get("locks")
        self.error_messages = []
        
    def validate_datetime_logic(self):
        has_errors = False
        if self.start_datetime < datetime.now() or self.end_datetime < datetime.now():
            self.error_messages.append("Neither start nor end datetime can be in the past.")
            has_errors = True
        if self.end_datetime < self.start_datetime:
            self.error_messages.append("End datetime cannot be before start datetime.")
            has_errors = True
        if self.end_datetime == self.start_datetime:
            self.error_messages.append("End datetime cannot be the same as start datetime.")
            has_errors = True
        if self.end_datetime > datetime.now() + timedelta(days=60) or self.start_datetime > datetime.now() + timedelta(days=60):
            self.error_messages.append("Event limits have to be within the next 60 days.")
            has_errors = True
        return not has_errors

    def validate_duration_restrictions(self):
        has_errors = False
        if self.subtype == "Lock maintenance":
            minimum = restrictions_data["lock maintenance"]["min_duration_hours"]
            maximum = restrictions_data["lock maintenance"]["max_duration_hours"]
            if self.duration_hours < minimum or self.duration_hours > maximum:
                self.error_messages.append(f"Lock maintenance duration must be between {minimum} and {maximum} hours.")
                has_errors = True   
        elif self.subtype == "Transit":
            if self.vessel_size == "Small":
                minimum = restrictions_data["small vessel transit"]["min_duration_hours"]
                maximum = restrictions_data["small vessel transit"]["max_duration_hours"]
                if self.duration_hours < minimum or self.duration_hours > maximum:
                    self.error_messages.append(f"Small vessel transit duration must be between {minimum} and {maximum} hours.")
                    has_errors = True
            elif self.vessel_size == "Medium":
                minimum = restrictions_data["medium vessel transit"]["min_duration_hours"]
                maximum = restrictions_data["medium vessel transit"]["max_duration_hours"]
                if self.duration_hours < minimum or self.duration_hours > maximum:
                    self.error_messages.append(f"Medium vessel transit duration must be between {minimum} and {maximum} hours.")
                    has_errors = True
            elif self.vessel_size == "Large":
                minimum = restrictions_data["large vessel transit"]["min_duration_hours"]
                maximum = restrictions_data["large vessel transit"]["max_duration_hours"]
                if self.duration_hours < minimum or self.duration_hours > maximum:
                    self.error_messages.append(f"Large vessel transit duration must be between {minimum} and {maximum} hours.")
                    has_errors = True
        return not has_errors
    
    def validate_resources_logic(self):
        has_errors = False
        if self.junior_pilots > resources_data["junior_pilots"]:
            self.error_messages.append("Not enough junior pilots in existence.")
            has_errors = True
        if self.senior_pilots > resources_data["senior_pilots"]:
            self.error_messages.append("Not enough senior pilots in existence.")
            has_errors = True
        if self.tugboats > resources_data["tugboats"]:
            self.error_messages.append("Not enough tugboats in existence.")
            has_errors = True
        if self.maintenance_teams > resources_data["maintenance_teams"]:
            self.error_messages.append("Not enough maintenance teams in existence.")
            has_errors = True
        return not has_errors
            
    def validate_resources_restrictions(self):
        has_errors = False
        if self.subtype == "Lock maintenance":
            if self.junior_pilots != restrictions_data["lock maintenance"]["junior_pilots"]:
                self.error_messages.append(f"The amount of selected junior pilots does not match the required amount of junior pilots for a lock maintenance ({restrictions_data["lock maintenance"]["junior_pilots"]}).")
                has_errors = True
            if self.senior_pilots != restrictions_data["lock maintenance"]["senior_pilots"]:
                self.error_messages.append(f"The amount of selected senior pilots does not match the required amount of senior pilots for a lock maintenance ({restrictions_data["lock maintenance"]["senior_pilots"]}).")
                has_errors = True
            if self.tugboats != restrictions_data["lock maintenance"]["tugboats"]:
                self.error_messages.append(f"The amount of selected tugboats does not match the required amount of tugboats for a lock maintenance ({restrictions_data["lock maintenance"]["tugboats"]}).")
                has_errors = True
            if self.maintenance_teams != restrictions_data["lock maintenance"]["maintenance_teams"]:
                self.error_messages.append(f"The amount of selected maintenance teams does not match the required amount of maintenance teams for a lock maintenance ({restrictions_data["lock maintenance"]["maintenance_teams"]}).")
                has_errors = True
            if self.locks not in restrictions_data["lock maintenance"]["locks"]:
                self.error_messages.append("A lock maintenance requires only one lock.")
                has_errors = True
        elif self.subtype == "Transit":
            locks = sorted(self.locks)
            subtype = f"{self.vessel_size.lower()} vessel transit"
            if self.junior_pilots != restrictions_data[subtype]["junior_pilots"]:
                self.error_messages.append(f"The amount of selected junior pilots does not match the required amount of junior pilots for a {subtype} ({restrictions_data[subtype]['junior_pilots']}).")
                has_errors = True
            if self.senior_pilots != restrictions_data[subtype]["senior_pilots"]:
                self.error_messages.append(f"The amount of selected senior pilots does not match the required amount of senior pilots for a {subtype} ({restrictions_data[subtype]['senior_pilots']}).")
                has_errors = True
            if self.tugboats != restrictions_data[subtype]["tugboats"]:
                self.error_messages.append(f"The amount of selected tugboats does not match the required amount of tugboats for a {subtype} ({restrictions_data[subtype]['tugboats']}).")
                has_errors = True
            if self.maintenance_teams != restrictions_data[f"{subtype}"]["maintenance_teams"]:
                self.error_messages.append(f"The amount of selected maintenance teams does not match the required amount of maintenance teams for a {subtype} ({restrictions_data[f'{subtype}']['maintenance_teams']}).")
                has_errors = True
            if locks not in restrictions_data[subtype]["locks"]:
                self.error_messages.append(f"A {subtype} requires three locks in a row and only three locks.")
                has_errors = True
        return not has_errors
    
    def static_validations(self):
        return (self.validate_datetime_logic() and self.validate_duration_restrictions() and self.validate_resources_logic() and self.validate_resources_restrictions())
    
    def validate_resources_availability(self):
        events_data = load_json("events.json")
        has_errors = False
        overlapping_events = []
        for event_data in events_data:
            if type(event_data) == str:
                pass
            else:
                event_start = datetime.fromisoformat(event_data["start_datetime"])
                event_end = datetime.fromisoformat(event_data["end_datetime"])
                if (self.start_datetime < event_end and self.end_datetime > event_start):
                    parsed_event_data = event_data.copy()
                    parsed_event_data["start_datetime"] = event_start
                    parsed_event_data["end_datetime"] = event_end
                    overlapping_events.append(parsed_event_data)
        if not overlapping_events:
            return True, None
        current_checkpoint = self.start_datetime
        while current_checkpoint < self.end_datetime:
            used_junior_pilots = 0
            used_senior_pilots = 0
            used_tugboats = 0
            used_maintenance_teams = 0
            used_locks = []
            for event in overlapping_events:
                if event["start_datetime"] <= current_checkpoint < event["end_datetime"]:
                    used_junior_pilots += event["junior_pilots"]
                    used_senior_pilots += event["senior_pilots"]
                    used_tugboats += event["tugboats"]
                    used_maintenance_teams += event["maintenance_teams"]
                    used_locks.extend(event["locks"])
            if (used_junior_pilots + self.junior_pilots) > resources_data["junior_pilots"]:
                self.error_messages.append(f"Not enough junior pilots available at {current_checkpoint.strftime('%Y-%m-%d %H:%M')} .")
                has_errors = True
            if (used_senior_pilots + self.senior_pilots) > resources_data["senior_pilots"]:
                self.error_messages.append(f"Not enough senior pilots available at {current_checkpoint.strftime('%Y-%m-%d %H:%M')} .")
                has_errors = True
            if (used_tugboats + self.tugboats) > resources_data["tugboats"]:
                self.error_messages.append(f"Not enough tugboats available at {current_checkpoint.strftime('%Y-%m-%d %H:%M')} .")
                has_errors = True
            if (used_maintenance_teams + self.maintenance_teams) > resources_data["maintenance_teams"]:
                self.error_messages.append(f"Not enough maintenance teams available at {current_checkpoint.strftime('%Y-%m-%d %H:%M')} .")
                has_errors = True
            for lock in self.locks:
                if lock in used_locks:
                    self.error_messages.append(f"Lock {lock} is already in use at {current_checkpoint.strftime('%Y-%m-%d %H:%M')} .")
                    has_errors = True
            current_checkpoint += timedelta(hours=1)
        return not has_errors, self.error_messages
    
    def validate_recurrence_limits(self):
        has_errors = False
        if self.type == "Recurring event":
            if (self.end_datetime + timedelta(days=(self.interval * (self.repeats - 1)))) > datetime.now() + timedelta(days=60):
                self.error_messages.append("Recurring event limits have to be within the next 60 days.")
                has_errors = True
        return not has_errors
    
    def static_validations_recurrences(self):
        return (self.static_validations() and self.validate_recurrence_limits())
    
    def validate_recurrences(self):
        has_errors = False
        for i in range(self.repeats):
            step = i + 1
            start = self.start_datetime + timedelta(days=i * self.interval)
            end = self.end_datetime + timedelta(days=i * self.interval)
            temporal_event_data = {
                "type": self.type,
                "repeats": self.repeats,
                "interval": self.interval,
                "start_datetime": start.isoformat(),
                "end_datetime": end.isoformat(),
                "subtype": self.subtype,
                "vessel_size": self.vessel_size if self.subtype == "Transit" else None,
                "junior_pilots": self.junior_pilots,
                "senior_pilots": self.senior_pilots,
                "tugboats": self.tugboats,
                "maintenance_teams": self.maintenance_teams,
                "locks": self.locks
            }
            temporal_event = Event(temporal_event_data)
            is_valid, error_messages = temporal_event.validate_resources_availability()
            if not is_valid:
                error_message = f"Errors in recurrence {step}:"
                for error in temporal_event.error_messages:
                    error_message += (f"\n + {error}")
                self.error_messages.append(error_message)
                has_errors = True
        return not has_errors, self.error_messages

    def one_time_event_next_available_datetime(self):
        while self.end_datetime < (datetime.now() + timedelta(days=59, hours=23)):
            self.start_datetime += timedelta(hours=1)
            self.end_datetime += timedelta(hours=1)
            self.error_messages = []
            if self.validate_resources_availability()[0]:
                return True, "The selected datetime is unavailable", self.start_datetime, self.end_datetime
            else:
                continue
        return False, "No available datetime found in the next 60 days", None, None
    
    def recurring_event_next_available_datetime(self):
        while self.validate_recurrence_limits():
            self.start_datetime += timedelta(hours=1)
            self.end_datetime += timedelta(hours=1)
            self.error_messages = []
            if self.validate_recurrences()[0]:
                return True, "The selected datetime is unavailable", self.start_datetime, self.end_datetime
            else:
                continue
        return False, "No available datetime found in the next 60 days", None, None