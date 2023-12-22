import{j as e}from"./jsx-runtime-ffb262ed.js";import{b as w}from"./formik.esm-49513253.js";import{l as m}from"./logo-pass-culture-1302d26b.js";import{R as a}from"./Thumb-e957c9e8.js";import"./index-76fb7be0.js";import"./_commonjsHelpers-de833af9.js";import"./hoist-non-react-statics.cjs-3f8ebaa8.js";import"./full-next-ebff3494.js";import"./Button-eca29e00.js";import"./index-a587463d.js";import"./index-f665786b.js";import"./index-48a71f03.js";import"./full-right-83efe067.js";import"./SvgIcon-c0bf369c.js";import"./Button.module-ec1646c9.js";import"./stroke-pass-cf331655.js";import"./Tooltip-7f0a196a.js";import"./useTooltipProps-b20503ef.js";import"./BaseCheckbox-0e6f2221.js";import"./BaseFileInput-5ea36249.js";import"./stroke-offer-ff89e161.js";import"./BaseInput-433b1c48.js";import"./BaseRadio-06d1d75a.js";import"./FieldError-10cbd29d.js";import"./stroke-error-ed5fe82d.js";import"./FieldSuccess-31bdacb0.js";import"./stroke-valid-9c345a33.js";import"./full-clear-9268779e.js";import"./Divider-7c035ea9.js";import"./SubmitButton-6174c831.js";import"./index-9d475cdf.js";import"./SelectInput-cdc4214a.js";import"./stroke-down-3d79f44b.js";import"./typeof-7fd5df1e.js";import"./stroke-close-3a7bfe9e.js";import"./Banner-de0c0ffa.js";import"./shadow-tips-help-841f916a.js";import"./shadow-tips-warning-66fb0429.js";import"./LinkNodes-efb5e12f.js";import"./full-link-9eb5e1cb.js";import"./InfoBox-8a1c95bc.js";const se={title:"ui-kit/forms/RadioButton",component:a},l=({withBorder:i,label1:f,label2:x})=>e.jsx(w,{initialValues:{},onSubmit:()=>{},children:({getFieldProps:n})=>e.jsxs(e.Fragment,{children:[e.jsx(a,{...n("gender"),label:f,name:"gender",value:"male",withBorder:i}),e.jsx(a,{...n("gender"),label:x,name:"gender",value:"female",withBorder:i})]})}),r=l.bind({});r.args={label1:"Male",label2:"Female"};const o=l.bind({});o.args={withBorder:!0,label1:"Male",label2:"Female"};const s=({src:i})=>e.jsxs("div",{style:{display:"flex",gap:"1rem"},children:[e.jsx("img",{src:i,width:100}),e.jsxs("p",{style:{display:"flex",flexDirection:"column"},children:[e.jsx("strong",{children:"Long titre lorem ipsum mon offre"}),"Test de sous-titre"]})]}),t=l.bind({});t.args={label1:e.jsx(s,{src:m}),label2:e.jsx(s,{src:m})};var d,p,u;r.parameters={...r.parameters,docs:{...(d=r.parameters)==null?void 0:d.docs,source:{originalSource:`({
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
  </Formik>`,...(F=(B=t.parameters)==null?void 0:B.docs)==null?void 0:F.source}}};const de=["Default","WithBorder","WithChildren"];export{r as Default,o as WithBorder,t as WithChildren,de as __namedExportsOrder,se as default};
