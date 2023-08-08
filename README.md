# vision-assistant-for-driving

## Create Visual Instruction Data for Self-Driving

## 1. Install requirements
```
pip3 install -r requirements.txt
```

## 2. Set OpenAI API Key
1. Set it in a .env file (Recommended)
```
OPENAI_API_KEY=sk-
```
2. Set it in code
```
openai.api_key = "sk-"
```

## 3. Run
```
cd instruct-data
python3 generate-instructions.py
```