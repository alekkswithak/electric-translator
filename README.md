# Electric Translator

A FastAPI app utilizing ChatGPT 3.5 for efficient text translation across multiple languages.

## Setup

### Initial Setup

From the project root directory, run:

```
docker-compose up --build
```

### Subsequent runs

Simply use:

```
docker-compose up
```

Once the application starts, access the Swagger documentation at `localhost/docs` for further details.

## Useage

The application offers two endpoints for text translation:

### /translate

_Parameters:_

- _text_: The text to be translated (extensive text lengths are supported).
- _langauges_: A list of desired target languages for translation.

_Returns:_

- _task_id_: This identifier also represents the text ID for tracking purposes.

You can follow the progress of the translation tasks in `/api/logs/celery.log`, once the tasks stop firing, the translation is complete.

### /translate/{task_id}

_Argument:_

- _task_id_: The unique ID assigned to the text translation task.

_Returns_:

- While the task is ongoing, only the status is returned. Upon completion, a response structure similar to the following is provided:

```
{
  "id": <text_id>,
  "text": "string",
  "translations": [
    {
      "id": <translation_id>,
      "text_id": <text_id>,
      "language": "<language>",
      "status": "complete",
      "translated_content": "翻譯的例子"
    },
    ...
  ]
}
```
