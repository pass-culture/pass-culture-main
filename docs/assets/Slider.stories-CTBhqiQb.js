import{i as e}from"./preload-helper-xPQekRTU.js";import{t}from"./jsx-runtime-CaZkqeYb.js";import{n,t as r}from"./Slider-DexlpIal.js";import{i,o as a,s as o,t as s}from"./index.esm-5TnhCUVg.js";var c,l,u,d,f,p;e((()=>{i(),n(),c=t(),l={title:`@/ui-kit/forms/Slider`,component:r},u=({children:e})=>(0,c.jsx)(s,{...a({defaultValues:{scale:`km`}}),children:(0,c.jsx)(`form`,{children:e})}),d={args:{name:`myField`,scale:`km`,onChange:()=>{}},decorators:[e=>(0,c.jsx)(`div`,{style:{padding:`2rem`},children:(0,c.jsx)(e,{})})]},f={args:{name:`myField`,scale:`km`},decorators:[e=>(0,c.jsx)(`div`,{style:{width:300,height:300},children:(0,c.jsx)(u,{children:(0,c.jsx)(e,{})})})],render:e=>{let{register:t}=o();return(0,c.jsx)(r,{...e,...t(`myField`)})}},d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
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
}`,...d.parameters?.docs?.source}}},f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
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
    const {
      register
    } = useFormContext<{
      myField: number;
    }>();
    return <Slider {...args} {...register('myField')} />;
  }
}`,...f.parameters?.docs?.source}}},p=[`Default`,`WithinForm`]}))();export{d as Default,f as WithinForm,p as __namedExportsOrder,l as default};