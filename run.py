import logging

import gradio as gr
from gspread_editor import GSpreadEditor
import gspread

import constants
from dateman import DateManager


# Enable logging
logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Authenticate with Google and get the sheet
gc, authorized_user = gspread.oauth_from_dict(constants.GSPREAD_CREDENTIAL, constants.GSPREAD_AUTH_USER)
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

    name_dict = {
        "유진": "check_in_yujin",
        "애리": "check_in_aeri",
        "지은": "check_in_jieun",
    }

    button_dict = {}
    with gr.Row():
        for name, api_name in name_dict.items():
            btn = gr.Button(name, scale=2)
            button_dict[api_name]= btn


    excuse_radio = gr.Radio(["없음", "운동", "재택", "연차"], label="개인사유", info="다른 사정이라도 있으셨나요?")

    with gr.Column():
        custom_checker = gr.Checkbox(label="네, 시간을 직접 넣을게요.", info="출근시간이 너무 지났으면 직접 넣으실 수 있어요.")
        with gr.Row():
            custom_hour = gr.Number(label="HH", minimum= 0, maximum=24)
            custom_minute = gr.Number(label="MM", minimum= 0, maximum=60)
    test_result = gr.Textbox(label="", placeholder= "Welcome!")

    for api_name, btn in button_dict.items():
        inputs =[btn, excuse_radio]
        if custom_checker:
            inputs += [custom_checker, custom_hour, custom_minute]
        btn.click(
            geditor.check_in,
            inputs=inputs,
            outputs=[test_result],
            api_name=api_name)

    logger.info("Launching...")
    demo.launch(server_name="0.0.0.0", auth=(constants.USER_ID, constants.PASSWORD))
