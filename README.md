# YouTube Music Controller

## Installation

Create a virtual environment with a specific Python version

```sh
/path/to/python312 -m venv venv
```

Activate the virtual environment

- For Windows:

    ```shell
    venv\Scripts\activate
    ```

- For Linux:

    ```sh
    source venv/bin/activate
    ```

Install Tailwind CSS

```sh
npm install -D tailwindcss
```

Install Python Dependencies

```sh
pip install -r requirements.txt
```

Create a `users.json` file:

```json
{
    "users": [
        {
            "id": "1",
            "username": "Jonah",
            "firefox_profile": "/path/to/firefox/profile",
            "profile_pic": "jonah.jpg"
        },
        {
            "id": "2",
            "username": "example_user",
            "firefox_profile": "/home/jonah/.mozilla/firefox/m47jlqb9.default-release",
            "profile_pic": "0trashpanda.jpg"
        }
    ]
}
```

## Usage

Start Tailwind CSS watcher

```sh
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```

Run the server

```sh
python server.py
```
