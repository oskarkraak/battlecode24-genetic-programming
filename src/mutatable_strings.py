actions = [
    "if (rc.canBuild([$TRAP1], rc.getLocation().subtract([$DIR1]))) rc.build([$TRAP1], rc.getLocation().subtract([$DIR1]));",
]

ifs = [
    "if ([$INT1] > [$INT2]) [$ACTION1]",
    "if ([$INT1] == [$INT2]) [$ACTION1]",
    "if ([$INT1] != [$INT2]) [$ACTION1]",
    "if ([$INT1] > [$INT2]) [$IF1]",
    "if ([$INT1] == [$INT2]) [$IF1]",
    "if ([$INT1] != [$INT2]) [$IF1]"
]

directions = [
    "directions[0]",
    "directions[1]",
    "directions[2]",
    "directions[3]",
    "directions[4]",
    "directions[5]",
    "directions[6]",
    "directions[7]",
]

trap_types = [
    "TrapType.EXPLOSIVE",
    "TrapType.STUN",
    "TrapType.WATER",
]

ints = [
    "rc.getMapHeight()",
    "rc.getMapWidth()",
    "rc.getRoundNum()",
    "GameConstants.SETUP_ROUNDS",
]

#####
#####
#####

mapping = [
    ("INT", "int", ints),
    ("ACTION", "action", actions),
    ("IF", "if", ifs),
    ("DIR", "direction", directions),
    ("TRAP", "trap_type", trap_types),
]