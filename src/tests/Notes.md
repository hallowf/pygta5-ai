## Notes


#### Pickle instead of np.load/save

pickle seems like a viable solution and does consume slightly less memory and probably execution time,
however there seems to be something off
below if importing the data with pickle and np, np.array_equal(a,b) returns false, however iterating trough the arrays and comparing the shapes there seems to be no difference

    >>> import pickle
    >>> import numpy as np
    >>> a = pickle.load(open("training/training_data_test.npy", "rb"))
    >>> b = np.load("training/training_data_test.npy")
    >>> np.array_equal(a,b)
    False
    >>> for c in a:
    ...     for d in b:
    ...             if (c[0].shape==d[0].shape):
    ...                     ba.append(True)
    ...             else:
    ...                     ba.append(False)
    ...
    >>> print(False in ba)
    False


#### line_profiler
`kernprof.py -v -l <script> <your_script_args>`.
`python -m line_profiler <data_file>`

#### memory_profiler
[pypi](https://pypi.org/project/memory-profiler/)

#### mprof
mprof run python -m memory_profiler get_training_data.py test --s int

mprof plot gtd_function_maxTrainDataLen

gtd = get_training_data



#### normalization keras
And remember to do /255 when you grab an image for prediction as well
Normalizing is scaling data to fit in range of -1 to 1 which is the best for those types of neural networks

### Performance

#### capture

`FPS = 1 / frame loop`


    capture test structure
    for i in list(range(200))[::-1]:
          take screenshot

    time module

    mss ~~0.06409240908183335
    winapi ~~0.06700372695922852
    mss with mean 0.06502873063087464
    winapi with mean 0.07244414329528809

    timeit module 3 runs

    mss = 10.721638161588494
    winapi = 10.896841332865604

    average fps:
    mss: 15
    win32api 15


### memory and speed

##### capture_memory_test() with 5000 len and save at 1000
    Line #      Hits         Time  Per Hit   % Time  Line Contents
    ==============================================================
    159                                           @profile
    160                                           def capture_memory_test():
    161         1        937.0    937.0      0.0      print("Starting")
    162         1      21164.0  21164.0      0.0      sct = mss.mss()
    163         1          7.0      7.0      0.0      training_data = []
    164         1          4.0      4.0      0.0      file_name = "test_capture.npy"
    165      5001      30694.0      6.1      0.0      for i in list(range(5000))[::-1]:
    166      5000      24565.0      4.9      0.0          output = [0,0,0]
    167      5000  317998957.0  63599.8     85.4          screen = np.array(sct.grab((0,40,800,640)))
    168      5000   11497356.0   2299.5      3.1          screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    169      5000    2841109.0    568.2      0.8          screen = cv2.resize(screen, (160,120))
    170      5000    6127631.0   1225.5      1.6          if keyboard.is_pressed("a"):
    171                                                       output = [1,0,0]
    172      5000    3695162.0    739.0      1.0          elif keyboard.is_pressed("w"):
    173                                                       output = [0,1,0]
    174      5000    4279551.0    855.9      1.1          elif keyboard.is_pressed("d"):
    175         5         48.0      9.6      0.0              output = [0,0,1]
    176                                                   else:
    177      4995      52360.0     10.5      0.0              output = [0,0,0]
    178      5000      47913.0      9.6      0.0          training_data.append([screen, output])
    179      5000      57215.0     11.4      0.0          if len(training_data) % 1000 == 0:
    180         5       3316.0    663.2      0.0              print("Saving data")
    181         5   25772028.0 5154405.6      6.9              np.save(file_name, training_data)

##### get_training_data with 10000 len and record
    Line #      Hits         Time  Per Hit   % Time  Line Contents
    ==============================================================
        90                                               @profile
        91                                               def record(self):
        92         5        148.0     29.6      0.0          for i in list(range(4))[::-1]:
        93         4       3620.0    905.0      0.0              print(i+1)
        94         4   13669060.0 3417265.0      3.4              time.sleep(1)
        95                                                   # lst = time.time()
        96         1          5.0      5.0      0.0          while(True):
        97      5001      29991.0      6.0      0.0              if self.stop_running:
        98         1        766.0    766.0      0.0                  self.__del__()
        99         1         58.0     58.0      0.0                  raise UserInterrupt("User pressed hotkey")
       100      5000  292573632.0  58514.7     72.2              screen = np.array(sct.grab((0,40,800,640)))
       101      5000   12050771.0   2410.2      3.0              screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
       102      5000    2862152.0    572.4      0.7              screen = cv2.resize(screen, (160,120))
       103      5000    1471988.0    294.4      0.4              keys = self.key_check()
       104      5000     104802.0     21.0      0.0              output = self.keys_to_output(keys)
       105      5000      60084.0     12.0      0.0              self.training_data.append([screen, output])
       106      5000      39121.0      7.8      0.0              self.training_data.append([screen, output])
       107      5000      56256.0     11.3      0.0              self.training_data_lenght = len(self.training_data)
       108      5000      33632.0      6.7      0.0              if self.training_data_lenght >= self.data_limit:
       109                                                           self.__del__()
       110                                                           raise CrashingRisk("This dataset is now %s of lenght\nClosing program before a crash occurs" % self.training_data_lenght)
       111      5000      48768.0      9.8      0.0              if self.training_data_lenght % 500 == 0:
       112        20      15079.0    754.0      0.0                  print("Current lenght: %s" % self.training_data_lenght)
       113        20        569.0     28.4      0.0                  if not self.delay_save:
       114        20      26780.0   1339.0      0.0                      print("Saving data")
       115        20   81960425.0 4098021.2     20.2                      np.save(self.file_name, self.training_data)
       116        20        431.0     21.6      0.0                      if self.do_split:
       117                                                                   if self.training_data_lenght >= self.split_at:
       118                                                                       print("Splitting data")
       119                                                                       self.split_data()

##### get_training_data with 10000 len and exp_record

    Line #      Hits         Time  Per Hit   % Time  Line Contents
    ==============================================================
       119                                               @profile
       120                                               def exp_record(self):
       121                                                   """Experimental recording uses keyboard directly
       122                                                       instead of calling secondary functions"""
       123         5        141.0     28.2      0.0          for i in list(range(4))[::-1]:
       124         4       2910.0    727.5      0.0              print(i+1)
       125         4   13669344.0 3417336.0      2.2              time.sleep(1)
       126                                                   # lst = time.time()
       127         1          6.0      6.0      0.0          while(True):
       128     10100      56597.0      5.6      0.0              if self.stop_running:
       129         1   19860583.0 19860583.0      3.2                  self.__del__()
       130         1         60.0     60.0      0.0                  raise UserInterrupt("User pressed hotkey")
       131     10099      57868.0      5.7      0.0              output = [0,0,0]
       132     10099  534540065.0  52930.0     85.9              screen = np.array(sct.grab((0,40,800,640)))
       133     10099   23013373.0   2278.8      3.7              screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
       134     10099    5769587.0    571.3      0.9              screen = cv2.resize(screen, (160,120))
       135     10099    8824217.0    873.8      1.4              if keyboard.is_pressed("a"):
       136         7         75.0     10.7      0.0                  output = [1,0,0]
       137     10092    7372911.0    730.6      1.2              elif keyboard.is_pressed("w"):
       138                                                           output = [0,1,0]
       139     10092    8429946.0    835.3      1.4              elif keyboard.is_pressed("d"):
       140                                                           output = [0,0,1]
       141                                                       else:
       142     10092     110098.0     10.9      0.0                  output = [0,0,0]
       143     10099     130606.0     12.9      0.0              self.training_data.append([screen, output])
       144     10099      93668.0      9.3      0.0              self.training_data_lenght +=1
       145     10099      71674.0      7.1      0.0              if self.training_data_lenght >= self.data_limit:
       146                                                           self.__del__()
       147                                                           raise CrashingRisk("This dataset is now %s of lenght\nClosing program before a crash occurs" % self.training_data_lenght)
       148     10099      96734.0      9.6      0.0              if self.training_data_lenght % 500 == 0:
       149        20      16665.0    833.2      0.0                  print("Current lenght: %s" % self.training_data_lenght)
       150        20        501.0     25.1      0.0                  if not self.delay_save:
       151                                                               print("Saving data")
       152                                                               np.save(self.file_name, self.training_data)
       153                                                               if self.do_split:
       154                                                                   if self.training_data_lenght >= self.split_at:
       155                                                                       print("Splitting data")
       156                                                                       self.split_data()


### Other notes

1. Both mss and win32 api seems to have the same performance mss probably uses win32api on windows
2. Keyboard inspite having the known limitation: `Other applications, such as some games, may register hooks that swallow all key events. In this case keyboard will be unable to report events`
  it still seems to work with gta5
