from datetime import datetime
import pytz, os, collections, re
from win32 import win32gui, win32api, win32process
import win32.lib.win32con as win32con
import win32com.client
import pyautogui, random
from testtemp import *
import time

fight_started = False
boss_fight = False
fight_timer_start = 0

#################################################################
#################################################################
# Part of code from https://github.com/Yiyuan-Dong/AutoHS
#################################################################
#################################################################

# "D 04:23:18.0000001 GameState.DebugPrintPower() -     GameEntity EntityID=1"
GAME_STATE_PATTERN = re.compile(r"D [\d]{2}:[\d]{2}:[\d]{2}.[\d]{7} GameState.DebugPrint(Game|Power)\(\) - (.+)")

# "GameEntity EntityID=1"
GAME_ENTITY_PATTERN = re.compile(r" *GameEntity EntityID=(\d+)")

# "Player EntityID=2 PlayerID=1 GameAccountId=[hi=112233445566778899 lo=223344556]"
PLAYER_PATTERN = re.compile(r" *Player EntityID=(\d+) PlayerID=(\d+).*")

# "FULL_ENTITY - Creting ID=89 CardID=EX1_538t"
# "FULL_ENTITY - Creating ID=90 CardID="
FULL_ENTITY_PATTERN = re.compile(r" *FULL_ENTITY - Creating ID=(\d+) CardID=(.*)")

# "SHOW_ENTITY - Updating Entity=90 CardID=NEW1_033o"
# "SHOW_ENTITY - Updating Entity=[entityName=UNKNOWN ENTITY [cardType=INVALID] id=32 zone=DECK zonePos=0 cardId= player=1] CardID=VAN_EX1_539"
SHOW_ENTITY_PATTERN = re.compile(r" *SHOW_ENTITY - Updating Entity=(.*) CardID=(.*) *")

# CHANGE_ENTITY 比较罕见，主要对应“呱”等变形行为
# "CHANGE_ENTITY - Updating Entity=[entityName=凯恩·血蹄 id=37 zone=PLAY zonePos=3 cardId=VAN_EX1_110 player=2] CardID=hexfrog"
CHANGE_ENTITY_PATTERN = re.compile(r" *CHANGE_ENTITY - Updating Entity=(.*) CardID=(.*) *")

# "BLOCK_START BlockType=DEATHS Entity=GameEntity EffectCardId=System.Collections.Generic.List`1[System.String] EffectIndex=0 Target=0 SubOption=-1 "
BLOCK_START_PATTERN = re.compile(r" *BLOCK_START BlockType=([A-Z]+) Entity=(.*) EffectCardId=.*")

# "BLOCK_END"
BlOCK_END_PATTERN = re.compile(r" *BLOCK_END *")

# "PlayerID=1, PlayerName=UNKNOWN HUMAN PLAYER"
# "PlayerID=2, PlayerName=Example#51234"
PLAYER_ID_PATTERN = re.compile(r"PlayerID=(\d+), PlayerName=(.*)")

# "TAG_CHANGE Entity=GameEntity tag=NEXT_STEP value=FINAL_WRAPUP "
# "TAG_CHANGE Entity=Example#51234 tag=467 value=4 "
# "TAG_CHANGE Entity=[entityName=UNKNOWN ENTITY [cardType=INVALID] id=14 zone=DECK zonePos=0 cardId= player=1] tag=ZONE value=HAND "
TAG_CHANGE_PATTERN = re.compile(r" *TAG_CHANGE Entity=(.*) tag=(.*) value=(.*) ")

# "tag=ZONE value=DECK"
TAG_PATTERN = re.compile(r" *tag=(.*) value=(.*)")

class LogInfo:
    def __init__(self):
        self.log = []
    def append(self, info):
        self.log.append(info)
    @property
    def length(self):
        return len(self.log)

def dry_run():
    bounty_button = [450, 350]
    confirm_team_button = [840, 625]
    select_team_button = [1445, 895]

    click(select_team_button)
    time.sleep(10)
    click(bounty_button)
    click(select_team_button)
    time.sleep(10)
    click(select_team_button)
    click(confirm_team_button)
    time.sleep(10)
    click(select_team_button)

