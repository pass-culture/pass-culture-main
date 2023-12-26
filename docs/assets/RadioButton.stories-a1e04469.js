import{j as e}from"./jsx-runtime-4cb93332.js";import{b as w}from"./formik.esm-8d42c991.js";import{l as m}from"./logo-pass-culture-1302d26b.js";import{R as a}from"./Thumb-5b544978.js";import"./index-83a10e79.js";import"./_commonjsHelpers-de833af9.js";import"./full-next-ebff3494.js";import"./Button-a27a2a57.js";import"./index-a587463d.js";import"./index-4a87243b.js";import"./index-a9c6ff12.js";import"./full-right-83efe067.js";import"./SvgIcon-04d0ac1c.js";import"./Button.module-ec1646c9.js";import"./stroke-pass-cf331655.js";import"./Tooltip-1aec8863.js";import"./useTooltipProps-e39310f5.js";import"./BaseCheckbox-a0b74514.js";import"./BaseFileInput-baa5bac9.js";import"./stroke-offer-db646768.js";import"./BaseInput-0dfdd1cf.js";import"./BaseRadio-4cf2ec4b.js";import"./FieldError-66875701.js";import"./stroke-error-ed5fe82d.js";import"./FieldSuccess-7104acd6.js";import"./stroke-valid-9c345a33.js";import"./full-clear-9268779e.js";import"./Divider-98b6f559.js";import"./SubmitButton-5794aeb7.js";import"./index-9d475cdf.js";import"./SelectInput-394a5c6a.js";import"./stroke-down-3d79f44b.js";import"./typeof-7fd5df1e.js";import"./stroke-close-3a7bfe9e.js";import"./Banner-f287853f.js";import"./shadow-tips-help-841f916a.js";import"./shadow-tips-warning-66fb0429.js";import"./LinkNodes-b886ae87.js";import"./full-link-9eb5e1cb.js";import"./InfoBox-910ddbb0.js";const me={title:"ui-kit/forms/RadioButton",component:a},l=({withBorder:i,label1:f,label2:x})=>e.jsx(w,{initialValues:{},onSubmit:()=>{},children:({getFieldProps:n})=>e.jsxs(e.Fragment,{children:[e.jsx(a,{...n("gender"),label:f,name:"gender",value:"male",withBorder:i}),e.jsx(a,{...n("gender"),label:x,name:"gender",value:"female",withBorder:i})]})}),r=l.bind({});r.args={label1:"Male",label2:"Female"};const o=l.bind({});o.args={withBorder:!0,label1:"Male",label2:"Female"};const s=({src:i})=>e.jsxs("div",{style:{display:"flex",gap:"1rem"},children:[e.jsx("img",{src:i,width:100}),e.jsxs("p",{style:{display:"flex",flexDirection:"column"},children:[e.jsx("strong",{children:"Long titre lorem ipsum mon offre"}),"Test de sous-titre"]})]}),t=l.bind({});t.args={label1:e.jsx(s,{src:m}),label2:e.jsx(s,{src:m})};var d,p,u;r.parameters={...r.parameters,docs:{...(d=r.parameters)==null?void 0:d.docs,source:{originalSource:`({
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
  </Formik>`,...(F=(B=t.parameters)==null?void 0:B.docs)==null?void 0:F.source}}};const se=["Default","WithBorder","WithChildren"];export{r as Default,o as WithBorder,t as WithChildren,se as __namedExportsOrder,me as default};
