### Running python webserver
1. `cd python_server`
2. `pip install -r requirements.txt`
3. `uvicorn main:app --host 0.0.0.0 --port 7090`


### Running Svelte App
1. `npm i`
2. `npm run dev -- --open` 

***updating urls***
- `src/lib/DataStream.svelte` line 20
- `src/lib/CameraStream.svelte` line 27
