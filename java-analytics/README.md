## Объектная оценка на Java

Требуется JDK 11 или новее и PowerShell. Первый запуск загружает Gson 2.13.2 с Maven Central и проверяет SHA-256. Команды из корня проекта:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\java-analytics\run.ps1 data/scenario.json data/session_good.json results/java-good.json
powershell -NoProfile -ExecutionPolicy Bypass -File .\java-analytics\run.ps1 data/scenario.json data/session_late.json results/java-late.json
powershell -NoProfile -ExecutionPolicy Bypass -File .\java-analytics\run.ps1 data/scenario.json data/session_unity.json results/java-unity.json
```

Ожидаемые результаты: 100/успех, 60/неуспех (просрочен leave_zone), 0/неуспех (истекли сроки двух критических действий). Полный JSON содержит статусы событий, пропуски, критические ошибки и рекомендацию. Некорректный журнал завершает запуск с кодом 2 и сообщением в stderr. Компонент запускается отдельно от Unity, используя её JSON-журнал или демонстрационный файл.

Для проверки исходников начните с `java-analytics/src/training/AssessmentService.java` (порядок, сроки и баллы), затем посмотрите `JsonFiles.java`, `Scenario.java` и `Session.java` (входной контракт). Для сопоставления используйте `analytics/assess.py` и тот же набор данных.

Для проверки Python из корня проекта: python -m unittest discover -s analytics -v.
