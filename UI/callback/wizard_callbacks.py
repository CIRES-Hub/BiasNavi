from dash.dependencies import Input, Output, State
from UI.app import app

elements = ["menu-dataset", "chat-box", "data-view"]


@app.callback(
    Output("wizard-modal", "is_open"),
    Output("wizard-modal", "style"),
    Output("wizard-title", "children"),
    Output("wizard-body", "children"),
    Output("menu-dataset", "style"),
    Output("chat-box", "style"),
    Output("menu-prompt", "style"),
    Output("data-view", "style"),
    Output("snapshot-view", "style"),
    Output("evaluation-view", "style"),
    Output("code-view", "style"),
    Output("report-view", "style"),
    Output("base-styles", "data"),
    Output("next-step", "n_clicks"),
    Output("overlay", "style"),
    Input("menu-help-wizard", "n_clicks"),
    Input("next-step", "n_clicks"),
    State("wizard-modal", "is_open"),
    State("wizard-modal", "style"),
    State("menu-dataset", "style"),
    State("chat-box", "style"),
    State("menu-prompt", "style"),
    State("data-view", "style"),
    State("snapshot-view", "style"),
    State("evaluation-view", "style"),
    State("code-view", "style"),
    State("report-view", "style"),
    State("base-styles", "data"),
    prevent_initial_call=True,
)
def toggle_wizard(n_clicks_open, n_clicks_next, is_open, modal_style, menu_dataset_style, chat_box_style,
                  menu_prompt_style, data_view_style, snapshot_view_style, evaluation_view_style, code_view_style,
                  report_view_style, base_styles):
    # Define steps for the wizard with positions and content
    if not base_styles:
        base_styles = {
            "menu-dataset": menu_dataset_style,
            "chat-box": chat_box_style,
            "menu-prompt": menu_prompt_style,
            "data-view": data_view_style,
            "snapshot-view": snapshot_view_style,
            "evaluation-view": evaluation_view_style,
            "code-view": code_view_style,
            "report-view": report_view_style,
        }

    steps = [
        {
            "title": "Import Your Dataset",
            "body": "You can upload your csv dataset here.",
            "position": {"top": "0px", "left": "0px", },
            "highlight": "menu-dataset"
        },
        {
            "title": "Chat with Your Dataset",
            "body": "Type your query here to interact with AI to know more about the bias in your dataset. RAG can be used to enhance the answer quality",
            "position": {"top": "300px", "left": "0px"},
            "highlight": "chat-box"
        },
        {
            "title": "Customize the Prompts for Chat",
            "body": "You can edit the prompts here to make the chat more personalized and effective.",
            "position": {"top": "50px", "left": "100px"},
            "highlight": "menu-prompt"
        },
        {
            "title": "Check and Manipulate Your Dataset",
            "body": "You can check the uploaded dataset in the data view here and manipulate the table to edit your data. "
                    "You can save a edited dataset snapshot here and download the edited dataset.",
            "position": {"top": "300px", "left": "100px"},
            "highlight": "data-view"
        },
        {
            "title": "Restore and Delete Dataset Snapshots",
            "body": "You can check the uploaded dataset here and manipulate the table to edit your data.",
            "position": {"top": "100px", "left": "200px"},
            "highlight": "snapshot-view"
        },
        {
            "title": "Evaluate Your Dataset",
            "body": "After editing your dataset, you can evaluate your dataset here to see if the bias is mitigated.",
            "position": {"top": "300px", "left": "200px"},
            "highlight": "evaluation-view"
        },
        {
            "title": "Modify Your Dataset With Python",
            "body": "You can modify your dataset with python code running in a safe sandbox here.",
            "position": {"top": "500px", "left": "200px"},
            "highlight": "code-view"
        },
        {
            "title": "Get Your Dataset Report",
            "body": "You can analyze your dataset with BiasNavi and get a comprehensive report here.",
            "position": {"top": "600px", "left": "100px"},
            "highlight": "report-view"
        },
    ]

    # Define the highlight effect
    highlight_style = {"position": "relative", "z-index": "1060"}

    # Handle modal opening and navigation through steps
    if n_clicks_open or n_clicks_next:
        if not is_open:
            # On first open, start at step 1
            step = 0
            return (
                True,
                {**modal_style, **steps[step]["position"]},
                steps[step]["title"],
                steps[step]["body"],
                highlight_style if steps[step]["highlight"] == "menu-dataset" else base_styles["menu-dataset"],
                highlight_style if steps[step]["highlight"] == "chat-box" else base_styles["chat-box"],
                highlight_style if steps[step]["highlight"] == "menu-prompt" else base_styles["menu-prompt"],
                highlight_style if steps[step]["highlight"] == "data-view" else base_styles["data-view"],
                highlight_style if steps[step]["highlight"] == "snapshot-view" else base_styles["snapshot-view"],
                highlight_style if steps[step]["highlight"] == "evaluation-view" else base_styles["evaluation-view"],
                highlight_style if steps[step]["highlight"] == "code-view" else base_styles["code-view"],
                highlight_style if steps[step]["highlight"] == "report-view" else base_styles["report-view"],
                base_styles,
                0,
                {"position": "fixed", "top": "0", "left": "0", "width": "100%", "height": "100%",
                 "backgroundColor": "rgba(0, 0, 0, 0.7)", "z-index": "100", "display": "block"},
            )
        else:
            step = min(n_clicks_next, len(steps))  # Move to next step
            if step < len(steps):
                return (
                    True,
                    {**modal_style, **steps[step]["position"]},
                    steps[step]["title"],
                    steps[step]["body"],
                    highlight_style if steps[step]["highlight"] == "menu-dataset" else base_styles["menu-dataset"],
                    highlight_style if steps[step]["highlight"] == "chat-box" else base_styles["chat-box"],
                    highlight_style if steps[step]["highlight"] == "menu-prompt" else base_styles["menu-prompt"],
                    highlight_style if steps[step]["highlight"] == "data-view" else base_styles["data-view"],
                    highlight_style if steps[step]["highlight"] == "snapshot-view" else base_styles["snapshot-view"],
                    highlight_style if steps[step]["highlight"] == "evaluation-view" else base_styles[
                        "evaluation-view"],
                    highlight_style if steps[step]["highlight"] == "code-view" else base_styles["code-view"],
                    highlight_style if steps[step]["highlight"] == "report-view" else base_styles["report-view"],
                    base_styles,
                    n_clicks_next,
                    {"position": "fixed", "top": "0", "left": "0", "width": "100%", "height": "100%",
                     "backgroundColor": "rgba(0, 0, 0, 0.7)", "z-index": "100", "display": "block"},
                )
            else:
                # Close the wizard after all steps are completed
                return False, modal_style, "", "", base_styles["menu-dataset"], base_styles["chat-box"], base_styles[
                    "menu-prompt"], base_styles["data-view"], base_styles["snapshot-view"], base_styles[
                    "evaluation-view"], base_styles["code-view"], base_styles["report-view"], base_styles, 0, {
                    "position": "fixed", "top": "0", "left": "0", "width": "100%", "height": "100%",
                    "backgroundColor": "rgba(0, 0, 0, 0.5)", "z-index": "100", "display": "none"},

    return is_open, modal_style, "", "", base_styles["menu-dataset"], base_styles["chat-box"], base_styles[
        "menu-prompt"], base_styles["data-view"], base_styles["snapshot-view"], base_styles["evaluation-view"], \
    base_styles["code-view"], base_styles["report-view"], base_styles, 0, {"position": "fixed", "top": "0", "left": "0",
                                                                           "width": "100%", "height": "100%",
                                                                           "backgroundColor": "rgba(0, 0, 0, 0.5)",
                                                                           "z-index": "100", "display": "none"},


@app.callback(
    Output("overlay", "style", allow_duplicate=True),
    Input("wizard-modal", "is_open"),
    State("overlay", "style"),
    State("next-step", "n_clicks"),
    prevent_initial_call=True,
)
def close_overlay(is_open, overlay_style, n_clicks):
    if not is_open:
        # Hide the overlay if the modal is closed manually (using the close button)
        return {"display": "none"}
    return overlay_style
