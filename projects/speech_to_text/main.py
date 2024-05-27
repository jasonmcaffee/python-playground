from pywhispercpp.model import Model

def main():
    print("hello")
    model = Model('base.en', n_threads=6)
    segments = model.transcribe('file.mp3', speed_up=True)
    for segment in segments:
        print(segment.text)

main()