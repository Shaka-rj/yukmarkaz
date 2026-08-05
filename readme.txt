storage - create strage folder
click: utils/create_table.py - create sqlite3 table in storage folder. (yuklar.db, bot_user.db)

=================================================
userbot:
main.py--------> read.py -> send.py [telegram bot]
              |         |-> writer.py
              |
telegram bot: |
main.py       |-> bot/main.py -> states.py -> ......
==================================================
data folder

group.py - for userbot reading group
places.json - for utils/region_detector.py

