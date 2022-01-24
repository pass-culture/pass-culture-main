import pygments.token

from pcapi import settings


def get_prompt_color():
    # Colors come from https://github.com/mbadolato/iTerm2-Color-Schemes/blob/master/windowsterminal/Ubuntu.json
    if settings.ENV in "production":
        return "#cc0000"  # red
    if settings.ENV == "staging":
        return "#ad7fa8"  # purple
    if settings.ENV == "testing":
        return "#06989a"  # cyan
    return None  # do not customize locally


prompt_color = get_prompt_color()


c = get_config()

c.TerminalInteractiveShell.autoformatter = None
if prompt_color:
    c.TerminalInteractiveShell.highlighting_style_overrides = {
        pygments.token.Token.Prompt: f"{prompt_color} bold",
        pygments.token.Token.PromptNum: f"{prompt_color} bold",
        pygments.token.Token.OutPrompt: f"{prompt_color} bold",
        pygments.token.Token.OutPromptNum: f"{prompt_color} bold",
    }
c.TerminalInteractiveShell.term_title = False
