def clean_ffmpeg_error(stderr: str) -> str:
    """
    Strips the noisy ffmpeg banner and configuration from stderr, 
    leaving only the actual error messages at the end.
    """
    if not stderr:
        return ""
        
    lines = stderr.splitlines()
    cleaned_lines = []
    
    # Filter out common banner/diagnostic noise
    skip_keywords = [
        "ffmpeg version", "built with", "configuration:", "libavutil", 
        "libavcodec", "libavformat", "libavdevice", "libavfilter", 
        "libswscale", "libswresample", "libpostproc"
    ]
    
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
        # Skip lines that look like version info or configuration
        if any(keyword in line_strip for keyword in skip_keywords):
            continue
        # Skip lines that are just indented configuration details
        if line.startswith("  ") and not (line_strip.startswith("[") or "Error" in line_strip):
            continue
            
        cleaned_lines.append(line_strip)
        
    return "\n".join(cleaned_lines)
