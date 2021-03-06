import cv2
import os,glob
import numpy as np
import core.utils as utils
import tensorflow as tf
import time

s1 = time.time()
def mul_image(watch_dir="./docs/images", output_path='./output'):
    imageDir = os.path.abspath(watch_dir)
    imageList = glob.glob(os.path.join(imageDir, '*.jpg'))
    # print(imageList)

    graph = tf.Graph()
    pb_file = "./yolov3_coco_v3.pb"
    return_elements = ["input/input_data:0", "pred_sbbox/concat_2:0", "pred_mbbox/concat_2:0",
                       "pred_lbbox/concat_2:0"]
    return_tensors = utils.read_pb_return_tensors(graph, pb_file, return_elements)

    with tf.Session(graph=graph) as sess:

        for item in imageList:
            image_path      = item
            # print('item',item)
            end = "/"
            name = item[item.rfind(end):]
            # print(name)
            num_classes     = 80
            input_size      = 608
            out =output_path + name

            original_image = cv2.imread(image_path)
            # original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
            original_image_size = original_image.shape[:2]
            image_data = utils.image_preporcess(np.copy(original_image), [input_size, input_size])
            image_data = image_data[np.newaxis, ...]

            pred_sbbox, pred_mbbox, pred_lbbox = sess.run(
            [return_tensors[1], return_tensors[2], return_tensors[3]],
                    feed_dict={ return_tensors[0]: image_data})

            pred_bbox = np.concatenate([np.reshape(pred_sbbox, (-1, 5 + num_classes)),
                            np.reshape(pred_mbbox, (-1, 5 + num_classes)),
                            np.reshape(pred_lbbox, (-1, 5 + num_classes))], axis=0)


            bboxes = utils.postprocess_boxes(pred_bbox, original_image_size, input_size, 0.45)

            # print('bboxes:',bboxes)
            # bboxes: [[301.13088989 118.44700623 346.95623779 172.39486694   0.97461057   0]...]

            bboxes = utils.nms(bboxes, 0.45, method='nms')
            # print('bboxes:',bboxes)
            # bboxes: [array([105.31238556,  54.51167679, 282.53552246, 147.27146912, 0.99279714,   0.        ])]

            image = utils.draw_bbox(original_image, bboxes)

            cv2.imwrite(out, image)

save_many = mul_image()
s2 = time.time()
print('总用时：', s2 - s1)