def log_reader_iter():
    logfilePath = 'C:/Program Files (x86)/Hearthstone/Logs/power.log'
    
    # print('expect to see this once only')
    while True:
        if not os.path.exists(logfilePath):
            print('waiting for log file to be created')
            time.sleep(1)
            # status = collections.defaultdict(dict)
            # start_game(status)
            # dry_run()
            continue

        with open(logfilePath, 'r', encoding='utf8') as f:             
            while True:
                logs = LogInfo()
                # print('created log container')
                while True:
                    line = f.readline()
                    if line == "":
                        break
                    else:
                        logs.append(line)
                yield logs

log_iter = log_reader_iter()



##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################
# ██    ██ ██████  ██████   █████  ████████ ███████     ███████ ████████  █████  ████████ ██    ██ ███████ 
# ██    ██ ██   ██ ██   ██ ██   ██    ██    ██          ██         ██    ██   ██    ██    ██    ██ ██      
# ██    ██ ██████  ██   ██ ███████    ██    █████       ███████    ██    ███████    ██    ██    ██ ███████ 
# ██    ██ ██      ██   ██ ██   ██    ██    ██               ██    ██    ██   ██    ██    ██    ██      ██ 
#  ██████  ██      ██████  ██   ██    ██    ███████     ███████    ██    ██   ██    ██     ██████  ███████ 
##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################



