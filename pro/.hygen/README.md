## Hygen

[Documentation](http://www.hygen.io/docs/faq)

Hygen est un générateur de code. Voici un example d'utilisation:

```javascript
$ yarn new:component

yarn run v1.22.10
$ hygen new component
✔ Which design level? · new_components
✔ What is the component name? · TestComponent
✔ Where is the directory(Optional) ·

Loaded templates: .hygen
       added: src/components/new_components/TestComponent/TestComponent.tsx
       added: src/components/new_components/TestComponent/index.tsx
       added: src/components/new_components/TestComponent/README.md
       added: src/components/new_components/TestComponent/TestComponent.stories.tsx
       added: src/components/new_components/TestComponent/styles.module.scss
       added: src/components/new_components/TestComponent/__specs__/TestComponent.spec.tsx
```

Note: A voir si nous prenons ou non le découpage en atmos/molecules/organisms plutot que ui-kit/new_components/screen

### Cookbook

#### Conditional Rendering ([documentation](http://www.hygen.io/docs/templates#conditional-rendering))

```ejs
"<%= message ? `where/to/render/${name}.js` : null %>"
```