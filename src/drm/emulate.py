import io
import logging
import numpy as np
import random
import traceback
from datetime import datetime
from time import sleep

from opex import ObjectPredictions, ObjectPrediction, BBox, Polygon
from PIL import Image
from rdh import Container, MessageContainer, create_parser, configure_redis, run_harness, log
from wai.logging import init_logging, set_logging_level, add_logging_level


EMULATE = "drm-emulate"

_logger = logging.getLogger(EMULATE)


OUTPUT_INDEXED_PNG = "indexed-png"
OUTPUT_GRAYSCALE_PNG = "grayscale-png"
OUTPUT_BLUECHANNEL_PNG = "bluechannel-png"
OUTPUT_OPEX = "opex"
OUTPUTS = [
    OUTPUT_BLUECHANNEL_PNG,
    OUTPUT_GRAYSCALE_PNG,
    OUTPUT_INDEXED_PNG,
    OUTPUT_OPEX,
]


def input_is_image(output: str) -> bool:
    """
    Determines whether the input for the specified output type is an image.

    :param output: the output that is to be generated
    :type output: str
    :return: True if input must be an image
    :rtype: bool
    """
    return output in [OUTPUT_BLUECHANNEL_PNG, OUTPUT_GRAYSCALE_PNG, OUTPUT_INDEXED_PNG, OUTPUT_OPEX]


def process_data(msg_cont):
    """
    Processes the message container, forwards the predictions.

    :param msg_cont: the message container to process
    :type msg_cont: MessageContainer
    """
    config = msg_cont.params.config

    try:
        start_time = datetime.now()
        if config.verbose:
            log("process_data - start processing data")

        data_out = None
        if input_is_image(config.output):
            img = Image.open(io.BytesIO(msg_cont.message['data']))
            w, h = img.size
            if config.output in [OUTPUT_BLUECHANNEL_PNG, OUTPUT_GRAYSCALE_PNG, OUTPUT_INDEXED_PNG]:
                out = None
                if config.output == OUTPUT_BLUECHANNEL_PNG:
                    if config.labels is not None:
                        arr = np.zeros((w, h, 3), dtype=np.uint8)
                        arr_blue = np.random.rand(w, h, 1) * (len(config.labels)+1)
                        arr[:, :, 2] = arr_blue[:, :, 0]
                        out = Image.fromarray(arr.astype('uint8')).convert('RGB')
                    else:
                        out = Image.new('RGB', (w, h))
                elif config.output == OUTPUT_GRAYSCALE_PNG:
                    if config.labels is not None:
                        arr = np.zeros((w, h, 3), dtype=np.uint8)
                        arr_gray = np.random.randint(0, len(config.labels)+1, (w, h, 1), dtype=np.uint8)
                        arr[:, :, 0] = arr_gray[:, :, 0]
                        arr[:, :, 1] = arr_gray[:, :, 0]
                        arr[:, :, 2] = arr_gray[:, :, 0]
                        out = Image.fromarray(arr).convert('L')
                    else:
                        out = Image.new('L', (w, h))
                elif config.output == OUTPUT_INDEXED_PNG:
                    if config.labels is not None:
                        arr = np.random.randint(0, len(config.labels)+1, (w, h), dtype=np.uint8)
                        out = Image.fromarray(arr).convert('P')
                    else:
                        out = Image.new('P', (w, h))
                if out is not None:
                    buf = io.BytesIO()
                    out.save(buf, format="PNG")
                    data_out = buf.getvalue()
            elif config.output == OUTPUT_OPEX:
                objs = []
                if config.num_objects > 0:
                    for i in range(config.num_objects):
                        x = random.randint(1, w)
                        y = random.randint(1, h)
                        w = random.randint(1, w)
                        h = random.randint(1, h)
                        label = "object"
                        if config.labels is not None:
                            label = config.labels[random.randint(0, len(config.labels)-1)]
                        bbox = BBox(left=x, top=y, right=x+w-1, bottom=y+h-1)
                        poly = Polygon(points=[[x, y], [x+w-1, y], [x+w-1, y+h-1], [x, y+h-1]])
                        obj = ObjectPrediction(label=label, bbox=bbox, polygon=poly)
                        objs.append(obj)
                preds = ObjectPredictions(id=start_time.strftime("%Y%m%d-%H%M%S.%f"), objects=objs)
                data_out = preds.to_json_string()
                print(data_out)

        if data_out is None:
            raise Exception("Unhandled output type: %s" % config.output)

        if config.delay > 0:
            sleep(config.delay)

        msg_cont.params.redis.publish(msg_cont.params.channel_out, data_out)
        if config.verbose:
            log("process_data - predictions published: %s" % msg_cont.params.channel_out)
            end_time = datetime.now()
            processing_time = end_time - start_time
            processing_time = int(processing_time.total_seconds() * 1000)
            log("process_data - finished processing data: %d ms" % processing_time)
    except KeyboardInterrupt:
        msg_cont.params.stopped = True
    except:
        log("process_data - failed to process: %s" % traceback.format_exc())


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    init_logging()

    parser = create_parser("Emulates a Deep Learning model processing data via Redis.", prog=EMULATE, prefix="redis_")
    parser.add_argument("-o", "--output", choices=OUTPUTS, help="The type of output to generated.", default=None, required=True)
    parser.add_argument("-d", "--delay", metavar="SEC", help="The delay between receiving the data and generating the output in seconds.", default=0.5, type=float, required=False)
    parser.add_argument("--labels", metavar="LABEL", help="The labels to generate.", default=None, type=str, required=False, nargs="*")
    parser.add_argument("-n", "--num_objects", metavar="NUM", help="The number of random object detection objects to generate.", default=10, type=int, required=False)
    parser.add_argument("-v", "--verbose", required=False, action='store_true', help='Whether to be more verbose with the output.')
    add_logging_level(parser)
    parsed = parser.parse_args(args=args)
    set_logging_level(_logger, parsed.logging_level)

    config = Container()
    config.output = parsed.output
    config.delay = parsed.delay
    config.verbose = parsed.verbose
    config.labels = parsed.labels
    config.num_objects = parsed.num_objects

    params = configure_redis(parsed, config=config)
    run_harness(params, process_data)


def sys_main() -> int:
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    """
    try:
        main()
        return 0
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    main()
