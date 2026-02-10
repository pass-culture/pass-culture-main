import{j as d}from"./jsx-runtime-D6_mKtUG.js";import{S as l}from"./SearchInput-DByE21vA.js";import{r as p}from"./iframe-DChMq0nj.js";import"./full-clear-Q4kCtSRL.js";import"./stroke-search-Bph5aoaJ.js";import"./TextInput-CeCoriBJ.js";import"./index-CDcEzP0y.js";import"./SvgIcon-3G7vhxrW.js";import"./FieldFooter-3et8xZNZ.js";import"./full-error-BFAmjN4t.js";import"./index.module-D5cU5I97.js";import"./FieldHeader-DICmG3kf.js";import"./Tooltip-BVgeL5L4.js";import"./preload-helper-PPVm8Dsz.js";const T={title:"@/design-system/SearchInput",component:l},r={args:{label:"Default"}},e={args:{label:"Label",description:"description"}},a={args:{label:"Disabled",disabled:!0,value:"test"}},s={args:{label:"Disabled",error:"This is an error message"}},t={args:{label:"Required",required:!0}},o={args:{label:"Characters count",maxCharactersCount:200}},n={args:{label:"Characters count and error",maxCharactersCount:200,error:"This is an error message"}},c={render:()=>{const[u,i]=p.useState("default value");return d.jsx(l,{label:"Controlled",value:u,onChange:m=>{i(m.target.value)},name:"search"})}};r.parameters={...r.parameters,docs:{...r.parameters?.docs,source:{originalSource:`{
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
