import bpy
from .analytics_prompt import show_analytics_prompt
from .review_prompt import show_review_prompt

def check_prompts() -> None:
    """
    Called after a successful export.
    Increments export count and determines if any prompts should be shown.
    Only one prompt can be shown per export to avoid overlaps.
    """
    try:
        addon_id = __package__.split(".")[0]
        prefs = bpy.context.preferences.addons[addon_id].preferences
        
        # Increment export count
        prefs.export_count += 1
        
        # 1. Analytics Prompt (Highest Priority)
        # Check if we should show the analytics prompt
        if bpy.app.online_access:
            if not prefs.enable_analytics and not prefs.analytics_prompt_dismissed:
                show_analytics_prompt()
                return # Exit early so we don't show the review prompt
            
        # 2. Review Prompt Check
        if not prefs.review_prompt_dismissed:
            if prefs.export_count >= prefs.next_review_target:
                show_review_prompt()
                return

    except Exception as e:
        print(f"Error checking prompts: {e}")
