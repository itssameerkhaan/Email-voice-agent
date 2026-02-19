# Parakeet ASR Model - Local Setup

## Location
**Model stored at:** `D:\langGraph\email_agent\parakeet_model`

## Usage

### In Python:
```python
import os
# Set cache directory
os.environ['NEMO_CACHE_DIR'] = r"D:\langGraph\email_agent\parakeet_model\cache"

import nemo.collections.asr as nemo_asr
# Load model (will use local cache)
model = nemo_asr.models.ASRModel.from_pretrained("nvidia/parakeet-tdt-0.6b-v2"