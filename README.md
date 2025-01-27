To control Home Assistant by using any script, a long-lived access token is needed. You can obtain this token with the following steps:
 - Enter the Home Assistant GUI and log in.
 - Go to your account menu and the security tab.
 - Scroll down until you see 'Long-lived access token'
 - Create a token and copy it somewhere. The token will not be repeated.
 - Insert this token in main.py into the TOKEN variable.
 - Your script will now be able to access Home assistant.