def updateStatus(status):
    # print('updating status')
    global fight_started, fight_timer_start
    global boss_fight
    
    logs = next(log_iter)
    log_len = logs.length
    # print('[logs_len = %d]' % log_len)
    tmpDict = collections.defaultdict(dict)

    if log_len > 0:
        curTime = datetime.now(pytz.timezone('America/Los_Angeles'))
        cur_time = curTime.strftime('_%H_%M_%S_%f_')
        cur_time = ''
        tempLog = 'tempLog/log' + cur_time + '.log'
        tempOp = 'tempLog/op.log'
        writer = open(tempLog, 'w', encoding='utf8')
        opwriter = open(tempOp, 'w', encoding='utf8')
        lastEntity = 'EMPTY_ENTITY'
        for line in logs.log:


            match_obj = GAME_STATE_PATTERN.match(line)

            if match_obj is None: continue
            # print(line)

            line_str = match_obj.group(2)

            if line_str == "CREATE_GAME":
                # status = collections.defaultdict(dict)
                status.clear()

            match_obj = TAG_CHANGE_PATTERN.match(line_str)
            if match_obj is not None:
                entity=fetch_entity_id(match_obj.group(1), status)
                lastEntity = 'Entity=' + entity
                # print('entity=' + entity)
                tag=match_obj.group(2)
                # if tag == 'LETTUCE_BOUNTY_BOSS': boss_fight = True
                value=match_obj.group(3)
                status[lastEntity][tag]=value
                tmpDict[lastEntity][tag]=value

            match_obj = TAG_PATTERN.match(line_str)
            if match_obj is not None:
                tag=match_obj.group(1)
                value=match_obj.group(2)
                status[lastEntity][tag] = value
                tmpDict[lastEntity][tag]=value


            match_obj = GAME_ENTITY_PATTERN.match(line_str)
            if match_obj is not None:
            #     return LineInfoContainer(
                    # LOG_LINE_GAME_ENTITY,
                entityID = match_obj.group(1)
                lastEntity = 'Entity=1'
                status[lastEntity]['EntityID'] = entityID
                tmpDict[lastEntity]['EntityID'] = entityID


            #     )

            match_obj = PLAYER_PATTERN.match(line_str)
            if match_obj is not None:
            #     return LineInfoContainer(
            #         LOG_LINE_PLAYER_ENTITY,
                entityID=match_obj.group(1)
                player=match_obj.group(2)
                lastEntity = 'Entity=' + entityID
                status[lastEntity]['EntityID'] = entityID
                status[lastEntity]['PlayerID'] = player
                tmpDict[lastEntity]['EntityID'] = entityID
                tmpDict[lastEntity]['PlayerID'] = player

            #     )

            match_obj = FULL_ENTITY_PATTERN.match(line_str)
            if match_obj is not None:
                # return LineInfoContainer(
                #     LOG_LINE_FULL_ENTITY,
                entity=match_obj.group(1)
                card=match_obj.group(2)
                lastEntity = 'Entity=' + entity
                status[lastEntity]['CardID'] = card
                status[lastEntity]['CardID'] = card
                tmpDict[lastEntity]['CardID'] = card
                
                # )

            match_obj = SHOW_ENTITY_PATTERN.match(line_str)
            if match_obj is not None:
            #     return LineInfoContainer(
        #         LOG_LINE_SHOW_ENTITY,
                entity=fetch_entity_id(match_obj.group(1), status)
                lastEntity = 'Entity=' + entity
                    # card=match_obj.group(2)

            #     )

            match_obj = CHANGE_ENTITY_PATTERN.match(line_str)
            if match_obj is not None:
            #     return LineInfoContainer(
            #         LOG_LINE_CHANGE_ENTITY,
                entity=fetch_entity_id(match_obj.group(1), status)
                lastEntity = 'Entity=' + entity
            #         card=match_obj.group(2)
            #     )

            # match_obj = BLOCK_START_PATTERN.match(line_str)
            # if match_obj is not None:
            #     return LineInfoContainer(
            #         LOG_LINE_BLOCK_START,
            #         type=match_obj.group(1),
            #         card=match_obj.group(2)
            #     )

            # match_obj = BlOCK_END_PATTERN.match(line_str)
            # if match_obj is not None:
            #     return LineInfoContainer(
            #         LOG_LINE_BLOCK_END
            #     )

            # match_obj = PLAYER_ID_PATTERN.match(line_str)
            # if match_obj is not None:
            #     # return LineInfoContainer(
            #     #     LOG_LINE_PLAYER_ID,
            #         player=match_obj.group(1)
            #         name=match_obj.group(2)
            #         status[player]['PlayerName'] = name
                # )

            if "CREATE_GAME" in line_str:
                fight_started = True
                boss_fight = False
                fight_timer_start = parseTime(line)
            
            if "tag=STEP value=FINAL_GAMEOVER" in line_str:
                fight_started = False
            # boss_list = ['残暴的野猪人']
            # for boss in boss_list:
            #     if boss in line_str:
            #         # print('line=%s' % line)
            #         boss_fight = True
            if "GameState.DebugPrintPower() -     tag=LETTUCE_BOUNTY_BOSS value=1" in line:
                boss_fight = True
            
            writer.write(line)
        writer.close()
        
        # print('operations in this log=...')
        for item in tmpDict:
            opwriter.write(item)
            opwriter.write(str(tmpDict[item]))
        opwriter.close()


    

    # print('[fight_started=%s]' % str(fight_started))
    # print('[boss_fight=%s]' % str(boss_fight))
    return status

def parseTime(line):
    time_line = line[2:10]
    year = str(datetime.today().year)
    month = str(datetime.today().month)
    day = str(datetime.today().day)

    curtime = year + '-' + month + '-' + day + ' ' + time_line
    parsetime = datetime.strptime(curtime, '%Y-%m-%d %H:%M:%S')
    return parsetime.timestamp()



def fetch_entity_id(input_string, status):
    if input_string == "旅店老板": return '1'
    if input_string == "GameEntity": return '1'
    if input_string[0] != "[":
        return input_string

    # 去除前后的 "[", "]"
    kv_list = input_string[1:-1]

    # 提取成形如 [... , "id=233" , ...]的格式
    kv_list = kv_list.split(" ")

    for item in kv_list:
        kv = item.split("=")
        if kv[0] == 'entityName': entityName = kv[1]
        if kv[0] == 'id': returnitem = kv[1]

    status['Entity=' + returnitem]['entityName'] = entityName
    return returnitem

def click(position):
    pyautogui.moveTo(position[0], position[1])
    # time.sleep(0.1)
    pyautogui.mouseDown()
    pyautogui.mouseUp()

