import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport(title='Theme Test', width=600, height=400)

with dpg.window(label="Line Chart Test", width=600, height=400):
    with dpg.plot(label="Example", height=-1, width=-1):
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        with dpg.plot_axis(dpg.mvYAxis, label="y") as y_axis:
            line_tag = dpg.add_line_series([0, 1, 2, 3], [0, 1, 0, 1], parent=y_axis, label="Test")

# define theme
with dpg.theme() as line_theme:
    with dpg.theme_component(dpg.mvLineSeries):
        dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 0, 0, 255))  # red

# bind theme to line
dpg.bind_item_theme(line_tag, line_theme)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
