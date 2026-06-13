import fastf1.plotting as pl
from matplotlib import pyplot as plt
from typing import Optional, List, Tuple, Dict
from core.lap_handler import get_best_lap

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

def add_curve_markers(ax, session, driver_name, show_label=True):
    fastest_lap = get_best_lap(session, driver_name)
    car_data = fastest_lap.get_car_data().add_distance()
    circuit_info = session.get_circuit_info()

    ymin, ymax = ax.get_ylim()

    ax.vlines(
        x=circuit_info.corners['Distance'],
        ymin=ymin,
        ymax=ymax,
        color='gray',
        linestyles='dotted'
    )

    if show_label:
        for _, corner in circuit_info.corners.iterrows():
            txt = f"{corner['Number']}{corner['Letter']}"
            ax.text(
                corner['Distance'],
                ymax,
                txt,
                va='bottom',
                ha='center',
                size='small'
            )

def add_telemetry_plot(ax,
                       telemetry,
                       channel: str,
                       driver_name: str,
                       session,
                       distance_col: str = 'Distance',
                       show_curves: bool = True,
                       show_label: bool = True) -> None:
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
    ax.grid(False)

    if show_curves:
        add_curve_markers(ax, session, driver_name, show_label)

def create_telemetry_comparision(telemetry,
                                 driver_name: str,
                                 session,
                                 channels: Optional[List[str]] = None,
                                 figsize: Tuple[int, int] =(12,14),
                                 show_curves: bool = True,
                                 show_label: bool = True):
    if channels is None:
        channels = list(TELEMETRY_CHANNELS.keys())

    invalid_channels = [ch for ch in channels if ch not in TELEMETRY_CHANNELS]
    if invalid_channels:
        raise ValueError(f"Invalid channels {invalid_channels}")

    n_channels = len(channels)
    height_ratios = [TELEMETRY_CHANNELS[ch]['height_ratio'] for ch in channels]

    fig, axs = plt.subplots(
        n_channels, 1,
        sharex=True,
        figsize=figsize,
        gridspec_kw={'height_ratios': height_ratios}
    )

    if n_channels == 1:
        axs = [axs]

    plt.subplots_adjust(hspace=0.05)

    for idx, channel in enumerate(channels):
        show_label = (idx == 0)
        add_telemetry_plot(axs[idx], telemetry, channel, driver_name, session, show_curves=show_curves, show_label=show_label)

    axs[0].legend(loc = 'upper right')
    axs[-1].set_xlabel('Distance (m)')

    return fig

def create_telemetry(telemetry,
                     driver_name: str,
                     session,
                     channels: Optional[List[str]] = None,
                     show_curves: bool = True):
    return create_telemetry_comparision(telemetry, driver_name, session, channels=channels, show_curves=show_curves)

def create_dual_driver_comparision(telemetry_driver1,
                                   driver1_name: str,
                                   telemetry_driver2,
                                   driver2_name: str,
                                   session,
                                   channels: Optional[List[str]] = None,
                                   figsize: Tuple[int, int] =(14,14),
                                   show_curves: bool = True):
    if channels is None:
        channels = list(TELEMETRY_CHANNELS.keys())
        
    n_channels = len(channels)
    height_ratios = [TELEMETRY_CHANNELS[ch]['height_ratio'] for ch in channels]

    fig, axs = plt.subplots(
        n_channels, 1,
        sharex=True,
        figsize=figsize,
        gridspec_kw={'height_ratios': height_ratios}
    )

    if n_channels == 1:
        axs = [axs]

    plt.subplots_adjust(hspace=0.15)

    for idx, channel in enumerate(channels):
        add_telemetry_plot(axs[idx], telemetry_driver1, channel, driver1_name, session)
        add_telemetry_plot(axs[idx], telemetry_driver2, channel, driver2_name, session)

        if show_curves:
            add_curve_markers(axs[idx],session, driver1_name)

    axs[0].legend(loc = 'upper right')
    axs[-1].set_xlabel('Distance (m)')
    fig.suptitle(f'{driver1_name} vs {driver2_name}', fontsize=16, fontweight='bold')

    return fig