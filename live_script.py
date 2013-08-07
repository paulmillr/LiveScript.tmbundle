import os
import subprocess
import sublime
import sublime_plugin


class LiveScript(sublime_plugin.TextCommand):

    LIVESCRIPT = 'lsc'
    SETTINGS = sublime.load_settings('LiveScript.sublime-settings')
    WINDOW_NAME = 'livescript_output'

    def run(self, edit):
        text = self._text_to_compile()
        text = text.encode('utf8')
        window = self.view.window()
        js, error = self._compile(text)
        self._write_to_window(window, edit, js, error)

    def _args(self):
        return self.LIVESCRIPT, '--stdin', '--compile', '--bare'

    def _compile(self, text):
        path = self._path()
        args = self._args()

        try:
            return self._execute_command(path, args, text)
        except OSError as e:
            sublime.status_message(str(e))
            return '', str(e)

    def _execute_command(self, path, args, text):
        proc = subprocess.Popen(args, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env={'PATH': path})

        return proc.communicate(text)

    def _path(self):
        lsc = self.SETTINGS.get('livescript_path')
        path = os.getenv('PATH')

        return os.pathsep.join(filter(None, (path, lsc)))

    def _text_selected(self):
        return any(not selected.empty() for selected in self.view.sel())

    def _text_to_compile(self):
        if self._text_selected():
            region = self.view.sel()[0]
        else:
            region = sublime.Region(0, self.view.size())

        return self.view.substr(region)

    def _write_to_panel(self, panel, edit, text):
        panel.set_read_only(False)
        panel.insert(edit, 0, text)
        panel.sel().clear()
        panel.set_read_only(True)

    def _write_to_window(self, window, edit, js, error):
        panel = window.get_output_panel(self.WINDOW_NAME)
        panel.set_syntax_file('Packages/JavaScript/JavaScript.tmLanguage')

        text = js or error
        text = text.decode('utf8')

        self._write_to_panel(panel, edit, text)

        window.run_command('show_panel',
                           {'panel': 'output.{0}'.format(self.WINDOW_NAME)})
