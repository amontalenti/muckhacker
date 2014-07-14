---
layout: home
tags:
  - internal
title: Markdown Guide
---

# Markdown Guide

Markdown is a lightweight "markup" language (get it?) that is a powerful alternative to HTML for content-heavy (that is, text-oriented) content.

Not only is Markdown supported in many tools we use -- like Github, Lighthouse, Trello, and Wordpress -- but it also provides a simplified, lowest-common-denominator way for everyone on the marketing and product team to participate easily and simply in content creation, copy edits, and the like.

## Learning Markdown

There are a slew of resources for learning Markdown online, but one thing to watch out for is that there are several "Markdown flavors" out there.

Here is a good learning plan for Markdown:

1. [Github's Markdown basics page][markdown-basics]
2. [Github's Markdown syntax for tables][markdown-tables]
3. [An advanced guide to Markdown with Pelican][markdown-pelican]

[markdown-basics]: https://help.github.com/articles/markdown-basics
[markdown-tables]: https://help.github.com/articles/github-flavored-markdown#tables
[markdown-pelican]: http://www.joshuazhang.net/posts/2013/Mar/markdown-for-pelican-ref.html

Once you've read these three, you should be good to with the basics. How about putting your knowledge to work? Well, to do that, you'll need a **Markdown editor** of some sort.

## Using Prose.io

A great way to get started with Markdown (and even to continue editing Markdown moving forward) is to use the excellent Prose.io editor. Simply navigate to [Prose.io][prose] and authenticate your Github account through that site.

[prose]: http://prose.io

You'll be able to see the features of Prose.io. It's a nice, clean interface -- you get the main Markdown editing view, you get a preview button on the right hand side, and a save button, which will automagically save your work using a Github commit. The little "help" icon also provides an inline help and reference for Markdown syntax. What's great about this interface is that it will syntax highlight Markdown for you even when you're editing the plain text, but then preview it as HTML when you click the preview button.

This project is open source and can quickly navigate to any file accessible in your Github account. The main thing it isn't good at right now is working with images and printing content, but this will probably get better over time. (It's a new tool.)

## Using SimpleNote

An alternative to Prose.io is [SimpleNote][simplenote] from Automattic. SimpleNote has its own storage of your plain text and Markdown notes, and supports Markdown edit/preview in their web-based version. They also support syncing across pretty much every major mobile platform -- Android, iOS, and they have tablet editions of their app. Once you have a Markdown file from SimpleNote, it's easy enough to copy-paste it into Github to be part of the CMS.

## Using iA Writer

A lot of journalists also swear by the iPad Markdown-compatible writing environment designed by Information Architects, called [iA Writer][iawriter]. It provides a clean, "focus" mode that allows you to focus 100% on creation and writing-as-craft.

I hear iA Writer on an iPad with a Bluetooth Keyboard makes for a great "journalist typewriter 2.0".

[iawriter]: http://www.iawriter.com/

## Going local

You may find it more convenient to run a local Markdown editor. On Mac OS X, a very simple Markdown editor is [Byword][byword]. If you use [Sublime Text 2][sublime], it will be a little more advanced, but it will also support HTML and CSS, which may come in handy when working with the public website templates. iA Writer also has a Mac OS X version.

For working with Github, I'd recommend using [Github's official Mac OS X app][github-app].


[byword]: http://bywordapp.com/
[sublime]: http://www.sublimetext.com/2
[github-app]: https://mac.github.com/

All you need to do is edit the `.md` files locally on your machine and commit / push them via Github when you're ready to share.
