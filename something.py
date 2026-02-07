from datetime import datetime, timedelta, date, time
from pathlib import Path
import json

baseDirectory_1 = Path(__file__).resolve().parent
with open(baseDirectory_1 / "restrictions.json", "r", encoding="utf-8") as f:
    restrictions = json.load(f)

baseDirectory_2 = Path(__file__).resolve().parent
with open(baseDirectory_2 / "resources.json", "r", encoding="utf-8") as f:
    resources = json.load(f)

schedulePath = baseDirectory_1 / "schedule.json"

now = datetime.now()


def loadSchedule() -> list[dict]:
    if not schedulePath.exists():
        return []
    with open(schedulePath, "r", encoding="utf-8") as f:
        return json.load(f)


def saveSchedule(records: list[dict]) -> None:
    with open(schedulePath, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)


def nextEventId(records: list[dict]) -> str:
    maxId = 0
    for record in records:
        value = str(record.get("id", "0"))
        if value.isdigit():
            maxId = max(maxId, int(value))
    return f"{maxId + 1:02d}"


def parseDateValue(value) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def parseTimeValue(value) -> time:
    if isinstance(value, time):
        return value
    return time.fromisoformat(value)


def recordToDateTimes(record: dict) -> tuple[datetime, datetime]:
    startDate = parseDateValue(record["startDate"])
    startTime = parseTimeValue(record["startTime"])
    endDate = parseDateValue(record["endDate"])
    endTime = parseTimeValue(record["endTime"])
    return datetime.combine(startDate, startTime), datetime.combine(endDate, endTime)


def lockLine(lockValue: str) -> str:
    text = str(lockValue)
    return text[1:] if len(text) > 1 else ""


