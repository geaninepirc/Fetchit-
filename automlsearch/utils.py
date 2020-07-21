import cv2
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.layers import Dense, Conv2D, Flatten, Dropout, MaxPooling2D
from keras.applications.densenet import preprocess_input
import numpy as np

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import json

from .models import ProductInTrainedModel

# pre-necessaries
class ModelClassifier():
    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)

    def predict(self, image):
        pred = self.model.predict(image, steps=1)
        # index = np.argmax(pred)
        return pred

def make_model(num_classes):
    IMG_SHAPE = (224,224,3)
    base_model = tf.keras.applications.DenseNet121(input_shape=IMG_SHAPE, include_top=False, weights='imagenet')
    base_model.trainable = True
    # Let's take a look to see how many layers are in the base model
    print("Number of layers in the base model: ", len(base_model.layers))
    
    # Fine tune from this layer onwards
    fine_tune_at = 280
    
    # Freeze all the layers before the `fine_tune_at` layer
    for layer in base_model.layers[:fine_tune_at]:
      layer.trainable =  False
    
    model = tf.keras.Sequential([
      base_model,
      keras.layers.GlobalAveragePooling2D(),
      Dropout(0.5),
      keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(loss='categorical_crossentropy',
                  optimizer = tf.keras.optimizers.RMSprop(lr=1e-5),
                  #optimizer = tf.keras.optimizers.Adam(lr=5e-5),
                  metrics=['acc'])
    
    return model


# train_model
def train_model(num_classes, batch_size, train_path, val_path, model_root_path):
    # data generators
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        width_shift_range=0.2,
        height_shift_range=0.2,        
        preprocessing_function=preprocess_input,
        validation_split=0.0
    )

    val_datagen = ImageDataGenerator(
        rescale=1./255,
        preprocessing_function=preprocess_input,
        validation_split = 0.0
    )

    train_generator = train_datagen.flow_from_directory(
        train_path,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',    
        subset='training',
        seed=0
    )

    validation_generator = val_datagen.flow_from_directory(
        val_path,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset = 'training',
        seed=0
    )

    class_indices = train_generator.class_indices

    print("-- Writing Class Indices --")
    with open(os.path.join(BASE_DIR, model_root_path, 'class_indices.json'), 'w') as outfile:
        json.dump(class_indices, outfile)
    print("------- End -------")

    model = make_model(num_classes)
    model.summary()

    filepath="InceptionV3-{epoch:02d}-{val_acc:.2f}.hdf5"
    checkpoint = ModelCheckpoint(os.path.join(BASE_DIR, model_root_path, filepath), monitor='val_acc', verbose=1, save_best_only=True, mode='max')
    callbacks_list = [checkpoint]

    epochs = 100
    steps_per_epoch = train_generator.n // batch_size
    validation_steps = validation_generator.n // batch_size

    history = model.fit_generator(train_generator, 
                                steps_per_epoch = steps_per_epoch,
                                epochs=epochs, 
                                workers=4,
                                validation_data=validation_generator, 
                                validation_steps=validation_steps,
                                callbacks=callbacks_list)

    return history

# process one image
def process_one_image(model_path, filename):
    classifier = ModelClassifier(model_path)
    print('model loaded')
    
    # load image and convert to float image
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED) / 255.0

    # preprocessing for InceptionV3
    img = cv2.resize(img, (224,224))
    img = (img * 2 - 1) / 255.0
    img_expanded = tf.expand_dims(img, 0)  # Create batch axis

    # predict        
    pred = classifier.predict(img_expanded)    
    return pred[0]
    
def create_readable_product_list(result_list, json_file_path):
    with open(json_file_path) as json_file:
        product_dict = json.load(json_file)
        product_list = list(product_dict.items())
        new_result = []
        for res in result_list:
            product_uid = [prdct[0] for prdct in product_list if prdct[1] == res['id']][0]
            product_obj = ProductInTrainedModel.objects.get(product_uid=product_uid)
            new_result.append({
                'class_id': res['id'],
                'product_id': product_obj.product.pk,
                'product_name': product_obj.product.name,
                'similarity': res['similarity']
            })

        return sorted(new_result, key=lambda x: x['similarity'], reverse=True)
        
                     
