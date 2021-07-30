"""
====================================
Streaming FURY with user interaction
====================================

"""
from fury import actor, window
import numpy as np

import multiprocessing
from fury.stream.server import web_server
from fury.stream.client import FuryStreamClient, FuryStreamInteraction
import logging
logging.root.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    interactive = True
    use_raw_array = False
    use_high_res = False
    if use_high_res:
        window_size = (1280, 720)
        max_window_size = (1920, 1080)
    else:
        window_size = (300, 300)
        max_window_size = (400, 400)
    # 0 ms_stream means that the frame will be sent to the server
    # right after the rendering

    ms_interaction = 1
    ms_stream = 0
    # max number of interactions to be stored inside the queue
    max_queue_size = 17
    ######################################################################
    centers = np.array([
        [0, 0, 0],
        [-1, 0, 0],
        [1, 0, 0]
    ])
    colors = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ])

    actors = actor.sphere(
        centers, opacity=.5, radii=.4, colors=colors)
    scene = window.Scene()

    scene.add(actors)

    showm = window.ShowManager(
        scene, size=(window_size[0], window_size[1])
    )

    ###########################################################################
    # ms define the amount of mileseconds that will be used in the timer event.
    # Otherwise, if ms it's equal to zero the shared memory it's updated at
    # each  render event
    # showm.window.SetOffScreenRendering(1)
    # showm.window.EnableRenderOff()
    showm.initialize()

    stream = FuryStreamClient(
        showm, max_window_size=max_window_size,
        use_raw_array=use_raw_array)
    stream_interaction = FuryStreamInteraction(
        showm, max_queue_size=max_queue_size,
        use_raw_array=use_raw_array)

    if use_raw_array:
        p = multiprocessing.Process(
            target=web_server,
            args=(
                stream.img_manager.image_buffers,
                None,
                stream.img_manager.info_buffer,
                None,
                stream_interaction.circular_queue.head_tail_buffer,
                None,
                stream_interaction.circular_queue.buffer._buffer,
                None,
                8000,
                'localhost',
                True,
                True,
                True
            )
        )

    else:
        p = multiprocessing.Process(
            target=web_server,
            args=(
                None,
                stream.img_manager.image_buffer_names,
                None,
                stream.img_manager.info_buffer_name,
                None,
                stream_interaction.circular_queue.head_tail_buffer_name,
                None,
                stream_interaction.circular_queue.buffer.buffer_name,
                8000,
                'localhost',
                True,
                True,
                True
            )
        )
    p.start()
    stream_interaction.start(ms=ms_interaction)
    stream.start(ms_stream,)
    if interactive:
        showm.start()
    p.kill()
    stream.stop()
    stream_interaction.stop()
    stream.cleanup()
    stream_interaction.cleanup()
    # open a browser using the following the url
    # http://localhost:8000/

    window.record(
        showm.scene, size=window_size, out_path="viz_interaction.png")
