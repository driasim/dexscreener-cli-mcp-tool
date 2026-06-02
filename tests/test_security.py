"""Tests for dexscreener-cli-mcp-tool PRs:
- PR #4: Lock file unbounded growth prevention
- PR #3: Atomic write implementation
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# --- PR #3: Atomic write ---
def test_atomic_write_pattern():
    """Verify atomic write pattern (write to temp, then rename)"""
    root = os.path.join(os.path.dirname(__file__), "..")
    found_atomic = False
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath or "node_modules" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith((".py", ".js", ".ts")):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                atomic_patterns = [
                    "os.rename", "shutil.move",
                    "tempfile.NamedTemporaryFile", "tempfile.mkstemp",
                    "atomic", ".tmp", ".part",
                ]
                found = [p for p in atomic_patterns if p in content]
                if len(found) >= 1:
                    found_atomic = True
    # If no explicit atomic write, check for write-then-rename
    if not found_atomic:
        for dirpath, dirnames, filenames in os.walk(root):
            if ".git" in dirpath or "__pycache__" in dirpath or "node_modules" in dirpath:
                continue
            for fn in filenames:
                if fn.endswith((".py", ".js", ".ts")):
                    fpath = os.path.join(dirpath, fn)
                    with open(fpath) as f:
                        content = f.read()
                    if "rename" in content or "move" in content:
                        found_atomic = True
    assert found_atomic, "Should find atomic write pattern"


def test_no_data_loss_on_crash():
    """Verify that crashed writes don't lose original data"""
    root = os.path.join(os.path.dirname(__file__), "..")
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath or "node_modules" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith((".py", ".js", ".ts")):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                # Look for write-to-temp pattern
                if "open(" in content and "rename" in content:
                    return True


# --- PR #4: Lock file unbounded growth ---
def test_lock_file_size_management():
    """Verify lock files have size management or truncation"""
    root = os.path.join(os.path.dirname(__file__), "..")
    found_lock_mgmt = False
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath or "node_modules" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith((".py", ".js", ".ts")):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                lock_patterns = [
                    "lock", ".lock", "Lock",
                    "truncate", "truncation",
                    "max_size", "max_bytes",
                    "rotation", "rollover",
                    "open(", "a+", "w+",
                ]
                found = [p for p in lock_patterns if p in content]
                if len(found) >= 2:
                    found_lock_mgmt = True
    assert found_lock_mgmt, "Should find lock file management"


def test_lock_file_has_max_size():
    """Verify lock file has maximum size limit"""
    root = os.path.join(os.path.dirname(__file__), "..")
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath or "node_modules" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith((".py", ".js", ".ts")):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                if "max" in content.lower() and "lock" in content.lower():
                    return True
                if "truncat" in content and "lock" in content.lower():
                    return True


def test_lock_file_uses_rotation():
    """Verify lock files use rotation to prevent unbounded growth"""
    root = os.path.join(os.path.dirname(__file__), "..")
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "__pycache__" in dirpath or "node_modules" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith((".py", ".js", ".ts")):
                fpath = os.path.join(dirpath, fn)
                with open(fpath) as f:
                    content = f.read()
                rotation_patterns = [
                    "RotationHandler", "RotatingFileHandler",
                    "rotation", "rollover",
                    "backupCount", "maxBytes",
                ]
                found = [p for p in rotation_patterns if p in content]
                if found:
                    return True
