# Exemple — changer le fond de l'en-tête d'un tableau

Branche de discussion, jamais mergée. Illustre `NOTES.md` sur un cas concret.

**Demande du design** : « l'en-tête gris des tableaux passe sur le token `color.background.subtle` » (`#f1f1f4`, `@pass-culture/design-system/lib/pro/light.css`).

## AVANT — avec Bootstrap

### 1. Trouver ce qui peint l'en-tête : trois recettes pour un même concept

`api/src/pcapi/routes/backoffice/templates/components/presentation/list.html:37` (toutes les pages de liste)

```html
<thead>
  <tr class="bg-secondary-subtle fs-7 align-middle">{{ table_header }}</tr>
</thead>
```

`api/src/pcapi/routes/backoffice/templates/offer/details.html:205` (idem `products/details.html`, `artists/details.html`, `accounts/get/details/personal_information_registration.html`)

```html
<thead class="table-light">
  <tr class="table-secondary fs-7">
```

`api/src/pcapi/routes/backoffice/templates/components/history/actions.html:6` (conditionnel)

```html
<tr {%+ if use_new_tab_ui %}
    class="bg-secondary-subtle fs-7 align-middle"
    {% endif %}>
```

Résultat aujourd'hui (`static/backoffice/css/bundle.css`) : **deux gris différents** pour le même « en-tête » — `#e9ecef` (`bg-secondary-subtle`) et `#e2e3e5` (`table-secondary`). Aucun des deux n'est un token DS.

### 2. Traduire le token en langage Bootstrap : aucune variable ne correspond

`api/src/pcapi/static/backoffice/scss/pc/_variables.scss`

```scss
// Option A : changer la couleur « secondary subtle »
$secondary-bg-subtle: #f1f1f4;
```

Effets de bord : `bg-secondary-subtle` n'est pas « l'en-tête de tableau », c'est « la couleur secondaire, version pâle ». Changent aussi :

- les badges `format_badge(..., "secondary")` (`Pass 17`, `Pass 18`, `En instruction`… — `routes/backoffice/filters.py:251`, 12 appels dans les templates),
- les vignettes sans image `.offer-no-image` (`components/presentation/images.html`, `products/details.html`, `artists/details.html`).

Et ça ne touche pas les en-têtes `table-secondary` des pages de détail.

```scss
// Option B : changer la variante « table-secondary »
$table-variants: map-merge($table-variants, ("secondary": #f1f1f4));
```

Piège : `$table-variants` est calculée par Bootstrap (`shift-color($secondary, -80%)`) au premier `@import "../bootstrap/variables"`, **avant** les surcharges BO. Surcharger `$secondary` ou `$light` ne sert donc à rien — preuve : le BO fixe `$light: $white`, mais `bundle.css` sort `.table-light{--bs-table-bg: #f8f9fa}`. Il faut écraser la map elle-même, et les couleurs de survol, bordure et zébrure restent dérivées par Bootstrap (`mix()`, `color-contrast()`), pas par le DS.

### 3. Comprendre la cascade Bootstrap pour que la couleur s'affiche

`api/src/pcapi/static/backoffice/scss/pc/_variables.scss:145`

```scss
$table-bg: inherit;
```

Sans ce hack, `.table > :not(caption) > * > *` repeint chaque cellule avec `var(--bs-table-bg)` + un `box-shadow: inset 0 0 0 9999px …` et masque le `bg-*` posé sur le `<tr>`.

**Bilan** : 3 recettes à recenser, 2 variables Bootstrap dont aucune ne veut dire « en-tête de tableau », des effets de bord sur des badges et des images, un ordre d'import à connaître. Pour un dev backend, c'est de la rétro-ingénierie de Bootstrap, pas de l'application d'une maquette.

## APRÈS — composant sorti de Bootstrap, vocabulaire DS

`api/src/pcapi/static/backoffice/scss/pc/_tokens.scss` (copie des tokens DS, ou import du paquet épinglé plus tard)

```scss
:root {
  --color-background-subtle: #f1f1f4;
  --color-background-hover: #f1f1f4;
  --color-border-subtle: #cbcdd2;
  --color-text-subtle: #696a6f;
  --typography-body-xs-font-size: 0.75rem;
}
```

`api/src/pcapi/static/backoffice/scss/pc/components/_table.scss`

```scss
.pc-table {
  width: 100%;
  border-collapse: collapse;
}

.pc-table__head {
  background-color: var(--color-background-subtle);
  color: var(--color-text-subtle);
  font-size: var(--typography-body-xs-font-size);
}

.pc-table__cell {
  padding: 0.5rem;
  border-bottom: 1px solid var(--color-border-subtle);
}

.pc-table__row:hover {
  background-color: var(--color-background-hover);
}
```

`api/src/pcapi/routes/backoffice/templates/components/presentation/list.html` (et toutes les pages de détail, une seule recette)

```html
<table class="pc-table">
  <thead class="pc-table__head">
    <tr>
      <th class="pc-table__cell" scope="col">Nom</th>
    </tr>
  </thead>
  <tbody>
    <tr class="pc-table__row">
      <td class="pc-table__cell">Le Grand Rex</td>
    </tr>
  </tbody>
</table>
```

### La même demande du design, après

- « L'en-tête passe sur `background.subtle` » → **une ligne** dans `_table.scss`, le nom du token est celui de Figma.
- « `background.subtle` change de valeur » → **une ligne** dans `_tokens.scss` (ou une montée de version du paquet), et tout ce qui dit « subtle » suit, comme voulu.
- Aucun badge, aucune image ne bouge : un composant ne partage une couleur qu'en partageant un token, explicitement.

## En résumé

| | Bootstrap | Hors Bootstrap |
| --- | --- | --- |
| Vocabulaire | `secondary`, `light`, `bg-*-subtle`, `table-*` | Celui du DS : `background.subtle`, `text.subtle`… |
| Où changer | À deviner (2 variables, 3 recettes) | `_table.scss` ou `_tokens.scss` |
| Valeurs | Calculées par Bootstrap (`shift-color`, `mix`) | Tokens DS tels quels |
| Effets de bord | Badges, images, tout `bg-secondary-subtle` | Aucun hors du composant |
| Prérequis | Connaître la cascade et l'ordre d'import Bootstrap | Lire 20 lignes de CSS |
