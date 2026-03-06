import regex


def _get_cluster_length(cluster: str) -> tuple[int, int]:
    """
    Calculate the 'batch' length of a single grapheme cluster.

    Args:
        cluster (str): A single grapheme cluster.

    Returns:
        tuple[int, int]: (number of base emojis, number of non-emoji characters)
    """
    count = 0
    char_length = 0
    for char in cluster:
        # Skip zero-width joiners only
        if char == "\u200d":
            continue
        # Skip skin tone modifiers (range U+1F3FB to U+1F3FF)
        if 0x1F3FB <= ord(char) <= 0x1F3FF:
            continue
        # If the character has the Emoji property, count it as a base emoji
        if regex.match(r"\p{Emoji}", char):
            count += 1
        else:
            char_length += 1
    return count, char_length


def batch_length(s: str) -> int:
    """
    Calculate the 'batch' length of a string according to Batch API rules.

    Batch's API counts each emoji as 2 characters while other characters are counted
    normally. This function handles complex emoji cases (skin tones, ZWJ sequences, etc.)
    to match Batch's length calculation.

    For details on Unicode Text Segmentation, see:
    - https://unicode.org/reports/tr29/
    - https://pypi.org/project/regex/

    Args:
        s (str): The input string.

    Returns:
        int: The computed 'batch' length of the string.
    """
    graphemes = regex.findall(r"\X", s)
    total = 0
    for cluster in graphemes:
        emoji_count, char_length = _get_cluster_length(cluster)
        total += (emoji_count * 2) + char_length
    return total


def shorten_for_batch(s: str, max_length: int, placeholder: str = "...", preserve_words: bool = False) -> str:
    """
    Truncate a string to meet Batch API length limits while preserving emoji integrity.

    The function ensures the truncated string (including placeholder) doesn't exceed
    max_length according to Batch's counting rules (emojis count as 2 characters).

    By default, truncation is done strictly at the grapheme cluster level, which may cut a word.
    If preserve_words is set to True, the function will try to truncate at the last word boundary
    (i.e., a space) encountered before reaching the limit.

    Args:
        s (str): The input string to truncate.
        max_length (int): The maximum allowed 'batch' length.
        placeholder (str): String to append if truncation occurs (default: "...").
        preserve_words (bool): If True, attempts to preserve word boundaries.

    Returns:
        str: The truncated string with placeholder if needed.
    """
    if batch_length(s) <= max_length:
        return s

    truncated = ""
    current_length = 0
    last_space_index = None
    clusters = regex.findall(r"\X", s)
    truncated_clusters = []  # To keep track of clusters added

    for i, cluster in enumerate(clusters):
        emoji_count, char_length = _get_cluster_length(cluster)
        cluster_length = (emoji_count * 2) + char_length

        # Check if the current cluster is a whitespace, to mark possible word boundary.
        if preserve_words and cluster.isspace():
            last_space_index = i

        if current_length + cluster_length > max_length - batch_length(placeholder):
            # If preserving words and we encountered a space, truncate at that point.
            if preserve_words and last_space_index is not None:
                truncated_clusters = clusters[:last_space_index]
            break
        truncated_clusters.append(cluster)
        current_length += cluster_length

    truncated = "".join(truncated_clusters)
    return truncated + placeholder
