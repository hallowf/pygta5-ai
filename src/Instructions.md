## concatenate data
np.concatenate([a, b])

## Cli params
parameters that start with `--` are optional

### Capturing params:
1. identifier(str) - just a string that gets appended to the file names
2. --exp-record - if this argument is passed an experimental capture mode is enabled
  - It uses the keyboard module to capture directly the keys input on the main loop

##### Examples:

`python get_training_data.py bike`

`python get_training_data.py car --exp-record`

### Training params:
1. backend(str) - Which backend to use keras or tflearn
2. identifier(str) - just a string that gets appended to the file names
3. network(str) - Which model to build for the network, available Models:
  - Keras
    - VGG
    - CIFAR10
    - MLP
    - unknown
  - TFLearn
    - alexnetv2
4. --optimizer(str) - Optimizer to user with keras models only, optimizers are:
  - Adam
  - SGD
  - RMSprop
  - Adamax
  - Adagrad
  - Adadelta
  - Nadam
5. --learning_rate(float) - Learning rate to use with tflearn models

##### Examples:

`python train_model.py keras bike CIFAR10 --optimizer Adam`

`python train_model.py tfl bike alexnetv2 --learning-rate 1e-3`
