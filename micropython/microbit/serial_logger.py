#!/usr/bin/env python3
# coding: utf-8
# �V���A������M����
# Copyright (c) 2019 Wataru KUNINO

import sys
import serial

buf_n= 128                                              # ��M�o�b�t�@�e��(�o�C�g)
argc = len(sys.argv)                                    # �����̐���argc�֑��

print('Serial Logger (usage: '+sys.argv[0]+' /dev/ttyACMx)')       # �^�C�g���\��
if argc >= 2:                                           # ���̓p�����[�^���̊m�F
    port = sys.argv[1]                                  # �|�[�g����ݒ�
else:
    port = '/dev/ttyACM0'

try:
    com = serial.Serial(port, 115200, timeout = 0.01)
except Exception as e:                                  # ��O����������
    print(e)                                            # �G���[���e��\��
    exit()                                              # �v���O�����̏I��

while com:
    rx = com.read(buf_n)
    if len(rx) == 0:
        continue
    rx = rx.decode()
    s=''                                                # �\���p�̕�����ϐ�s
    for c in rx:
        if ord(c) >= ord(' ') and ord(c) <= ord('~'):   # �\���\����
            s += c                                      # ������s�֒ǉ�
    print(s)
