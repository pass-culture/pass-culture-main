import{j as r}from"./jsx-runtime-vNq4Oc-g.js";import{b as p}from"./formik.esm-ymFmkpzG.js";import{S as u}from"./SelectInput-6KaGHNHr.js";import"./index-4g5l5LRQ.js";import"./_commonjsHelpers-4gQjN7DL.js";import"./index-XNbs-YUW.js";import"./stroke-down-4xbrRvHV.js";import"./SvgIcon-QVOPtTle.js";const F={title:"ui-kit/forms/SelectInput",component:u},m=[{value:"cinema",label:"Cinéma"},{value:"theatre",label:"Théatre"},{value:"musique",label:"Musique"}],e={args:{name:"select",hasError:!1,options:m,disabled:!1}},t={args:{name:"select",options:m,filterVariant:!0},decorators:[c=>r.jsx(p,{initialValues:{category:"theatre"},onSubmit:()=>{},children:r.jsx(c,{})})]};var a,o,s;e.parameters={...e.parameters,docs:{...(a=e.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
