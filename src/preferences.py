import bpy


class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    enable_analytics: bpy.props.BoolProperty(
        name="Enable Usage Analytics",
        description=(
            "Send anonymous usage data to help improve the addon. "
            "No personal data, filenames or scene content is collected."
        ),
        default=False,
    )

    analytics_prompt_dismissed: bpy.props.BoolProperty(
        name="Don't show the analytics prompt",
        description="If enabled, the opt-in popup will not appear after exports",
        default=False,
    )

    def draw(self, context):
        layout = self.layout

        layout.label(text="Privacy", icon="HIDE_OFF")
        layout.prop(self, "enable_analytics")

        if self.enable_analytics:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="What is collected (anonymously):", icon="INFO")
            col.label(text="   \u2022  Export events (format, object count)")
            col.label(text="   \u2022  Addon activation")
            col.label(text="   \u2022  Blender version")
            col.label(text="   \u2022  Anonymized hardware ID (not reversible)")
        else:
            layout.prop(self, "analytics_prompt_dismissed")
