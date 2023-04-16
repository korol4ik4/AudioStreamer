from audiostreamer import AudioStreamer
from time import sleep


### save microphone to file

ms = AudioStreamer(blocksize=8)
mque = ms.microphone_stream()  # mque = queue for microphone must geted
ms.save(filename ="test.pcm")
print('save from microphone')
input('for play saved inter return')
print('play..')
ms.stop()  # stop to mic stream

# stream file
fs = AudioStreamer(queue_max_size=4)
fque = fs.file_stream("test.pcm")
sleep(2)
# play stream
ps = AudioStreamer(samplerate=16000, filename_to_save="test2.pcm")
ps.play_stream(fque)
#sleep(10)



