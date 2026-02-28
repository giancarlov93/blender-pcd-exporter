import bpy

def show_review_prompt() -> None:
    """
    Schedules the review prompt popup.
    """
    def _draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Loving the addon?")
        col.label(text="Please consider leaving a review to help others find it.")
        
        row = col.row(align=True)
        # Remind me later option
        row.operator(ReviewPromptAction.bl_idname,
                     text="Remind me later", icon='TIME').action = 'LATER'
        # Leave a review
        row.operator(ReviewPromptAction.bl_idname,
                     text="Leave a Review!", icon='URL').action = 'LEAVE_REVIEW'

    def _show():
        bpy.context.window_manager.popup_menu(
            _draw, title="Support GV Point Cloud Exporter", icon='GREASEPENCIL'
        )
        return None  # run only once

    bpy.app.timers.register(_show, first_interval=0.5)

class ReviewPromptAction(bpy.types.Operator):
    bl_idname = "gv_pce.review_action"
    bl_label = ""
    bl_options = {'INTERNAL'}

    action: bpy.props.EnumProperty(
        items=[
            ('LATER', 'Later', ''),
            ('LEAVE_REVIEW', 'Leave Review', ''),
        ]
    )

    def execute(self, context):
        try:
            addon_id = __package__.split(".")[0]
            prefs = context.preferences.addons[addon_id].preferences
            if self.action == 'LEAVE_REVIEW':
                prefs.review_prompt_dismissed = True
                bpy.ops.wm.url_open(url="https://extensions.blender.org/add-ons/gv-point-cloud-exporter/reviews/new/")
            elif self.action == 'LATER':
                # Shift target forward by 25
                prefs.next_review_target += 25
        except Exception as e:
            print(f"Error handling review action: {e}")
        return {'FINISHED'}
