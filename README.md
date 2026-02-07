# ⚡ termux-pip (tpip)

`termux-pip` is a CLI utility that configures your Termux environment to use pre-compiled, self-contained wheels for heavy Python packages. Say goodbye to `clang` errors and hour-long builds.

---

## 🚀 Why use tpip?

* **⚡ Instant Install:** Installs `numpy`, `pandas`, `scipy`, `lxml` and others in seconds.
* **📦 Self-Contained:** Our wheels are **bundled** (or statically linked). You don't need to manually run `pkg install libopenblas` or `libxml2`. Everything is inside the `.whl`.
* **🔧 Native Experience:** Once set up, you just use standard `pip install`. No new commands to learn.

## 📦 Installation
```
pip install tpip
```

## 🛠 Usage

### 1. Setup the Repository
Run this command once to configure your pip to point to our optimized Termux index:
```
tpip setup
```

### 2. Install Packages
Now, simply use pip as usual. It will automatically prefer our pre-compiled wheels.
```
# No need to install build dependencies
pip install numpy pandas pillow
```

---

## **Advanced: Building Wheels** (`tpip build`)
You can build packages locally using our **Recipe System**.

`tpip build` automates the complex compilation process by pulling build recipes (patches, flags, and system dependencies) from our repository.
```
tpip build <package_name>
# Example: tpip build numpy
```

**What this command does**:
1. **Fetches Recipe**: Downloads the correct YAML recipe and patches (if available) for the package
2. **Installs Deps**: Automatically runs `pkg install` for necessary build tools (clang, cmake, libs)
3. **Patches & Builds**: Applies Android-specific patches (if available) and compiles the wheel locally

---

## How it works

Normally, pip downloads source code and tries to compile it on your phone, which requires build tools and system libraries.

`tpip setup` changes your pip configuration to include the **Termux-PyPI** index. This repository hosts wheels that are:
1.  **Pre-compiled** on GitHub Actions via Docker.
2.  **Repaired** to include all necessary dynamic libraries (like OpenBLAS) inside the wheel itself.

## ⚠️ Disclaimer
This is an unofficial community project. It is not affiliated with the official Termux development team.