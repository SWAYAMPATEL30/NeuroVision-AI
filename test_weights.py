import tensorflow as tf

print("Building ResNet architecture")
model = tf.keras.applications.ResNet50V2(
    include_top=True,
    weights=None,
    classes=4
)
try:
    model.load_weights('major_project-main/models/resnet_model.h5')
    print("Successfully loaded weights into ResNet50V2!")
except Exception as e:
    print("Failed with ResNet50V2:", str(e))

model2 = tf.keras.applications.ResNet50(
    include_top=True,
    weights=None,
    classes=4
)
try:
    model2.load_weights('major_project-main/models/resnet_model.h5')
    print("Successfully loaded weights into ResNet50!")
except Exception as e:
    print("Failed with ResNet50:", str(e))
    
# Or maybe it has a custom top?
try:
    base = tf.keras.applications.ResNet50(include_top=False, input_shape=(224, 224, 3))
    x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
    x = tf.keras.layers.Dense(4, activation='softmax')(x)
    m = tf.keras.models.Model(inputs=base.input, outputs=x)
    m.load_weights('major_project-main/models/resnet_model.h5')
    print("Successfully loaded weights into custom ResNet50!")
except Exception as e:
    print("Failed custom ResNet:", str(e))
