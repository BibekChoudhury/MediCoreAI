"""
Backward-compatible wrappers for older imports.
Prefer importing from utils.patient_context in new code.
"""

from utils.patient_context import (  # noqa: F401
    build_missing_context_warnings,
    calculate_profile_completeness,
    format_patient_context_for_prompt as format_context_for_prompt,
    get_or_create_patient_profile,
    get_patient_context as get_user_context,
)