##############################################################################################
##############################################################################################
##############################################################################################
# ███████ ███████ ██      ███████  ██████ ████████     ███████ ██ ███    ██  █████  ██           █████  ██     ██  █████  ██████  ██████  
# ██      ██      ██      ██      ██         ██        ██      ██ ████   ██ ██   ██ ██          ██   ██ ██     ██ ██   ██ ██   ██ ██   ██ 
# ███████ █████   ██      █████   ██         ██        █████   ██ ██ ██  ██ ███████ ██          ███████ ██  █  ██ ███████ ██████  ██   ██ 
#      ██ ██      ██      ██      ██         ██        ██      ██ ██  ██ ██ ██   ██ ██          ██   ██ ██ ███ ██ ██   ██ ██   ██ ██   ██ 
# ███████ ███████ ███████ ███████  ██████    ██        ██      ██ ██   ████ ██   ██ ███████     ██   ██  ███ ███  ██   ██ ██   ██ ██████  
##############################################################################################
##############################################################################################
##############################################################################################

def select_final_award():
    print('Select final award now..')
    waittime = 10
    # print('[wait time=%d]' % waittime)
    time.sleep(waittime)
    
    award_positions = [
    # 3 prizes
                [1000,315],     #[645,447],
            [700,770], [1330, 800],

#    [1225,877],[1418,455],

    # 4 prizes
            [739, 260], [1322, 410],
        [632,757], [1150, 830],  

    # 5 prizes
                [990, 316], 
        [640, 450],         [1340, 450],
            [730, 850], [1250, 850]
            ]
    for i in range(13):
        time.sleep(1)
        click(award_positions[0])

    counter = 1

    for i in range(1):
        for position in award_positions:
            click(position)
        # time.sleep(0.2)
    time.sleep(2.5)
    click([990,615])
    
    time.sleep(7)
    click([944, 878])
    
def wait(num_seconds):
    print('waiting %s seconds' % num_seconds)
    if num_seconds < 1:
        time.sleep(num_seconds)
        return
    for i in range(num_seconds):
        time.sleep(1)
        print('.', end='', flush=True)
    print('')


def start_game(status):
    print('starting game..')
    curTime = datetime.now(pytz.timezone('America/Los_Angeles'))
    cur_time = curTime.strftime('%Y %b %d %H:%M %S %p %z')
    print('[time=%s]start game' % cur_time)
    
    # select_stage_button = [1508, 837]
    select_team_button = [1445, 895]
    
    global fight_started

    bounty_button = [450, 350]
    confirm_team_button = [840, 625]

    counter = 0
    while not fight_started:
        # print('fight status= %s' % (str(fight_started)))
        click(select_team_button)
        status = updateStatus(status)
        time.sleep(1)
        
        if counter >= 10:
        # click top left for hero selection
            click(bounty_button)
        if counter >= 20:
            click(confirm_team_button)
            # select final prize
        if counter == 30:
            select_final_award()
        if counter >= 35:
            restartHearthStoneAndRunMercenary()
            counter = 0
        counter += 1
    
##############################################################################################
##############################################################################################
##############################################################################################
# ███████ ██  ██████  ██   ██ ████████     ███████ ████████  █████   ██████  ███████ 
# ██      ██ ██       ██   ██    ██        ██         ██    ██   ██ ██       ██      
# █████   ██ ██   ███ ███████    ██        ███████    ██    ███████ ██   ███ █████   
# ██      ██ ██    ██ ██   ██    ██             ██    ██    ██   ██ ██    ██ ██      
# ██      ██  ██████  ██   ██    ██        ███████    ██    ██   ██  ██████  ███████                                                                                    
##############################################################################################
##############################################################################################
##############################################################################################


