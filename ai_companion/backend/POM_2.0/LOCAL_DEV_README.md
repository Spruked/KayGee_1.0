# Local Development: Coqui_TTS Integration

## How to Use Local Coqui_TTS in This Workspace

1. **Install Coqui_TTS in Editable Mode**

   Open a terminal and run:
   ```
   cd "f:/Caleon_Genesis_1.0/Coqui_TTS"
   pip install -e .
   ```
   This makes the local TTS package available for all modules in your workspace.

2. **Import TTS in Your Code**

   Use:
   ```python
   from TTS.api import TTS
   ```
   This will always use your local source, not the pip version.

3. **Development Workflow**
   - Any changes to the Coqui_TTS codebase are instantly reflected in your Phonatory Output Module.
   - You can debug, extend, or patch TTS and test immediately.

4. **Testing Integration**
   - Run your test suite in `Phonatory Output Module/tests/` to verify everything is wired up.
   - Example:
     ```
     cd "c:/Users/bryan/Master Modular Build files for Caleon X/Phonatory Output Module"
     pytest
     ```

5. **Troubleshooting**
   - If you get import errors, double-check the editable install and your Python environment.
   - Use `which python` and `pip list` to confirm the environment.

---

**You are now set up for full local development and integration!**
