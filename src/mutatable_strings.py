actions = [
    # Movement
    "if (rc.canMove([$DIR1])) rc.move([$DIR1]);"

    # Fighting
    "if (rc.canAttack([$LOC_RAD_FOUR1])) rc.attack([$LOC_RAD_FOUR1]);",
    "if (rc.canHeal([$LOC_RAD_FOUR1])) rc.heal([$LOC_RAD_FOUR1]);",

    # Building
    "if (rc.canBuild([$TRAP1], [$LOC_RAD_TWO1])) rc.build([$TRAP1], [$LOC_RAD_TWO1]);",
    "if (rc.canDig([$LOC_RAD_TWO1])) rc.dig([$LOC_RAD_TWO1]);",
    "if (rc.canFill([$LOC_RAD_TWO1])) rc.fill([$LOC_RAD_TWO1]);",

    # Flags
    "tryPickupFlag(rc);"

    # Upgrades
    # TODO
]

locations_radius_two = [
    "rc.getLocation().translate([$INTTWO1], [$INTTWO2])"
]

locations_radius_four = [
    "rc.getLocation().translate([$INTFOUR1], [$INTFOUR2])"
]

inttwo = range(-2, 2)

intfour = range(-4, 4)

ifs = [
    # Ints
    "if ([$INT1] > [$INT2]) [$ACTION1]",
    "if ([$INT1] == [$INT2]) [$ACTION1]",
    "if ([$INT1] != [$INT2]) [$ACTION1]",
    "if ([$INT1] > [$INT2]) [$IF1]",
    "if ([$INT1] == [$INT2]) [$IF1]",
    "if ([$INT1] != [$INT2]) [$IF1]",
    # Bools
    "if ([$BOOL1]) [$ACTION1]",
    "if ([$BOOL1]) [$IF1]",
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

bools = [
    "rc.hasFlag()"
]

ints = [
    # Map
    "rc.getMapHeight()",
    "rc.getMapWidth()",
    # Rounds
    "rc.getRoundNum()",
    "GameConstants.SETUP_ROUNDS",
    # Crumbs
    "rc.getCrumbs()",
    # Fighting
    "rc.getHealth()",
]

#####
#####
#####

mapping = [
    ("INT", "int", ints),
    ("BOOL", "bool", bools),
    ("ACTION", "action", actions),
    ("INT_RAD_TWO", "int_rad_two", inttwo),
    ("INT_RAD_FOUR", "int_rad_four", intfour),
    ("IF", "if", ifs),
    ("DIR", "direction", directions),
    ("LOC_RAD_TWO", "LOC_RAD_TWO", locations_radius_two),
    ("LOC_RAD_FOUR", "LOC_RAD_FOUR", locations_radius_four),
    ("TRAP", "trap_type", trap_types),
]