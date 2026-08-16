def assert_disjoint_eval(train_rows, eval_rows):
    train_ids = {r["prompt_id"] for r in train_rows}
    eval_ids = {r["prompt_id"] for r in eval_rows}
    overlap = train_ids.intersection(eval_ids)
    if overlap or not train_ids.isdisjoint(eval_ids):
        raise ValueError(f"eval harness leak: overlapping prompt_id set {sorted(overlap)[:5]}")
    return True
