import{t as e}from"./jsx-runtime-BuabnPLX.js";import{a as t,o as n,t as r}from"./index.esm-DBEDw5YR.js";import{t as i}from"./IconRadio-01qv_QHj.js";var a=e(),o={title:`@/ui-kit/forms/IconRadio`,component:i},s=({children:e})=>(0,a.jsx)(r,{...t({defaultValues:{myField:!0}}),children:(0,a.jsx)(`form`,{children:e})}),c={args:{label:`Radio input`,name:`myField`,icon:`A`,checked:!1,onChange:()=>{}},decorators:[e=>(0,a.jsx)(`div`,{style:{padding:`2rem`},children:(0,a.jsx)(e,{})})]},l={args:{label:`Radio input`,name:`myField`,icon:`B`},decorators:[e=>(0,a.jsx)(`div`,{style:{padding:`2rem`},children:(0,a.jsx)(s,{children:(0,a.jsx)(e,{})})})],render:e=>{let{register:t}=n();return(0,a.jsx)(i,{...e,...t(`myField`)})}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
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
}`,...c.parameters?.docs?.source}}},l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
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
}`,...l.parameters?.docs?.source}}};var u=[`Default`,`WithinForm`];export{c as Default,l as WithinForm,u as __namedExportsOrder,o as default};