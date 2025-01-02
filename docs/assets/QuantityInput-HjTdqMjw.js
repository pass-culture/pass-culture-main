import{j as t}from"./jsx-runtime-CfatFE5O.js";import{useMDXComponents as i}from"./index-DUy19JZU.js";import{ae as s}from"./index-CSpumuM7.js";import{Q as r}from"./QuantityInput.stories-CBzodWX6.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./iframe-Da4bhVd_.js";import"../sb-preview/runtime.js";import"./index-B5DG7xGS.js";import"./index-CJyPbrN5.js";import"./formik.esm-DyanDbCL.js";import"./BaseCheckbox-BRleJ5rT.js";import"./index-DeARc5FM.js";import"./SvgIcon-B6esR8Vf.js";import"./TextInput-CjQ0Ox_l.js";import"./BaseInput-DeM_2B66.js";import"./FieldLayout-B6X2AoDt.js";import"./full-clear-CvNWe6Ae.js";import"./full-close-DkqMqJw6.js";import"./Button-DJHQc1no.js";import"./stroke-pass-C0Oiu4_F.js";import"./Tooltip-CNRbx6pV.js";import"./useTooltipProps-C5TDwaI9.js";import"./Button.module-B-6rmrBu.js";import"./types-DjX_gQD6.js";import"./FieldError-B3YKY1IQ.js";import"./stroke-error-BKdTEWJV.js";function o(n){const e={a:"a",blockquote:"blockquote",br:"br",code:"code",h1:"h1",h2:"h2",p:"p",pre:"pre",strong:"strong",...i(),...n.components};return t.jsxs(t.Fragment,{children:[`
`,`
`,`
`,t.jsx(s,{of:r}),`
`,t.jsx(e.h1,{id:"quantityinput",children:"QuantityInput"}),`
`,t.jsxs(e.p,{children:[`A QuantityInput component is a combinaison of a TextInput and a Checkbox
to define `,t.jsx(e.strong,{children:"quantities"}),`. This component should be used when undefined quantity
is meant to be interpreted as unlimited.`]}),`
`,t.jsx(e.h2,{id:"using-quantityinput-over-textinput",children:"Using QuantityInput over TextInput"}),`
`,t.jsx(e.pre,{children:t.jsx(e.code,{className:"language-jsx",children:`<TextInput
  label="Quantity"
  placeholder="Illimité"
  type="number"
  value={quantity}
  onChange={setQuantity}
/>
`})}),`
`,t.jsx(e.p,{children:`This lacks accessibility support.
Placeholders are generally something to avoid since they disappear when the input is focused,
or when the user starts typing.
They tend to be stylised with a lighter color, which can be hard to read for some users.
In this case, the placeholder was used to indicate that the quantity was unlimited,
which is not a placeholder's purpose.`}),`
`,t.jsxs(e.blockquote,{children:[`
`,t.jsxs(e.p,{children:['"The placeholder text should provide a brief hint to the user as to the expected type of data that should be entered into the control."',t.jsx(e.br,{}),`
`,"-- ",t.jsx(e.a,{href:"https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#attr-placeholder",rel:"nofollow",children:"MDN Web Docs"})]}),`
`]}),`
`,t.jsxs(e.p,{children:["If undefined quantity is meant to be interpreted as unlimited, the QuantityInput component should always be used.",t.jsx(e.br,{}),`
`,"Otherwise, using TextInput is fine enough (mind min, max, and step props attributes)."]}),`
`,t.jsx(e.h2,{id:"extending-props",children:"Extending props"}),`
`,t.jsxs(e.p,{children:[`The QuantityInput component picks a few props from the TextInput component,
which itself sees its props extended from FieldLayoutBase and BaseInput.`,t.jsx(e.br,{}),`
`,`It's best to choose what needs to be picked than extending the props from the TextInput component
so the QuantityInput component can be more flexible and easier to maintain.`]})]})}function B(n={}){const{wrapper:e}={...i(),...n.components};return e?t.jsx(e,{...n,children:t.jsx(o,{...n})}):o(n)}export{B as default};
