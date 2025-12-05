#!/usr/bin/python3
import threading
import FreeSimpleGUI as sg
import Encrypt


def Encryption_thread(work_id, window):
    """Thread that runs the image capture safely."""
    try:
        Encrypt.createImages()
        thread_result = {"ok": True, "id": work_id}
    except Exception as e:
        thread_result = {"ok": False, "id": work_id, "error": str(e)}

    # notify GUI thread
    window.write_event_value('-THREAD DONE-', thread_result)
    # thread exits here


############################# Begin GUI code #############################
def the_gui():
    sg.theme('DarkBlue')

    layout = [
        [sg.Text('PRNG Generator')],
        [sg.Text('Please Select Option')],
        [sg.Text(size=(40, 1), key='-OUTPUT-')],
        [sg.Text(size=(25, 1), key='-OUTPUT2-')],
        [sg.Text('⚫', text_color='blue', key=i, pad=(0,0), font='Default 14') for i in range(20)],
        [
            sg.Button('Generate PRNG'),
            sg.Button('Average Entropy', button_color='orange'),
            sg.Button('Predict PRNG', button_color='green'),
            sg.Button('Exit', button_color='red'),
        ],
    ]

    window = sg.Window('Random Numbers Are Not', layout)

    work_id = 0
    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        # ------------------ RUN PRNG GENERATION ------------------
        if event == 'Generate PRNG':
            sg.popup_non_blocking(
                'Spacebar: takes PNG Photos\nq: close webcam and analyze\nc: clear captured_images',
                grab_anywhere=True
            )

            window['-OUTPUT-'].update(f'Generating PRNG {work_id}')
            window[work_id].update(text_color='red')

            try:
                thread_id = threading.Thread(
                    target=Encryption_thread,
                    args=(work_id, window),
                    daemon=True
                )
                thread_id.start()
            except Exception as e:
                window['-OUTPUT2-'].update("ERROR: Could not start thread")
                sg.popup_error(f"Thread Error:\n{e}")
                window[work_id].update(text_color='yellow')
                continue

            work_id = work_id + 1 if work_id < 19 else 0

        # ------------------ THREAD FINISHED ------------------
        if event == '-THREAD DONE-':
            result = values[event]
            completed_id = result["id"]

            if result.get("ok") is False:
                # Thread failed
                window['-OUTPUT2-'].update(f"FAILED Work ID {completed_id}")
                window[completed_id].update(text_color='yellow')
                sg.popup_error(f"Error during image capture:\n{result.get('error')}")
                continue

            # Thread succeeded
            window['-OUTPUT2-'].update(f'Complete Work ID "{completed_id}"')
            window[completed_id].update(text_color='green')

            # Analyze PRNG safely
            try:
                prng = Encrypt.analyzeImages()
                prng_len = len(prng) if prng is not None else 0
                sg.popup_non_blocking(
                    f'Raw Key: {prng}\nKey Length: {prng_len}',
                    grab_anywhere=True
                )
            except Exception as e:
                sg.popup_error(f"Error analyzing images:\n{e}")

        # ------------------ AVERAGE ENTROPY ------------------
        if event == 'Average Entropy':
            try:
                avg_entropy = Encrypt.entropy()
                if avg_entropy is not None:
                    sg.popup_non_blocking(
                        f'The average entropy of these images is: {avg_entropy:.4f}',
                        grab_anywhere=True
                    )
                else:
                    sg.popup_non_blocking('No images in directory', grab_anywhere=True)
            except Exception as e:
                sg.popup_error(f"Entropy Error:\n{e}")

    window.close()


############################# Main #############################
if __name__ == '__main__':
    try:
        the_gui()
    except Exception as e:
        sg.popup_error(f"Fatal GUI Error:\n{e}")

    print('Exiting Program')
