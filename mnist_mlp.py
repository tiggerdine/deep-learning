import os

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

from helpers import neuron_layer, heavy_side, leaky_relu

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def one_hidden_layers(X, n_hidden1=300, n_outputs=10, activation_func=tf.nn.sigmoid):
    print("Network with one hidden layer")
    with tf.name_scope("dnn"):
        hidden1 = neuron_layer(X, n_hidden1, name="hidden1", activation=activation_func)
        logits = neuron_layer(hidden1, n_outputs, name="outputs")
    return logits


def two_hidden_layers(X, n_hidden1=300, n_hidden2=100, n_outputs=10, activation_func=tf.nn.sigmoid):
    print("Network with two hidden layers")
    with tf.name_scope("dnn"):
        hidden1 = neuron_layer(X, n_hidden1, name="hidden1", activation=activation_func)
        hidden2 = neuron_layer(hidden1, n_hidden2, name="hidden2", activation=activation_func)
        logits = neuron_layer(hidden2, n_outputs, name="outputs")
    return logits


def mlp_network(layers, learning_rate, epochs, batches, activation_func, seed):
    tf.random.set_random_seed(seed)

    n_inputs = 28 * 28
    learning_rate = learning_rate
    n_epochs = epochs
    batch_size = batches

    X = tf.placeholder(tf.float32, shape=(None, n_inputs), name="X")
    y = tf.placeholder(tf.int64, shape=None, name="y")

    if layers == 1:
        logits = one_hidden_layers(X=X, activation_func=activation_func)
    else:
        logits = two_hidden_layers(X=X, activation_func=activation_func)

    with tf.name_scope("loss"):
        xentropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=y, logits=logits)
        loss = tf.reduce_mean(xentropy, name="loss")

    with tf.name_scope("train"):
        optimizer = tf.train.GradientDescentOptimizer(learning_rate)
        training_op = optimizer.minimize(loss)

    with tf.name_scope("eval"):
        correct = tf.nn.in_top_k(logits, y, 1)
        accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))

    init = tf.global_variables_initializer()
    saver = tf.train.Saver()

    mnist = input_data.read_data_sets("/tmp/data")

    from datetime import datetime

    now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    root_logdir = "tf_logs"
    logdir = "{}/run-{}/".format(root_logdir, now)

    accuracy_summary = tf.summary.scalar('Accuracy', accuracy)
    # TODO close
    file_writer = tf.summary.FileWriter(logdir, tf.get_default_graph())

    with tf.Session() as sess:
        init.run()
        counter = 0
        for epoch in range(n_epochs):
            for iteration in range(mnist.train.num_examples // batch_size):
                counter += 1
                X_batch, y_batch = mnist.train.next_batch(batch_size)
                sess.run(training_op, feed_dict={X: X_batch, y: y_batch})
                acc_train = accuracy.eval(feed_dict={X: X_batch, y: y_batch})
                acc_val = accuracy_summary.eval(feed_dict={X: mnist.validation.images, y: mnist.validation.labels})

                # print("'\r{0}".format(epoch),
                #       "Train Accuracy: {:3f}  Validation Accuracy: {:3f}".format(acc_train, acc_val), end='')

                if counter % 10 == 0:
                    file_writer.add_summary(acc_val, counter)

            save_path = saver.save(sess, "tmp/my_model_final.ckpt")

        acc_test = accuracy.eval(feed_dict={X: mnist.test.images, y: mnist.test.labels})
        print("\nTest Accuracy: {:3f}".format(acc_test))

    file_writer.close()

def main(learning_rate, epochs, batches):
    layers = 1
    seed = 420

    # print("Perceptron Network")
    # mlp_network(layers, learning_rate, epochs, batches, heavy_side, seed)

    # print("Sigmoid Network")
    # mlp_network(layers, learning_rate, epochs, batches, tf.nn.sigmoid, seed)

    print("Relu Network")
    mlp_network(layers, learning_rate, epochs, batches, tf.nn.relu, seed)

    # print("Leaky Relu Network")
    # mlp_network(layers, learning_rate, epochs, batches, leaky_relu, seed)

    # print("Elu Network")
    # mlp_network(layers, learning_rate, epochs, batches, tf.nn.elu, seed)


if __name__ == "__main__":
    main(0.1, 2, 50)
