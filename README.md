# Usability and Security of Brainwave-Based Authentication in Real-World Applications - Thesis Artifacts

[![License](https://img.shields.io/badge/License-BSD_3--Clause-green.svg)](https://opensource.org/licenses/BSD-3-Clause) [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)]() [![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/) [![status: experimental](https://github.com/GIScience/badges/raw/master/status/experimental.svg)](https://github.com/GIScience/badges#experimental)

> **Abstract** Through recent advantages in consumer-grade brain-computer interfaces, many ideas long confined to labs are now becoming viable for exploration and deployment in the real world. One such idea is the usage of brainwaves for digital authentication. While the approach's feasibility has been shown, research into real-world usability and security is still lacking. Further, although prototype implementations exist, these are primarily self-contained applications that are not publicly available. To overcome these limitations and allow for easier prototyping in the future, we developed NeuroPack, a Python library tailored toward developing brainwave-based authentication systems. As part of this library, we further developed KeyWave, an illustrative realization of a brainwave-based authentication system that can be easily integrated into existing applications. KeyWave additionally provides a possible solution to the conundrum of continuous authentication using brainwaves by constantly monitoring the recorded EEG signals to detect abnormal behavior. To demonstrate both NeuroPack and KeyWave, we further envisioned, designed, and implemented the Foundation Password Manager. This application enables users to use KeyWave to authenticate themselves on arbitrary websites, moving brainwave-based authentication from a theoretical concept into a real-world use case.

This repository contains all additional artifacts created for my master's thesis, "Usability and Security of Brainwave-Based Authentication in Real-World Applications". 

The thesis was written at the IT Security group at Paderborn University. Further, it was supervised by Patricia Arias Cabarcos, who also leads the group. The contents of this repository represent the state of all additional artifacts at the time of submission. This repository does not include the data used within the thesis. For testing of NeuroPack, new data can be recorded if a compatible device is present. Alternatively, data from other sources and projects can be used [1].


### Text Artifacts 📄
- [Consent Form](./documents/consent_form)
- [Ethics Request](./documents/ethics_request.pdf)
- [Flyer](./documents/flyer)
- [Questionnaire in queXML format](./documents/questionnaire)
- [Study Protocol](./documents/study_protocol.pdf)


### Code Artifacts 💻
- [NeuroPack](./code/neuropack)
- [Foundation Password Manager](./code/fpm)
- [FPM Browser Plugin](./code/fpm-browser-plugin)


# Installation
All code artifacts within this repository require a set of external dependencies. In the case of the [FPM Browser Plugin](./code/fpm-browser-plugin), the plugin must be bundled and added to the browser. A description of how to do this can be found in [Mozilla's official documentation](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Your_first_WebExtension#installing). The remaining two artifacts, [NeuroPack](./code/neuropack) and the [Foundation Password Manager](./code/fpm), are both written in Python. To use them, please ensure that you have Python 3.8 or higher installed. While both might work with older versions, it was not tested.
Further, it is recommended to use a virtual environment. Instruction on how to do this can be found [here](https://docs.python.org/3/library/venv.html). Some dependencies might not work on certain operating systems or require additional configurations. This mainly concerns Linux systems using niche desktop environments. In case of problems, please refer to the official documentation of the affected dependencies. NeuroPack and the FPM are tested to run on Windows 10 and Linux Mint. In the latter case, we tested the Cinnamon and Mate desktop environments. During development, we noticed that all user interface-dependent artifacts, e.g., the FPM and acquisition tasks contained within NeuroPack, need longer to load initially. This was observed regardless of whether the used hardware was stronger or weaker than the one used for testing on Linux.

## NeuroPack
For NeuroPack to work, it requires several external dependencies to be installed. The following are needed:
```
play_sounds
tk
scipy
matplotlib
statsmodels
brainflow
numpy
```
To install these dependencies, please use the following command:
```
pip install -r code/neuropack/requirements.txt
```

On some systems, the used TKinter GUI framework needs additional steps to be used. Please refer to the official documentation in case of problems.

## Foundation Password Manager
Likewise to NeuroPack, the FPM requires several external dependencies to be installed. Most of these are used to create the GUI (Kivy), communicate with the browser plugin (CherryPy), or use system features like file choosers or the clipboard (Plyer, Pyperclip). The following dependencies are required:
```
cryptography==38.0.1
Kivy==2.1.0
kivymd==1.0.2
pyperclip
plyer
numpy
cherrypy
cherrypy_cors
polib
```
To install them, the following command can be used:
```
pip install -r code/fpm/requirements.txt
```
Please note that the FPM implementation included within this repository also uses NeuroPack. While the latter could be installed via PyPi, this would no longer reflect the state of the code at the time of submission. Therefore, the NeuroPack implementation included within this repository is used. This fact requires that the FPM is installed in the same environment as NeuroPack.

An easy way to ensure this is, instead of installing the dependencies for both separately, to install them from the requirements file in the code directory:
```
pip install -r code/requirements.txt
```

Once installed, the Foundation Password Manager can be started by starting the main.py file in the fpm folder or using the "StartFPM.bat" file on Windows, respectively, the "StartFPM.sh" file on Linux. In all cases, the scripts must be used with the root folder of this repository as the working directory.

# Usage
A description of how to use the FPM can be found within the thesis. Likewise, an overview of the components included in NeuroPack can be found within the thesis. Additionally, this repository contains several Jupyter Notebooks providing examples of how NeuroPack can be used. To use these, Jupyter has to be installed and setup separately:
```
pip install jupyter
```

The notebooks are:
- [A short introduction to NeuroPack](./code/neuropack/examples/introduction.ipynb)
- [Recreation of the recording process described by Krigolson et al. [1]](./code/neuropack/examples/P300_Krigolson.ipynb)
- [Playground for the different ERP acquisition tasks](./code/neuropack/examples/tasks.ipynb)
- [The code used in the thesis to perform the benchmarking](./code/neuropack/examples/benchmark.ipynb) (Needs Scikit-learn)

To see how KeyWave, part of NeuroPack, was added to the FPM, please refer to the following files:
- [Setup of KeyWave](./code/fpm/lib/auth_factory.py)
- [Authentication](./code/fpm/lib/browser_communication/browser_worker.py)
- [Enrollment](./code/fpm/lib/dialogs.py)

# Limitations
The code contained in this repository is highly experimental and should be treated as such. Its target audience are mainly researchers and students who wish to explore the notion of brainwave-based authentication. Using the code in a production environment is not recommended and might lead to security issues. 

Further, the documentation and tests provided alongside the code were partly generated with the help of Github Copilot. Although manually checked, these generated parts can contain errors or ambiguities.
In case of severe differences between the documentation and the code, the code should be considered the correct version.

# Known Bugs
The code artifacts within this repository contain some known bugs that were not addressed due to time constraints. While undesirable, they do not affect the core functionalities of the artifacts.

### Foundation Password Manager
- When closing the FPM, the included web server used for communication with the plugin can sometimes stay alive for a prolonged time period. To address this, the FPM sends a "close" command to the server, which triggers a stop of the extra process. This command is sometimes sent when the server is already stopped, which leads to an exception. Currently, this case is handled by ignoring the exception, yet a more stable solution would be desirable.

### Browser Plugin
- The companion browser plugin cannot submit the auto-filled credentials on some websites. This issue was not further investigated or addressed due to the limited timeframe. It is noted that this behavior might be due to calling the "submit" function on a login form instead of submitting it by clicking the button.

### NeuroPack
- NeuroPack is sometimes unable to find a device despite being turned on and in pairing mode. This can happen when the "disconnect" function was not correctly called for another device beforehand. In this case, the previous device might still be connected to the system and blocks the Bluetooth adapter used by NeuroPack. A workaround for this is to make sure the previous device is completely turned off or turn Bluetooth off and on again.
- The AudioTask and its derivatives do not work reliably on all systems.

# <a name="license"></a> License
The contents of this repository are licensed using the BSD 3-Clause License. See the [LICENSE file](./LICENSE) for details. Derivative work should be marked as such.
Pictures in the [example folder of NeuroPack](./code/neuropack/examples/data/images/random/) are taken from Pexels.com and are not subject to the license. More info on how the pictures are licensed can be found [here](./code/neuropack/examples/data/images/random/info.txt). Further, we used icons from Google's Material Icons collection in our flyer. More info on them can be found in the respective [repository](https://github.com/google/material-design-icons).

# Contributions
This repository is an archive and, therefore, not open for contributions.

# Acknowledgements
I thank my supervisor, Patricia, for her guidance, encouragement, and patience while working on this thesis. Further, I thank all members of her group, who were always willing to help and support me if needed. Likewise, I would like to express my thanks to Felix, who has always been willing to offer his assistance beyond his role as the second reviewer. My deepest gratitude goes to Jan-Luca, Lukas, Niko, and Serkis for helping proofread my thesis. Lastly, I thank everyone who participated in my user study or the initial pilot study.

# References
[1] A. Barachant, "muse-lsl-python” GitHub, 2017. https://github.com/urish/muse-lsl-python (accessed Apr. 25, 2023).

[2] O. E. Krigolson, C. C. Williams, A. Norton, C. D. Hassall, and F. L. Colino, “Choosing MUSE: Validation of a Low-Cost, Portable EEG System for ERP Research,” Front. Neurosci., vol. 11, Mar. 2017, doi: 10.3389/fnins.2017.00109.