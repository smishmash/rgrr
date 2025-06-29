# RGRr Rules for Gemini

This document provides an overview of RGRr for AI agents that assist with development.

## Overview

RGRr is a python program to simulate resource distribution using different rules, in particular
following preferential attachment. It has a core simulator, a multi-step simulator, and different
mechanisms for adjusting distribution of resources. It also has different visualization methods.

As an AI assistant, your role is to help develop RGRr.

## Python Development Guidance

- **Style:** RGRr follows PEP 8. Code should pass `pw format`, which uses `black`.
- **Generated Files:** Python packages with generated files should extend their import path in
  `__init__.py`.
- **Unit Testing:** Unit tests should pass after each change.
- **Documentation:** All new code should have documentation.
- **Typing:** All new code should have type declarations.
- **Type Checking:** `mypy .` should not report errors after each change.
