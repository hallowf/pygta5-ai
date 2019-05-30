import os,sys,argparse, time
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
        self.no_matches = 0
        self.data_loaded = False
        self.check_training_data()

    def check_training_data(self):
        self.data_loaded = True
        zero_file = self.file_name.replace(".npy", "0.npy")
        def checker():
            a = None
            if os.path.isfile(self.file_name) or os.path.isfile(zero_file):
                print("Found file, checking for more...")
                datas = os.listdir("training")
                print("Data list:\n%s" % datas)
                check = "training_data_%s" % self.identifier
                for file in datas:
                    if check in file and not file.endswith("balanced.npy"):
                        print("Found: %s" % file)
                        if a == None:
                            a = np.load("training/%s" % file)
                            print("a Dataframe")
                            self.check_dataframe(a)
                        else:
                            b = np.load("training/%s" % file)
                            print("b Dataframe")
                            self.check_dataframe(b)
                            a = np.concatenate([a,b])
                self.training_data = a
            else:
                raise MissingDataSet("File %s was not found" % (self.file_name))
        checker()

    def check_dataframe(self, data=None):
        if data == None:
            self.df = pd.DataFrame(self.training_data)
            print(self.df.head())
            print(Counter(self.df[1].apply(str)))
        else:
            df = pd.DataFrame(data)
            print(df.head())
            print(Counter(df[1].apply(str)))

    def do_save(self):
        self.check_dataframe()
        np.save(self.final_name, self.training_data)


    def balance_data(self,shuf=True):
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
                self.no_matches += 1

        print("\n\nNo matches: %s\n" % self.no_matches)
        forwards = forwards[:len(lefts)][:len(rights)]
        lefts = lefts[:len(forwards)]
        rights = rights[:len(forwards)]

        self.training_data = forwards + lefts + rights
        if shuf:
            shuffle(self.training_data)


        self.do_save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Capture training data')
    parser.add_argument("identifier", type=str, help='An identifier for training data filename')
    parser.add_argument("--ns","--no-shuffle", help="if used training data isn't shuffled", action="store_false")
    parser.add_argument("--co","--concat-only", help="If used it will not balance data, only concatenate it", action="store_true")
    args = parser.parse_args()
    print("Balancing data\n\tshuffle:%s\n\tconcat only:%s" % (args.ns, args.co))
    try:
        b = Balancer(args.identifier)
        if args.co:
            b.do_save()
        else:
            b.balance_data(args.ns)
    except (MissingDataSet,Exception) as e:
        en = e.__class__.__name__
        if en != "MissingDataSet":
            print("\n\nUnexpected exception occured\n\n")
        raise e
    sys.exit(0)
