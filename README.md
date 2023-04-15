## To Develop

Create virtual environment
```
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pip install -r compose/crawler/requirements-dev.txt
```

install pre-commit git hooks
```
pre-commit install
```

make your self env variables
```
cp sample.env .env
```

prepare composes for local dev. We separate production-oriented compose and dev (in docker-compose.yml.override)
```
cp sample.docker-compose.override.yml docker-compose.override.yml
cp sample.docker-compose.yml docker-compose.yml
```