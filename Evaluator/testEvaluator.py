from Evaluator import Evaluator

ev = Evaluator()
ev.addDetection(1,2)
ev.addDetection(2,2)
ev.addDetection(1.1,3)

ev.interpolate()

ev.addDetection(3,3)
ev.addDetection(1,10)
ev.interpolate()