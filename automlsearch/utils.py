from django.conf import settings

import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential, load_model
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from keras.callbacks import ModelCheckpoint
from keras.layers import Conv2D, MaxPooling2D, Activation, Dropout, Flatten, Dense

import cv2
import numpy as np
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from .models import ProductInTrainedModel

def create_initial_model(num_classes, IMG_WIDTH, IMG_HEIGHT):
    model = Sequential()
    model.add(Conv2D(64, (3, 3), input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())  # this converts our 3D feature maps to 1D feature vectors
    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, ))
    model.add(Activation('sigmoid'))

    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    return model

# train_model
def train_model(model, batch_size, IMG_WIDTH, IMG_HEIGHT, train_path, val_path, save_root):
    train_data_generator = ImageDataGenerator(
        rotation_range=180,
        width_shift_range=0.2,
        height_shift_range=0.2,
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        preprocessing_function=keras.applications.densenet.preprocess_input,
        fill_mode='nearest',)

    test_data_generator = ImageDataGenerator(
        rescale=1./255,
        preprocessing_function=keras.applications.densenet.preprocess_input
    )

    train_generator = train_data_generator.flow_from_directory(
        train_path, 
        target_size=(IMG_WIDTH, IMG_HEIGHT), 
        batch_size=batch_size, 
        class_mode='categorical',)

    class_indices = train_generator.class_indices

    print("-- Writing Class Indices --")
    with open(os.path.join(BASE_DIR, save_root, 'class_indices_{}.json'.format(int(datetime.now().timestamp()))), 'w') as outfile:
        json.dump(class_indices, outfile)
    print("------- End -------")

    test_generator = test_data_generator.flow_from_directory(
        val_path,
        target_size=(IMG_WIDTH, IMG_HEIGHT), 
        batch_size=batch_size, 
        class_mode='categorical',
    )

    filepath = os.path.join(BASE_DIR, save_root, "CustomModel-{epoch:02d}-{acc:.2f}-{val_acc:.2f}.h5")
    checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
    callbacks_list = [checkpoint]

    history = model.fit_generator(
        train_generator,
        steps_per_epoch = train_generator.n // batch_size,
        epochs=100,
        validation_data=test_generator,
        validation_steps=test_generator.n // batch_size,
        callbacks=callbacks_list
    )

    return history

# process one image

def load_search_model(model_path):
    settings.ML_MODEL = load_model(model_path)
    print("loaded ...")

def search_class(image_path, IMG_WIDTH, IMG_HEIGHT):
    # model = load_model(model_path)
        
    # load image and convert to float image
    img_bgr = cv2.imread(image_path, cv2.IMREAD_UNCHANGED) 
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB) 
    img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
    img = keras.applications.densenet.preprocess_input(img) / 255.0
    # img = (img * 2 - 1) / 255.0
    img_expanded = np.expand_dims(img, 0)  # Create batch axis
    pred = settings.ML_MODEL.predict(img_expanded, steps=1)

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
        
                     
