# telegram_game_update_mailer
Телеграм бот, рассыльщик уведомлений о обновлении игр.  
### Поддерживаемые источники:  
1. steam: Counter-Strike: Global Offensive, Dota 2, PLAYERUNKNOWN'S BATTLEGROUNDS, Apex Legends, Counter-Strike
2. battle.net: Call of Duty: Warzone

### Переменные окружения в docker-compose:
Переменные окружения прописываются в файле docker.env. Для работы требуется указать следующие переменные:  
1. BOT_API_TOKEN = Телеграм api токен, можно получить у бота @BotFather
2. LOG_LEVEL = Уровень логирования, доступные значения DEBUG, INFO, WARNING, ERROR, CRITICAL
3. UPDATE_FREQUENCY = Периодичность обновления новостей из источников задается в секундах
4. POSTGRES_DB = Имя бд
5. POSTGRES_USER = Имя пользователя бд
6. POSTGRES_DB = Пароль для бд

### Запуск бота:
`docker-compose up`