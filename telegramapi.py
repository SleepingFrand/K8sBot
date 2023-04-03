import telebot
from config import TELEGRAN_TOKEN
from kuberapi import *

bot = telebot.TeleBot(TELEGRAN_TOKEN)

# Обработчик команды /get_pod_info
@bot.message_handler(commands=['get_pod_info'])
def get_pod_info(message):
    try:
        # Получить имя и namespace выбранного Pod
        pod_name = message.text.split()[1]
        namespace = message.text.split()[2] # Замените на нужный namespace

        # Получить информацию о Pod
        pod_info = get_pod_info(pod_name, namespace)

        # Отправить информацию о Pod пользователю
        message_text = f"Имя: {pod_info.metadata.name}\n"\
                       f"Namespace: {pod_info.metadata.namespace}\n"\
                       f"Состояние: {pod_info.status.phase}\n"\
                       f"IP: {pod_info.status.pod_ip}\n"\
                       "Контейнеры: \n"
        for cont in pod_info.spec.containers:
            message_text += f"\t{cont.name}\n"
        bot.reply_to(message, message_text)
    except Exception as e:
        bot.reply_to(message, "Ошибка: {}".format(str(e)))

@bot.message_handler(commands=['get_pod'])
def get_pod(message):
    try:
        if len(message.text.split()) == 1:
            namespaces = get_namespaces().items
            for namespace in namespaces:
                pods = get_namespased_items(namespace.metadata.name, 'pod')
                pods_status = print_items_status(pods)
                bot.send_message(message.chat.id , namespace.metadata.name + ':\n' + pods_status)
        else:
            pods = get_namespased_items(message.text.split()[1], 'pod')
            pods_status = print_items_status(pods)
            bot.send_message(message.chat.id , message.text.split()[1] + ':\n' + pods_status)

    except Exception as e:
        bot.reply_to(message, "Ошибка: {}".format(str(e)))

@bot.message_handler(commands=['get_namespace'])
def get_namespace(message):
    try:
        bot.send_message(message.chat.id, print_namespase_list())
    except Exception as e:
        bot.reply_to(message, "Ошибка: {}".format(str(e)))

@bot.message_handler(commands=['get_node'])
def get_nodes(message):
    try:
        bot.send_message(message.chat.id, print_items_status((get_node())))
    except Exception as e:
        bot.reply_to(message, "Ошибка: {}".format(str(e)))

@bot.message_handler(commands=['del_pod'])
def del_pod(message):
    try:
        pod_name = message.text.split()[1]
        namespace = message.text.split()[2] 
        pod = get_pod_info(pod_name, namespace)
        delete_pod((pod))
        bot.reply_to(message, "Удален pod: "+pod_name)
    except Exception as e:
        bot.reply_to(message, "Ошибка: {}".format(str(e)))

@bot.message_handler(commands=['cordon_node'])
def cordon_node(message):
    try:
        Schedule_node_mode(message.text.split()[1], True)
        bot.reply_to(message, 'Готово')
    except Exception as e:
        bot.reply_to(message, "Ошибка: {}".format(str(e)))

@bot.message_handler(commands=['uncordon_node'])
def uncordon_node(message):
    try:
        Schedule_node_mode(message.text.split()[1], False)
        bot.reply_to(message, 'Готово')
    except Exception as e:
        bot.reply_to(message, "Ошибка: {}".format(str(e)))

@bot.message_handler(commands=['drain_node'])
def drain_node(message):
    try:
        Drain_node(message.text.split()[1])
        bot.reply_to(message, 'Готово')
    except Exception as e:
        bot.reply_to(message, "Ошибка: {}".format(str(e)))

@bot.message_handler(commands=['logs_pod'])
def logs_pod(message):
    try:
        if len(message.text.split()) == 3:
            bot.reply_to(message, get_logs_pod(get_pod_info(message.text.split()[1], message.text.split()[2])))
        elif len(message.text.split()) == 4:
            bot.reply_to(message, get_logs_pod(get_pod_info(message.text.split()[1], message.text.split()[2]),
                int(message.text.split()[3])))
    except Exception as e:
        bot.reply_to(message, "Ошибка: {}".format(str(e)))
    
@bot.message_handler(commands=['logs_namespace'])
def logs_namespace(message):
    try:
        pods = get_namespased_items(message.text.split()[1], 'pod')
        if len(message.text.split()) == 2:
            logs = get_logs_pods(pods)
            for log in logs:
                bot.send_message(message.chat.id, log)
        elif len(message.text.split()) == 3:
            logs = get_logs_pods(pods, int(message.text.split()[2]))
            for log in logs:
                bot.send_message(message.chat.id, log)
    except Exception as e:
        bot.reply_to(message, "Ошибка: {}".format(str(e)))

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот для управления Kubernetes кластером. Я могу помочь вам с удалением подов, получением информации о неймспейсах, нодах и многое другое. Просто отправьте мне команду и я помогу!")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Вот некоторые доступные команды для работы с Kubernetes:\n"+
    "-/get_pod или /get_pod <namespace> - получить поды\n"+
    "-/get_pod_info <name> <namespace> - подробрая информация\n"+
    "-/get_nodes - получает ноды\n"+
    "-/del_pod <name> <namespace> - удаляет pod\n"+
    "-/<un>cordon_node <name> - мутит узел\n"+
    "-/drain_node <name> - мутит и удаляет pod с узла\n"+
    "-/logs_pod <name> <namespace> (<line>) - выводит логи <line> кол-ва, по умолчанию 10\n"+
    "-/logs_namespace <namespace> (<line>) - выводит логи со всего namespace\n")

HANDLER = bot.message_handler