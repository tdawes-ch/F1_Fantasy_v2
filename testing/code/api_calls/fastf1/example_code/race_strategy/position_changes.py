import matplotlib.pyplot as plt
import fastf1.plotting

fastf1.plotting.setup_mpl(mpl_timedelta_support=False, color_scheme='fastf1')

# Load the session
session = fastf1.get_session(2023, 1, 'R')
session.load(telemetry=False, weather=False)

fig, ax = plt.subplots(figsize=(8.0, 4.9))

# For each driver, plot their position over the laps
for drv in session.drivers:
    drv_laps = session.laps.pick_drivers(drv)
    
    abb = drv_laps['Driver'].iloc[0]
    style = fastf1.plotting.get_driver_style(identifier=abb,
                                             style=['color', 'linestyle'],
                                             session=session)
    
    ax.plot(drv_laps['LapNumber'], drv_laps['Position'],
            label=abb, **style)

# Finalize the plot
ax.set_ylim([20.5, 0.5])
ax.set_yticks([1, 5, 10, 15, 20])
ax.set_xlabel('Lap')
ax.set_ylabel('Position')

# Add legend outside the plot area
ax.legend(bbox_to_anchor=(1.0, 1.02))
plt.tight_layout()

plt.show()