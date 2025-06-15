def is_covert_heuristic(src_ip: str) -> bool:
    """
    Heuristic rule:
    If the last octet of the source IP is not 21, consider it a covert packet.
    """
    try:
        last_octet = int(src_ip.strip().split(".")[-1])
        return last_octet != 21
    except Exception as e:
        print(f"[Detector] Error parsing IP '{src_ip}': {e}")
        return False

TP, TN, FP, FN = 0, 0, 0, 0

def update_stats(predicted: bool, actual: bool):
    global TP, TN, FP, FN
    if predicted and actual:
        TP += 1
    elif not predicted and not actual:
        TN += 1
    elif predicted and not actual:
        FP += 1
    elif not predicted and actual:
        FN += 1