import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random
from spbpu_ruz import getExtRuz
import datetime
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
cursor.execute('''create table if not exists main (id SERIAL PRIMARY KEY,
                  datetime INT NOT NULL, desc STR, author STR);''')
conn.commit()
cursor.close()
conn.close()


def workWithBD(command: str):
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(command)
        conn.commit()
        c = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        return e

def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random.randint(0, 65536)})

token = '4fd114fff83dae203a5680c865dd86639291c231b74444c20ddd451216e985d8268c79b142c05b811fd92'
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text.lower()
            if request == "пары" or request == "-n":
                ruz = getExtRuz()
                if ruz[datetime.datetime.now().weekday()]:
                    tmp = []
                    for i in ruz[datetime.datetime.now().weekday()]:
                        if datetime.time.fromisoformat(i.time.split('-')[1].zfill(5) + ':00') < datetime.datetime.now().time():
                            tmp.append('🟥' + str(i))
                        elif datetime.time.fromisoformat(i.time.split('-')[1].zfill(5) + ':00') > datetime.datetime.now().time() and\
                            datetime.time.fromisoformat(i.time.split('-')[0].zfill(5) + ':00') < datetime.datetime.now().time():
                            tmp.append('🟨' + str(i))
                        else:
                            tmp.append('0' + str(i))
                    write_msg(event.user_id, str('\n'.join(tmp)))
                else:
                    write_msg(event.user_id, 'Сегодня пар нет')
            elif request == "завтра" or request == "-t":
                ruz = getExtRuz()
                if ruz[datetime.datetime.now().weekday() + 1]:
                    write_msg(event.user_id, str('\n'.join(['🟦' + str(i) for i in ruz[datetime.datetime.now().weekday() + 1]])))
                else:
                    write_msg(event.user_id, 'Сегодня пар нет')
            elif request == "-h":
                write_msg(event.user_id, """-n или \"пары\" для получения списка сегодняшних пар
-t или \"завтра\" для получения списка завтрашних пар
-z для получения списка задач
-d для удаление задач
-a для создания задач
-h что-бы ещё раз увидеть это окно""")
            elif request == "-z":
                try:
                    tmp = []
                    for i in workWithBD('SELECT * FROM main'):
                        if i[1] > datetime.datetime.now().timestamp():
                            tmp.append(f'⦁{i[0]}. ' + i[2] + f'\n ‍ ‍ ‍ ‍ ‍•‍{str(datetime.datetime.fromtimestamp(i[1]))} [id{i[3]}|A]')
                        else:
                            tmp.append('🗑 ' + i[2])
                    if tmp:
                        write_msg(event.user_id, '\n'.join(tmp))
                        workWithBD(f'DELETE FROM main WHERE datetime < {int(datetime.datetime.now().timestamp())}')
                    else:
                        write_msg(event.user_id, 'Пусто')
                except Exception as e:
                    write_msg(event.user_id, '❗' + str(e))
            elif request[:2] == '-a':
                d = request.split()
                try:
                    tmp = int(datetime.datetime.strptime(d[1], "%Y-%m-%d").timestamp() + 64800)
                except Exception as e:
                    write_msg(event.user_id, "Неверно указана дата (гггг-мм-дд)\nБудет использована завтрашняя дата\n❗ " + str(e))
                    tmp = int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp() + 64800)
                tmp = workWithBD(f'INSERT INTO main (datetime, desc, author) VALUES({tmp},' +\
                    f' \"{" ".join(d[2:])}\", \"{event.user_id}\")')
                if type(tmp) == list:
                    write_msg(event.user_id, "✔Успех")
                elif type(tmp) == Exception:
                    write_msg(event.user_id, '❗' + str(tmp))
            elif request[:2] == '-d':
                d = request.split()[1]
                tmp = workWithBD(f'DELETE FROM main WHERE id={d}')
                if type(tmp) == list:
                    write_msg(event.user_id, "✔Успех")
                elif type(tmp) == Exception:
                    write_msg(event.user_id, '❗' + str(tmp))
            else:
                write_msg(event.user_id, "-h для помощи")
