import{j as t}from"./jsx-runtime-CfatFE5O.js";import{useMDXComponents as o}from"./index-DUy19JZU.js";import{M as r}from"./index-Cz3MCgmM.js";import{Q as p}from"./QuantityInput.stories-Dfyw1Vip.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./iframe-Dw0dJecd.js";import"./index-MhaI5ydX.js";import"./index-CJyPbrN5.js";import"./formik.esm-DyanDbCL.js";import"./BaseCheckbox-CAknIdKI.js";import"./index-DeARc5FM.js";import"./SvgIcon-CUWb-Ez8.js";import"./TextInput-lGM1fPdB.js";import"./BaseInput-zpkrYXWy.js";import"./FieldLayout-Dd55Pa2G.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-help-blUMxBcv.js";import"./Button-CSQAIFQX.js";import"./stroke-pass-CALgybTM.js";import"./Tooltip-CPMX2zM9.js";import"./useTooltipProps-C5TDwaI9.js";import"./Button.module-CvOOzViS.js";import"./types-DjX_gQD6.js";import"./FieldError-DblMbt5C.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-DooUcf1c.js";function i(e){const n={br:"br",code:"code",h1:"h1",h2:"h2",p:"p",pre:"pre",strong:"strong",...o(),...e.components};return t.jsxs(t.Fragment,{children:[`
`,`
`,`
`,t.jsx(r,{of:p}),`
`,t.jsx(n.h1,{id:"quantityinput",children:"QuantityInput"}),`
`,t.jsxs(n.p,{children:["A QuantityInput component is a combinaison of a TextInput and a Checkbox to define ",t.jsx(n.strong,{children:"quantities"}),". This component should be used when undefined quantity is meant to be interpreted as unlimited."]}),`
`,t.jsx(n.h2,{id:"using-quantityinput-over-textinput",children:"Using QuantityInput over TextInput"}),`
`,t.jsx(n.pre,{children:t.jsx(n.code,{className:"language-jsx",children:`<TextInput
  label="Quantity"
  type="number"
  value={quantity}
  onChange={setQuantity}
/>
`})}),`
`,t.jsxs(n.p,{children:["If undefined quantity is meant to be interpreted as unlimited, the QuantityInput component should always be used.",t.jsx(n.br,{}),`
`,"Otherwise, using TextInput is fine enough (mind min, max, and step props attributes)."]}),`
`,t.jsx(n.h2,{id:"extending-props",children:"Extending props"}),`
`,t.jsxs(n.p,{children:["The QuantityInput component picks a few props from the TextInput component, which itself sees its props extended from FieldLayoutBase and BaseInput.",t.jsx(n.br,{}),`
`,"It's best to choose what needs to be picked than extending the props from the TextInput component so the QuantityInput component can be more flexible and easier to maintain."]})]})}function L(e={}){const{wrapper:n}={...o(),...e.components};return n?t.jsx(n,{...e,children:t.jsx(i,{...e})}):i(e)}export{L as default};
