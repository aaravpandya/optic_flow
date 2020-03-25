import xml.etree.ElementTree as ET
import pandas as pd

tree = ET.parse('Set03_video01.xml')
root = tree.getroot()
boxes = []
for vehicle in root.iter('vehicle'):
    if(vehicle.attrib['radar'] == "True"):

        x, y, h, w = int(vehicle[0].attrib['x']), int(vehicle[0].attrib['y']), int(
            vehicle[0].attrib['h']), int(vehicle[0].attrib['w'])
        frame_start, frame_end, speed = int(vehicle[1].attrib['frame_start']), int(
            vehicle[1].attrib['frame_end']), float(vehicle[1].attrib['speed'])
        boxes.append([frame_start, frame_end, x, y, h, w, speed])
    


df = pd.DataFrame(boxes)
df.to_csv("Set03_video01.csv", index=False, header=["frame_start", "frame_end", "x", "y", "h", "w", "speed"])