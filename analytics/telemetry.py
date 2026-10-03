from __future__ import annotations
from typing import Iterable
import numpy as np
import pandas as pd

CONTINUOUS_CHANNELS = {
    "Speed",
    "RPM",
    "Throttle",
    "Brake"
}

DISCRETE_CHANNELS = {
    "DRS",
    "nGear"
}

def prepare_telemetry(telemetry: pd.DataFrame) -> pd.DataFrame:
    if telemetry is None or telemetry.empty:
        raise ValueError("Telemetry data is empty or None.")

    if "Distance" not in telemetry.columns:
        raise ValueError("Telemetry data must contain a 'Distance' column.")

    result = telemetry.copy()
    result = result.dropna(subset=["Distance"])
    result = result.drop_duplicates(subset=["Distance"], keep="first")

    if result.empty:
        raise ValueError("Telemetry doesn't contain valid distance.")

    return result.reset_index(drop=True)

def interpolate_continuous(source: pd.DataFrame, target_distance: np.array, channel: str) -> np.array:
    if channel not in source.columns:
        return np.full(target_distance.shape, np.nan, dtype=float)

    values = pd.to_numeric(source[channel], errors="coerce")
    valid = (source["Distance"].notna() & values.notna())

    if valid.sum() < 2:
        return np.full(target_distance.shape, np.nan, dtype=float)

    source_distance = (source.loc[valid, "Distance"].to_numpy(dtype=float))
    source_values = (values.loc[valid].to_numpy(dtype=float))

    return np.interp(target_distance, source_distance, source_values)

def interpolate_discrete(source: pd.DataFrame, target_distance: np.array, channel: str) -> np.array:
    if channel not in source.columns:
        return np.full(target_distance.shape, np.nan)

    values = source[channel]

    valid = (source["Distance"].notna() & values.notna())

    if valid.sum() == 0:
        return np.full(target_distance.shape, np.nan)

    source_distance = (source.loc[valid, "Distance"].to_numpy(dtype=float))
    source_values = (values.loc[valid].to_numpy(dtype=float))

    right_indexes = np.searchsorted(source_distance, target_distance, side="left")
    right_indexes = np.clip(right_indexes, 0, len(source_distance) - 1)

    left_indexes = np.clip(right_indexes - 1, 0, len(source_distance) - 1)

    left_distance = source_distance[left_indexes]
    right_distance = source_distance[right_indexes]

    use_right = (np.abs(target_distance - right_distance) < np.abs(target_distance - left_distance))

    nearest_indexes = np.where(use_right, right_indexes, left_indexes)

    return source_values[nearest_indexes]

def interpolate_telemetry_by_distance(telemetry1: pd.DataFrame, telemetry2: pd.DataFrame,
                                      channels: Iterable[str] | None = None, step: float = 1.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    if step <= 0:
        raise ValueError("Step must be a positive number.")

    data1 = prepare_telemetry(telemetry1)
    data2 = prepare_telemetry(telemetry2)

    if channels is None:
        requested_channels = (CONTINUOUS_CHANNELS | DISCRETE_CHANNELS)
    else:
        requested_channels = set(channels)

    common_min_distance = max(float(data1["Distance"].min()), float(data2["Distance"].min()))
    common_max_distance = max(float(data1["Distance"].max()), float(data2["Distance"].max()))

    if common_min_distance >= common_max_distance:
        raise ValueError("Telemetry data does not have overlapping distance ranges for interpolation.")

    target_distance = np.arange(common_min_distance, common_max_distance, step, dtype=float)

    result1 = pd.DataFrame({"Distance": target_distance})
    result2 = pd.DataFrame({"Distance": target_distance})

    for channel in requested_channels:
        if channel in CONTINUOUS_CHANNELS:
            result1[channel] = interpolate_continuous(data1, target_distance, channel)
            result2[channel] = interpolate_continuous(data2, target_distance, channel)
        elif channel in DISCRETE_CHANNELS:
            result1[channel] = interpolate_discrete(data1, target_distance, channel)
            result2[channel] = interpolate_discrete(data2, target_distance, channel)
        else:
            raise ValueError(f"Channel '{channel}' is not recognized as continuous or discrete.")

    return result1, result2