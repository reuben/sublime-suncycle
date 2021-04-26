import sublime
import subprocess
from os import path

INTERVAL = 5 # interval in seconds to do new cycle check

PACKAGE = path.splitext(path.basename(__file__))[0]

def logToConsole(str):
    print(PACKAGE + ': {0}'.format(str))

class Settings():
    def __init__(self, onChange=None):
        self.loaded = False
        self.onChange = onChange

        self.load()

    def load(self):
        settings = self._sublimeSettings = sublime.load_settings(PACKAGE + '.sublime-settings')
        settings.clear_on_change(PACKAGE)
        settings.add_on_change(PACKAGE, self.load)

        if not settings.has('day'):
            raise KeyError('SunCycle: missing day setting')

        if not settings.has('night'):
            raise KeyError('SunCycle: missing night setting')

        self.day = settings.get('day')
        self.night = settings.get('night')

        if self.loaded and self.onChange:
            self.onChange()

        self.loaded = True

    def unload(self):
        self._sublimeSettings.clear_on_change(PACKAGE)
        self.loaded = False


class SunCycle():
    def __init__(self):
        self.halt = False
        sublime.set_timeout(self.start, 500) # delay execution so settings can load

    def getDayOrNight(self):
        """Checks DARK/LIGHT mode of macos."""
        cmd = 'defaults read -g AppleInterfaceStyle'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
        return 'night' if bool(p.communicate()[0]) else 'day'

    def cycle(self):
        sublimeSettings = sublime.load_settings('Preferences.sublime-settings')

        if sublimeSettings is None:
            raise Exception('Preferences not loaded')

        config = getattr(self.settings, self.getDayOrNight())

        sublimeSettingsChanged = False

        newColorScheme = config.get('color_scheme')
        if newColorScheme and newColorScheme != sublimeSettings.get('color_scheme'):
            logToConsole('Switching to color scheme {0}'.format(newColorScheme))
            sublimeSettings.set('color_scheme', newColorScheme)
            sublimeSettingsChanged = True

        newTheme = config.get('theme')
        if newTheme and newTheme != sublimeSettings.get('theme'):
            logToConsole('Switching to theme {0}'.format(newTheme))
            sublimeSettings.set('theme', newTheme)
            sublimeSettingsChanged = True

        if sublimeSettingsChanged:
            sublime.save_settings('Preferences.sublime-settings')

    def start(self):
        self.settings = Settings(onChange=self.cycle)
        self.loop()

    def loop(self):
        if not self.halt:
            sublime.set_timeout(self.loop, INTERVAL * 1000)
            self.cycle()

    def stop(self):
        self.halt = True
        if hasattr(self, 'settings'):
            self.settings.unload()

# stop previous instance
if 'sunCycle' in globals():
    globals()['sunCycle'].stop()

# start cycle
sunCycle = SunCycle()
