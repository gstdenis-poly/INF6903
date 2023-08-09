# Description: user graphic interface of recorder.

# Include required librairies
import webbrowser
import webview
import webview.menu as wm

class RecorderGui:
    css = '''
        .form-control {
            font-size: 1rem;
            font-weight: 400;
            line-height: 1.5;
            background-color: white;
            background-clip: padding-box;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        }
        #title {
            padding: 5px 0px 5px 10px;
            transition: border-color .15s ease-in-out,box-shadow .15s ease-in-out;
            width: 390px;
        }
        #delay {
            padding-bottom: 2px;
            cursor: pointer;
            width: 150px;
        }
        button {
            width: 247px;
            font-family: "Poppins", sans-serif;
            font-weight: 500;
            font-size: 14px;
            background: #fd1d1d;
            border: 0;
            padding: 10px 0px;
            color: #fff;
            transition: 0.4s;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: red;
        }
        #countdown_container {
            background: black;
            opacity: 0.7;
            display: none;
            position: absolute;
            top: 0px;
            left: 0px;
            bottom: 0px;
            right: 0px;
        }
        #countdown {
            background: red;
            height: 100%;
            position: relative;
            width: 100px;
            margin-left: 160px;
            color: white;
            font-size: 82px;
            text-align: center;
        }
    '''
    js = '''
        function show_countdown(start) {
            var countdown_element = document.querySelector('#countdown');
            countdown_element.innerHTML = start;

            var countdown_container = document.querySelector('#countdown_container');
            countdown_container.style.display = 'block';

            var countdown = start;
            var interval = setInterval(function() {
                countdown -= 1;
                if (countdown >= 0)
                    countdown_element.innerHTML = countdown;
                else {
                    clearInterval(interval);
                    countdown_container.style.display = 'none';
                }
            }, 1000);
        }

        function record() {
            var title_input = document.querySelector('#title');
            var rec_title = title_input.value;
            title_input.value = '';

            var rec_delay = document.querySelector('#delay').value;
            if (rec_delay > 0)
                show_countdown(rec_delay);
                
            setTimeout(function() {
                pywebview.api.record(rec_title);
            }, rec_delay * 1000);
        }

    '''
    html = '''
        <!DOCTYPE html>
        <html>
            <head>
                <style>
                    %s
                </style>
                <script>
                    %s
                </script>
            </head>
            <body>
                <input type="text" id="title" class="form-control" placeholder="Title of recording (optional)"/>
                <select id="delay" class="form-control">
                    <option value="0">No delay</option>
                    <option value="3">3 seconds delay</option>
                    <option value="5">5 seconds delay</option>
                    <option value="10">10 seconds delay</option>
                </select>
                <button onclick="record();">Record</button>
                <div id="countdown_container">
                    <div id="countdown"></div>
                </div>
            </body>
        </html>
    ''' % (css, js)

    recorder = None
    window = None
    help_window = None

    def select_recordings_folder(self):
        recordings_folder = self.window.create_file_dialog(webview.FOLDER_DIALOG)[0]
        self.recorder.set_recordings_folder(recordings_folder)

    def quit(self):
        self.window.destroy()

    def read_me(self):
        webbrowser.open('https://github.com/gstdenis-poly/INF6903/tree/main/client#readme')

    def open_website(self):
        webbrowser.open('http://localhost:8000')

    def record(self, rec_title):
        self.window.hide()
        self.recorder.record(rec_title)
        self.window.show()

    def __init__(self, recorder):
        self.recorder = recorder
        self.window = webview.create_window('Recorder', html = self.html, 
                                            resizable = False, js_api = self,
                                            height = 130, width = 420, on_top = True)
        menu_items = [
            wm.Menu('File',
                [
                    wm.MenuAction('Select recordings folder', self.select_recordings_folder),
                    wm.MenuSeparator(),
                    wm.MenuAction('Quit', self.quit),
                ]
            ),
            wm.Menu('About',
                [
                    wm.MenuAction('Read me', self.read_me),
                    wm.MenuSeparator(),
                    wm.MenuAction('INF6903', self.open_website)
                ]
            )
        ]
        webview.start(menu = menu_items)