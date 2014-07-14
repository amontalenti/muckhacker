---
layout: home
tags:
  - internal
title: Site Motivation
---

# Motivation

This document explains the motivation behind MuckHacker.

## A CMS you can understand

The code that implements the whole CMS is in a single Python file that uses Flask plus some plugins, and that everyone can read/understand with ease.

## Developing is easy

Developing locally uses a normal Flask server, so changes in templates/CSS/JS are reflected instantaneously and don't require a complicated watch/rebuild process locally. A special "livereload" mode is included for convenience which wraps the Flask server in a livereload-compliant server, which lets you use it with the official browser plugins.

## One command to build the site

It's fast. If you run `python app.py build`, like magic, within <1s, you'll get a build/ directory with all the static assets. Likewise, fab tasks make it almost as fast to deploy new changes of a beta/staging/production site.

## Assets are managed sanely

Thanks to Flask-Assets integration, you get sane CSS/JS bundles with local develop and production modes.

## It bundles a Markdown CMS

Enough said -- Markdown is the future!
