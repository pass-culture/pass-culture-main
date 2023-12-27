import{j as r}from"./jsx-runtime-4cb93332.js";import{b as p}from"./formik.esm-8d42c991.js";import{S as u}from"./SelectInput-badf7177.js";import"./index-83a10e79.js";import"./_commonjsHelpers-de833af9.js";import"./index-e2bfc4ae.js";import"./stroke-down-3d79f44b.js";import"./SvgIcon-04d0ac1c.js";const F={title:"ui-kit/forms/SelectInput",component:u},m=[{value:"cinema",label:"Cinéma"},{value:"theatre",label:"Théatre"},{value:"musique",label:"Musique"}],e={args:{name:"select",hasError:!1,options:m,disabled:!1}},t={args:{name:"select",options:m,filterVariant:!0},decorators:[c=>r.jsx(p,{initialValues:{category:"theatre"},onSubmit:()=>{},children:r.jsx(c,{})})]};var a,o,s;e.parameters={...e.parameters,docs:{...(a=e.parameters)==null?void 0:a.docs,source:{originalSource:`{
  args: {
    name: 'select',
    hasError: false,
    options: mockCategoriesOptions,
    disabled: false
  }
}`,...(s=(o=e.parameters)==null?void 0:o.docs)==null?void 0:s.source}}};var n,i,l;t.parameters={...t.parameters,docs:{...(n=t.parameters)==null?void 0:n.docs,source:{originalSource:`{
  args: {
    name: 'select',
    options: mockCategoriesOptions,
    filterVariant: true
  },
  decorators: [Story => <Formik initialValues={{
    category: 'theatre'
  }} onSubmit={() => {}}>
        <Story />
      </Formik>]
}`,...(l=(i=t.parameters)==null?void 0:i.docs)==null?void 0:l.source}}};const I=["Default","SelectInputFilter"];export{e as Default,t as SelectInputFilter,I as __namedExportsOrder,F as default};
