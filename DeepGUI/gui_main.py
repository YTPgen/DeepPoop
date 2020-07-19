from deep_poop.generator import Generator
import PySimpleGUI as sg


def generate_video(config):
    Generator(
        video_file=config['-video_path'],
        scene_threshold=config['scene_threshold'],
        subscene_threshold=config['subscene_threshold'],
        length=int(config['final_length']),
        scene_min_len=config['scene_min_len'],
        abruptness=config['abruptness'],
        reuse=config['reuse'],
        downscale=config['downscale'],
        max_intensity=config['max_intensity'],
        easy_start=config['easy_start']
    ).generate()


MAIN_WINDOW_WIDTH = 200
MAIN_WINDOW_HEIGHT = 100

file_browser = [
    [
        sg.Text("Source video"),
        sg.In(size=(25,1), enable_events=True, key='-video_path'),
        sg.FileBrowse(),
    ]
]


settings = [
    [sg.Text('Scene Threshold')],
    [sg.Slider(
        tooltip='scene_threshold',
        key='scene_threshold',
        range=(0,1),
        default_value=0.5,
        size=(20,15),
        resolution=0.1,
        orientation='horizontal',
        font=('Helvetica', 12))],
    [sg.Text('Sub-Scene Threshold')],
    [sg.Slider(
        tooltip='subscene_threshold',
        key='subscene_threshold',
        range=(0,1),
        default_value=0.4,
        size=(20,15),
        resolution=0.1,
        orientation='horizontal',
        font=('Helvetica', 12))],
    [sg.Text('Final video length')],
    [sg.Slider(
        tooltip='length',
        key='final_length',
        range=(0,500),
        default_value=20,
        size=(20,15),
        orientation='horizontal',
        font=('Helvetica', 12))],
    [sg.Text('Minimum Scene length')],
    [sg.Slider(
        tooltip='scene_length',
        key='scene_min_len',
        range=(0,500),
        default_value=600,
        size=(20,15),
        orientation='horizontal',
        font=('Helvetica', 12))],
    [sg.Text('Abruptness')],
    [sg.Slider(
        tooltip='Abruptness',
        key='abruptness',
        range=(0,1),
        default_value=0.2,
        size=(20,15),
        orientation='horizontal',
        font=('Helvetica', 12))],
    [sg.Text('Reuse Scenes')],
    [sg.Slider(
        tooltip='reuse',
        key='reuse',
        range=(0,1),
        default_value=1,
        resolution=1,
        size=(20,15),
        orientation='horizontal',
        font=('Helvetica', 12))],
    [sg.Text('Downscale')],
    [sg.Slider(
        tooltip='Downscale',
        key='downscale',
        range=(0,10),
        default_value=1,
        size=(20,15),
        orientation='horizontal',
        font=('Helvetica', 12))],
    [sg.Text('Max Intensity')],
    [sg.Slider(
        tooltip='Max intensity',
        key='max_intensity',
        range=(0,100),
        default_value=20,
        resolution=1,
        size=(20,15),
        orientation='horizontal',
        font=('Helvetica', 12))],
    [sg.Text('Easy Start')],
    [sg.Slider(
        tooltip='Easy start',
        key='easy_start',
        range=(0,1),
        default_value=0,
        resolution=1,
        size=(20,15),
        orientation='horizontal',
        font=('Helvetica', 12))],
]


generate_button = [
    [sg.Button(
        button_text='Poopify',
        tooltip='Bring out the full potential of that video!',
        key='generate'
    )]
]

layout = [
    [
        sg.Frame(layout=file_browser, title='Sauce'),
        sg.HSeparator(),
        sg.Frame(layout=settings, title='Settings')

    ],
    [
        sg.Frame(layout=generate_button, title='Generate')
    ]
]


window = sg.Window(title='DeepPoop', layout=layout, margins=(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT))

# Run the Event Loop

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == 'generate':
       generate_video(values)


window.close()