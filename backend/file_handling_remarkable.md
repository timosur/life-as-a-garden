# Local process

## Upload new garden to remarkable

1. Call http://127.0.0.1:8000/api/garden/print
   -> Prints PDF to ./output/Lebensgarten.pdf
2. Run `docker run -v $HOME/.config/rmapi/:/home/app/.config/rmapi/ -v $HOME/rmapi:/tmp/rmapi/ -v /Users/timosur/code/life-as-a-garden/backend/output:/tmp/rmapi/output rmapi mv Lebensgarten/Lebensgarten Lebensgarten/[CURRENT_DATE]` to rename the latest Lebensgarten
3. Run `docker run -v $HOME/.config/rmapi/:/home/app/.config/rmapi/ -v $HOME/rmapi:/tmp/rmapi/ -v /Users/timosur/code/life-as-a-garden/backend/output:/tmp/rmapi/output rmapi put /tmp/rmapi/output/Lebensgarten.pdf /Lebensgarten` to upload new latest Lebensgarten

## Download latest garden to file and analyze the png for checked plants

1. Run `docker run -v $HOME/.config/rmapi/:/home/app/.config/rmapi/ -v $HOME/rmapi:/tmp/rmapi/ rmapi geta Lebensgarten/Lebensgarten` to download latest Lebensgarten to zip fiel located in $HOME/rmapi
2. Run `cd ~/code/life-as-a-garden/backend/input && mkdir Lebensgarten && cd Lebensgarten && unzip ~/rmapi/Lebensgarten.zip` to unzip
3. Run `~/code/remarks/.venv/bin/python -m remarks ~/code/life-as-a-garden/backend/input/Lebensgarten ~/code/life-as-a-garden/backend/input` to convert the remarkable specific folder structure containing the data to PDF
4. Run `magick -density 300 Lebensgarten\ _remarks.pdf -quality 100 Lebensgarten.png`
5. Analyze Page one png (Lebensgarten-1.png) using LLM
   -> Prompt:

```txt
You are given an image containing **only a checklist**, where each item consists of a label and a checkbox.

The checkboxes can appear in two states:

* ☐ or empty → "checkboxIsFilled": false
* ☒, marked, crossed, filled, or circled → "checkboxIsFilled": true

Your task is to extract each checklist item and return it in the following JSON format:

json
{
  "content": [
    {
      "label": "Partnerschaft",
      "checkboxIsFilled": true
    },
    {
      "label": "Kinder",
      "checkboxIsFilled": false
    }
  ]
}


Be robust: if a checkbox is clearly marked in any way (checked, crossed, filled, or circled), treat it as "checkboxIsFilled": true.

**Only return the JSON.** Ignore anything else.
```

Returning for example:

```json
{
  "content": [
    {
      "label": "Bobo",
      "checkboxIsFilled": false
    },
    {
      "label": "Yoga",
      "checkboxIsFilled": false
    },
    {
      "label": "Oma",
      "checkboxIsFilled": false
    },
    {
      "label": "Finja",
      "checkboxIsFilled": false
    },
    {
      "label": "Schwimmen",
      "checkboxIsFilled": false
    },
    {
      "label": "Frankes",
      "checkboxIsFilled": false
    },
    {
      "label": "Mats",
      "checkboxIsFilled": false
    },
    {
      "label": "Meditation",
      "checkboxIsFilled": false
    },
    {
      "label": "Schweigerehem",
      "checkboxIsFilled": false
    },
    {
      "label": "Mama",
      "checkboxIsFilled": false
    },
    {
      "label": "Lesen",
      "checkboxIsFilled": false
    },
    {
      "label": "Fadhad fahren",
      "checkboxIsFilled": false
    },
    {
      "label": "Journaling",
      "checkboxIsFilled": false
    },
    {
      "label": "Joggen",
      "checkboxIsFilled": false
    },
    {
      "label": "Waldbaden",
      "checkboxIsFilled": false
    },
    {
      "label": "Kiitem",
      "checkboxIsFilled": false
    },
    {
      "label": "Spass bei der Arbeit",
      "checkboxIsFilled": false
    },
    {
      "label": "Sinn in der Arbeit",
      "checkboxIsFilled": false
    },
    {
      "label": "Psychotherapie",
      "checkboxIsFilled": false
    },
    {
      "label": "DJ",
      "checkboxIsFilled": false
    },
    {
      "label": "Magic",
      "checkboxIsFilled": false
    },
    {
      "label": "Schach",
      "checkboxIsFilled": false
    }
  ]
}
```
