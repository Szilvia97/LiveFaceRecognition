import PySimpleGUI as psg
from firebase import firebase
from datetime import datetime


psg.theme('LightGreen3')
layout=[[psg.Text('Válaszd ki a tárgyat',size=(100, 1), font='Lucida',justification='left')],
        [psg.Combo(['Szoftverteszteles','OOP', 'Szoftverfejlesztes','Diszkret matematika', 'Kriptografia','Webtechnologiak'],key='subject')],
        [psg.Text('Válaszd ki az óra típusát ',size=(30, 1), font='Lucida',justification='left')],
        [psg.Combo(['Eloadas','Labor'],key='type')],
        [psg.Text('Válaszd ki a szakot ',size=(30, 1), font='Lucida',justification='left')],
        [psg.Combo(['Szamitastechnika','Informatika','Tavkozles'],key='class')],
        [psg.Text('Válaszd ki a hetet ',size=(30, 1), font='Lucida',justification='left')],
        [psg.Combo(['het1','het2', 'het3', 'het4', 'het5'],key='week')],
        [psg.Text('Válaszd ki a termet ',size=(30, 1), font='Lucida',justification='left')],
        [psg.Combo(['114','312', '230'],key='classroom')],
        # [psg.Text('Válaszd ki az időpontot',size=(30, 1), font='Lucida',justification='left')],
        # [psg.Listbox(values=['8:00 - 9:50', '10:00 - 11:50', '12:30 - 14:20'], select_mode='extended', key='time', size=(30, 6))],
        [psg.Button('Kezdés', font=('Times New Roman',12), size=(10, 1)),psg.Button('Leállítás', font=('Times New Roman',12),size=(10, 1))]]

window =psg.Window('Jelenlét',layout, size=(360,360), auto_size_buttons=True, auto_size_text=True, resizable=True,finalize=True)

firebase = firebase.FirebaseApplication('https://studentdatas-2ea41.firebaseio.com/', None)


while True:
        event, values = window.read()
        if event in ('Leállítás', None):
            break           
        if event == 'Kezdés':
            # win.close()
            now = datetime.now()
            date_string = now.strftime("%Y-%m-%d")
            time_string = now.strftime("%H:%M:%S")

            studentData =  {'deviceId': '', 
                            'isAttendanceRecovery': '',
                            'neptunId': '',
                            'profile': '',
                            'studentName': ''
                            }  
            
            subject = values['subject']
            type = values['type']
            className = values['class']
            week = values['week']
            classroom = values['classroom']
            
            result = firebase.post('Jelenlet/' + subject + '/' + type + '/' + className + '/' + week + '/' + classroom + '/' + date_string + '/' + time_string, studentData)  
            print(result) 
        
            # psg.popup('Az óra adatai',      
                # 'Az óra neve: '+ values['subject'] + '\nTípusa: '+ values['type'] +' \nIdőpont: ' + classTime[1:len(classTime)-1] +' \nSzak: ' + values['class'])



        # elif event == 'Download':
            