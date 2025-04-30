import{j as s}from"./jsx-runtime-BYYWji4R.js";import{F as g}from"./formik.esm-Dmsc_7od.js";import{T as x}from"./TextInput-k60BGBWT.js";const f={title:"ui-kit/forms/TextInput",component:x,decorators:[c=>s.jsx(g,{initialValues:{email:""},onSubmit:()=>{},children:s.jsx(c,{})})]},e={args:{name:"email",label:"Email",isLabelHidden:!0}},r={args:{...e.args,readOnly:!0,value:"A text wrapped in a span"}},a={args:{...e.args,externalError:"This field is required"}};var t,n,o;e.parameters={...e.parameters,docs:{...(t=e.parameters)==null?void 0:t.docs,source:{originalSource:`{
  args: {
    name: 'email',
    label: 'Email',
    isLabelHidden: true
  }
}`,...(o=(n=e.parameters)==null?void 0:n.docs)==null?void 0:o.source}}};var i,l,m;r.parameters={...r.parameters,docs:{...(i=r.parameters)==null?void 0:i.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    readOnly: true,
    value: 'A text wrapped in a span'
  }
}`,...(m=(l=r.parameters)==null?void 0:l.docs)==null?void 0:m.source}}};var u,d,p;a.parameters={...a.parameters,docs:{...(u=a.parameters)==null?void 0:u.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    externalError: 'This field is required'
  }
}`,...(p=(d=a.parameters)==null?void 0:d.docs)==null?void 0:p.source}}};const E=["Default","ReadOnly","WithExternalError"],S=Object.freeze(Object.defineProperty({__proto__:null,Default:e,ReadOnly:r,WithExternalError:a,__namedExportsOrder:E,default:f},Symbol.toStringTag,{value:"Module"}));export{e as D,S as T};
