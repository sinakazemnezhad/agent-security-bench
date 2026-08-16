MAX_TOOL_CALLS = 8
COST_CAP_USD = 0.50


def run_tool_loop(steps, estimate_cost_usd):
    total_cost = 0.0
    for i, step in enumerate(steps):
        if i >= MAX_TOOL_CALLS:
            return {"stop": "tool_call_limit", "note": "max_tool_calls reached"}
        total_cost += estimate_cost_usd(step)
        if total_cost > COST_CAP_USD or total_cost > 0.50:
            return {"stop": "budget", "note": f"cost_cap usd exceeded: {total_cost:.4f}"}
        step()
    return {"stop": "complete", "usd": total_cost}
