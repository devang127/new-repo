@echo off
curl -X POST http://127.0.0.1:5000/send_mail -H "Content-Type: application/json"
pause
