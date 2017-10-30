---
layout: home
tags:
  - internal
title: Flask Guide
---

# Flask Guide

Our public website is built using [Flask][flask], the world's simplest and smallest web framework for Python.

The tutorial that we followed to whip together this project is called ["Dead easy yet powerful static website generator with Flask"][dead-easy]. In this tutorial, Flask is combined with several Flask plugins, including [Frozen-Flask][frozen-flask] and [Flask-Assets][flask-assets], to create a local web application for static files with basic templating support that also supports Markdown and Jinja2 templating.

The layout of the local repository on your machine is straightforward. I'll walk through it now.

## Cloning the project

<small>*Note*: These steps assume you already have `git`, `virtualenv`, and `npm` installed and set up locally.</small>

To get this project locally, you just need to clone it from Github into your `~/repos` directory:

    cd ~/repos
    git clone git@github.com:amontalenti/muckhacker.git web
    cd muckhacker

Then, you need to set up a `virtualenv` for the project and install its requirements:

    mkvirtualenv muckhacker
    pip install -r requirements.txt

Finally, you need to install two dependencies via `npm`, the Node.JS package manager. These handle LESS -> CSS compilation (`lessc`) and CSS minification (`clean-css`):

    sudo npm install -g less
    sudo npm install -g clean-css

Once all of that is installed, you should be able to build the static website by issuing this command:

    python app.py build

You will then have the built static website in the `build/` directory.

## Develop locally

The cool thing about this project is that the Flask server is a full-fledged Python web server that live-compiles your assets and templates. The `python app.py build` command uses an extension to Flask called Frozen-Flask, which actually crawls every accessible URL and generates static HTML/CSS that can be easily uploaded to a static web server. This makes deployment dead easy.

But, when locally developing with Flask, you *don't* need to re-generate the whole site after each change. (This is a major advantage over systems like `hyde` and `pelican`.)

To run a local development server, you have two options.

### Flask runserver

You can use:

    python app.py runserver

