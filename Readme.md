# setup:

## install Redis
install redis engine and run it locally.

## Create a .env file in the root directory for this project
```
REDIS_URL=redis://localhost:6379
FLASK_ENV=DEV
```

# dev, run
```bash
python animals.py
waitress-serve --listen=*:5000 animals:app
```

# debug mode (VSCODE)
```json
"configurations": [
    {
        "name": "Py Flask Anim",
        "type": "debugpy",
        "request": "launch",
        "module": "flask",
        "env": {
        "FLASK_APP": "animals.py",
        "FLASK_DEBUG": "1"
        },
        "args": [
        "run", 
        "--host=0.0.0.0", 
        "--port=5000"
        ],
        "jinja": true,
        "autoStartBrowser": false
    }
]
```

# deploy
```bash
git commit -m "... some changes"
git push heroku main
```
