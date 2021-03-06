import pygame

import math

import my_globals as g
import battle_ai as bai
import battle_command as cmd
import field_command as fcmd

class Hero (object):
    dic = {}

    def __init__(self, index, attr = {}, resD = {}, resS = {}, skillType = None, weaponType = None, commands = [], skills = [], equip = {}, spr = None, size = 32, icon = None):
        self.index = ""

        self.attr = attr
        if not self.attr:
            self.attr = {}
            self.attr["name"] = "???"
            self.attr["lvl"] = 1
            self.attr["exp"] = 0
            self.attr["str"] = 5
            self.attr["end"] = 5
            self.attr["wis"] = 5
            self.attr["spr"] = 5
            self.attr["agi"] = 5
            self.attr["lck"] = 5

        self.attr["hp"] = self.baseMaxHP
        self.attr["sp"] = self.baseMaxSP

        self.exp = 0

        self.resD = resD
        for dmgType in range(0, g.DamageType.SIZE):
            if not dmgType in resD:
                self.resD[dmgType] = 0

        self.resS = resS
        for status in range(0, g.BattlerStatus.SIZE):
            if not status in resS:
                self.resS[status] = 0

        self.weaponType = weaponType
        self.skillType = skillType
        self.commands = commands
        self.skills = skills

        self.attrMods = {}

        if not equip:
            self.equip = {}
            self.equip["wpn"] = None
            self.equip["acc1"] = None
            self.equip["acc2"] = None
        else:
            self.equip = equip

        self.size = size
        self.spr = spr
        if not self.spr:
            self.spr = "spr/battle/hero-asa.png"

        self.icon = icon
        if not self.icon:
            self.icon = pygame.image.load("spr/battle/hero-asa.png")

        Hero.dic[index] = self

    @property
    def baseMaxHP (self):
        return min(50 + self.attr["end"] * math.ceil(self.attr["lvl"] // 2), g.HERO_MAX_HP)

    @property
    def baseMaxSP (self):
        return min(self.attr["wis"] + self.attr["spr"] + self.attr["lvl"], g.HERO_MAX_SP)

    @property
    def baseHit(self):
        return min(90 + self.attr["agi"] - self.attr["str"], g.HERO_MAX_RATE)

    @property
    def baseEva(self):
        return min(1 + self.attr["agi"] - self.attr["end"], g.HERO_MAX_RATE)

    @property
    def baseAtk(self):
        return min(self.attr["str"] + self.attr["lvl"], g.HERO_MAX_STAT)

    @property
    def baseDef(self):
        return min(self.attr["end"] + self.attr["lvl"], g.HERO_MAX_STAT)

    @property
    def baseMAtk(self):
        return min(self.attr["wis"] + self.attr["lvl"], g.HERO_MAX_STAT)

    @property
    def baseMDef(self):
        return min(self.attr["spr"] + self.attr["lvl"], g.HERO_MAX_STAT)

    @property
    def totalMaxHP (self):
        total = self.baseMaxHP
        for item in self.equip:
            if self.equip[item].name != "":
                if "maxHP" in self.equip[item].attr:
                    total += self.equip[item].attr["maxHP"]
        return total

    @property
    def totalMaxSP(self):
        total = self.baseMaxSP
        for item in self.equip:
            if self.equip[item].name != "":
                if "maxSP" in self.equip[item].attr:
                    total += self.equip[item].attr["maxSP"]
        return total

    @property
    def totalAtk(self):
        total = self.baseAtk
        for item in self.equip:
            if self.equip[item].name != "":
                if "atk" in self.equip[item].attr:
                    total += self.equip[item].attr["atk"]
        return total

    @property
    def totalDef(self):
        total = self.baseDef
        for item in self.equip:
            if self.equip[item].name != "":
                if "def" in self.equip[item].attr:
                    total += self.equip[item].attr["def"]
        return total

    @property
    def totalMAtk(self):
        total = self.baseMAtk
        for item in self.equip:
            if self.equip[item].name != "":
                if "matk" in self.equip[item].attr:
                    total += self.equip[item].attr["matk"]
        return total

    @property
    def totalMDef(self):
        total = self.baseMDef
        for item in self.equip:
            if self.equip[item].name != "":
                if "mdef" in self.equip[item].attr:
                    total += self.equip[item].attr["mdef"]
        return total

    @property
    def totalAgi(self):
        total = self.attr['agi']
        for item in self.equip:
            if self.equip[item].name != "":
                if "agi" in self.equip[item].attr:
                    total += self.equip[item].attr["agi"]
        return total

    @property
    def totalLck(self):
        total = self.attr['lck']
        for item in self.equip:
            if self.equip[item].name != "":
                if "lck" in self.equip[item].attr:
                    total += self.equip[item].attr["lck"]
        return total

    @property
    def totalHit(self):
        total = self.baseHit
        for item in self.equip:
            if self.equip[item].name != "":
                if "hit" in self.equip[item].attr:
                    total += self.equip[item].attr["hit"]
        return total

    @property
    def totalEva(self):
        total = self.baseEva
        for item in self.equip:
            if self.equip[item].name != "":
                if "eva" in self.equip[item].attr:
                    total += self.equip[item].attr["eva"]
        return total

    @property
    def isDead(self):
        return self.attr['hp'] < 1

    def total_resD(self, damageType):
        total = self.resD[damageType]
        for item in self.equip:
            if self.equip[item].name != "":
                if damageType in self.equip[item].resD:
                    total += self.equip[item].resD[damageType]
        return total

    def total_resS(self, status):
        total = self.resS[status]
        for item in self.equip:
            if self.equip[item].name != "":
                if status in self.equip[item].resS:
                    total += self.equip[item].resS[status]
        return total

    def knows_skill(self, skillToCheck):
        for skill in self.skills:
            if skillToCheck.name == skill.name:
                return True
        return False

    def heal_hp(self, value, damageType):

        value -= math.floor(value * self.resD[damageType])

        self.attr['hp'] +=  value
        self.check_hp()

    def check_hp(self):
        if self.attr['hp'] > self.baseMaxHP:
            self.attr['hp'] = self.baseMaxHP

    def revive(self, hpPercent):
        self.attr['hp'] = max(1, math.floor(self.baseMaxHP * hpPercent / 100))

class Monster (object):
    dic = {}

    def __init__(self, index, attr = {}, resD = {}, resS = {}, drops = [], steals = [], spr = None, size = 16, icon = None):
        self.ai = bai.dic[index]

        self.attr = attr
        if not self.attr:
            self.attr = {}
            self.attr["name"] = "???"
            self.attr["lvl"] = 1
            self.attr["hp"] = 10
            self.attr["sp"] = 10
            self.attr["atk"] = 6
            self.attr["def"] = 6
            self.attr["matk"] = 6
            self.attr["mdef"] = 6
            self.attr["hit"] = 95
            self.attr["eva"] = 3
            self.attr["agi"] = 5
            self.attr["lck"] = 3
            self.attr['exp'] = 1
            self.attr['gold'] = 1

        self.resD = resD
        for dmgType in range(0, g.DamageType.SIZE):
            if not dmgType in resD:
                self.resD[dmgType] = 0
        self.resS = resS
        for status in range(0, g.BattlerStatus.SIZE):
            if not status in resS:
                self.resS[status] = 0

        self.drops = drops
        self.steals = steals

        self.size = size
        self.spr = spr
        if not self.spr:
            self.spr = "spr/battle/mon-slime.png"

        self.icon = icon
        if not self.icon:
            self.icon = pygame.image.load("spr/battle/mon-slime.png")

        Monster.dic[index] = self

class InvItem (object):
    dic = {}

    def __init__(self, index, desc, icon, itemType = g.ItemType.NONE, limit = 99, useAction = None, battleAction = None, sortPriority = {}):
        self.index = -len(InvItem.dic)
        self.name = index
        self.desc = desc
        self.icon = icon
        self.itemType = itemType
        self.limit = limit

        self.useAction = useAction
        if useAction != None:
            self.usableField = True
        else:
            self.usableField = False

        self.battleAction = battleAction
        if battleAction != None:
            self.usableBattle = True
        else:
            self.usableBattle = False

        self.sortPriority = sortPriority
        if not self.sortPriority:
            self.sortPriority["field"] = 99
            self.sortPriority["battle"] = 99
            self.sortPriority["recovery"] = 99
            self.sortPriority["damage"] = 99

        InvItem.dic[index] = self

    def __lt__(self, other):
        return self.index > other.index


class Equip (InvItem):

   def __init__(self, index, desc, icon, itemType = g.ItemType.ACC, dmgType = g.DamageType.NONE, attr = {}, resD = {}, resS = {}, onAttack = None, onHit = None, limit = 99, useAction = None, battleAction = None, sortPriority = {}):
        InvItem.__init__(self, index, desc, icon, itemType, limit, useAction, battleAction, sortPriority)

        if itemType != g.ItemType.ACC and dmgType == None:
            self.dmgType = g.DamageType.PHYS
        else:
            self.dmgType =g.DamageType.NONE

        self.attr = attr
        self.resD = resD
        self.resS = resS

        self.onAttack = onAttack
        self.onHit = onHit
        self.dmgType = dmgType


class Skill (object):
    dic = {}

    def __init__(self, index, desc, icon, skillType, spCost, meterReq, useAction, battleAction):
        self.name = index
        self.desc = desc
        self.icon = icon
        self.skillType = skillType
        self.spCost = spCost
        self.meterReq = meterReq
        self.useAction = useAction
        if (useAction != None):
            self.usableField = True
        else:
            self.usableField = False
        self.battleAction = battleAction
        if (battleAction != None):
            self.usableBattle = True
        else:
            self.usableBattle = False

        Skill.dic[index] = self

    def check_cost(user, skill):
        if user.attr['sp'] >= skill.spCost:
            if skill.skillType != g.SkillType.MUSIC:
                if g.meter[skill.skillType] >= skill.meterReq:
                    return True
            else:
                if len(g.meter[skill.skillType]) >= skill.meterReq:
                    return True
        return False

class Animagus (object):
    dic = {}

    def __init__(self, name, baseExp, growth, skills):
        self.name = name
        self.level = 1
        self.baseExp =  baseExp
        self.levelUpAt = self.expToNext
        self.exp = 0
        self.growth = growth
        self.skills = skills
        self.skillsTaught = []

        if not self in Animagus.dic:
            Animagus.dic[name] = self

    @property
    def expToNext(self):
        return math.ceil(pow(self.baseExp, 1 + (self.level / 7)))


def create_data():
    #########
    ##ITEMS##
    #########
    name = ""
    desc = ""
    icon = ""
    itemType = g.ItemType.NONE
    limit = 1
    useAction = None
    battleAction = None
    sortPriority = {}
    sortPriority["field"] = 0
    sortPriority["battle"] = 0
    sortPriority["recovery"] = 0
    sortPriority["damage"] = 0

    InvItem(name, desc, icon, itemType, limit, useAction, battleAction, sortPriority)

    name = "Potion"
    desc = "Restores 50 HP"
    icon = "&iPotion"
    itemType = g.ItemType.CONSUMABLE
    limit = 99
    useAction = fcmd.Potion
    battleAction = cmd.Potion
    sortPriority = {}
    sortPriority["field"] = 0
    sortPriority["battle"] = 0
    sortPriority["recovery"] = 0
    sortPriority["damage"] = 99

    InvItem(name, desc, icon, itemType, limit, useAction, battleAction, sortPriority)

    name = "Revive"
    desc = "Restores life to a fallen ally"
    icon = "&iSalts"
    itemType = g.ItemType.CONSUMABLE
    limit = 99
    useAction = fcmd.Revive
    battleAction = cmd.Revive
    sortPriority = {}
    sortPriority["field"] = 10
    sortPriority["battle"] = 10
    sortPriority["recovery"] = 10
    sortPriority["damage"] = 99

    InvItem(name, desc, icon, itemType, limit, useAction, battleAction, sortPriority)

    name = "Antidote"
    desc = "Cures poison"
    icon = "&iAntidote"
    itemType = g.ItemType.CONSUMABLE
    limit = 99
    useAction = None
    battleAction = cmd.Antidote
    sortPriority = {}
    sortPriority["field"] = 11
    sortPriority["battle"] = 11
    sortPriority["recovery"] = 11
    sortPriority["damage"] = 99

    InvItem(name, desc, icon, itemType, limit, useAction, battleAction, sortPriority)

    name = "Royal Blade"
    desc = "A blade imbued with the royal blood"
    icon = "&iSword"
    equipType = g.ItemType.SWORD
    attr = {}
    attr["atk"] = 5
    dmgType = g.DamageType.PHYS
    resD = {}
    resS = {}
    onAttack = None
    onHit = None
    limit = 20
    useAction = None
    battleAction = None
    sortPriority = {}

    Equip(name, desc, icon, equipType, dmgType, attr, resD, resS, onAttack, onHit, limit, useAction, battleAction, sortPriority)

    name = "Resobell"
    desc = "An exceptionally resonant bell"
    icon = "&iBell"
    equipType = g.ItemType.BELL
    attr = {}
    attr["atk"] = 1
    attr["matk"] = 3
    dmgType = g.DamageType.PHYS
    resD = {}
    resS = {}
    onAttack = None
    onHit = None
    limit = 20
    useAction = None
    battleAction = None
    sortPriority = {}

    Equip(name, desc, icon, equipType, dmgType, attr, resD, resS, onAttack, onHit, limit, useAction, battleAction, sortPriority)

    name = "Fur Gloves"
    desc = "They're warm, but not particularly intimidating"
    icon = "&iGlove"
    equipType = g.ItemType.BELL
    attr = {}
    attr["atk"] = 2
    dmgType = g.DamageType.PHYS
    resD = {}
    resS = {}
    onAttack = None
    onHit = None
    limit = 20
    useAction = None
    battleAction = None
    sortPriority = {}

    Equip(name, desc, icon, equipType, dmgType, attr, resD, resS, onAttack, onHit, limit, useAction, battleAction, sortPriority)

    name = "Stone Ring"
    desc = "A heavy ring carved from solid stone, worn smooth by wear"
    icon = "&iRing"
    equipType = g.ItemType.ACC
    attr = {}
    attr["def"] = 1
    attr['agi'] = -1
    dmgType = None
    resD = {}
    resD[g.DamageType.EARTH] = 0.10
    resS = {}
    onAttack = None
    onHit = None
    limit = 99
    useAction = None
    battleAction = None
    sortPriority = {}

    Equip(name, desc, icon, equipType, dmgType, attr, resD, resS, onAttack, onHit, limit, useAction, battleAction, sortPriority)

    name = "Crystal Shard"
    desc = "A fragment of broken crystal that glows dimly"
    icon = "&iGem"
    equipType = g.ItemType.ACC
    attr = {}
    attr["maxSP"] = 5
    dmgType = None
    resD = {}
    resS = {}
    onAttack = None
    onHit = None
    limit = 99
    useAction = None
    battleAction = None
    sortPriority = {}

    Equip(name, desc, icon, equipType, dmgType, attr, resD, resS, onAttack, onHit, limit, useAction, battleAction, sortPriority)

    name = "Pepper Charm"
    desc = "A pulsing red gem, hot to the touch"
    icon = "&iCharm"
    equipType = g.ItemType.ACC
    attr = {}
    attr["agi"] = 2
    dmgType = None
    resD = {}
    resD[g.DamageType.FIRE] = 0.10
    resD[g.DamageType.COLD] = -0.10
    resS = {}
    onAttack = None
    onHit = None
    limit = 99
    useAction = None
    battleAction = None
    sortPriority = {}

    Equip(name, desc, icon, equipType, dmgType, attr, resD, resS, onAttack, onHit, limit, useAction, battleAction, sortPriority)

    ################
    ##BLOOD SKILLS##
    ################
    name = "Sacrifice"
    desc = "Lower Luxe's max HP to recover the party's SP"
    icon = "&iBlood"
    skillType = g.SkillType.BLOOD
    spCost = 0
    meterReq = 0
    useAction = None
    battleAction = cmd.Sacrifice

    Skill(name, desc, icon, skillType, spCost, meterReq, useAction, battleAction)

    name = "Blood Slash"
    desc = "Deals NULL damage to an enemy that scales with the blood meter"
    icon = "&iBlood"
    skillType = g.SkillType.BLOOD
    spCost = 15
    meterReq = 0
    useAction = None
    battleAction = cmd.BloodSlash

    Skill(name, desc, icon, skillType, spCost, meterReq, useAction, battleAction)

    ################
    ##MUSIC SKILLS##
    ################

    name = "Finale"
    desc = "Empty the music meter and resolve the melody"
    icon = "&iMusic"
    skillType = g.SkillType.MUSIC
    spCost = 0
    meterReq = 1
    useAction = None
    battleAction = cmd.Finale

    Skill(name, desc, icon, skillType, spCost, meterReq, useAction, battleAction)

    name = "Staccato"
    desc = "Deals ELEC damage to an enemy"
    icon = "&iNote-ylw"
    skillType = g.SkillType.MUSIC
    spCost = 10
    meterReq = 0
    useAction = None
    battleAction = cmd.Staccato

    Skill(name, desc, icon, skillType, spCost, meterReq, useAction, battleAction)

    name = "Adagio"
    desc = "Restores some HP to an ally"
    icon = "&iNote-wht"
    skillType = g.SkillType.MUSIC
    spCost = 15
    meterReq = 0
    useAction = fcmd.Adagio
    battleAction = cmd.Adagio

    Skill(name, desc, icon, skillType, spCost, meterReq, useAction, battleAction)

    ################
    ##MOON SKILLS##
    ################

    name = "Transform"
    desc = "Change's Asa physical form and alters attributes relative to the strength of the moon"
    icon = "&iMoon"
    skillType = g.SkillType.MOON
    spCost = 0
    meterReq = 1
    useAction = None
    battleAction = cmd.Transform

    Skill(name, desc, icon, skillType, spCost, meterReq, useAction, battleAction)

    name = "Double Cut"
    desc = "Perform two normal attacks"
    icon = "&iMoon"

    skillType = g.SkillType.MOON
    spCost = 12
    meterReq = 1
    useAction = None
    battleAction = cmd.DoubleCut

    Skill(name, desc, icon, skillType, spCost, meterReq, useAction, battleAction)

    ################
    ##ENEMY SKILLS##
    ################
    name = "Toxic"
    desc = "Small chance to inflict Poison"
    icon = ""
    skillType = g.SkillType.ENEMY
    spCost = 10
    meterReq = 0
    useAction = None
    battleAction = cmd.Toxic

    Skill(name, desc, icon, skillType, spCost, meterReq, useAction, battleAction)

    name = "Symbioism"
    desc = "Restores some HP to an ally"
    icon = ""
    skillType = g.SkillType.ENEMY
    spCost = 10
    meterReq = 0
    useAction = None
    battleAction = cmd.Symbioism

    Skill(name, desc, icon, skillType, spCost, meterReq, useAction, battleAction)

    ##########
    ##HEROES##
    ##########
    equip = {}
    equip["wpn"] = InvItem.dic["Royal Blade"]
    equip["acc1"] = InvItem.dic["Crystal Shard"]
    equip["acc2"] = InvItem.dic[""]

    attr = {}
    attr["name"] = "Luxe"
    attr["title"] = "The Exiled King"
    attr["lvl"] = 5
    attr["exp"] = 0
    attr["str"] = 10
    attr["end"] = 10
    attr["wis"] = 9
    attr["spr"] = 7
    attr["agi"] = 12
    attr["lck"] = 11

    resD = {}
    resD[g.DamageType.FIRE] = .5
    resD[g.DamageType.COLD] = -.5
    resS = {}
    weaponType = g.ItemType.SWORD
    skillType = g.SkillType.BLOOD
    commands = []
    commands.append(cmd.Attack)
    commands.append(cmd.UseSkill)
    commands.append(cmd.UseItem)
    commands.append(cmd.Defend)
    skills = [Skill.dic["Sacrifice"]]

    spr = "spr/battle/heroes/luxe.png"
    size = 48
    icon = pygame.image.load("spr/battle/icons/luxe.png")

    Hero(attr["name"], attr, resD, resS, skillType, weaponType, commands, skills, equip, spr, size, icon)

    equip = {}
    equip["wpn"] = InvItem.dic["Resobell"]
    equip["acc1"] = InvItem.dic["Stone Ring"]
    equip["acc2"] = InvItem.dic[""]
    attr = {}
    attr["name"] = "Elle"
    attr["title"] = "Royal Vibramancer"
    attr["lvl"] = 5
    attr["exp"] = 0
    attr["str"] = 7
    attr["end"] = 8
    attr["wis"] = 12
    attr["spr"] = 11
    attr["agi"] = 10
    attr["lck"] = 7

    resD = {}
    resD[g.DamageType.ELEC] = .5
    resD[g.DamageType.EARTH] = -.5
    resS = {}
    weaponType = g.ItemType.BELL
    skillType = g.SkillType.MUSIC
    commands = []
    commands.append(cmd.Attack)
    commands.append(cmd.UseSkill)
    commands.append(cmd.UseItem)
    commands.append(cmd.Defend)
    skills = [Skill.dic["Finale"]]

    spr = "spr/battle/heroes/elle.png"
    size = 48
    icon = pygame.image.load("spr/battle/icons/elle.png")

    Hero(attr["name"], attr, resD, resS, skillType, weaponType, commands, skills, equip, spr, size, icon)

    equip = {}
    equip["wpn"] = InvItem.dic["Fur Gloves"]
    equip["acc1"] = InvItem.dic["Pepper Charm"]
    equip["acc2"] = InvItem.dic[""]
    attr = {}
    attr["name"] = "Asa"
    attr["title"] = "The Last Wolf"
    attr["lvl"] = 5
    attr["exp"] = 0
    attr["str"] = 12
    attr["end"] = 12
    attr["wis"] = 7
    attr["spr"] = 6
    attr["agi"] = 7
    attr["lck"] = 5

    resD = {}
    resD[g.DamageType.DARK] = .5
    resD[g.DamageType.LIGHT] = -.5
    resS = {}
    weaponType = g.ItemType.GLOVE
    skillType = g.SkillType.MOON
    commands = []
    commands.append(cmd.Attack)
    commands.append(cmd.UseSkill)
    commands.append(cmd.UseItem)
    commands.append(cmd.Defend)
    skills = [Skill.dic["Transform"]]

    spr = "spr/battle/heroes/asa.png"
    size = 48
    icon = pygame.image.load("spr/battle/icons/asa.png")

    Hero(attr["name"], attr, resD, resS, skillType, weaponType, commands, skills, equip, spr, size, icon)

    ############
    ##MONSTERS##
    ############
    attr = {}
    attr["name"] = "Slime"
    attr["lvl"] = 3
    attr["hp"] = 20
    attr["sp"] = 10
    attr["atk"] = 15
    attr["def"] = 12
    attr["matk"] = 15
    attr["mdef"] = 15
    attr["hit"] = 95
    attr["eva"] = 5
    attr["agi"] = 10
    attr["lck"] = 5
    attr['exp'] = 5
    attr['gold'] = 5

    drops = []
    drops.append(("Potion", 25))

    steals = []

    resD = {}
    resS = {}

    spr = "spr/battle/monsters/slime.png"
    size = 32
    icon = pygame.image.load("spr/battle/icons/slime.png")

    Monster(attr["name"], attr, resD, resS, drops, steals, spr, size, icon)

    attr = {}
    attr["name"] = "Mold"
    attr["lvl"] = 5
    attr["hp"] = 35
    attr["sp"] = 20
    attr["atk"] = 20
    attr["def"] = 15
    attr["matk"] = 5
    attr["mdef"] = 5
    attr["hit"] = 95
    attr["eva"] = 5
    attr["agi"] = 13
    attr["lck"] = 5
    attr['exp'] = 7
    attr['gold'] = 6

    drops = []
    drops.append(("Revive", 10))
    drops.append(("Antidote", 25))

    steals = []

    resD = {}
    resD[g.DamageType.FIRE] = -1
    resS = {}

    spr = "spr/battle/monsters/mold.png"
    size = 32
    icon = pygame.image.load("spr/battle/icons/mold.png")

    Monster(attr["name"], attr, resD, resS, drops, steals, spr, size, icon)

    attr = {}
    attr["name"] = "Sapling"
    attr["lvl"] = 4
    attr["hp"] = 40
    attr["sp"] = 40
    attr["atk"] = 16
    attr["def"] = 12
    attr["matk"] = 30
    attr["mdef"] = 30
    attr["hit"] = 95
    attr["eva"] = 5
    attr["agi"] = 20
    attr["lck"] = 5
    attr['exp'] = 6
    attr['gold'] = 7

    drops = []
    drops.append(("Potion", 10))

    steals = []

    resD = {}
    resD[g.DamageType.FIRE] = -1
    resS = {}

    spr = "spr/battle/monsters/sapling.png"
    size = 32
    icon = pygame.image.load("spr/battle/icons/sapling.png")

    Monster(attr["name"], attr, resD, resS, drops, steals, spr, size, icon)

    attr = {}
    attr["name"] = "Beetle"
    attr["lvl"] = 2
    attr["hp"] = 20
    attr["sp"] = 10
    attr["atk"] = 18
    attr["def"] = 10
    attr["matk"] = 10
    attr["mdef"] = 10
    attr["hit"] = 100
    attr["eva"] = 25
    attr["agi"] = 20
    attr["lck"] = 20
    attr['exp'] = 5
    attr['gold'] = 5

    drops = []
    drops.append(("Revive", 5))

    steals = []

    resD = {}
    resS = {}

    spr = "spr/battle/monsters/beetle.png"
    size = 32
    icon = pygame.image.load("spr/battle/icons/beetle.png")

    Monster(attr["name"], attr, resD, resS, drops, steals, spr, size, icon)

    ###########
    ##ANIMAGI##
    ###########

    name = "Signis"
    baseExp = 15
    growth = {}
    skills = []
    skills.append(Skill.dic["Blood Slash"])
    skills.append(Skill.dic["Staccato"])
    skills.append(Skill.dic["Double Cut"])

    Animagus(name, baseExp, growth, skills)

    name = "Zeir"
    baseExp = 15
    growth = {}
    growth["end"] = 1
    skills = []

    Animagus(name, baseExp, growth, skills)

    name = "Luna"
    baseExp = 15
    growth = {}
    growth["str"] = 1
    skills = []

    Animagus(name, baseExp, growth, skills)

    name = "Felix"
    baseExp = 25
    growth = {}
    growth["spr"] = 1
    skills = []
    skills.append(Skill.dic["Adagio"])

    Animagus(name, baseExp, growth, skills)

create_data()
