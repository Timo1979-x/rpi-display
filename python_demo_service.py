if __name__ == '__main__':
    import time
    import systemd.daemon

    print('Starting up ...')
    # time.sleep(10)
    print('Startup complete')
    systemd.daemon.notify('READY=1')

    while True:
        f = open('/sys/class/thermal/thermal_zone0/temp', 'r')
        temperature = int(f.read()) / 1000
        print(f"℃: {temperature:.2f}")
        f.close()
        time.sleep(1)