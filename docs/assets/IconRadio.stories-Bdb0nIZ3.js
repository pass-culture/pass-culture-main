import{i as e}from"./preload-helper-xPQekRTU.js";import{t}from"./jsx-runtime-CaZkqeYb.js";import{i as n,o as r,s as i,t as a}from"./index.esm-CIQ4CLBT.js";import{n as o,t as s}from"./IconRadio-38yyWkTe.js";var c,l,u,d,f,p;e((()=>{n(),o(),c=t(),l={title:`@/ui-kit/forms/IconRadio`,component:s},u=({children:e})=>(0,c.jsx)(a,{...r({defaultValues:{myField:!0}}),children:(0,c.jsx)(`form`,{children:e})}),d={args:{label:`Radio input`,name:`myField`,icon:`A`,checked:!1,onChange:()=>{}},decorators:[e=>(0,c.jsx)(`div`,{style:{padding:`2rem`},children:(0,c.jsx)(e,{})})]},f={args:{label:`Radio input`,name:`myField`,icon:`B`},decorators:[e=>(0,c.jsx)(`div`,{style:{padding:`2rem`},children:(0,c.jsx)(u,{children:(0,c.jsx)(e,{})})})],render:e=>{let{register:t}=i();return(0,c.jsx)(s,{...e,...t(`myField`)})}},d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Radio input',
    name: 'myField',
    icon: 'A',
    checked: false,
    onChange: () => {
      //  Control the result here with e.target.checked
    }
  },
  decorators: [Story => {
    return <div style={{
      padding: '2rem'
    }}>
          <Story />
        </div>;
  }]
}`,...d.parameters?.docs?.source}}},f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Radio input',
    name: 'myField',
    icon: 'B'
  },
  decorators: [Story => <div style={{
    padding: '2rem'
  }}>
        <Wrapper>
          <Story />
        </Wrapper>
      </div>],
  render: args => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const {
      register
    } = useFormContext<{
      myField: boolean;
    }>();
    return <IconRadio {...args} {...register('myField')} />;
  }
}`,...f.parameters?.docs?.source}}},p=[`Default`,`WithinForm`]}))();export{d as Default,f as WithinForm,p as __namedExportsOrder,l as default};