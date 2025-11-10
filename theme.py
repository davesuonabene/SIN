import dearpygui.dearpygui as dpg

def apply_theme():
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (18, 18, 18), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (24, 24, 24), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (20, 20, 20), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 30, 30), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (50, 50, 50), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (20, 20, 20), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Header, (40, 40, 40), category=dpg.mvThemeCat_Core)

            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 4, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 6, 4, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_PopupBorderSize, 0, category=dpg.mvThemeCat_Core)

        with dpg.theme_component(dpg.mvNode):
            dpg.add_theme_color(dpg.mvNodeCol_TitleBar, (40, 40, 40), category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_color(dpg.mvNodeCol_NodeBackground, (30, 30, 30), category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_color(dpg.mvNodeCol_NodeBackgroundHovered, (35, 35, 35), category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_color(dpg.mvNodeCol_NodeBackgroundSelected, (35, 35, 35), category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_color(dpg.mvNodeCol_NodeOutline, (0, 0, 0, 0), category=dpg.mvThemeCat_Nodes)
            

        with dpg.theme_component(dpg.mvNodeAttribute):
            dpg.add_theme_color(dpg.mvNodeCol_Pin, (150, 150, 150), category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_color(dpg.mvNodeCol_PinHovered, (200, 200, 200), category=dpg.mvThemeCat_Nodes)

        with dpg.theme_component(dpg.mvNodeLink):
            dpg.add_theme_color(dpg.mvNodeCol_Link, (150, 150, 150), category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_color(dpg.mvNodeCol_LinkHovered, (200, 200, 200), category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_color(dpg.mvNodeCol_LinkSelected, (200, 200, 200), category=dpg.mvThemeCat_Nodes)

    dpg.bind_theme(global_theme)