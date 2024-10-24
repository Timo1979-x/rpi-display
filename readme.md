# Назначение

периодически получает температуру ядра Raspberry pi и загрузку CPU. Выводит их на экран. Если температура поднимется выше указанной, включается вентилятор через gpio pin X,
а когда опускается ниже другого указанного значения, кулер выключается.

# Железо
- Raspberry pi
- [1.3 inch oled hat](https://www.waveshare.com/wiki/1.3inch_OLED_HAT)
- полевик irf3205
- гребенки 2x20 (папа и мама)
- разъем для кулера
- маломощный диод
- сглаживающий электролитический конденсатор
- пара резисторов

# Минимальные содинения
указаны номера контактов гребенки raspberry pi.
- pin1 3,3V
- pin6 GND
- pin23 SCLK
- pin19 MOSI
- pin22 GPIO 0.6 (Reset input)
- pin18 GPIO 0.5 (data/command)
- pin24 CE0 (chip select)

# Дополнительные соединения
- pin36 key1
- pin38 key2
- pin40 key1

- pin29 joystick up ?
- pin31 joystick down ?
- pin33 joystick left ?
- pin35 joystick right ?
- pin37 joystick press ?

# Установка сервиса
```
sudo raspi-config
```
Выбрать "Interfacing Options" -> "SPI" -> "Yes to enable the SPI interface".

Перезагрузиться и проверить:
```bash
grep 'spi=on' /boot/firmware/config.txt
```

после этого воспользоваться ansible (ну или вручную сделать шаги, описанные в плэйбуке):
```bash
cd ./ansible
ansible-playbook display.yml
```

# TODO
## выводить процент заряда bluetooth
/sys/kernel/debug/bluetooth/hci0/device_list

https://github.com/TheWeirdDev/Bluetooth_Headset_Battery_Level/

```bash
bluetoothctl devices
bluetoothctl info D1:1B:54:37:0D:8F | grep "Battery Percentage:"
```