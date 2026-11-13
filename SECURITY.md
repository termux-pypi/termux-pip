# Security Policy

## ⚠️ Security Warning

**IMPORTANT:** `tpip build` executes code from recipe files and applies patches to source code. Only use recipes from trusted sources.

### Trusted Sources
- ✅ Official repository: https://github.com/termux-pypi/recipes
- ❌ Unknown or third-party recipe files may contain malicious code

### What Could Go Wrong
Using untrusted recipe files could lead to:
- Arbitrary code execution during package build
- Installation of backdoors or malware
- Data exfiltration from your device
- System compromise

## Security Features

This project implements multiple security validations:

1. **Package Name Validation** - Prevents path traversal attacks

## Reporting Security Vulnerabilities

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please email: **admin@loamfy.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours and work on a fix promptly.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Best Practices

When using `tpip`:

1. **Use official recipes only** - Download from https://github.com/termux-pypi/recipes
2. **Review recipe files** - Before building, check the recipe.yaml and patches
3. **Keep updated** - Run `pip install --upgrade termux-pip` regularly
4. **Report suspicious recipes** - If you find malicious recipes, report them immediately

## Acknowledgments

We thank the security research community for helping keep this project secure.
