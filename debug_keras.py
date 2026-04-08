import traceback
import sys
import tensorflow as tf

class DummyDTypePolicy:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return str(self.name)
    @property
    def variable_dtype(self):
        return self.name
    @property
    def compute_dtype(self):
        return self.name

# Patch InputLayer
_original_from_config = tf.keras.layers.InputLayer.from_config
@classmethod
def _patched_from_config(cls, config):
    if 'batch_shape' in config:
        config['batch_input_shape'] = config.pop('batch_shape')
    if 'dtype' in config and isinstance(config['dtype'], dict):
        if config['dtype'].get('class_name') == 'DTypePolicy':
           config['dtype'] = config['dtype']['config']['name']
    return _original_from_config(config)

tf.keras.layers.InputLayer.from_config = _patched_from_config

with open('error_log.txt', 'w', encoding='utf-8') as f:
    try:
        with tf.keras.utils.custom_object_scope({'DTypePolicy': DummyDTypePolicy}):
            tf.keras.models.load_model('major_project-main/models/resnet_model.h5', compile=False)
        f.write("Loaded resnet_model successfully\n")
    except Exception as e:
        f.write("resnet_model failed:\n")
        traceback.print_exc(file=f)

    try:
        with tf.keras.utils.custom_object_scope({'DTypePolicy': DummyDTypePolicy}):
            tf.keras.models.load_model('major_project-main/models/inception_model.h5', compile=False)
        f.write("Loaded inception_model successfully\n")
    except Exception as e:
        f.write("\ninception_model failed:\n")
        traceback.print_exc(file=f)
