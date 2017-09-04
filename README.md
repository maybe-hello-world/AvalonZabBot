# AvalonZabBot  
Simple Telegram bot that announce fired triggers from Zabbix  
Used environment variables:  
 * zabbx_login - login of Zabbix user  
 * zabbix_password - password of Zabbix API user  
 * zabbix_url - full url to zabbix_abi.php file  
 * telebot_token - token for telegram bot
 
Variant 1: set environment vars in system and run script  
Variant 2: docker pull maybehelloworld/avalonzabbot and start with -e options
