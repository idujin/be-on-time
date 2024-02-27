import logging

import altair as alt
import gradio as gr
import constants
from csv_editor import CSVEditor

from dateman import DateManager
from display import *

# Enable logging
logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

dateman = DateManager()
ceditor = CSVEditor()

with gr.Blocks() as log_demo:
    
    users = ["유진", "애리", "지은"]
    data_radio = gr.Radio(choices= users, label="점수 확인하기", info="사용자를 선택하세요.", interactive=True, value="유진")
    selcted_user = alt.selection_point(encodings=['color'])
    
    plot = gr.Plot(value = make_plot(users,except_user=["애리"]), label="Plot", scale=1)
    df = display_dataframe(data_radio.value)
    data_radio.change(display_dataframe, inputs=[data_radio],outputs=[df])

    logger.info("Launching Leader board...")

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

    test_result = gr.Textbox(label="", placeholder= "Welcome!")
    excuse_radio = gr.Radio(["없음", "운동", "재택", "연차"], label="개인사유", info="다른 사정이라도 있으셨나요?")

    with gr.Column():
        custom_checker = gr.Checkbox(label="네, 시간을 직접 넣을게요.", info="출근시간이 너무 지났으면 직접 넣으실 수 있어요.")
        with gr.Row():
            custom_hour = gr.Number(label="HH", minimum= 0, maximum=24)
            custom_minute = gr.Number(label="MM", minimum= 0, maximum=60)

    for api_name, btn in button_dict.items():
        inputs =[btn, excuse_radio]
        if custom_checker:
            inputs += [custom_checker, custom_hour, custom_minute]
        btn.click(
            ceditor.check_in,
            inputs=inputs,
            outputs=[test_result],
            api_name=api_name)

    logger.info("Launching Check-in...")

pages = gr.TabbedInterface([demo, log_demo], ["Check-in", "Leader board"])

if __name__ == "__main__":
    logger.info("Launching...")
    pages.launch(server_name="0.0.0.0", auth=(constants.USER_ID, constants.PASSWORD))