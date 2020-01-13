#!/bin/bash
echo "HOME="${HOME}
echo "diff "${HOME}"/iot : "${HOME}"/sens"
echo "[diff]-------------------------------------------------------------------"
diff ~/sens/README.md ~/iot/iot-sensor-core-esp32/README.md
diff -r ~/sens/target ~/iot/iot-sensor-core-esp32/target |grep -v ".jpg" |grep -v ".pdf" |grep -v ".BAK"
diff -r ~/sens/iot-sensor-core-esp32 ~/iot/iot-sensor-core-esp32 |grep -v ".jpg" |grep -v ".pdf" |grep -v ".BAK"|grep -v "のみに存在: target"|grep -v "のみに存在: README.md"
echo "[cmp]-------------------------------------------------------------------"
cmp ~/sens/README.pdf ~/iot/iot-sensor-core-esp32/README.pdf
cmp ~/sens/iotcore.jpg ~/iot/iot-sensor-core-esp32/iotcore.jpg
cmp ~/sens/target/iot-sensor-core-esp32.ino.bin ~/iot/iot-sensor-core-esp32/target/iot-sensor-core-esp32.ino.bin
cmp ~/sens/target/iot-sensor-core-esp32.ino.partitions.bin ~/iot/iot-sensor-core-esp32/target/iot-sensor-core-esp32.ino.partitions.bin
cmp ~/sens/target/boot_app0.bin ~/iot/iot-sensor-core-esp32/target/boot_app0.bin
cmp ~/sens/target/bootloader_qio_80m.bin ~/iot/iot-sensor-core-esp32/target/bootloader_qio_80m.bin
