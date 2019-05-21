## Notes
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



1. Both mss and win32 api seems to have the same performance mss probably uses win32api on windows
2. Keyboard inspite having the known limitation: `Other applications, such as some games, may register hooks that swallow all key events. In this case keyboard will be unable to report events`
  it still seems to work with gta5
