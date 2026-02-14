import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.integrate import odeint

# --- Configuration ---
# Masses (kg)
m1 = 1.0
m2 = 1.0
# Lengths (m)
L1 = 1.0
L2 = 1.0
# Gravity (m/s^2)
g = 9.81
# Duration and Time steps
t_stop = 20.0
dt = 0.04
t = np.arange(0, t_stop, dt)

# --- Physics Engine ---
def derivs(state, t):
    # Unpack state: theta1, omega1, theta2, omega2
    theta1, w1, theta2, w2 = state
    
    # Differential equations for Double Pendulum
    # These are derived from the Lagrangian of the system
    delta = theta2 - theta1
    den1 = (m1 + m2) * L1 - m2 * L1 * np.cos(delta) * np.cos(delta)
    den2 = (L2 / L1) * den1

    dw1dt = (m2 * L1 * w1 * w1 * np.sin(delta) * np.cos(delta) +
             m2 * g * np.sin(theta2) * np.cos(delta) +
             m2 * L2 * w2 * w2 * np.sin(delta) -
             (m1 + m2) * g * np.sin(theta1)) / den1

    dw2dt = (-m2 * L2 * w2 * w2 * np.sin(delta) * np.cos(delta) +
             (m1 + m2) * g * np.sin(theta1) * np.cos(delta) -
             (m1 + m2) * L1 * w1 * w1 * np.sin(delta) -
             (m1 + m2) * g * np.sin(theta2)) / den2

    return [w1, dw1dt, w2, dw2dt]

# Initial State: [theta1, omega1, theta2, omega2]
# High initial angles create more chaotic motion
state0 = [np.pi/2, 0, np.pi/2, 0]

# Solve ODE
solution = odeint(derivs, state0, t)

# Calculate x, y positions
theta1 = solution[:, 0]
theta2 = solution[:, 2]

x1 = L1 * np.sin(theta1)
y1 = -L1 * np.cos(theta1)
x2 = x1 + L2 * np.sin(theta2)
y2 = y1 - L2 * np.cos(theta2)

# --- Visualization ---
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(-(L1 + L2 + 0.5), (L1 + L2 + 0.5))
ax.set_ylim(-(L1 + L2 + 0.5), (L1 + L2 + 0.5))
ax.set_aspect('equal')
ax.grid(False)
ax.set_facecolor('black') # Dark background for "Instagram" look

# Elements to animate
line, = ax.plot([], [], 'o-', lw=2, color='white') # The rods and masses
trace, = ax.plot([], [], '-', lw=1, color='cyan', alpha=0.8) # The trail
time_template = 'Time = %.1fs'
time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes, color='white')

# History for the trace (store last N points)
history_len = 100
history_x, history_y = [], []

def animate(i):
    # Current positions
    thisx = [0, x1[i], x2[i]]
    thisy = [0, y1[i], y2[i]]
    
    # Update pendulum arm
    line.set_data(thisx, thisy)
    
    # Update trail
    if i == 0:
        history_x.clear()
        history_y.clear()
    
    history_x.append(x2[i])
    history_y.append(y2[i])
    
    # Keep trail to a fixed length
    if len(history_x) > history_len:
        history_x.pop(0)
        history_y.pop(0)
        
    trace.set_data(history_x, history_y)
    
    # Update time text
    time_text.set_text(time_template % (i*dt))
    
    return line, trace, time_text

ani = animation.FuncAnimation(fig, animate, len(t), interval=dt*1000, blit=True)

plt.title("Double Pendulum Chaos", color='white')
plt.show()