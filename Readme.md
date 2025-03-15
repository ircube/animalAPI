
# dev, run
```bash
python animals.py
waitress-serve --listen=*:5000 animals:app
```

# deploy
```bash
git commit -m "... some changes"
git push heroku main
```
