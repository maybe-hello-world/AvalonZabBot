import telebot
import json
import time
import requests
import os

# Needed env variables:
# zabbix_url - full URL to Zabbix api_jsonrpc.php file
# zabbix_login - login of Zabbix API user
# zabbix_password - password for Zabbix API user
# telebot_token - token of Telegram bot

#some startup procedures
headers = {'Content-type': 'application/json'}
zabbix_url = os.environ['zabbix_url']
zabbix_login = os.environ['zabbix_login']
zabbix_password = os.environ['zabbix_password']
telebot_token = os.environ['telebot_token']

bot = telebot.TeleBot(telebot_token)
#

severity_dict = {
    0: "Not classified",
    1: "Information",
    2: "Warning",
    3: "average",
    4: "high",
    5: "disaster"
}

#auth
dataj = json.dumps({
    "jsonrpc": "2.0",
    "method":"user.login",
    "params":
        {
            "user": zabbix_login,
            "password": zabbix_password
        },
    "id": 1,
    "auth": None
    })
r = requests.post(zabbix_url, data=dataj, headers=headers)
auth_token = json.loads(r.text)['result']

def get_host(id_):
    dataj = json.dumps({
    "jsonrpc": "2.0",
    "method": "host.get",
    "params": {
        "output": [
            "host"
        ],
        "filter": {
            "hostid": id_
        }
    },
    "auth": auth_token,
    "id": 1
    })

    r = requests.post(zabbix_url, data=dataj, headers=headers)
    r = json.loads(r.text)['result'][0]['host']
    return r

@bot.message_handler(regexp="^.*@[A-Za-z0-9]+Bot.*\/{0,1}alarm[s]{0,1}.*$")
@bot.message_handler(commands = ["alarm", "alarms"])
def yell_alarms(message):
    dataj = json.dumps({
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "filter": {
                "status": [0],
                "value": [1, 2],
                "priority": [4, 5]
            },
            "output": [
                "description",
                "priority",
                "hosts"
            ],
            "withUnacknowledgedEvents": True,
            "monitored": 0,
            "sortfield": ["priority"],
            "expandDescription": "true",
            "selectHosts": "refer",
            "min_severity": 4
        },
        "auth": auth_token,
        "id": 1
    })

    r = requests.post(zabbix_url,data = dataj, headers=headers)
    r = json.loads(r.text)['result']
    if not r:
        bot.send_message(message.chat.id, "No any alarms =)")
    else:
        for trigger in r:
            ans = trigger['description'] + '\n' + "Severity: " + str.upper(severity_dict[int(trigger['priority'])])
            for host in trigger['hosts']:
                ans += '\n' + get_host(host['hostid'])
            bot.send_message(message.chat.id, ans)

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
			
		# Yes, i know what I'm doing
        except BaseException:
            time.sleep(5)
            continue
