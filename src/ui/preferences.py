import bpy


class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__.split(".")[0]  # "gv_point_cloud_exporter" (top-level package)

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

    review_prompt_dismissed: bpy.props.BoolProperty(
        name="Review prompt dismissed",
        description="Internal flag to track if the user has left a review",
        default=False,
    )

    next_review_target: bpy.props.IntProperty(
        name="Next Review Target",
        description="The number of exports required before showing the next review prompt",
        default=5,
    )

    export_count: bpy.props.IntProperty(
        name="Total Exports",
        description="Number of times the user has exported a file using the addon",
        default=0,
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
