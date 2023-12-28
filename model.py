import tensorflow as tf
import numpy as np
import csv
import pandas as pd


# refers to maximum expected vocabulary words
max_features = 1000
# max sentence length
max_len = 50

def test_model():
    vocab = []
    with open('./data/archive/chatlogs.csv', newline='') as csvfile:
        commentreader = csv.DictReader(csvfile)
        for row in commentreader:
            vocab.append(row['message'])
    embed_model = embedding_model(pre_model=None, training_dataset=vocab)
    embed_model.fit()

def pre_process_training_set():
    chat_train = pd.read_csv(
        "./data/archive/chatlogs.csv",
        names=["id",
               "message",
               "association_to_offender",
               "time",
               "case_total_reports",
               "allied_report_count",
               "enemy_report_count",
               "most_common_report_reason",
               "chatlog_id",
               "champion_name"
])
    chat_train['association_to_offender'] = chat_train['association_to_offender'].apply(
        lambda x: 1 if x == 'offender' else 0)

    def parse_min_to_sec(time_str):
        m, s = time_str.split(":")
        try:
            return int(m) * 60 + int(s)
        except ValueError:
            return 0

    chat_train['time'] = chat_train['time'].apply(
        lambda x: parse_min_to_sec(x))
    chat_features = chat_train.copy()
    chat_labels = chat_features.pop('association_to_offender')


def init_testing(dataset):
    tensor_vocab = tf.data.Dataset.from_tensor_slices(dataset)
    vectorize_layer = tf.keras.layers.TextVectorization(
        max_tokens=max_features,
        output_mode='int',
        output_sequence_length=max_len)
    vectorize_layer.adapt(tensor_vocab.batch(64))
    print(vectorize_layer.get_vocabulary())
    return {
        "token_vec": vectorize_layer
    }


def embedding_model(pre_model=None, training_dataset=None):
    model = pre_model
    if pre_model is None:

        pre_layers = init_testing(training_dataset if training_dataset is not None else [])
        input_layer_msg = tf.keras.Input(shape=(1,), name='message')
        token_vec_layer = pre_layers['token_vec'](input_layer_msg)
        embed_a = tf.keras.layers.Embedding(1000, 64, input_length=10)(token_vec_layer)
        # The model will take as input an integer matrix of size (batch,
        # input_length), and the largest integer (i.e. word index) in the input
        # should be no larger than 999 (vocabulary size).
        # Now model.output_shape is (None, 10, 64), where `None` is the batch
        input_layer_else = tf.keras.Input(shape=(3,))
        concat_a = tf.keras.layers.Concatenate([input_layer_else, embed_a])
        embed_b = tf.keras.layers.Embedding(67, )(concat_a)
        hidden_1 = tf.keras.layers.Dense(18, activation='relu')(embed_b)
        output_layer = tf.keras.layers.Dense(1, activation='softmax')(hidden_1)
        input_array = np.random.randint(1000, size=(32, 10))
        model = tf.keras.Model(inputs=[input_layer_msg, input_layer_else], outputs=output_layer)
        model.compile('rmsprop', 'mse')
        print(model.summary())
        tf.keras.utils.plot_model(model, "final_model.png")
    return model

    # output_array = model.predict(input_array)
