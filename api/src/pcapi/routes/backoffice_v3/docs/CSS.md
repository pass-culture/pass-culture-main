## Backoffice CSS code convention


This documentation describe CSS class names code convention.

We use scss as a preprocessing language for css, read their [documentation](https://sass-lang.com/documentation/).

To watch for scss changes:

```bash
boussole watch --config src/pcapi/static/backofficev3/scss/boussole.yml --backend yaml
```

There is 4 categories of css rules:

1. [Base](#base-rules)
2. [Layout](#layout-rules)
3. [Module](#module-rules)
4. [State](#state-rules)

### Common rules and general convention

**We do not use `style=` attributes on element**

Except in JS when it's needed, when a `state` class is not possible.

Otherwise, forbidden for styling.

**We do not do styling using the `#id` selector, we use `.class`**

For the CSS language, the ID selectors are not needed since the performance difference between ID selectors and class selectors is
virtually non-existent and can make style structuring more complex due to increased specificity.

It also often (not to say always) leads to W3C validation errors [read more](HTML.md).

**We use prefixed class, example: `.pc-script-*` for a no-css but just pass Culture organisation scripting purposes (with python or js).**

When we separate the rules into four categories, conventions of namings are necessary to immediately understand to
which category that specific style belongs to and its role in the general set of the page.

Use a prefix to differentiate layout rules, status and module. (example `l-` for layout).
 
The use of prefixes such as `.grid-` also helps to clarify the separation between different layout styles. 
For state rules, use `.is-` as in `.is-hidden` or `.is-collapsed`. This makes it possible to describe things in a very readable way.

Modules represent the major part of a project. This is the reason why, the fact that each module starts with a prefix like `.module-` would be too long and useless. 
Modules just use the name of the module itself.

```css
/* Example of Module */
.pc-example { }
/* Text module */
.pc-callout { }
/* Test module with state */
.pc-callout.is-collapsed { }
/* Form module */
.pc-field { }
/* line alignement */
.pc-l-inline { }
``` 

### Base rules

A basic rule applies to an element that uses a selector element, a descendant selector, or a child selector, as well as than any pseudo-class. 
It has no class or ID selector. It defines the default style of an element for all his appearances on the page.

### Layout rules

For example, to use two styles of layout and switch from a fluid to fixed element:

```scss
.pc-article {
  width: 80%;
  float: left;
}
.pc-sidebar {
  width: 20%;
  float: right;
}
.pc-l-fixed {
  .pc-article {
    width: 600px;
  }
  .pc-sidebar {
    width: 200px;
  }
}
```

In this last example, the `.pc-l-fixed` class changes the design to making the layout fixed (width defined in pixels) while it was front fluid (width set in percentage).

### Module rules

A module is a smaller page component, it's your navigation bar, your carousels, your dialogs, your widgets etc.
These are the amenities on your page. The modules are found inside layout components, example:

```scss
.pc-module {
  &> h2 {
    padding: 5px;
  }
  span {
    background: #0aaaf1;
  }
}
``` 
Using `.module span` is fine if you can expect `span` to be used and laid out the same at each of its occurrences in this module.

For example, if you add another `span`, you will be in trouble:

```html
<div class="pc-folder">
  <span>32 items</span>
  <span>Name of the file</span>
</div>
```

You could decide here to add a class names to identify parts of the module:

```html
<div class="pc-folder">
  <span class="pc-folder-items">32 items</span>
  <span class="pc-folder-name">Name of the file</span>
</div>
```

Fight against specificity:

```scss
.pc-pod {
  width: 100%;
  input[type="text"] {
    width: 50%;
  }
} 
.pc-sidebar .pc-pod input[type="text"] {
  width: 100%;
}
.pc-pod-callout {
  width: 200px;
}
.pc-sidebar .pc-pod-callout input[type="text"], 
.pc-pod-callout input[type="text"] {
  width: 180px;
}
```

We have split our selectors to be able to override the specificity of the `.pc-sidebar`.

Instead, we should rather recognize that the arrangement fixed sidebar is a subclass of the `.`pod container and so, layout it accordingly:

```scss
.pc-pod {
  width: 100%;
  input[type="text"] {
    width: 50%;
  }
}
.pc-pod-constrained {
  input[type="text"] {
    width: 100%;
  }
}
.pc-pod-callout {
  width: 200px;
  input[type="text"] {
    width: 180px;
  }
}
```

### State rules

A state is something that grows and supersedes others styles. 

For example, an accordion section can either be in the state folded, or in the unrolled state. A message appears either in a success state or in an error state.

```html
{% set search_field_id = random_hash() %}
<header class="is-collapsed">
    <form>
      <div class="msg is-error">
        There was an error!
      </div>
      <label for="{{ search_field_id }}" class="is-hidden">Search:</label>
      <input id="{{ search_field_id }}" type="text">
    </form>
</header>
```

**Usage of `!important`**

You should always prefer to use more specific selector to override a previous behavior, and thus should not need `!important` flag.

However, if the `style=` attribute is used and not under your control (for example through a JavaScript library), then it might be your only way:

Keep in mind:

- Keep it inactive until you really need it, 
- **usage of `!important` should be avoided by all means**,
- **usage of `HTMLElement` attribute `style` should also be avoided by all means**.

### Learn more about smacss

We advised any developers to read at least once the smacss best practices ebook:

- Download the ebook:
  - English: http://smacss.com/files/smacss-en.zip
  - French: http://smacss.com/files/smacss-fr.pdf
- Visit their Website: http://smacss.com
