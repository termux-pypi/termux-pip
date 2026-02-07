# termux-pip (tpip)
**Termux-pip** is a CLI utility designed to solve Python compilation issues on Android. It focuses on creating **portable, statically linked wheels**

## Install
`pip install tpip`

## Usage

### 1. `tpip setup`
Configures your environment to use the **termux-pypi** repository
* Once setup, you can use standard `pip install` to get pre-compiled packages
* **No system dependencies required at runtime:** The packages from our index are statically linked (bundled) with necessary libraries



```bash
# 1. Connect to the repo
tpip setup

# 2. Install heavy packages (standard pip now uses our index)
pip install numpy pandas pillow

```

> **Note:** This is an unofficial tool. It is not affiliated with the official Termux project
