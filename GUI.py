import PySimpleGUI as sg
from PIL import Image
import os.path
import io
import BullseyeProcessing as bp
import ExcelMaker as em

#TODO: INSERT DIRECTORY IN THE LINE BELOW.
directory = 'C:/Users/student/Desktop/PC Lab'
#TODO: INSERT EXCEL SHEET IN LINE BELOW.
excel_file = directory + '/Output.xlsx'

Image.MAX_IMAGE_PIXELS=None

img = Image.open(directory+'/Logo.png')
img.thumbnail((300,300))
bio = io.BytesIO()
img.save(bio,format="PNG")

file_list_column = [
    [sg.Image(data=bio.getvalue(),size=(300,300))],
    [sg.Text(size=(30,1),text_color='red',key="-ERROR-")],
    [
        sg.Text("Image Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
        )
    ],
]
image_viewer_column = [
    [sg.Text("Choose an image from list on left:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(size=(400,400), key="-IMAGE-")],
    [sg.Button('Run Annular Analysis'),sg.Button('Run Global Analysis'), sg.Button('Reset')],
]

image_input_row = [
    [sg.Text("Input Day:"), sg.InputText(size=(2,1),key='-DAY-')],
    [sg.Listbox(values=('aSMA','ED1','ED2','DAPI'),size=(6,4),key="-LISTBOX-")],
    [sg.Text("Vessel No.: "), sg.InputText(size=(2,1),key='-VESSEL-')],
    [sg.Text("Image Length (um): "), sg.InputText(size=(5,5),key='-SCALE-')]
]

image_results_column = [
    [sg.Text("Results Below")],
    [sg.Text("Ring 1 Quantity: "), sg.Text(size=(25,1),key="-R1-")],
    [sg.Text("Ring 2 Quantity: "), sg.Text(size=(25,1),key="-R2-")],
    [sg.Text("Ring 3 Quantity: "), sg.Text(size=(25,1),key="-R3-")],
    [sg.Text("Ring 4 Quantity: "), sg.Text(size=(25,1),key="-R4-")],
    [sg.Text("Total Nuceli Count: "), sg.Text(size=(25,1),key="-RESULT-")],
    [sg.Text("Lumen Area: "), sg.Text(size=(25,1),key="-COUNT-")],
    [sg.Text("Global Cell Count: "), sg.Text(size=(25,1),key="-GLOBAL-")]
]

layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
        sg.Column(image_input_row),
        sg.VSeperator(),
        sg.Column(image_results_column)
    ]
]

window = sg.Window("Image Viewer", layout,location=(0,0)).Finalize()
window.Maximize()
did_it_just_run = False

sg.Popup('Welcome!', '1. Select folder\n2. Select image from folder\n3. Manually enter timepoint of image\n4. Select the stain\n5. Run Analysis\n6. Click Reset and repeat!\n(All data is stored to Excel file automatically)')

while True:
    event, values = window.read()
    file = directory + '/Logo.png'
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            f
            for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".png", ".gif",".tif",".jpg"))
            ]
        window["-FILE LIST-"].update(fnames)
    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(
                values["-FOLDER-"],values["-FILE LIST-"][0]
            )
            im = Image.open(filename)
            im.thumbnail((500,500))
            bio = io.BytesIO()
            im.save(bio,format="PNG")
            window["-TOUT-"].update(im.filename)
            window["-IMAGE-"].update(data=bio.getvalue())
            window["-ERROR-"].update('')
        except:
            window["-ERROR-"].update('Ensure all fields are properly selected')
    elif event == "Run Global Analysis":
        filename = directory
        cell_count = bp.global_count(filename,values["-DAY-"][0],values["-LISTBOX-"][0])
        window["-GLOBAL-"].update(cell_count)
    elif event == "Run Annular Analysis":
        try:
            assert(did_it_just_run == False)
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            print(filename)
            print(directory+'/'+values["-LISTBOX-"][0]+"_d"+values["-DAY-"][0]+'.tif')
            centers, points, ring1_coords, ring2_coords, ring3_coords, ring4_coords,\
            r1, r2,r3,r4,nuclei_count,lumen,time = bp.bullseye(filename,
                                                               directory+'/Data1/'+values["-LISTBOX-"][0]+"_d"+values["-DAY-"][0]+'.tif',
                                                               'Annular Analysis',directory,values["-SCALE-"][0])
            p = bp.plot_signal(centers, ring1_coords, ring2_coords, ring3_coords, ring4_coords, values["-LISTBOX-"][0],directory)
            filename = directory + '/my_images/schematic_'+time+'.png'
            im = Image.open(filename)
            im.thumbnail((500,500))
            bio = io.BytesIO()
            im.save(bio,format="PNG")
            window["-TOUT-"].update(im.filename)
            window["-IMAGE-"].update(data=bio.getvalue())
            window["-R1-"].update(str(r1)+' cells')
            window["-R2-"].update(str(r2)+' cells')
            window["-R3-"].update(str(r3)+' cells')
            window["-R4-"].update(str(r4)+' cells')
            window["-RESULT-"].update(str(nuclei_count)+' nuclei'),
            window["-COUNT-"].update(str(lumen)+' um^2')
            window["-ERROR-"].update('')
            df = em.update_table(values["-DAY-"][0], values["-LISTBOX-"][0],
                                 r1, r2, r3, r4, nuclei_count, lumen, values["-VESSEL-"], time)
            did_it_just_run = True
        except:
            window["-ERROR-"].update('Ensure all fields are properly selected')
    elif event == "Reset":
        window["-TOUT-"].update('')
        window["-IMAGE-"].update()
        window["-R1-"].update('')
        window["-R2-"].update('')
        window["-R3-"].update('')
        window["-R4-"].update('')
        window["-RESULT-"].update('')
        window["-COUNT-"].update('')
        window["-ERROR-"].update('')
        did_it_just_run = False

em.write_to_excel(df,excel_file)
window.close()