def fight_stage(status):
    global fight_started, fight_timer_start
    
    curTime = datetime.now(pytz.timezone('America/Los_Angeles'))
    cur_time = curTime.strftime('%Y %b %d %H:%M %S %p %z')
    print('[time=%s][entering fight_stage]' % cur_time)
    
    
    status = updateStatus(status)
    # printStatus(status)
    boardMinions = getMyBoardMinions(status)
    enemyMinions = getEnemyMinion(status)
    availableMinions = getAvailableMinions(status)

    print('number of board minions=%d' % len(boardMinions))
    print('number of availableMinions minions=%d' % len(availableMinions))
    
    end_turn_position = [1558, 482]

    printflag = False
    counter = 0
    while len(boardMinions) < 3 and len(availableMinions) > 0:
        if not printflag:
            print('minions not on board..')
            printflag = True
        click(end_turn_position)
        status = updateStatus(status)
        boardMinions = getMyBoardMinions(status)
        availableMinions = getAvailableMinions(status)
        time.sleep(1)
        if counter > 60:
            return
        counter += 1

    # fight_timer_start = time.time()
    # wait(15)

    time.sleep(10)
    
    # 190
    skill_positions = [[], [770, 474], [960, 474], [1150, 474]]

    minion_pos_x = [
                    # diff = 160
                    #0
                    [],
                    # 1
                    [960],
                    # 2
                    [880, 1040],
                    # 3 
                    [800, 960, 1120],
                    # 4
                    [740, 880, 1040, 1200],
                    #5
                    [640, 800, 960, 1120, 1280],
                    # 6
                    [580, 740, 880, 1040, 1100, 1260],
                    # 7
                    [480, 640, 800, 960, 1100, 1280, 1440],
                    ]

    my_minion_y = 725
    enemy_minion_y = 300

    enemy_size = len(enemyMinions)
    my_minion_size = len(boardMinions)

    
    skill_selections_override = {
                                # 1:3,
                                # 2:3,
                                # 3:3
                                }
    target_selections_override = {
    # 2:[minion_pos_x[my_minion_size][0], enemy_minion_y]
    }

    
    select_team_button = [1445, 895]
    default_first_hero_pos = [807, 731]

    status = updateStatus(status)


    counter = 0
    while fight_started:
        
        if counter > 20: 
            restartHearthStoneAndRunMercenary()
            return
        counter += 1
        status = updateStatus(status)
        boardMinions = getMyBoardMinions(status)
        enemyMinions = getEnemyMinion(status)
        enemy_size = len(enemyMinions)

        while not isBoardReadyToFight(boardMinions):
            # status = updateStatus(status)
            # print('number of enemies=%d' % enemy_size)
            my_minion_size = len(boardMinions)
            # print('number of my minions=%d' % my_minion_size)
            # print('not all skills are selected..')
        
            
            for i in range(my_minion_size):
                if 'LETTUCE_HAS_MANUALLY_SELECTED_ABILITY' in boardMinions[i] and \
                    boardMinions[i]['LETTUCE_HAS_MANUALLY_SELECTED_ABILITY'] == '1':
                        continue
                pyautogui.rightClick()
                click(select_team_button)
                
                minion_pos = int(boardMinions[i]['ZONE_POSITION']) - 1
                minion_full_position = [ minion_pos_x[my_minion_size][minion_pos], my_minion_y ]

                click(minion_full_position)

                default_target_skill = skill_positions[1]
                if minion_pos + 1 in skill_selections_override:
                    click(skill_positions[skill_selections_override[minion_pos + 1]])



                # external injection for skill

                click(default_target_skill)
                
                default_target_x = minion_pos_x[enemy_size][0]
                default_target_y = enemy_minion_y
                target_full_position = [default_target_x, default_target_y]

                # external injection for target
                if minion_pos in target_selections_override:
                    target_full_position = target_selections_override[minion_pos]

                click(target_full_position)

            wait(.5)
            updateStatus(status)
                # wait(5)
            boardMinions = getMyBoardMinions(status)

        wait_exp_time = 60
        # print('All skills are now selected.., wait %d seconds' % wait_exp_time)
        if not fight_started: 
            print('fight elapsed [time=%d] seconds' % (time.time() - fight_timer_start))
            return
        print('exp wait time required [%d] seconds' % (wait_exp_time - (time.time() - fight_timer_start)))
        while time.time() - fight_timer_start <= wait_exp_time:
            time.sleep(1)
            
        # time.sleep(wait_exp_time)
        time.sleep(.7)
        click(end_turn_position)
        
        for i in range(15):
            # accelerate animation
            click([451, 471])
            time.sleep(.1)
        
        updateStatus(status)

        if not fight_started: 
            print('fight elapsed [time=%d] seconds' % (time.time() - fight_timer_start))
            return

