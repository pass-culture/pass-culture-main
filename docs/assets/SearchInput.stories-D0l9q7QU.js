import{i as e,s as t}from"./preload-helper-xPQekRTU.js";import{C as n}from"./iframe-V6w_gXQk.js";import{t as r}from"./jsx-runtime-CaZkqeYb.js";import{n as i,t as a}from"./SearchInput-C1sLsKR6.js";var o,s,c,l,u,d,f,p,m,h,g,_;e((()=>{i(),o=t(n(),1),s=r(),c={title:`@/design-system/SearchInput`,component:a},l={args:{label:`Default`}},u={args:{label:`Label`,description:`description`}},d={args:{label:`Disabled`,disabled:!0,value:`test`}},f={args:{label:`Disabled`,error:`This is an error message`}},p={args:{label:`Required`,required:!0}},m={args:{label:`Characters count`,maxCharactersCount:200}},h={args:{label:`Characters count and error`,maxCharactersCount:200,error:`This is an error message`}},g={render:()=>{let[e,t]=(0,o.useState)(`default value`);return(0,s.jsx)(a,{label:`Controlled`,value:e,onChange:e=>{t(e.target.value)},name:`search`})}},l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Default'
  }
}`,...l.parameters?.docs?.source}}},u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Label',
    description: 'description'
  }
}`,...u.parameters?.docs?.source}}},d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Disabled',
    disabled: true,
    value: 'test'
  }
}`,...d.parameters?.docs?.source}}},f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Disabled',
    error: 'This is an error message'
  }
}`,...f.parameters?.docs?.source}}},p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Required',
    required: true
  }
}`,...p.parameters?.docs?.source}}},m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Characters count',
    maxCharactersCount: 200
  }
}`,...m.parameters?.docs?.source}}},h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Characters count and error',
    maxCharactersCount: 200,
    error: 'This is an error message'
  }
}`,...h.parameters?.docs?.source}}},g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  render: () => {
    const [value, setValue] = useState<string>('default value');
    return <SearchInput label='Controlled' value={value} onChange={e => {
      setValue(e.target.value);
    }} name='search' />;
  }
}`,...g.parameters?.docs?.source}}},_=[`Default`,`HasDescription`,`IsDisabled`,`HasError`,`IsRequired`,`HasCharactersCount`,`HasCharactersCountAndError`,`Controlled`]}))();export{g as Controlled,l as Default,m as HasCharactersCount,h as HasCharactersCountAndError,u as HasDescription,f as HasError,d as IsDisabled,p as IsRequired,_ as __namedExportsOrder,c as default};