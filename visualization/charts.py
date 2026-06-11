import fastf1.plotting as pl
from matplotlib import pyplot as plt
from typing import Optional, List, Tuple

TELEMETRY_CHANNELS = {
    'Speed': {
        'label': 'Speed',
        'ylabel': 'Speed (km/h)',
        'height_ratio': 5
    },
    'RPM': {
        'label': 'RPM',
        'ylabel': 'RPM',
        'height_ratio': 5
    },
    'Throttle': {
        'label': 'Throttle',
        'ylabel': 'Throttle (%)',
        'height_ratio': 5
    },
    'Brake': {
        'label': 'Brake',
        'ylabel': 'Brake (%)',
        'height_ratio': 5
    },
    'DRS': {
        'label': 'DRS',
        'ylabel': 'DRS Status',
        'height_ratio': 5
    },
    'nGear': {
        'label': 'nGear',
        'ylabel': 'Gear Number',
        'height_ratio': 5
    }
}

def get_driver_style(driver_abbr, session):
    return pl.get_driver_style(identifier=driver_abbr,
                                style=['color', 'linestyle'],
                                session=session)

def add_telemetry_plot(ax,
                       telemetry,
                       channel: str,
                       driver_name: str,
                       session,
                       distance_col: str = 'Distance') -> None:
    if channel not in telemetry.columns:
        raise ValueError(f"Channel {channel} not found in telemetry data")

    style = get_driver_style(driver_name, session)
    config = TELEMETRY_CHANNELS.get(channel, {})

    ax.plot(
        telemetry[distance_col],
        telemetry[channel],
        label = driver_name,
        **style
    )

    ax.set_ylabel(config.get('ylabel', channel))
    ax.grid(True, alpha=0.3)

def create_telemetry_comparision(telemetry,
                                 driver_name: str,
                                 session,
                                 channels: Optional[List[str]] = None,
                                 figsize: Tuple[int, int] =(12,14)):
    if channels is None:
        channels = list(TELEMETRY_CHANNELS.keys())

    invalid_channels = [ch for ch in channels if ch not in TELEMETRY_CHANNELS]
    if invalid_channels:
        raise ValueError(f"Invalid channels {invalid_channels}")

    n_channels = len(channels)
    height_ratio = [TELEMETRY_CHANNELS[ch]['height_ratio'] for ch in channels]

    fig, axs = plt.subplots(
        n_channels, 1,
        sharex=True,
        figsize=figsize,
        gridspec_kw={'height_ratios': height_ratio}
    )

    if n_channels == 1:
        axs = [axs]

    plt.subplots_adjust(hspace=0.05)

    for idx, channel in enumerate(channels):
        add_telemetry_plot(axs[idx], telemetry, channel, driver_name, session)

    axs[0].legend(loc = 'upper right')
    axs[-1].set_xlabel('Distance (m)')

    return fig

def create_telemetry(telemetry,
                     driver_name: str,
                     session):
    return create_telemetry_comparision(telemetry, driver_name, session)