##############################################################################################
##############################################################################################
##############################################################################################
# ██████  ███████  █████  ██████  ██    ██     ████████  ██████      ███████ ██  ██████  ██   ██ ████████ 
# ██   ██ ██      ██   ██ ██   ██  ██  ██         ██    ██    ██     ██      ██ ██       ██   ██    ██    
# ██████  █████   ███████ ██   ██   ████          ██    ██    ██     █████   ██ ██   ███ ███████    ██    
# ██   ██ ██      ██   ██ ██   ██    ██           ██    ██    ██     ██      ██ ██    ██ ██   ██    ██    
# ██   ██ ███████ ██   ██ ██████     ██           ██     ██████      ██      ██  ██████  ██   ██    ██    
##############################################################################################
##############################################################################################
##############################################################################################

def isBoardReadyToFight(minions):
    if len(minions) == 0: return False
    for minion in minions:
        # print(minion)
        if not 'LETTUCE_HAS_MANUALLY_SELECTED_ABILITY' in minion: 
            # print(minion)
            return False
        if 'LETTUCE_HAS_MANUALLY_SELECTED_ABILITY' in minion and \
                minion['LETTUCE_HAS_MANUALLY_SELECTED_ABILITY'] != '1':
            # print(minion)
            return False
        
    return True
            

def select_award():

    print('[entering select_award]')
    curTime = datetime.now(pytz.timezone('America/Los_Angeles'))
    cur_time = curTime.strftime('%Y %b %d %H:%M %S %p %z')
    print('[time=%s]select award' % cur_time)
    
    award_position = [1123, 555]
    confirm_button = [1139, 851]
    
    print('click(award_position)')
    click(award_position)
    
    wait(.5)
    print('click(confirm_button)')
    click(confirm_button)
    
    wait(5)

##############################################################################################
##############################################################################################
##############################################################################################
#  ██████  ███    ██     ███    ███  █████  ██████  
# ██    ██ ████   ██     ████  ████ ██   ██ ██   ██ 
# ██    ██ ██ ██  ██     ██ ████ ██ ███████ ██████  
# ██    ██ ██  ██ ██     ██  ██  ██ ██   ██ ██      
#  ██████  ██   ████     ██      ██ ██   ██ ██      
##############################################################################################
##############################################################################################
##############################################################################################

def on_map():
    intrim_award_pos = [1118, 854]
    select_team_button = [1445, 895]
    stranger_award = [940, 750]
    award_confirm_x = 990
    award_confirm_y_from = 529
    award_confirm_y_to = 625
    final_award_confirm_button = [944, 879] 
    # mini_buttons = [[990, 576], [944, 879]]
    

    x_list = [521, 609, 751, 870, 981, 1062]
    x_list.reverse()
    click(select_team_button)
    for y in [518, 219]:
        for x in x_list:
            click([x, y])
        
        # for button in mini_buttons:
        #     click(button)
        click(select_team_button)
        click(intrim_award_pos)
        click(stranger_award)
        
        time.sleep(.5)

    rand = random.random()
    if rand < 0.3: 
        for y in range(award_confirm_y_from, award_confirm_y_to, 10):
            click([award_confirm_x, y])
        click(final_award_confirm_button)
        
        

    # rand = random.random()
    # if rand < 0.3: 
    #     for button in mini_buttons:
    #         click(button)

def getMyBoardMinions(status, printTag=False):
    minionlist = []
    for item in status:
        if 'CARDTYPE' in status[item] and status[item]['CARDTYPE'] == 'MINION' and \
            status[item]['CONTROLLER'] == '1' and status[item]['ZONE'] == 'PLAY':
                minionlist.append(status[item])
    if printTag: 
        print('My Board Minions=')
        printMinions(minionlist)
    return minionlist

def getEnemyMinion(status, printTag=False):
    minionlist = []
    for item in status:
        if 'CARDTYPE' in status[item] and status[item]['CARDTYPE'] == 'MINION' and \
            status[item]['CONTROLLER'] == '2' and status[item]['ZONE'] == 'PLAY':
                minionlist.append(status[item])
    if printTag:
        print('Enemy Minions=')
        printMinions(minionlist)
    return minionlist

