import tensorflow as tf
import traceback

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
original_init = tf.keras.layers.InputLayer.__init__
def patched_init(self, *args, **kwargs):
    if 'batch_shape' in kwargs:
        kwargs['batch_input_shape'] = kwargs.pop('batch_shape')
    original_init(self, *args, **kwargs)
tf.keras.layers.InputLayer.__init__ = patched_init

with open('error_log2.txt', 'w', encoding='utf-8') as f:
    try:
        with tf.keras.utils.custom_object_scope({'DTypePolicy': DummyDTypePolicy}):
            tf.keras.models.load_model('major_project-main/models/resnet_model.h5', compile=False)
        f.write("Loaded resnet_model successfully\n")
    except Exception as e:
        f.write("resnet_model failed:\n")
        traceback.print_exc(file=f)
