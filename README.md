# Image Converter

A desktop application for converting various image formats (including HEIC) to JPEG. Built with Python and Tkinter.


## Features

- Convert single images or entire folders to JPEG format
- Supports multiple input formats:
  - HEIC (iPhone/iOS images)
  - PNG
  - BMP
  - GIF
  - TIFF
  - WebP
- Adjustable JPEG quality settings
- User-friendly interface with progress tracking
- Preserves original file names
- Cross-platform support (Windows and macOS)

## Installation

### Windows
1. Go to the [Releases](../../releases) page
2. Download the latest `ImageConverter.exe`
3. Run the executable

### macOS
1. Go to the [Releases](../../releases) page
2. Download the latest `ImageConverter.dmg`
3. Open the DMG file
4. Drag the ImageConverter app to your Applications folder

## Usage

1. Launch the application
2. Click "Select File" to convert a single image or "Select Folder" to convert multiple images
3. Adjust the JPEG quality using the slider if desired
   - Higher quality = larger file size
   - Lower quality = smaller file size
4. Click "Convert" to start the conversion process
5. Monitor progress in the status bar
6. Converted images will be saved in the same location as the originals with a .jpg extension

## Building from Source

### Prerequisites
- Python 3.8 or later
- pip (Python package installer)

### Setup
1. Clone the repository
```bash
git clone https://github.com/yourusername/image-converter.git
cd image-converter
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python image_converter.py
```

### Building Executables
The repository includes GitHub Actions workflows that automatically build executables for Windows and macOS. To trigger a new build:

1. Create a new tag
```bash
git tag v1.x.x
git push origin v1.x.x
```

2. GitHub Actions will automatically:
   - Build the executables
   - Create a new release
   - Upload the built files

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Python](https://python.org)
- Uses [Pillow](https://python-pillow.org/) for image processing
- Uses [pillow-heif](https://github.com/bigcat88/pillow_heif) for HEIC support

## Support

If you encounter any issues or have questions:
1. Check the [Issues](../../issues) page to see if your problem has been reported
2. Create a new issue if needed

## Changelog

### v1.0.0
- Initial release
- Basic image conversion functionality
- HEIC support
- Quality adjustment slider
- Progress tracking
- Directory batch processing