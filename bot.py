import telebot
import config
import json
import requests

bot = telebot.TeleBot(config.token)

#some startup procedures
headers = {'Content-type': 'application/json'}
auth_token = ''
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
            "user": config.zabbix_login,
            "password": config.zabbix_password
        },
    "id": 1,
    "auth": None
    })
r = requests.post(config.zabbix_url, data=dataj, headers=headers)
auth_token = json.loads(r.text)['result']

def get_host(id):
    dataj = json.dumps({
    "jsonrpc": "2.0",
    "method": "host.get",
    "params": {
        "output": [
            "host"
        ],
        "filter": {
            "hostid": id
        }
    },
    "auth": auth_token,
    "id": 1
    })

    r = requests.post(config.zabbix_url, data=dataj, headers=headers)
    r = json.loads(r.text)['result'][0]['host']
    return r

@bot.message_handler(regexp="^.*@AvalonZabBot.*\/{0,1}alarm[s]{0,1}.*$")
@bot.message_handler(commands = ["alarms"])
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

    r = requests.post(config.zabbix_url,data = dataj, headers=headers)
    r = json.loads(r.text)['result']
    if len(r) == 0:
        bot.send_message(message.chat.id, "No any alarms =)")
    else:
        for trigger in r:
            ans = trigger['description'] + '\n' + severity_dict[int(trigger['priority'])]
            for host in trigger['hosts']:
                ans += '\n' + get_host(host['hostid'])
            bot.send_message(message.chat.id, ans)

if __name__ == '__main__':
    bot.polling(none_stop=True)