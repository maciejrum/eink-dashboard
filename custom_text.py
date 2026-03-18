#!/usr/bin/env python3
import sys

from eink_dashboard.text_demo import show_text

def main():
    text = " ".join(sys.argv[1:]).strip() or "Hello from Pi Zero"
    show_text(text)

if __name__ == "__main__":
    main()