def getAvailableMinions(status, printTag=False):
    minionlist = []
    for item in status:
        if 'CARDTYPE' in status[item] and status[item]['CARDTYPE'] == 'MINION' and \
            status[item]['CONTROLLER'] == '3':
            minionlist.append(status[item])

    if printTag: 
        print('Available Minions=')
        printMinions(minionlist)

    return minionlist

def printMinions(minionlist):
    for minion in minionlist:
        for key in minion:
            print('\t[%s=%s]' % (key, minion[key]))
        print('=======')
    print('.........')

def printStatus(status):
    print('printing status..')
    print('status=')
    print(status)
    idx = 1
    for itemname in status:
        print('idx=%d' % idx)
        print('{ %s' % itemname)
        for key in status[itemname]:
            print('\t[%s=%s]' % (key, status[itemname][key]))
        print('}.........')
        idx += 1    

def softQuitHearthStone():
    print('softQuitHearthStone')
    hwnd = get_HS_hwnd()
    if hwnd == 0:
        return

    move_window_foreground(hwnd)
    # esc -> quit
    pyautogui.press('esc')
    nonFightQuitButton = [960, 466]
    # inFightQuitButton = [960, 466]

    click(nonFightQuitButton)

    # doesn't look like will be in fight
    
def get_HS_hwnd():
    hwnd = win32gui.FindWindow(None, "炉石传说")
    if hwnd != 0:
        return hwnd

    hwnd = win32gui.FindWindow(None, "《爐石戰記》")
    if hwnd != 0:
        return hwnd

    hwnd = win32gui.FindWindow(None, "Hearthstone")
    return hwnd

def hardQuitHearthStone():
    hwnd = get_HS_hwnd()
    if hwnd == 0:
        return
    _, process_id = win32process.GetWindowThreadProcessId(hwnd)
    handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, process_id)
    win32api.TerminateProcess(handle, 0)
    win32api.CloseHandle(handle)

def startHearthStone():
    battlenet_hwnd = get_battlenet_hwnd()
    move_window_foreground(battlenet_hwnd, "战网")
    left, top, right, bottom = win32gui.GetWindowRect(battlenet_hwnd)
    click([left + 180, bottom - 110])


def restartHearthStoneAndRunMercenary():
    hardQuitHearthStone()
    time.sleep(10)
    startHearthStone()
    time.sleep(40)
    mercenary_button = [960, 480]
    click(mercenary_button)
    
    travel_point_button = [960, 260]
    for i in range(3):
        click(travel_point_button)
        time.sleep(5)

    map_selector_button = [1290, 760]
    time.sleep(6)
    click(map_selector_button)

def checkGameStatus():
    hwnd = get_HS_hwnd()
    if hwnd == 0:
        restartHearthStoneAndRunMercenary()



def move_window_foreground(hwnd, name=""):
    print('move_window_foreground')
    win32gui.BringWindowToTop(hwnd)
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(hwnd)
    # win32gui.ShowWindow(hwnd, win32con.SW_NORMAL)    

def get_battlenet_hwnd():
    hwnd = win32gui.FindWindow(None, "战网")
    if hwnd != 0:
        return hwnd

    hwnd = win32gui.FindWindow(None, "Battle.net")
    return hwnd

def run():
    global fight_started
    global boss_fight
    status = collections.defaultdict(dict)
    # status = updateStatus(status)
    checkGameStatus()
    while True:
        fight_started = False
        boss_fight = False
        status = collections.defaultdict(dict)
        start_game(status)
        # counter = 0
        while True:
            
            if fight_started:
                fight_stage(status)
                status = updateStatus(status)
                time.sleep(5)
            
            if boss_fight: break
            on_map()
            status = updateStatus(status)

        select_final_award()

if __name__ == '__main__':
    debug = False
    # debug = True

    if not debug: run()
    if debug: 
        # testFinalPrize()
        # testGame()
        # testBoard()
        testLog()
        # testScreenshot()