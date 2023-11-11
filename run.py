import gradio as gr
import gspread

import logging

import constants
from dateman import DateManager
from gspread_editor import GSpreadEditor

# Enable logging
logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Authenticate with Google and get the sheet
gc = gspread.service_account_from_dict(constants.GSPREAD_KEY)
sh = gc.open_by_url(constants.GSPREAD_URL)

dateman = DateManager()
geditor = GSpreadEditor()

with gr.Blocks() as demo:
    gr.Markdown(
        """
    # ALMOST DONE TODAY!
    본인 이름 버튼을 눌러서 출근 기록을 남겨주세요.

    """
    )
    with gr.Row():
        btn0 = gr.Button("유진", scale=2)
        btn1 = gr.Button("애리", scale=2)
        btn2 = gr.Button("지은", scale=2)
    excuse_radio = gr.Radio(["없음", "운동", "재택", "연차"], label="개인사유", info="다른 사정이라도 있으셨나요?")

    with gr.Row():
        custom_checker = gr.Checkbox(label="네, 시간을 직접 넣을게요.", info="출근시간이 너무 지났으면 직접 넣으실 수 있어요.")
        custom_hour = gr.Number(label="HH", minimum= 0, maximum=24)
        custom_minute = gr.Number(label="MM", minimum= 0, maximum=60)
    test_result = gr.Textbox(label="", placeholder= "Welcome!")

    if(custom_checker):
        btn0.click(geditor.check_in, inputs=[btn0, excuse_radio, custom_checker, custom_hour, custom_minute], outputs=[test_result])
        btn1.click(geditor.check_in, inputs=[btn1, excuse_radio, custom_checker, custom_hour, custom_minute], outputs=[test_result])
        btn2.click(geditor.check_in, inputs=[btn2, excuse_radio, custom_checker, custom_hour, custom_minute], outputs=[test_result])
    else: 
        btn0.click(geditor.check_in, inputs=[btn0, excuse_radio], outputs=[test_result])
        btn1.click(geditor.check_in, inputs=[btn1, excuse_radio], outputs=[test_result])
        btn2.click(geditor.check_in, inputs=[btn2, excuse_radio], outputs=[test_result])
    
demo.launch(server_name="0.0.0.0", auth=(constants.USER_ID, constants.PASSWORD))
