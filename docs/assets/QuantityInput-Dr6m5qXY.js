import{j as t}from"./jsx-runtime-BYYWji4R.js";import{useMDXComponents as o}from"./index-DUy19JZU.js";import{M as r}from"./index-DtsXZEle.js";import{Q as p}from"./QuantityInput.stories-BjQE6ox2.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./iframe-Cos0wx4G.js";import"./index-BUMxx5F6.js";import"./index-CBft-ReK.js";import"./formik.esm-Dmsc_7od.js";import"./BaseCheckbox-yx2QTGF8.js";import"./index-DeARc5FM.js";import"./SvgIcon-CyWUmZpn.js";import"./TextInput-Bx_PUY8J.js";import"./BaseInput-BI1b_EYZ.js";import"./FieldLayout-CaweZlPA.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-help-blUMxBcv.js";import"./Button-COUp2H-B.js";import"./stroke-pass-CALgybTM.js";import"./Tooltip-BpKRYYrm.js";import"./Button.module-D_4QtxUL.js";import"./types-yVZEaApa.js";import"./FieldError-azuIsM2E.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-CTPArH5Q.js";import"./index.module-DF6qn1Ex.js";function i(e){const n={br:"br",code:"code",h1:"h1",h2:"h2",p:"p",pre:"pre",strong:"strong",...o(),...e.components};return t.jsxs(t.Fragment,{children:[`
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
