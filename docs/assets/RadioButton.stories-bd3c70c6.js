import{j as e}from"./jsx-runtime-ffb262ed.js";import{a as w}from"./formik.esm-96bdd02b.js";import{l as m}from"./logo-pass-culture-1302d26b.js";import{R as l}from"./RadioButton-43e2bfa6.js";import"./index-76fb7be0.js";import"./_commonjsHelpers-de833af9.js";import"./hoist-non-react-statics.cjs-3f8ebaa8.js";import"./index-a587463d.js";import"./BaseCheckbox-2cbf2f9d.js";import"./BaseFileInput-5547a44b.js";import"./stroke-down-fe50db78.js";import"./BaseInput-fad17e7a.js";import"./SvgIcon-c0bf369c.js";import"./AutocompleteList-a5544a8b.js";import"./BaseRadio-d0e61859.js";import"./full-clear-9268779e.js";import"./Tooltip-383b3df2.js";import"./FieldError-0089fdbc.js";import"./stroke-error-ed5fe82d.js";import"./FieldSuccess-31bdacb0.js";import"./stroke-valid-9c345a33.js";const G={title:"ui-kit/forms/RadioButton",component:l},i=({withBorder:a,label1:f,label2:x})=>e.jsx(w,{initialValues:{},onSubmit:()=>{},children:({getFieldProps:s})=>e.jsxs(e.Fragment,{children:[e.jsx(l,{...s("gender"),label:f,name:"gender",value:"male",withBorder:a}),e.jsx(l,{...s("gender"),label:x,name:"gender",value:"female",withBorder:a})]})}),r=i.bind({});r.args={label1:"Male",label2:"Female"};const o=i.bind({});o.args={withBorder:!0,label1:"Male",label2:"Female"};const d=({src:a})=>e.jsxs("div",{style:{display:"flex",gap:"1rem"},children:[e.jsx("img",{src:a,width:100}),e.jsxs("p",{style:{display:"flex",flexDirection:"column"},children:[e.jsx("strong",{children:"Long titre lorem ipsum mon offre"}),"Test de sous-titre"]})]}),t=i.bind({});t.args={label1:e.jsx(d,{src:m}),label2:e.jsx(d,{src:m})};var n,p,u;r.parameters={...r.parameters,docs:{...(n=r.parameters)==null?void 0:n.docs,source:{originalSource:`({
  withBorder,
  label1,
  label2
}) => <Formik initialValues={{}} onSubmit={() => {}}>
    {({
    getFieldProps
  }) => {
    return <>
          <RadioButton {...getFieldProps('gender')} label={label1} name="gender" value="male" withBorder={withBorder} />
          <RadioButton {...getFieldProps('gender')} label={label2} name="gender" value="female" withBorder={withBorder} />
        </>;
  }}
  </Formik>`,...(u=(p=r.parameters)==null?void 0:p.docs)==null?void 0:u.source}}};var g,c,b;o.parameters={...o.parameters,docs:{...(g=o.parameters)==null?void 0:g.docs,source:{originalSource:`({
  withBorder,
  label1,
  label2
}) => <Formik initialValues={{}} onSubmit={() => {}}>
    {({
    getFieldProps
  }) => {
    return <>
          <RadioButton {...getFieldProps('gender')} label={label1} name="gender" value="male" withBorder={withBorder} />
          <RadioButton {...getFieldProps('gender')} label={label2} name="gender" value="female" withBorder={withBorder} />
        </>;
  }}
  </Formik>`,...(b=(c=o.parameters)==null?void 0:c.docs)==null?void 0:b.source}}};var h,B,F;t.parameters={...t.parameters,docs:{...(h=t.parameters)==null?void 0:h.docs,source:{originalSource:`({
  withBorder,
  label1,
  label2
}) => <Formik initialValues={{}} onSubmit={() => {}}>
    {({
    getFieldProps
  }) => {
    return <>
          <RadioButton {...getFieldProps('gender')} label={label1} name="gender" value="male" withBorder={withBorder} />
          <RadioButton {...getFieldProps('gender')} label={label2} name="gender" value="female" withBorder={withBorder} />
        </>;
  }}
  </Formik>`,...(F=(B=t.parameters)==null?void 0:B.docs)==null?void 0:F.source}}};const H=["Default","WithBorder","WithChildren"];export{r as Default,o as WithBorder,t as WithChildren,H as __namedExportsOrder,G as default};
//# sourceMappingURL=RadioButton.stories-bd3c70c6.js.map
