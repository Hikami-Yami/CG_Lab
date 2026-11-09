from model import Model
from canvas import Canvas
from app import App
import time

if __name__ == '__main__':
    start = time.process_time()

    canvas = Canvas(5000,5000)
    model = Model('model.obj')
    app = App(model, canvas)
    app.run()

    end = time.process_time()
    execution_time = end - start
    print(f"Время выполнения: {execution_time:.4f} сек")

