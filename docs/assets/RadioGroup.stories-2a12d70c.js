import{j as n}from"./jsx-runtime-ffb262ed.js";import{b as q}from"./formik.esm-49513253.js";import{b as h,c as B}from"./Thumb-e957c9e8.js";import"./index-76fb7be0.js";import"./_commonjsHelpers-de833af9.js";import"./hoist-non-react-statics.cjs-3f8ebaa8.js";import"./full-next-ebff3494.js";import"./Button-eca29e00.js";import"./index-a587463d.js";import"./index-f665786b.js";import"./index-48a71f03.js";import"./full-right-83efe067.js";import"./SvgIcon-c0bf369c.js";import"./Button.module-ec1646c9.js";import"./stroke-pass-cf331655.js";import"./Tooltip-7f0a196a.js";import"./useTooltipProps-b20503ef.js";import"./BaseCheckbox-0e6f2221.js";import"./BaseFileInput-5ea36249.js";import"./stroke-offer-ff89e161.js";import"./BaseInput-433b1c48.js";import"./BaseRadio-06d1d75a.js";import"./FieldError-10cbd29d.js";import"./stroke-error-ed5fe82d.js";import"./FieldSuccess-31bdacb0.js";import"./stroke-valid-9c345a33.js";import"./full-clear-9268779e.js";import"./Divider-7c035ea9.js";import"./SubmitButton-6174c831.js";import"./index-9d475cdf.js";import"./SelectInput-cdc4214a.js";import"./stroke-down-3d79f44b.js";import"./typeof-7fd5df1e.js";import"./stroke-close-3a7bfe9e.js";import"./Banner-de0c0ffa.js";import"./shadow-tips-help-841f916a.js";import"./shadow-tips-warning-66fb0429.js";import"./LinkNodes-efb5e12f.js";import"./full-link-9eb5e1cb.js";import"./InfoBox-8a1c95bc.js";const dr={title:"ui-kit/forms/RadioGroup",component:h},e={name:"question",legend:"This is the legend",direction:B.VERTICAL,group:[{label:"Oui",value:"question1"},{label:"Non",value:"question2"}],withBorder:!1},t=({direction:F,name:b,group:w,legend:R,withBorder:f})=>n.jsx(q,{initialValues:{question:{}},onSubmit:()=>{},children:({getFieldProps:k})=>n.jsx(h,{...k("group"),direction:F,group:w,name:b,legend:R,withBorder:f})}),r=t.bind({});r.args=e;const o=t.bind({});o.args={...e,withBorder:!0};const i=t.bind({});i.args={...e,direction:B.HORIZONTAL};var p,m,a;r.parameters={...r.parameters,docs:{...(p=r.parameters)==null?void 0:p.docs,source:{originalSource:`({
  direction,
  name,
  group,
  legend,
  withBorder
}) => <Formik initialValues={{
  question: {}
}} onSubmit={() => {}}>
    {({
    getFieldProps
  }) => {
    return <RadioGroup {...getFieldProps('group')} direction={direction} group={group} name={name} legend={legend} withBorder={withBorder} />;
  }}
  </Formik>`,...(a=(m=r.parameters)==null?void 0:m.docs)==null?void 0:a.source}}};var s,d,u;o.parameters={...o.parameters,docs:{...(s=o.parameters)==null?void 0:s.docs,source:{originalSource:`({
  direction,
  name,
  group,
  legend,
  withBorder
}) => <Formik initialValues={{
  question: {}
}} onSubmit={() => {}}>
    {({
    getFieldProps
  }) => {
    return <RadioGroup {...getFieldProps('group')} direction={direction} group={group} name={name} legend={legend} withBorder={withBorder} />;
  }}
  </Formik>`,...(u=(d=o.parameters)==null?void 0:d.docs)==null?void 0:u.source}}};var l,c,g;i.parameters={...i.parameters,docs:{...(l=i.parameters)==null?void 0:l.docs,source:{originalSource:`({
  direction,
  name,
  group,
  legend,
  withBorder
}) => <Formik initialValues={{
  question: {}
}} onSubmit={() => {}}>
    {({
    getFieldProps
  }) => {
    return <RadioGroup {...getFieldProps('group')} direction={direction} group={group} name={name} legend={legend} withBorder={withBorder} />;
  }}
  </Formik>`,...(g=(c=i.parameters)==null?void 0:c.docs)==null?void 0:g.source}}};const ur=["Default","WithBorder","Horizontal"];export{r as Default,i as Horizontal,o as WithBorder,ur as __namedExportsOrder,dr as default};
