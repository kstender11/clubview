def get_oembed(ig_url: str) -> str:
    if not ig_url:
        return None
    # Return a mock embed string for now
    return f'<iframe src="{ig_url}/embed" width="400" height="480"></iframe>'
