from roles import (
    WolfRole, 
    VillagerRole, 
    SeerRole, 
    WitchRole, 
    HunterRole, 
    IdiotRole
)



ROLE_MAP = {
    "Wolf": WolfRole,
    "Villager": VillagerRole,
    "Seer": SeerRole,
    "Witch": WitchRole,
    "Hunter": HunterRole,
    "Idiot": IdiotRole,
}

class Character:
    def __init__(self, role_name, player_obj):
        self.role_name = role_name
        self.player = player_obj
        self.role = ROLE_MAP[role_name]()