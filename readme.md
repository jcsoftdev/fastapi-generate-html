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
