from datetime import datetime
import pytz, os, collections, re, SMS
# from win32 import win32gui, win32api, win32process
# import win32.lib.win32con as win32con
# import win32com.client
import pyautogui, random
import log_reader, select_awards, fight_stages, global_variables, testtemp
import time

# fight_started = False
# fight_timer_start = 0


def click(position):
    pyautogui.moveTo(position[0], position[1])
    time.sleep(0.1)
    pyautogui.mouseDown()
    pyautogui.mouseUp()

    
def wait(num_seconds):
    # print('waiting %s seconds' % num_seconds)
    if num_seconds < 1:
        time.sleep(num_seconds)
        return
    for i in range(num_seconds):
        time.sleep(1)
    #     print('.', end='', flush=True)
    # print('')


def start_game_2_5(status):
    print('starting game..')
    curTime = datetime.now(pytz.timezone('America/Los_Angeles'))
    cur_time = curTime.strftime('%Y %b %d %H:%M %S %p %z')
    print('[time=%s]start game' % cur_time)
    
    select_stage_button = [1508, 837]
    select_team_button = [1445, 895]
    
    # global fight_started

    counter = 0
    while not global_variables.fight_started:
        # print('fight status= %s' % (str(fight_started)))
        click(select_team_button)
        status = log_reader.updateStatus(status)
        time.sleep(1)
        counter += 1
        if counter % 20 == 0:
            select_award_2_5()
            exit_stage_2_5()        
    


# def isBoardReadToFight(minions):
#     for minion in minions:
#         print(minion)
#         if not 'LETTUCE_HAS_MANUALLY_SELECTED_ABILITY' in minion: return False
#         if 'LETTUCE_HAS_MANUALLY_SELECTED_ABILITY' in minion and \
#                 minion['LETTUCE_HAS_MANUALLY_SELECTED_ABILITY'] != '1':
#             return False
#     return True
            

def select_award_2_5():


    
    award_position = [1123, 555]
    confirm_button = [1139, 851]
    
    time.sleep(3)
    for i in range(7):
        # print('click(award_position)')
        click(award_position)
        
        wait(.5)
        # print('click(confirm_button)')
        click(confirm_button)
        
        wait(1)


def exit_stage_2_5():

    # print('[entering exit_stage]')
    # curTime = datetime.now(pytz.timezone('America/Los_Angeles'))
    # cur_time = curTime.strftime('%Y %b %d %H:%M %S %p %z')
    # print('[time=%s][exit stage]' % cur_time)    
    
    check_map_button = [787, 993]
    forfeit_button = [1069, 795]
    confirm_button = [830, 610]

    # print('click(check_map_button)')
    wait(1)
    click(check_map_button)
    
    wait(1)
    # print('click(forfeit_button)')
    click(forfeit_button)
    
    wait(1)
    # print('click(confirm_button)')
    click(confirm_button)
    



def run():
    # global fight_started
    global_variables.init()
    status = collections.defaultdict(dict)
    # status = updateStatus(status)
    counter = 0
    while True:
        counter += 1
        if counter % 10 == 0:
            curTime = datetime.now(pytz.timezone('America/Los_Angeles'))
            cur_time = curTime.strftime('%Y %b %d %H:%M %S %p %z')
            SMS.sendMessage("Finished %d th run at %s" % (counter, cur_time))
        # fight_started = False
        global_variables.init()
        status = collections.defaultdict(dict)
        print('...round starts')
        start_game_2_5(status)
        while global_variables.fight_started:
            # print('in fight status..')
            fight_stages.fight_stage(status)
            status = log_reader.updateStatus(status)
        select_award_2_5()
        exit_stage_2_5()


if __name__ == '__main__':
    run()
    # testLog()