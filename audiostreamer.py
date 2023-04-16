import sounddevice as sd
import queue
import sys
from time import time
from threading import Thread


class AudioStreamer:
    def __init__(self, samplerate = 16000, blocksize = 8000, device = None,
                 dtype = 'int16', channels = 1, filename_to_save = None, queue_max_size=0,
                 full_buffer_wait_sec = 0):
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.device = device
        self.dtype = dtype  #  float64, float32, int32, int16, int8 and uint8
        self.dtypelen = self._dtype_len(self.dtype)
        self.channels = channels
        self.que =queue.Queue(queue_max_size)
        self.run = False
        self.file_to_save = None
        self.save(filename_to_save)
        self.full_buffer_wait_sec = full_buffer_wait_sec
        self.max_fail = 7
        self.fail = 0

    def save(self, filename):
        if filename:
            fts = open(filename, 'wb')
            self.file_to_save = fts
            return fts

    def save_stop(self):
        if self.file_to_save:
            self.file_to_save.close()
            self.file_to_save = None

    @staticmethod
    def _dtype_len(dtype:str):
        try:
            dtypelen = int(dtype[-2:]) // 8
        except:
            try:
                dtypelen = int(dtype[-1:]) // 8
            except:
                print("unpossible dtype ",dtype)
                print("set dtypelen =2 ")
                dtypelen = 2
        return dtypelen

    def microphone_stream(self):
        def callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            self.que.put(bytes(indata))  ## BYTES !!!!!!!!
            if self.file_to_save:
                try:
                    self.file_to_save.write(bytes(indata))
                except ValueError as e:
                    self.file_to_save = None  # pass

        def stream(samplerate, blocksize, device, dtype, channels, callback):
            try:
                with sd.RawInputStream(samplerate=samplerate, blocksize=blocksize, device=device,
                                       dtype=dtype, channels=channels, callback=callback):
                    self.run = True
                    while self.run:
                        pass
            except Exception as e:
                self.run = False
                raise Exception("stream fail ", e)
        thr = Thread(target=stream, args=(self.samplerate, self.blocksize, self.device, 'int16', 1,callback) )
        thr.start()
        return self.que

    def file_stream(self, filename):
        def stream():
            blocklen = self.blocksize * self.dtypelen
            sk = 0
            data = True
            with open(filename, "rb") as fn:
                self.run = True
                while data and self.run:
                    data = fn.read(blocklen)
                    sk += blocklen
                    fn.seek(sk)
                    if data:
                        try:
                            if len(data) == blocklen:  # discard incomplete block
                                self.que.put(data)
                        except queue.Full:  # wait and put last block
                            tm = time()
                            wait_sec = self.full_buffer_wait_sec

                            while self.que.full() and self.run:
                                if wait_sec and  wait_sec < time()-tm :
                                    break
                            if self.que.not_full:
                                self.que.put(data)
                            else:
                                self.run= False
                                raise queue.Full('file queue to long full')
        thr = Thread(target=stream)
        thr.start()
        return self.que

    def play_stream(self, que):
        def callback_output(outdata, frames: int, time, status):
            #global max_fail
            try:
                data = que.get_nowait()
                if self.file_to_save:
                    self.file_to_save.write(bytes(data))
                outdata[:] = data
                self.fail = 0
            except queue.Empty:
                outdata[:] = b'\0' * self.blocksize * self.dtypelen
                if self.fail > self.max_fail:
                    self.run = False
                    print("exit, not to play")
                else:
                    self.fail += 1
            except BaseException as e:
                print(e)
                if self.file_to_save:
                    print(" close file to save")
                    self.file_to_save.close()
                    self.file_to_save = None

        def stream():
            with sd.RawOutputStream(samplerate=self.samplerate, blocksize=self.blocksize, dtype=self.dtype,
                                    channels=self.channels, callback=callback_output):
                self.run = True
                while self.run:
                    pass

        thr = Thread(target=stream)
        thr.start()

    def stop(self):
        self.run = False
        if self.file_to_save:
            self.save_stop()
