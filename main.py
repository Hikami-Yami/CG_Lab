from model import Model
from canvas import Canvas
import time

if __name__ == '__main__':
    start = time.process_time()

    canvas = Canvas(1000,1000)
    m = Model('model.obj')
    canvas.render_model(m)
    canvas.save('image.png')

    end = time.process_time()
    execution_time = end - start
    print(f"Время выполнения: {execution_time:.4f} сек")