def sensitivity(values: dict, evaluator):
    """Evaluate a parameter grid and return the best setting by profit factor."""
    rows = []
    for name, options in values.items():
        for value in options:
            metrics = evaluator({name: value})
            rows.append({"parameter": name, "value": value, **metrics})
    return sorted(rows, key=lambda row: row.get("profit_factor", 0) or 0, reverse=True)
