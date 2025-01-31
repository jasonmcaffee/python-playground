# Python Playground
Playground for learning python, mainly geared towards machine learning, data gathering, and general python development.

## Setup
```shell
pip install -r requirements.txt
brew install chromedriver
brew upgrade chromedriver
xattr -d com.apple.quarantine /usr/local/bin/chromedriver
```
## Projects
### Slack
If you don't already have a slack app, you'll need to create one here https://api.slack.com/apps/A063A174E2Y/oauth

Give it permissions channels:read and channels:history

create a file in /projects/slack named `slack-api-token.txt` and paste your API token in there.
### Confluence
Project for downloading confluence pages, extracting data, and storing in a db for later use by ML.

See project readme [here](https://github.com/jasonmcaffee/python-playground/tree/main/projects/confluence)

### Akoya
Project for sandbox testing with Akoya.

#### Selenium ChromeDriver For Account Linking Automation
Brew install is probably an easier route than manually downloading:

```shell
brew install chromedriver
```

Note: The driver must match your version of chrome
```shell
brew upgrade chromedriver
```

You'll have to allow for chromedriver to run
```shell
xattr -d com.apple.quarantine /usr/local/bin/chromedriver
```


Setup the chrome web driver to automate going through the UI flow

https://sites.google.com/chromium.org/driver/getting-started