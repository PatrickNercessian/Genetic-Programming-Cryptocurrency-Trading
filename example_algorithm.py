# Just to visualize what an algorithm could look like, no actual use
def decision_example1(csv_df):
    should_buy = True
    stop_loss = 0
    confidence = 1.0

    # This should be what results from the tree
    recent_rsi = csv_df.rsi[-1]
    recent_close = csv_df.close[-1]
    if recent_rsi < 30:
        should_buy = True
        stop_loss = recent_close * 0.95
        confidence = (30 - recent_rsi) / 30

    return should_buy, stop_loss, confidence