class events:
    def __init__(self, data: dict):
        self.id = data["id"] if "id" in data else None
        self.type = data["type"] if "type" in data else None
        self.reps = data["reps"] if "reps" in data else None
        self.step = data["step"] if "step" in data else None
        self.startDate = data["startDate"] if "startDate" in data else None
        self.startTime = data["startTime"] if "startTime" in data else None
        self.endDate = data["endDate"] if "endDate" in data else None
        self.endTime = data["endTime"] if "endTime" in data else None
        self.subType = data["subType"] if "subType" in data else None
        self.jrPilots = data["jrPilots"] if "jrPilots" in data else None
        self.srPilots = data["srPilots"] if "srPilots" in data else None
        self.maintTeams = data["maintTeams"] if "maintTeams" in data else None
        self.tugboats = data["tugboats"] if "tugboats" in data else None
        self.locks = data["locks"] if "locks" in data else None
        self.shipSize = data["shipSize"] if "shipSize" in data else None
        self.direction = data["direction"] if "direction" in data else None
        self.priority = data["priority"] if "priority" in data else None
        self.startDateTime = (
            datetime.combine(self.startDate, self.startTime)
            if self.startDate and self.startTime
            else None
        )
        self.endDateTime = (
            datetime.combine(self.endDate, self.endTime)
            if self.endDate and self.endTime
            else None
        )
        self.duration = (
            self.endDateTime - self.startDateTime
            if self.startDateTime and self.endDateTime
            else None
        )
        self.durationInHours = (
            int(self.duration.total_seconds() // 3600) if self.duration else None
        )

    def toRecord(self, startDateTime: datetime, endDateTime: datetime) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "reps": self.reps,
            "step": self.step,
            "startDate": startDateTime.date().isoformat(),
            "startTime": startDateTime.time().isoformat(),
            "endDate": endDateTime.date().isoformat(),
            "endTime": endDateTime.time().isoformat(),
            "subType": self.subType,
            "jrPilots": self.jrPilots,
            "srPilots": self.srPilots,
            "maintTeams": self.maintTeams,
            "tugboats": self.tugboats,
            "locks": self.locks,
            "shipSize": self.shipSize,
            "direction": self.direction,
            "priority": self.priority,
        }

    def overlaps(
        self, startA: datetime, endA: datetime, startB: datetime, endB: datetime
    ) -> bool:
        return startA < endB and endA > startB

    def getLineId(self, locksValue: list[str] | None) -> str:
        if not locksValue:
            return ""
        return lockLine(locksValue[0])

    def validateAvailability(
        self,
        scheduleRecords: list[dict] | None = None,
        startDateTime: datetime | None = None,
        endDateTime: datetime | None = None,
    ) -> tuple[bool, str]:
        if scheduleRecords is None:
            scheduleRecords = loadSchedule()
        startDateTime = startDateTime or self.startDateTime
        endDateTime = endDateTime or self.endDateTime
        if not startDateTime or not endDateTime:
            return False, "Faltan fechas u horas para revisar disponibilidad."

        overlapRecords = []
        for record in scheduleRecords:
            recordStart, recordEnd = recordToDateTimes(record)
            if self.overlaps(startDateTime, endDateTime, recordStart, recordEnd):
                overlapRecords.append(record)

        totalJr = (self.jrPilots or 0) + sum(
            r.get("jrPilots", 0) for r in overlapRecords
        )
        totalSr = (self.srPilots or 0) + sum(
            r.get("srPilots", 0) for r in overlapRecords
        )
        totalMaint = (self.maintTeams or 0) + sum(
            r.get("maintTeams", 0) for r in overlapRecords
        )
        totalTug = (self.tugboats or 0) + sum(
            r.get("tugboats", 0) for r in overlapRecords
        )

        if totalJr > resources["jrPilots"]:
            return False, "No hay suficientes pilotos junior disponibles."
        if totalSr > resources["srPilots"]:
            return False, "No hay suficientes pilotos senior disponibles."
        if totalMaint > resources["maintTeams"]:
            return False, "No hay suficientes equipos de mantenimiento disponibles."
        if totalTug > resources["tugboats"]:
            return False, "No hay suficientes remolcadores disponibles."

        if overlapRecords and self.locks:
            currentLine = self.getLineId(self.locks)
            for record in overlapRecords:
                recordLocks = record.get("locks") or []
                recordLine = self.getLineId(recordLocks)
                recordSubType = record.get("subType")

                if self.subType == "Mantenimiento a una esclusa":
                    if recordLocks and self.locks and self.locks[0] in recordLocks:
                        return False, "La esclusa seleccionada no esta disponible."
                elif self.subType == "Tránsito":
                    if (
                        recordSubType == "Tránsito"
                        and currentLine
                        and currentLine == recordLine
                    ):
                        return (
                            False,
                            "La linea de esclusas seleccionada no esta disponible.",
                        )
                    if (
                        recordSubType == "Mantenimiento a una esclusa"
                        and currentLine
                        and currentLine == recordLine
                    ):
                        return (
                            False,
                            "La linea de esclusas seleccionada no esta disponible.",
                        )

        return True, "Availability validation passed."

    def findNextAvailableSlot(
        self, maxDays: int = 60
    ) -> tuple[bool, str, datetime | None, datetime | None]:
        if not self.startDateTime or not self.endDateTime:
            return False, "Faltan fechas u horas para buscar un hueco.", None, None
        scheduleRecords = loadSchedule()
        duration = self.endDateTime - self.startDateTime
        if duration.total_seconds() <= 0:
            return False, "Duracion invalida para buscar un hueco.", None, None

        currentStart = self.startDateTime
        limit = datetime.now() + timedelta(days=maxDays)
        while currentStart <= limit:
            currentEnd = currentStart + duration
            available, _ = self.validateAvailability(
                scheduleRecords, currentStart, currentEnd
            )
            if available:
                return True, "Next slot found.", currentStart, currentEnd
            currentStart += timedelta(hours=1)

        return False, "No se encontro un hueco en el rango permitido.", None, None

    def findNextAvailableSeriesStart(
        self, maxDays: int = 60
    ) -> tuple[bool, str, datetime | None, datetime | None]:
        if not self.reps or not self.step:
            return False, "Faltan repeticiones o intervalo.", None, None
        if not self.startDateTime or not self.endDateTime:
            return False, "Faltan fechas u horas para buscar un hueco.", None, None

        scheduleRecords = loadSchedule()
        duration = self.endDateTime - self.startDateTime
        if duration.total_seconds() <= 0:
            return False, "Duracion invalida para buscar un hueco.", None, None

        currentStart = self.startDateTime
        limit = datetime.now() + timedelta(days=maxDays)
        while currentStart <= limit:
            currentEnd = currentStart + duration
            lastEnd = currentStart + timedelta(days=self.step * (self.reps - 1)) + duration
            if lastEnd > limit:
                return False, "No se encontro un hueco en el rango permitido.", None, None

            tempRecords = list(scheduleRecords)
            ok = True
            for i in range(self.reps):
                offset = timedelta(days=self.step * i)
                instanceStart = currentStart + offset
                instanceEnd = instanceStart + duration
                available, _ = self.validateAvailability(
                    tempRecords, instanceStart, instanceEnd
                )
                if not available:
                    ok = False
                    break
                tempRecords.append(self.toRecord(instanceStart, instanceEnd))

            if ok:
                return True, "Next series slot found.", currentStart, currentEnd

            currentStart += timedelta(hours=1)

        return False, "No se encontro un hueco en el rango permitido.", None, None

    def validateAndAdd(self) -> tuple[bool, str, dict | None]:
        isValid, message = self.validateEvent()
        if not isValid:
            return False, message, None

        if self.type == "Evento recurrente" and self.reps and self.step:
            return self.validateAndAddRecurring()

        available, availabilityMessage = self.validateAvailability()
        if not available:
            found, _, nextStart, nextEnd = self.findNextAvailableSlot()
            if found:
                suggestion = (
                    f" Proxima disponibilidad: {nextStart.date().isoformat()} "
                    f"{nextStart.time().strftime('%H:%M')} - {nextEnd.time().strftime('%H:%M')}"
                )
                return (
                    False,
                    availabilityMessage + suggestion,
                    {"start": nextStart, "end": nextEnd},
                )
            return False, availabilityMessage, None

        scheduleRecords = loadSchedule()
        self.id = self.id or nextEventId(scheduleRecords)
        scheduleRecords.append(self.toRecord(self.startDateTime, self.endDateTime))
        saveSchedule(scheduleRecords)
        return True, f"Evento guardado con ID {self.id}.", None

    def validateAndAddRecurring(self) -> tuple[bool, str, dict | None]:
        if not self.reps or not self.step:
            return False, "Faltan repeticiones o intervalo para el evento recurrente.", None

        startDateTime = self.startDateTime
        endDateTime = self.endDateTime
        if not startDateTime or not endDateTime:
            return False, "Faltan fechas u horas para el evento recurrente.", None

        duration = endDateTime - startDateTime
        if duration.total_seconds() <= 0:
            return False, "Duracion invalida para el evento recurrente.", None

        lastEnd = startDateTime + timedelta(days=self.step * (self.reps - 1)) + duration
        if lastEnd > datetime.now() + timedelta(days=60):
            return False, "Las repeticiones exceden el limite de 2 meses.", None

        scheduleRecords = loadSchedule()
        tempRecords = list(scheduleRecords)
        failures = []

        for i in range(self.reps):
            offset = timedelta(days=self.step * i)
            instanceStart = startDateTime + offset
            instanceEnd = instanceStart + duration
            available, availabilityMessage = self.validateAvailability(
                tempRecords, instanceStart, instanceEnd
            )
            if not available:
                failures.append(
                    f"Repeticion {i + 1} ({instanceStart.date().isoformat()}): {availabilityMessage}"
                )
            else:
                tempRecords.append(self.toRecord(instanceStart, instanceEnd))

        if failures:
            found, _, nextStart, nextEnd = self.findNextAvailableSeriesStart()
            if found:
                suggestion = (
                    f" Proxima disponibilidad de la serie: {nextStart.date().isoformat()} "
                    f"{nextStart.time().strftime('%H:%M')} - {nextEnd.time().strftime('%H:%M')}"
                )
                return (
                    False,
                    " ".join(failures) + suggestion,
                    {"start": nextStart, "end": nextEnd},
                )
            return False, " ".join(failures), None

        updatedRecords = list(scheduleRecords)
        for i in range(self.reps):
            offset = timedelta(days=self.step * i)
            instanceStart = startDateTime + offset
            instanceEnd = instanceStart + duration
            self.id = nextEventId(updatedRecords)
            updatedRecords.append(self.toRecord(instanceStart, instanceEnd))

        saveSchedule(updatedRecords)
        return True, "Evento recurrente guardado con exito.", None

    def validateDateTimeLogic(self) -> tuple[bool, str]:
        if self.durationInHours < 0:
            return False, "El evento culmina antes de iniciar."
        elif self.durationInHours == 0:
            return False, "El evento inicia y culmina al instante."
        return True, "DateTime logic validation passed."

    def validateDateTimeVeracity(self) -> tuple[bool, str]:
        if self.validateDateTimeLogic()[0] and self.endDateTime < now:
            return False, "El evento inicia y culmina en el pasado."
        elif self.validateDateTimeLogic()[0] and self.startDateTime < now:
            return False, "El evento inicia en el pasado."
        else:
            return True, "DateTime veracity validation passed."

    def validateDurationInHours(self) -> tuple[bool, str]:
        if self.subType and self.shipSize:
            minimumAllowed = restrictions[self.subType]["shipSize"][self.shipSize][
                "durationInHours"
            ]["min"]
            maximumAllowed = restrictions[self.subType]["shipSize"][self.shipSize][
                "durationInHours"
            ]["max"]
        else:
            minimumAllowed = restrictions[self.subType]["durationInHours"]["min"]
            maximumAllowed = restrictions[self.subType]["durationInHours"]["max"]
        if self.durationInHours < minimumAllowed:
            return False, (
                f"El {self.subType.lower()} "
                + (
                    f"de una embarcación {self.shipSize.lower()} por el canal "
                    if self.shipSize
                    else ""
                )
                + f"toma como mínimo {minimumAllowed} horas."
            )
        elif self.durationInHours > maximumAllowed:
            return False, (
                f"El {self.subType.lower()} "
                + (
                    f"de una embarcación {self.shipSize.lower()} por el canal "
                    if self.shipSize
                    else ""
                )
                + f"toma a lo sumo {maximumAllowed} horas."
            )
        return True, "Duration validation passed."

    def validateRequiredQuantities(self) -> tuple[bool, str]:
        errors = []
        if self.subType and self.shipSize:
            requiredJrPilots = restrictions[self.subType]["shipSize"][self.shipSize][
                "jrPilots"
            ]
            requiredSrPilots = restrictions[self.subType]["shipSize"][self.shipSize][
                "srPilots"
            ]
            requiredMaintTeams = restrictions[self.subType]["shipSize"][self.shipSize][
                "maintTeams"
            ]
            requiredTugboats = restrictions[self.subType]["shipSize"][self.shipSize][
                "tugboats"
            ]
            if (
                requiredJrPilots[0] == "exactly"
                and self.jrPilots != requiredJrPilots[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} de una embarcación {self.shipSize.lower()} "
                    + f"requiere exactamente {requiredJrPilots[1]} piloto(s) junior.",
                )
            elif (
                requiredJrPilots[0] == "atLeast" and self.jrPilots < requiredJrPilots[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} de una embarcación {self.shipSize.lower()} "
                    + f"requiere al menos {requiredJrPilots[1]} piloto(s) junior.",
                )
            if (
                requiredSrPilots[0] == "exactly"
                and self.srPilots != requiredSrPilots[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} de una embarcación {self.shipSize.lower()} "
                    + f"requiere exactamente {requiredSrPilots[1]} piloto(s) senior.",
                )
            elif (
                requiredSrPilots[0] == "atLeast" and self.srPilots < requiredSrPilots[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} de una embarcación {self.shipSize.lower()} "
                    + f"requiere al menos {requiredSrPilots[1]} piloto(s) senior.",
                )
            if (
                requiredMaintTeams[0] == "exactly"
                and self.maintTeams != requiredMaintTeams[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} de una embarcación {self.shipSize.lower()} "
                    + f"requiere exactamente {requiredMaintTeams[1]} equipo(s) de mantenimiento.",
                )
            elif (
                requiredMaintTeams[0] == "atLeast"
                and self.maintTeams < requiredMaintTeams[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} de una embarcación {self.shipSize.lower()} "
                    + f"requiere al menos {requiredMaintTeams[1]} equipo(s) de mantenimiento.",
                )
            if (
                requiredTugboats[0] == "exactly"
                and self.tugboats != requiredTugboats[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} de una embarcación {self.shipSize.lower()} "
                    + f"requiere exactamente {requiredTugboats[1]} remolcador(es).",
                )
            elif (
                requiredTugboats[0] == "atLeast" and self.tugboats < requiredTugboats[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} de una embarcación {self.shipSize.lower()} "
                    + f"requiere al menos {requiredTugboats[1]} remolcador(es).",
                )
            if len(errors) > 0:
                return False, " ".join(errors)
            return True, "Required quantities validation passed."
        else:
            requiredJrPilots = restrictions[self.subType]["jrPilots"]
            requiredSrPilots = restrictions[self.subType]["srPilots"]
            requiredMaintTeams = restrictions[self.subType]["maintTeams"]
            requiredTugboats = restrictions[self.subType]["tugboats"]
            if (
                requiredJrPilots[0] == "exactly"
                and self.jrPilots != requiredJrPilots[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} requiere exactamente {requiredJrPilots[1]} piloto(s) junior.",
                )
            elif (
                requiredJrPilots[0] == "atLeast" and self.jrPilots < requiredJrPilots[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} requiere al menos {requiredJrPilots[1]} piloto(s) junior.",
                )
            if (
                requiredSrPilots[0] == "exactly"
                and self.srPilots != requiredSrPilots[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} requiere exactamente {requiredSrPilots[1]} piloto(s) senior.",
                )
            elif (
                requiredSrPilots[0] == "atLeast" and self.srPilots < requiredSrPilots[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} requiere al menos {requiredSrPilots[1]} piloto(s) senior.",
                )
            if (
                requiredMaintTeams[0] == "exactly"
                and self.maintTeams != requiredMaintTeams[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} requiere exactamente {requiredMaintTeams[1]} equipo(s) de mantenimiento.",
                )
            elif (
                requiredMaintTeams[0] == "atLeast"
                and self.maintTeams < requiredMaintTeams[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} requiere al menos {requiredMaintTeams[1]} equipo(s) de mantenimiento.",
                )
            if (
                requiredTugboats[0] == "exactly"
                and self.tugboats != requiredTugboats[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} requiere exactamente {requiredTugboats[1]} remolcador(es).",
                )
            elif (
                requiredTugboats[0] == "atLeast" and self.tugboats < requiredTugboats[1]
            ):
                errors.append(
                    f"El {self.subType.lower()} requiere al menos {requiredTugboats[1]} remolcador(es).",
                )
            if len(errors) > 0:
                return False, " ".join(errors)
            return True, "Required quantities validation passed."

    def validateLocksRelationship(self) -> tuple[bool, str]:
        if self.subType and self.shipSize:
            locksSegments = []
            a = []
            for lock in resources["locks"]:
                if str(lock)[0] not in locksSegments:
                    locksSegments.append(str(lock)[0])
            for segment in locksSegments:
                for lock in self.locks:
                    a.append(str(lock)[0])
                if segment not in a:
                    return (
                        False,
                        f"El {self.subType.lower()} de una embarcación cualquiera requiere pasar por todas las esclusas de una misma línea del canal.",
                    )
            for i in range(len(self.locks)):
                for j in range(i + 1, len(self.locks)):
                    if str(self.locks[i])[1] != str(self.locks[j])[1]:
                        return (
                            False,
                            f"El {self.subType.lower()} de una embarcación cualquiera por el canal requiere que todas las esclusas por las que pasa pertenezcan a la misma línea del canal.",
                        )
            return True, "Locks relationship validation passed."
        elif not self.locks or len(self.locks) != 1:
            return (
                False,
                "El mantenimiento a una esclusa requiere una y solo una esclusa.",
            )
        return True, "Locks relationship validation passed."

    def validateEvent(self) -> tuple[bool, str]:
        validations = [
            self.validateDateTimeLogic,
            self.validateDateTimeVeracity,
            self.validateDurationInHours,
            self.validateRequiredQuantities,
            self.validateLocksRelationship,
        ]
        for validation in validations:
            isValid, message = validation()
            if not isValid:
                return False, message
        return True, "All validations passed."
