## PcBackofficeApp

In our HTML templates, **we have forbidden** the usage of the `id` attributes.

In general, we will always prefer a css class name. CSS class names have their own standard, read [./CSS.md](CSS.md) for all details.

There are some case where you must set an `id` attributes, those are exceptions, and we must generate the id using:

```html
{% set some_id = random_hash() %}
```

## Required by forms

If `<label />` is not parent of the input, it won't be controlling the form element on click.

To control the form element attached to the label, you must use `for` attributes on `<label />`, and `id` attributes on the form element (`textarea`, `input`).

This is often necessary for input such as `<input type="checkbox" />` or `<input type="radio" />`.

### Examples

In this case, we **must** generate the id dynamically:

```html
<div class="form-floating">
  {% set date_field_id = random_hash() %}
  <input
    type="date"
    id="{{ date_field_id }}"
    name="{{ field.name }}"
    class="form-control"
    value="{{ field.data if field.data else "" }}"
  >
  <label for="{{ date_field_id }}">{{ field.label.text }}</label>
</div>
```

## Required by accessibility

The `aria-describedby` attribute:

- lists the `ids` of the elements that describe the object. It is used to establish a relationship between widgets or groups and the text that describes them,
- is not limited to form controls. It can also be used to associate static text with widgets, groups of elements, regions that have a heading, definitions, and more, 
can be used with semantic HTML elements and with elements that have an ARIA role.

### Examples

This is :heavy_multiplication_x::

```html
<button aria-describedby="trash-desc">Move to trash</button>
<p id="trash-desc">
  Items in the trash will be permanently removed after 30 days.
</p>
```

This is :heavy_check_mark::

```html
{% set trash_aria_describedby_id = random_hash() %}
<button aria-describedby="{{ trash_aria_describedby_id }}">Move to trash</button>
<p id="{{ trash_aria_describedby_id }}">
  Items in the trash will be permanently removed after 30 days.
</p>
```

## Required by Turbo Frame

You can use the attribute `id` to identify `<turbo-frame />`, this is the only case where you don't want to generate the `id` with, ex:

```html
<turbo-frame id="some_frame">
  <!-- your frame content -->
</turbo-frame>
```

