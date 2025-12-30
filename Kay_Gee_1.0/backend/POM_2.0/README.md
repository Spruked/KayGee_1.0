# Phonatory Output Module (POM)

## Overview
The Phonatory Output Module (POM) is a modular, extensible speech synthesis and vocal tract simulation system. It now includes the full Coqui TTS engine as a subdirectory, enabling advanced text-to-speech (TTS) and vocoder capabilities alongside custom phonatory and articulatory controls.

## Features
- Modular architecture for speech synthesis and vocal tract simulation
- Integrated [Coqui TTS](https://github.com/coqui-ai/TTS) for state-of-the-art TTS
- Custom modules for formant filtering, larynx, lips, tongue, uvula, and more
- Easy-to-run test scripts and example configurations
- Ready for research, prototyping, and production

## Directory Structure
```
Phonatory Output Module/
├── Coqui_TTS/           # Full Coqui TTS engine (TTS, vocoder, scripts, tests)
├── coqui/               # Model cache and reference audio (see coqui/README.md)
├── tests/               # POM-specific tests
├── formant_filter.py    # Formant filter module
├── integration_check.py # Integration test script
├── larynx_sim.py        # Larynx simulation
├── lip_control.py       # Lip control module
├── manifest_phonitory.json
├── output_voice.wav     # Most recent synthesized output
├── output_voice_first.wav # Previous output for comparison
├── phonitory_emitter.py # Main phonatory emitter logic
├── phonitory_output_module.py # Main entry point
├── requirements.txt     # Python dependencies
├── test_tts_basic.py    # Basic TTS test script
├── tongue_artic.py      # Tongue articulation module
├── uvula_control.py     # Uvula control module
├── voice_config.json    # Voice and model configuration
└── LOCAL_DEV_README.md  # Developer notes
```

## Setup
1. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   pip install -r Coqui_TTS/requirements.txt
   ```
   (Optional: set up a virtual environment for isolation.)

3. **Download or prepare TTS models**
   - The first run will auto-download required models, or you can manually place them in `coqui/`.

## Usage
- **Basic TTS Synthesis:**
  ```sh
  python test_tts_basic.py
  ```
  Output will be saved as `output_voice.wav`.

- **Advanced TTS and Phonatory Processing:**
  Use the main entry point for full-featured synthesis and vocal tract simulation:
  ```sh
  python phonitory_output_module.py
  ```
  This will synthesize a demo phrase and log diagnostics to `synthesis.log`.

  To use programmatically:
  ```python
  from phonitory_output_module import PhonatoryOutputModule
  emitter = PhonatoryOutputModule()
  out_path = emitter.phonate("Your text here.")
  emitter.diagnostics()
  ```
  See the `phonate` docstring for advanced options (pitch, formant, articulation, nasalization).

- **Custom Phonatory Modules:**
  Import and use modules like `formant_filter.py`, `larynx_sim.py`, etc., in your own scripts.

## Example
```python
from phonitory_output_module import main
main()
```

## Testing
Run all tests:
```sh
python -m unittest discover tests
```
Or run individual scripts in the `tests/` directory.

## Contribution
Contributions are welcome! Please open issues or pull requests. See `CONTRIBUTING.md` in `Coqui_TTS` for guidelines.

## License
- POM code: MIT (see LICENSE)
- Coqui_TTS: [MPL 2.0](https://opensource.org/licenses/MPL-2.0)

## Further Documentation
- See `Coqui_TTS/README.md` for TTS engine details
- See `coqui/README.md` for model cache and reference audio info
- Developer notes: `LOCAL_DEV_README.md`
