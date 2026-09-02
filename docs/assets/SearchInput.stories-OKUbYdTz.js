import{n as e}from"./rolldown-runtime-DkW27tQK.js";import{d as t}from"./iframe-BOncW1wH.js";import{t as n}from"./jsx-runtime-DeHZSEgm.js";import{n as r,t as i}from"./SearchInput-DsIrSuY9.js";var a,o,s,c,l,u,d,f,p,m,h,g;function _(){return(_=e((()=>{r(),a=t(),o=n(),s={title:`@/design-system/SearchInput`,component:i},c={args:{label:`Default`}},l={args:{label:`Label`,description:`description`}},u={args:{label:`Disabled`,disabled:!0,value:`test`}},d={args:{label:`Disabled`,error:`This is an error message`}},f={args:{label:`Required`,required:!0}},p={args:{label:`Characters count`,maxCharactersCount:200}},m={args:{label:`Characters count and error`,maxCharactersCount:200,error:`This is an error message`}},h={render:()=>{let[e,t]=(0,a.useState)(`default value`);return(0,o.jsx)(i,{label:`Controlled`,value:e,onChange:e=>{t(e.target.value)},name:`search`})}},c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Default'
  }
}`,...c.parameters?.docs?.source}}},l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Label',
    description: 'description'
  }
}`,...l.parameters?.docs?.source}}},u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Disabled',
    disabled: true,
    value: 'test'
  }
}`,...u.parameters?.docs?.source}}},d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Disabled',
    error: 'This is an error message'
  }
}`,...d.parameters?.docs?.source}}},f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Required',
    required: true
  }
}`,...f.parameters?.docs?.source}}},p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Characters count',
    maxCharactersCount: 200
  }
}`,...p.parameters?.docs?.source}}},m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Characters count and error',
    maxCharactersCount: 200,
    error: 'This is an error message'
  }
}`,...m.parameters?.docs?.source}}},h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  render: () => {
    const [value, setValue] = useState<string>('default value');
    return <SearchInput label='Controlled' value={value} onChange={e => {
      setValue(e.target.value);
    }} name='search' />;
  }
}`,...h.parameters?.docs?.source}}},g=[`Default`,`HasDescription`,`IsDisabled`,`HasError`,`IsRequired`,`HasCharactersCount`,`HasCharactersCountAndError`,`Controlled`]})))()}_();export{h as Controlled,c as Default,p as HasCharactersCount,m as HasCharactersCountAndError,l as HasDescription,d as HasError,u as IsDisabled,f as IsRequired,g as __namedExportsOrder,s as default};