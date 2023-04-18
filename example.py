# Example make by korol4ik
from audiostreamer import AudioStreamer

### stream microphone
ms = AudioStreamer()  # (blocksize=8)
mque = ms.microphone_stream()  # mque = queue for microphone must geted
ms.save(filename ="test2.pcm")  # save to file
print('save from microphone')
input('for play saved inter return')  # wait
print('play..')
ms.stop()  # stop to mic stream

# stream file
fs = AudioStreamer(queue_max_size=10)  # (queue_max_size=1) by file read not full file  in memory
fque = fs.file_stream("test2.pcm")

# play and save stream
ps = AudioStreamer(filename_to_save="testOutStream.pcm")
ps.play_stream(fque)
'''
while fque.qsize() > 0:
    print(fque.qsize())
'''



