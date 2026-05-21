import fastf1.plotting as pl
from matplotlib import pyplot as plt

def get_driver_style(driver_abbr, session):
    return pl.get_driver_style(identifier=driver_abbr,
                                style=['color', 'linestyle'],
                                session=session)

def add_speed_plot(ax, telemetry, driver_name, session):
    style = get_driver_style(driver_name, session)
    ax.plot(telemetry['Distance'], telemetry['Speed'], label = driver_name, **style)
    ax.set_ylabel('Speed (km/h)')

def add_rpm_plot(ax, telemetry, driver_name, session):
    style = get_driver_style(driver_name, session)
    ax.plot(telemetry['Distance'], telemetry['RPM'], label = driver_name, **style)
    ax.set_ylabel('RPM')

def add_throttle_plot(ax, telemetry, driver_name, session):
    style = get_driver_style(driver_name, session)
    ax.plot(telemetry['Distance'], telemetry['Throttle'], label = driver_name, **style)
    ax.set_ylabel('Throttle')

def add_brake_plot(ax, telemetry, driver_name, session):
    style = get_driver_style(driver_name, session)
    ax.plot(telemetry['Distance'], telemetry['Brake'], label = driver_name, **style)
    ax.set_ylabel('Brake')

def add_drs_plot(ax, telemetry, driver_name, session):
    style = get_driver_style(driver_name, session)
    ax.plot(telemetry['Distance'], telemetry['DRS'], label = driver_name, **style)
    ax.set_ylabel('DRS')

def add_gear_plot(ax, telemetry, driver_name, session):
    style = get_driver_style(driver_name, session)
    ax.plot(telemetry['Distance'], telemetry['nGear'], label = driver_name, **style)
    ax.set_ylabel('NGear')

def create_telemetry(telemetry, driver_name, session):
    AXS = {
        'speed': 0,
        'rpm': 1,
        'throttle': 2,
        'brake': 3,
        'drs': 4,
        'gear': 5
    }

    fig, axs = plt.subplots(
        6, 1,
        sharex = True,
        figsize = (10,13),
        gridspec_kw = {'height_ratios': [5, 5, 5, 5, 5, 5]}
    )

    plt.subplots_adjust(hspace = 0.05)

    add_speed_plot(axs[AXS['speed']], telemetry, driver_name, session)
    add_rpm_plot(axs[AXS['rpm']], telemetry, driver_name, session)
    add_throttle_plot(axs[AXS['throttle']], telemetry, driver_name, session)
    add_brake_plot(axs[AXS['brake']], telemetry, driver_name, session)
    add_drs_plot(axs[AXS['drs']], telemetry, driver_name, session)
    add_gear_plot(axs[AXS['gear']], telemetry, driver_name, session)

    axs[0].legend()
    axs[5].set_xlabel('Distance (m)')
    fig.suptitle(f"Telemetry Analysis - {driver_name}")
    return fig
