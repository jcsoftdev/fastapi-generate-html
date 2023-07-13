1. create the environment

```bash
python3 -m venv venv
```

2. activate the environment

```bash
source venv/bin/activate
```

3. install the dependencies

```bash
pip install -r requirements.txt
```

4. run fastapi

```bash
uvicorn main:app --reload
```

# with docker

1. build the image

```bash
docker build -t fastapi-generate-html .
```
2. run the container

```bash
docker run -d --name fastapi-generate-html -p 8000:80 fastapi-generate-html
```
or with docker-compose

```bash
docker-compose up -d
```
