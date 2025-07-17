from src.turret.pi_controller import PiController

controller = PiController(verbose=True)

try:
    while True:
        time1 = float(input("Enter time for charge (0.0-5.0): "))
        time2 = float(input("Enter time for load (0.0-1.0): "))
        if 0.0 <= time1 <= 5.0 and 0.0 <= time2 <= 1.0:
            controller.charge(time1)
            controller.load(time2)
        else:
            print("Time must be between 0.0 and 5.0.")

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    controller.stop()
