# Canonical bar dictionary

All downstream bars use a UTC-aware `DatetimeIndex` named `time`, sorted and unique, with `open`, `high`, `low`, `close`, and `volume` columns. `is_suspect` is retained when cleaning identifies an unusually large range; suspect observations are flagged, not silently deleted.
