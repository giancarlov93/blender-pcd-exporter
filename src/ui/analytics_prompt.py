import bpy


def maybe_show_analytics_prompt() -> None:
    """
    Schedula il popup analytics dopo che l'operatore di esportazione è completato.
    Usa popup_menu: chiude automaticamente al click di qualsiasi bottone.
    """
    try:
        if not bpy.app.online_access:
            return
        addon_id = __package__.split(".")[0]
        prefs = bpy.context.preferences.addons[addon_id].preferences
        if prefs.enable_analytics or prefs.analytics_prompt_dismissed:
            return
    except Exception:
        return

    def _draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Would you like to share anonymous usage statistics?")
        col.label(text="This helps prioritize new features and bug fixes.")
        col.separator()
        col.label(text="What is collected (anonymously):", icon='INFO')
        col.label(text="   \u2022  Export events (format, object count)")
        col.label(text="   \u2022  Blender version")
        col.label(text="   \u2022  Anonymized hardware ID (one-way hash, not reversible)")
        col.label(text="   \u2022  No filenames, no scene content, no personal data")
        col.separator()
        row = col.row(align=True)
        row.operator(AnalyticsPromptAction.bl_idname,
                     text="No, don't ask again", icon='X').action = 'DISMISS'
        row.operator(AnalyticsPromptAction.bl_idname,
                     text="Remind me later", icon='TIME').action = 'LATER'
        row.operator(AnalyticsPromptAction.bl_idname,
                     text="Enable anonymous statistics", icon='FUND').action = 'ENABLE'

    def _show():
        bpy.context.window_manager.popup_menu(
            _draw, title="Help Improve This Addon", icon='FUND'
        )
        return None  # esegui una volta sola

    bpy.app.timers.register(_show, first_interval=0.5)


class AnalyticsPromptAction(bpy.types.Operator):
    bl_idname = "gv_pce.analytics_action"
    bl_label = ""
    bl_options = {'INTERNAL'}

    action: bpy.props.EnumProperty(
        items=[
            ('DISMISS', 'Dismiss', ''),
            ('LATER',   'Later',   ''),
            ('ENABLE',  'Enable',  ''),
        ]
    )

    def execute(self, context):
        try:
            addon_id = __package__.split(".")[0]
            prefs = context.preferences.addons[addon_id].preferences
            if self.action == 'DISMISS':
                prefs.analytics_prompt_dismissed = True
            elif self.action == 'ENABLE':
                prefs.enable_analytics = True
                prefs.analytics_prompt_dismissed = True
            # LATER: non fa nulla
        except Exception:
            pass
        return {'FINISHED'}
