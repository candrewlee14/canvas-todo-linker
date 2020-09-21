# canvas-todo-linker
Links Canvas LMS Assignments to Microsoft To-Do.

To get executables, see Releases.
[Download latest release here.](https://github.com/candrewlee14/canvas-todo-linker/releases/latest/download/canvas_todo_linker.exe)

## How to get Canvas Config Info
1. Login to your Canvas account.
2. Go to *Profile* > *Settings* > *+ New Access Token*. You can copy and paste that token in the `CANVAS_TOKEN` field of the `config.json` file, or paste it at runtime when the prompt comes if the field is blank.
3. You can copy and paste `https://DOMAIN_HERE.instructure.com` into the `CANVAS_URL` field of the `config.json` file, or paste it at runtime when the prompt comes if the field is blank.

## How to Create a Release (Development)
Run `pyinstaller canvas_todo_linker.py --one-file`. The executable will be located in the `dist/` folder. 
