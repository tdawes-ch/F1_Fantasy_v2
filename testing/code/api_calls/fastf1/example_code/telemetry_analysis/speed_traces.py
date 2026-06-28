import matplotlib.pyplot as plt
import fastf1.plotting

# Enable Matplotlib patches for plotting timedelta values and load
# FastF1's dark color scheme
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')

# load a session and its telemetry data
session = fastf1.get_session(2021, 'Spanish Grand Prix', 'Q')
session.load()

# Select the two laps that we want to compare
ver_lap = session.laps.pick_drivers('VER').pick_fastest()
ham_lap = session.laps.pick_drivers('HAM').pick_fastest()

# Get the telemetry data for each lap and add distance column
ver_tel = ver_lap.get_car_data().add_distance()
ham_tel = ham_lap.get_car_data().add_distance()

# Create the plot with team colors
rbr_color = fastf1.plotting.get_team_color(ver_lap['Team'], session=session)
mer_color = fastf1.plotting.get_team_color(ham_lap['Team'], session=session)

fig, ax = plt.subplots()
ax.plot(ver_tel['Distance'], ver_tel['Speed'], color=rbr_color, label='VER')
ax.plot(ham_tel['Distance'], ham_tel['Speed'], color=mer_color, label='HAM')

ax.set_xlabel('Distance in m')
ax.set_ylabel('Speed in km/h')
ax.legend()
plt.suptitle(f"Fastest Lap Comparison \n "
             f"{session.event['EventName']} {session.event.year} Qualifying")

plt.show()