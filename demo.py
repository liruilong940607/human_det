import tqdm
import cv2
import argparse
import numpy as np
import torch

import humansegV2
import streamer_pytorch as streamer

parser = argparse.ArgumentParser(description='.')
parser.add_argument(
    '--camera', action="store_true")
parser.add_argument(
    '--images', default="", nargs="*")
parser.add_argument(
    '--videos', default="", nargs="*")
parser.add_argument(
    '--loop', action="store_true")
parser.add_argument(
    '--vis', action="store_true")
args = parser.parse_args()

def visulization(data):
    image, bboxes, probs = data
    probs = probs.unsqueeze(3)
    bboxes = (bboxes * probs).sum(dim=1, keepdim=True) / probs.sum(dim=1, keepdim=True)
    window = image[0].cpu().numpy().transpose(1, 2, 0)
    window = (window * 0.5 + 0.5) * 255.0
    window = np.uint8(window)
    bbox = bboxes[0, 0, 0].cpu().numpy()
    window = cv2.rectangle(
        window, 
        (int(bbox[0]), int(bbox[1])), 
        (int(bbox[2]), int(bbox[3])), 
        (255,0,0), 2)
    
    window = cv2.cvtColor(window, cv2.COLOR_BGR2RGB) 
    window = cv2.resize(window, (0, 0), fx=2, fy=2)

    cv2.imshow('window', window)
    cv2.waitKey(30)

det_engine = humansegV2.Detection()

if args.camera:
    data_stream = streamer.CaptureStreamer()
elif len(args.videos) > 0:
    data_stream = streamer.VideoListStreamer(
        args.videos * (10000 if args.loop else 1))
elif len(args.images) > 0:
    data_stream = streamer.ImageListStreamer(
        args.images * (10000 if args.loop else 1))

loader = torch.utils.data.DataLoader(
    data_stream, 
    batch_size=1, 
    num_workers=1, 
    pin_memory=False,
)

try:
    # no vis: ~ 70 fps
    for data in tqdm.tqdm(loader):
        bboxes, probs = det_engine(data)
        if args.vis:
            visulization([data, bboxes, probs])
        pass
except Exception as e:
    print (e)
    del data_stream
