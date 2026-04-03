import{t as e}from"./jsx-runtime-BuabnPLX.js";import{t}from"./Slider-B6ZntpQ0.js";import{a as n,o as r,t as i}from"./index.esm-1DeofPBh.js";var a=e(),o={title:`@/ui-kit/forms/Slider`,component:t},s=({children:e})=>(0,a.jsx)(i,{...n({defaultValues:{scale:`km`}}),children:(0,a.jsx)(`form`,{children:e})}),c={args:{name:`myField`,scale:`km`,onChange:()=>{}},decorators:[e=>(0,a.jsx)(`div`,{style:{padding:`2rem`},children:(0,a.jsx)(e,{})})]},l={args:{name:`myField`,scale:`km`},decorators:[e=>(0,a.jsx)(`div`,{style:{width:300,height:300},children:(0,a.jsx)(s,{children:(0,a.jsx)(e,{})})})],render:e=>{let{register:n}=r();return(0,a.jsx)(t,{...e,...n(`myField`)})}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'myField',
    scale: 'km',
    onChange: () => {
      //  Control the result here with e.target.value
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
    name: 'myField',
    scale: 'km'
  },
  decorators: [Story => <div style={{
    width: 300,
    height: 300
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
      myField: number;
    }>();
    return <Slider {...args} {...register('myField')} />;
  }
}`,...l.parameters?.docs?.source}}};var u=[`Default`,`WithinForm`];export{c as Default,l as WithinForm,u as __namedExportsOrder,o as default};