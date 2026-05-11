import plotly.graph_objects as go

def create_speed_chart(telemetry, driver_name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x = telemetry['Distance'],
        y = telemetry['Speed'],
        mode = 'lines',
        name = driver_name,
        line = dict(color='cyan', width=2)
    ))

    fig.update_layout(
        title = f"Speed Trace - {driver_name}",
        xaxis_title = "Distance (m)",
        yaxis_title = "Speed (km/h)",
        template = 'plotly_dark'
    )
    return fig