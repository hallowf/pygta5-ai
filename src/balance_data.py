import os,sys,argparse
import numpy as np
import pandas as pd
from collections import Counter
from random import shuffle

from custom_exceptions import MissingDataSet

# this https://keras.io/preprocessing/image/#flow
# takes data & label arrays, generates batches of augmented data.
# or https://keras.io/preprocessing/image/#flow_from_dataframe
# Takes the dataframe and the path to a directory and generates batches of augmented/normalized data.
# might be usefull
class Balancer(object):
    """docstring for Balancer."""

    def __init__(self, identifier):
        super(Balancer, self).__init__()
        self.identifier = identifier
        self.file_name = "training/training_data_{}.npy".format(self.identifier)
        self.final_name = "training/training_data_{}_balanced.npy".format(self.identifier)
        self.training_data = None
        self.df = None
        self.check_dataframe()

    def check_training_data(self):
        if os.path.isfile(self.file_name):
            self.training_data = list(np.load(self.file_name))
        else:
            raise MissingDataSet("File %s was not found" % (self.file_name))

    def check_dataframe(self):
        self.check_training_data()
        self.df = pd.DataFrame(self.training_data)
        print(self.df.head())
        print(Counter(self.df[1].apply(str)))

    def balance(self,shuf=True):
        lefts = []
        rights = []
        forwards = []
        if shuf:
            shuffle(self.training_data)

        for data in self.training_data:
            img = data[0]
            choice = data[1]

            if choice == [1,0,0]:
                lefts.append([img,choice])
            elif choice == [0,1,0]:
                forwards.append([img,choice])
            elif choice == [0,0,1]:
                rights.append([img,choice])
            else:
                print('no matches')

        if shuf:
            shuffle(self.training_data)

        forwards = forwards[:len(lefts)][:len(rights)]
        lefts = lefts[:len(forwards)]
        rights = rights[:len(forwards)]

        final_data = forwards + lefts + rights
        if shuf:
            shuffle(final_data)
        np.save(self.final_name, final_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Capture training data')
    parser.add_argument("identifier", type=str, help='An identifier for training data filename')
    parser.add_argument("--no-shuffle", help="if used training data isn't shuffled", action="store_false")
    args = parser.parse_args()
    print("Balancing data shuffle:%s" % args.no_shuffle)
    try:
        Balancer(args.identifier).balance(args.no_shuffle)
    except (MissingDataSet,Exception) as e:
        en = e.__class__.__name__
        if en != "MissingDataSet":
            print("\n\nUnexpected exception occured\n\n")
        raise e
    sys.exit(0)
