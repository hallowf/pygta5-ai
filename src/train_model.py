import sys, argparse

from network.keras_network import MainframeKeras
from network.tflearn_network import MainframeTFLearn

from custom_exceptions import InvalidBackend

class Trainer(object):
    """docstring for Trainer."""

    def __init__(self,backend,identifier,network_type, *args, **kwargs):
        super(Trainer, self).__init__()
        backends = {
            "keras": MainframeKeras,
            "tfl": MainframeTFLearn
        }
        if backend not in list(backends.keys()):
            raise InvalidBackend("Unknown backend %s" % backend)
        self.network_type = network_type
        self.identifier = identifier
        self.backend = backend
        self.optzr = kwargs.get("optimizer", None)
        self.lr = kwargs.get("learning_rate", None)
        self.mainframe = backends[backend]
        vals = "Backend: %s\nID: %s\nNetwork: %s\nOptimizer: %s\nLearning rate:%s" % (backend,
            identifier,network_type,self.optzr,self.lr)
        sys.stdout.write("Trainer Initialized with the following values:\n%s\n" % vals)

    def run_backend(self):
        if self.backend == "keras":
            if self.optzr:
                self.mainframe(self.identifier, self.network_type, self.optzr).run()
            else:
                self.mainframe(self.identifier, self.network_type).run()
        else:
            if self.lr:
                self.mainframe(self.identifier, self.network_type, self.lr)
            else:
                self.mainframe(self.identifier, self.network_type)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture training data")
    parser.add_argument("backend", type=str, help="Backend to use keras or tfl")
    parser.add_argument("identifier", type=str, help="An identifier for training data file")
    parser.add_argument("network", type=str, help="Model to build check instructions.md for available modules")
    parser.add_argument("--optimizer", type=str, help="Optimizer to user with keras models only")
    parser.add_argument("--learning-rate", type=float, help="Learning rate for model currently only used by tflearn")
    args = parser.parse_args()
    print(args.optimizer)
    sys.exit(0)
    try:
        if args.optimizer:
            Trainer(args.backend,args.identifier, args.network,optimizer=args.optimizer).run_backend()
        elif args.learning_rate:
            Trainer(args.backend,args.identifier, args.network,learning_rate=args.learning_rate).run_backend()
        else:
            Trainer(args.backend,args.identifier, args.network).run_backend()
    except (Exception) as e:
        raise e
