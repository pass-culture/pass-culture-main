import{j as d}from"./jsx-runtime-DGQzFquK.js";import{S as l}from"./SearchInput-CGel6Xy1.js";import{r as p}from"./iframe-CUVsTlqV.js";import"./full-clear-Q4kCtSRL.js";import"./stroke-search-Bph5aoaJ.js";import"./TextInput-B2Wd2fDy.js";import"./index-DSwX-CKq.js";import"./SvgIcon-B7TGVUwV.js";import"./FieldFooter-CI6YjPYJ.js";import"./full-error-BFAmjN4t.js";import"./index.module-RVKEEY6P.js";import"./FieldHeader-C0WV6X63.js";import"./Tooltip-D8svFw2z.js";import"./preload-helper-PPVm8Dsz.js";const T={title:"@/design-system/SearchInput",component:l},r={args:{label:"Default"}},e={args:{label:"Label",description:"description"}},a={args:{label:"Disabled",disabled:!0,value:"test"}},s={args:{label:"Disabled",error:"This is an error message"}},t={args:{label:"Required",required:!0}},o={args:{label:"Characters count",maxCharactersCount:200}},n={args:{label:"Characters count and error",maxCharactersCount:200,error:"This is an error message"}},c={render:()=>{const[u,i]=p.useState("default value");return d.jsx(l,{label:"Controlled",value:u,onChange:m=>{i(m.target.value)},name:"search"})}};r.parameters={...r.parameters,docs:{...r.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Default'
  }
}`,...r.parameters?.docs?.source}}};e.parameters={...e.parameters,docs:{...e.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Label',
    description: 'description'
  }
}`,...e.parameters?.docs?.source}}};a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Disabled',
    disabled: true,
    value: 'test'
  }
}`,...a.parameters?.docs?.source}}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Disabled',
    error: 'This is an error message'
  }
}`,...s.parameters?.docs?.source}}};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Required',
    required: true
  }
}`,...t.parameters?.docs?.source}}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Characters count',
    maxCharactersCount: 200
  }
}`,...o.parameters?.docs?.source}}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Characters count and error',
    maxCharactersCount: 200,
    error: 'This is an error message'
  }
}`,...n.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  render: () => {
    const [value, setValue] = useState<string>('default value');
    return <SearchInput label='Controlled' value={value} onChange={e => {
      setValue(e.target.value);
    }} name='search' />;
  }
}`,...c.parameters?.docs?.source}}};const j=["Default","HasDescription","IsDisabled","HasError","IsRequired","HasCharactersCount","HasCharactersCountAndError","Controlled"];export{c as Controlled,r as Default,o as HasCharactersCount,n as HasCharactersCountAndError,e as HasDescription,s as HasError,a as IsDisabled,t as IsRequired,j as __namedExportsOrder,T as default};
