import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-zMGudiS2.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./SearchInput-Pue9CBIn.js";var i=e(t(),1),a=n(),o={title:`@/design-system/SearchInput`,component:r},s={args:{label:`Default`}},c={args:{label:`Label`,description:`description`}},l={args:{label:`Disabled`,disabled:!0,value:`test`}},u={args:{label:`Disabled`,error:`This is an error message`}},d={args:{label:`Required`,required:!0}},f={args:{label:`Characters count`,maxCharactersCount:200}},p={args:{label:`Characters count and error`,maxCharactersCount:200,error:`This is an error message`}},m={render:()=>{let[e,t]=(0,i.useState)(`default value`);return(0,a.jsx)(r,{label:`Controlled`,value:e,onChange:e=>{t(e.target.value)},name:`search`})}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Default'
  }
}`,...s.parameters?.docs?.source}}},c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Label',
    description: 'description'
  }
}`,...c.parameters?.docs?.source}}},l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Disabled',
    disabled: true,
    value: 'test'
  }
}`,...l.parameters?.docs?.source}}},u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Disabled',
    error: 'This is an error message'
  }
}`,...u.parameters?.docs?.source}}},d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Required',
    required: true
  }
}`,...d.parameters?.docs?.source}}},f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Characters count',
    maxCharactersCount: 200
  }
}`,...f.parameters?.docs?.source}}},p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Characters count and error',
    maxCharactersCount: 200,
    error: 'This is an error message'
  }
}`,...p.parameters?.docs?.source}}},m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  render: () => {
    const [value, setValue] = useState<string>('default value');
    return <SearchInput label='Controlled' value={value} onChange={e => {
      setValue(e.target.value);
    }} name='search' />;
  }
}`,...m.parameters?.docs?.source}}};var h=[`Default`,`HasDescription`,`IsDisabled`,`HasError`,`IsRequired`,`HasCharactersCount`,`HasCharactersCountAndError`,`Controlled`];export{m as Controlled,s as Default,f as HasCharactersCount,p as HasCharactersCountAndError,c as HasDescription,u as HasError,l as IsDisabled,d as IsRequired,h as __namedExportsOrder,o as default};