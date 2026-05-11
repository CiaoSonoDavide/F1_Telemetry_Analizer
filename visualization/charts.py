import fastf1.plotting as pl
import plotly.graph_objects as go
from matplotlib import pyplot as plt


def create_speed_chart(telemetry, driver_name, session):
    fig = go.Figure()

    fig, ax = plt.subplots(figsize=(8,5))
    style = pl.get_driver_style(identifier=driver_name,
                                style=['color', 'linestyle'],
                                session=session)
    ax.plot(telemetry['Distance'], telemetry['Speed'], label=driver_name, **style)
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Speed (km/h)')
    ax.legend()
    plt.title(f"Speed Trace - {driver_name}")
    return fig