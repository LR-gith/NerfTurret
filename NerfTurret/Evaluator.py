import numpy as np
import matplotlib.pyplot as plt

class Evaluator:

    def __init__(self):
        self.detection = np.empty((0, 2))

    def addDetection(self, x, y):
        if self.detection.shape[0] > 2:
            self.detection = np.delete(self.detection, 0, axis=0)
        new_row = np.array([[x, y]])
        self.detection = np.vstack([self.detection, new_row])
        print(self.detection, "\n")

    def interpolate(self):
        x = self.detection[:, 0]
        y = self.detection[:, 1]
        # Step 2: Fit a 2nd-degree polynomial (quadratic curve) through the points
        coefficients = np.polyfit(x, y, 2)  # Returns coefficients [a, b, c] for ax^2 + bx + c
        polynomial = np.poly1d(coefficients)

        # Step 3: Generate x values for plotting the curve
        x_curve = np.linspace(min(x), max(x), 100)
        y_curve = polynomial(x_curve)

        # Step 4: Plot the points and the curve
        plt.plot(x_curve, y_curve, label='Fitted Curve')
        plt.scatter(x, y, color='red', label='Given Points')
        plt.title("Quadratic Curve Through 3 Points")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend()
        plt.grid(True)
        plt.show()
