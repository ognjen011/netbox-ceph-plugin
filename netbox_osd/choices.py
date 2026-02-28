from utilities.choices import ChoiceSet


class OSDTypeChoices(ChoiceSet):
    key = "CephOSD.osd_type"

    HDD = "hdd"
    SSD = "ssd"
    NVME = "nvme"

    CHOICES = [
        (HDD, "HDD", "blue"),
        (SSD, "SSD", "cyan"),
        (NVME, "NVMe", "purple"),
    ]


class OSDStatusChoices(ChoiceSet):
    key = "CephOSD.status"

    ACTIVE = "active"
    DOWN = "down"
    OUT = "out"
    DESTROYED = "destroyed"

    CHOICES = [
        (ACTIVE, "Active", "green"),
        (DOWN, "Down", "orange"),
        (OUT, "Out", "red"),
        (DESTROYED, "Destroyed", "gray"),
    ]


class NoteStatusChoices(ChoiceSet):
    """Status recorded on a status note — what state triggered the note."""

    DOWN = "down"
    OUT = "out"
    MAINTENANCE = "maintenance"
    RECOVERED = "recovered"
    OTHER = "other"

    CHOICES = [
        (DOWN, "Down", "orange"),
        (OUT, "Out", "red"),
        (MAINTENANCE, "Maintenance", "blue"),
        (RECOVERED, "Recovered", "green"),
        (OTHER, "Other", "gray"),
    ]