Which will just run a standard local development server on port 5000. You can then navigate to [http://localhost:5000][local-5000] and you will see the main index page. Navigating to [http://localhost:5000/pages/flask][local-5000-flask] will bring you to the rendered version of *this very page you are looking at now!*

### Flask livereload

The second option is to use:

    python app.py livereload

This runs a modified version of the Flask server that has built-in support for the excellent development tool, [livereload][livereload]. When combined with a [Safari, Chrome, or Firefox extension][livereload-ext], you no longer have to hit reload upon changing a local file during editing. This allows near-instantaneous feedback of your changes! Also, just like the normal server, you access this via [http://localhost:5000][local-5000].

## Deployment

### Deploying to divshot

**NOTE: divshot is out of business, probably need to switch to something like netlify.com now.**

Speaking of divshot, if you want to deploy to it, you simply need the Node-based tooling.

    sudo npm install -g divshot

Then you simply use:

    divshot push staging

And you will be able to see your pushed changes at [http://staging.yourapp.divshot.io][divshot-staging]. The `fab deploy_divshot` command simply changes some settings for production (e.g. enabling CSS minification).

## Content Management

### Markdown Pages

All Markdown-formatted files reside in the `pages/` directory. A simple Markdown-oriented CMS was layered atop Flask and was built in just a few lines of Python. It allows you to list all the Markdown pages by navigating to [http://localhost:5000/list][local-5000-list].

The CMS is super simple. All Markdown files have some metadata, using a de facto standard known as [YAML front matter][yaml-frontmatter]. The `title` property controls the page title. The `tags` property allows you to apply arbitrary tags to organize pages. For example, we could have tags like `case-study`, `faq`, or `landing-page`. The YAML front matter for this page looks like this:

    ---
    layout: home
    tags:
      - internal
    title: Flask Guide
    ---

By using this setup, we can be very flexible about the tools available to our frontend design and marketing team. Copy editing and content creation tasks can be performed by anyone on the team using [Github's editor][github-editor] or [Prose.io][prose-io] pointed at the `pages/` directory. Changes can be easily previewed upon push/commit via the automated Travis builds.

### Jinja2 Templates

Once you need to go beyond plain copy and content, you start to use [Jinja2 templates][jinja2]. This is an easy-to-learn templating language that shares a lot of functionality with Python, and even includes handy [designer documentation][jinja2-designer] which doesn't assume any Python programming knowledge.

The templates are located in `templates/`, and there is only a little more structure below that. A subdirectory called `layout/` contains base templates, which are used for header/footer setup or template heirarchy. This is also connected to the `layout` field in Markdown pages -- it's assumed that a certain Jinja2 template will be applied to a Markdown page based on that frontmatter metadata property. The second directory is `partials/`. This contains little template snippets that are re-usable from other templates.

The full functioning of Jinja2 templates is beyond the scope of this document, but needless to say, they are very powerful. The following template snippet shows how the Markdown page you are reading now is rendered:

    {% extends "layout/" + page.layout + ".jinja2.html" %}

    {% block title -%}
        {{ page.title }}
    {%- endblock title %}

    {% block content %}
        {{ page.html|safe }}

        <a href="{{ url_for("list") }}">&laquo; list all pages</a>
    {% endblock content %}

In this case, the page is extending `layout/home.jinja2.html` (a base template) and then filling in two blocks, `title` and `content` in order to render the page.

### LESS for CSS

Instead of using bare CSS, we use LESS, a CSS pre-processor. The compilation of `.less` files is handled automatically by `Flask-Assets`, a Flask plugin.

There is already a starting `.less` file in `assets/less/home.less`. To register a new `.less` file, you need to register it in the `Bundle` configuration in `app.py`. It is automatically piped through `lessc`, the LESS compiler, upon every load of a new version of the file.

### JavaScript libraries

There is also a set of JavaScript libraries included on every page, including [jQuery][jquery], [d3js][d3js] and [Underscore][underscore].

### Bootstrap for page structure

Building on LESS, you have [Bootstrap][bootstrap] available for page structure. The `bootstrap.css` file is automatically included, as well as the JavaScript support plugin, `bootstrap.js`.

### Any other assets

Any other assets (such as images, gifs, videos) can be included somewhere in the `assets/` directory.

### Minification

When deploying static assets to staging or production environments, the JavaScript code will be run through a JS minifier (rjsmin) and the CSS code will, as well (clean-css). 4 bundles will be built per page, which are:

* `css_all.css`: all custom CSS including LESS files, compiled & minified
* `js_all.js`: all custom JS, minified
* `css_lib.css`: all library CSS, minified
* `js_lib.js`: all library JS, minified

Obviously, minification makes things difficult to debug, which is why this is only a staging/production setting. When deploying to development or testing locally, the `ASSET_DEBUG = True` mode is set, which will output separate, unminified JS/CSS files for each file included. Hooray debuggability.

[flask]: http://flask.pocoo.org/
[dead-easy]: https://nicolas.perriault.net/code/2012/dead-easy-yet-powerful-static-website-generator-with-flask/
[frozen-flask]: https://pythonhosted.org/Frozen-Flask/
[flask-assets]: http://flask-assets.readthedocs.org/en/latest/
[local-5000]: http://localhost:5000
[local-5000-flask]: http://localhost:5000/pages/flask/
[livereload]: http://livereload.readthedocs.org/en/latest/
[livereload-ext]: http://feedback.livereload.com/knowledgebase/articles/86242
[divshot]: http://divshot.com
[divshot-development]: http://development.yourapp.divshot.io
[divshot-staging]: http://staging.yourapp.divshot.io
[local-5000-list]: http://localhost:5000/list
[yaml-frontmatter]: http://jekyllrb.com/docs/frontmatter/
[github-editor]: https://github.com/amontalenti/muckhacker/tree/master/pages
[prose-io]: http://prose.io/
[jinja2]: http://jinja.pocoo.org/
[jinja2-designer]: http://jinja.pocoo.org/docs/templates/
[bootstrap]: http://getbootstrap.com/
[jquery]: http://jquery.org
[d3js]: http://d3js.org
[underscore]: http://underscorejs.org/
