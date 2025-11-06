#!/usr/bin/python3
import threading
import time
import PySimpleGUI as sg
import Encrypt


def Encryption_thread(work_id, window):
    # LOCATION 1
    # this is our "long running function call"
    # sleep for a while as a simulation of a long-running computation
    sg.popup_non_blocking('Spacebar: takes PNG Photos\nq: close webcam and analyze\nc: clear captured_images', grab_anywhere=True)
    Encrypt.main()
    # at the end of the work, before exiting, send a message back to the GUI indicating end
    window.write_event_value('-THREAD DONE-', work_id)
    sg.popup_non_blocking('Finished!!', grab_anywhere=True)
    # at this point, the thread exits
    return



############################# Begin GUI code #############################
def the_gui():
    sg.theme('Light Brown 3')


    layout = [[sg.Text('PRNG Generator')],
              [sg.Text('Please Select Option')],
              [sg.Text(size=(40, 1), key='-OUTPUT-')],
              [sg.Text(size=(25, 1), key='-OUTPUT2-')],
              [sg.Text('⚫', text_color='blue', key=i, pad=(0,0), font='Default 14') for i in range(20)],
              [sg.Button('Generate PRNG'), sg.Button('Popup'), sg.Button('Exit')], ]

    window = sg.Window('Random Numbers Are Not', layout)
    # --------------------- EVENT LOOP ---------------------
    work_id = 0
    while True:
        # wait for up to 100 ms for a GUI event
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        if event == 'Generate PRNG':           # clicking "Go" starts a long running work item by starting thread
            window['-OUTPUT-'].update('Starting long work %s' % work_id)
            window[work_id].update(text_color='red')
            # STARTING a thread, which will run Encrypt.py
            thread_id = threading.Thread(
                target=Encryption_thread,
                args=(work_id, window,),
                daemon=True)
            thread_id.start()
            work_id = work_id+1 if work_id < 19 else 0

        # if message received from queue, then some work was completed
        if event == '-THREAD DONE-':
            completed_work_id = values[event]
            window['-OUTPUT2-'].update(
                'Complete Work ID "{}"'.format(completed_work_id))
            window[completed_work_id].update(text_color='green')

        ## This is just the syntax for a popup -- only here so I can easily copy/paste for now.
        #if event == 'Popup':
        #    sg.popup_non_blocking('This is a popup showing that the GUI is running', grab_anywhere=True)
    # if user exits the window, then close the window and exit the GUI func
    window.close()
    

############################# Main #############################


if __name__ == '__main__':
    the_gui()
    print('Exiting Program')