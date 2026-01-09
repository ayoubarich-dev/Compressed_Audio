# 🎵 Audio Compressor Pro

Intelligent audio compression application with real-time visualization and modern graphical interface.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)


## 📋 Description

Audio Compressor Pro is an advanced audio compressor that uses a combination of compression algorithms:
- **Delta Encoding**: Encodes differences between consecutive samples
- **RLE (Run-Length Encoding)**: Compresses repetitions
- **Huffman Coding**: Optimizes data encoding

The application features a modern graphical interface with waveform visualization and real-time compression metrics.

## ✨ Features

- 🎵 **Audio Visualization**: Original and compressed waveforms with animations
- 📊 **Detailed Metrics**: Size, duration, channels, sample rate, bit depth
- 📉 **Reduction Rate**: Prominent display with dynamic color coding
- 🎧 **Audio Playback**: Listen to original and compressed files directly
- 💾 **Proprietary Format**: Save as `.IRM` with optimal compression
- 🎨 **Modern Interface**: Dark theme with gradients and animations

## 🖼️ Preview

```
┌─────────────────────────────────────────────────────────────┐
│ 🎵 AUDIO COMPRESSOR PRO                             v2.0    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📁 File: music.wav                                          │
│  ▶ PLAY ORIGINAL                                             │
│  🗜️ COMPRESS                                                 │
│  ▶ PLAY COMPRESSED                                           │
│  ⏹ STOP                                                      │
│                                                               │
│  ━━━━━━━━━━━━━━━━ 100% ━━━━━━━━━━━━━━━━                    │
│  ✅ COMPRESSION: 86.2%                                        │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  🎵 AUDIO VISUALIZATION                                      │
│                                                               │
│  🎵 ORIGINAL    [green waveform]                            │
│  🗜️ COMPRESSED  [red waveform]                              │
│                                                               │
│  📉 REDUCTION RATE: 86.2%                                    │
│                                                               │
│  📊 METRICS                                                  │
│  💾 Size: 3.2MB → 450KB    📉 Reduction: 86.2%              │
│  ⏱️ Duration: 3:45         🎚️ Channels: Stereo             │
│  📡 Sample Rate: 44 kHz    🎯 Bit Depth: 16 bits            │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/ayoubarich-dev/Compressed_Audio
cd Compressed_Audio
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python main.py
```

## 📦 Dependencies

```
pydub==0.25.1
numpy==1.24.3
PySide6==6.5.2
bitarray==2.8.1
```

## 🎯 Usage

### Compressing a File

1. Click **"SELECT"** to choose an audio file
2. Supported formats: MP3, WAV, OGG, FLAC
3. Click **"COMPRESS"**
4. Choose save location (.IRM)
5. Visualize results in real-time

### Playback

- **▶ PLAY ORIGINAL**: Plays the source file
- **▶ PLAY COMPRESSED**: Decompresses and plays the .IRM file
- **⏹ STOP**: Stops playback

## 🔧 Project Architecture

```
audio-compressor/
├── main.py                     # Entry point
├── requirements.txt            # Dependencies
├── README.md                   # Documentation
│
└── src/
    ├── compression/            # Compression algorithms
    │   ├── stereotreatment.py  # Stereo processing
    │   ├── quantification.py   # Signal quantization
    │   ├── encoding.py         # Delta + RLE + Huffman
    │   └── utils.py            # Utilities
    │
    ├── core/                   # Business logic
    │   ├── compressor.py       # Compression/decompression
    │   └── audio_processor.py  # Audio processing
    │
    └── gui/                    # Graphical interface
        ├── main_window.py      # Main window
        ├── widgets.py          # Custom widgets
        ├── visualization_widget.py  # Visualizations
        ├── styles.py           # Themes and styles
        └── controllers.py      # UI controllers
```

## 🧮 Compression Algorithms

### 1. Stereo Processing
- Analyzes similarity between left/right channels
- Converts to mono if similar (< 20% difference)
- Differential encoding for distinct channels

### 2. Quantization
- Signal centering (mean = 0)
- Normalization between -1 and 1
- Quantization to 256 levels (8 bits)

### 3. Delta Encoding
```
Original: [100, 102, 101, 103]
Delta:    [100, +2, -1, +2]
```

### 4. Run-Length Encoding (RLE)
```
Data: [5, 5, 5, 5, 7, 7]
RLE:  [(5, 4), (7, 2)]
```

### 5. Huffman Coding
- Short codes for frequent values
- Long codes for rare values
- Statistics-based optimization

## 📊 Performance

| File Type    | Original Size | Compressed Size | Rate |
|--------------|---------------|-----------------|------|
| Music WAV    | 10 MB         | 1.5 MB          | 85%  |
| Podcast MP3  | 5 MB          | 800 KB          | 84%  |
| Mono Voice   | 3 MB          | 450 KB          | 85%  |

## 🎨 Color Scheme

- **Red**: ≥ 80% compression (excellent)
- **Orange**: 60-79% compression (good)
- **Yellow**: 40-59% compression (average)
- **Gray**: < 40% compression (poor)

## 🐛 Known Issues

- Decompression may take a few seconds for large files
- Proprietary .IRM format (not compatible with other players)
- Quality loss due to 8-bit quantization

## 🔮 Future Improvements

- [ ] Lossless compression support
- [ ] Block-based compression for large files
- [ ] Export to standard formats (MP3, OGG)
- [ ] Multi-threaded compression
- [ ] Batch mode for multiple files
- [ ] Adjustable compression levels
- [ ] Audio effects and filters
- [ ] Command-line interface

## 👨‍💻 Development

### Testing

```bash
# Run application in debug mode
python main.py
```

