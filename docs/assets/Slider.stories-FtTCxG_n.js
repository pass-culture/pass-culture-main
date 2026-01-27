import{j as e}from"./jsx-runtime-C_uOM0Gm.js";import{a,u as i,F as m}from"./index.esm-B74CwnGv.js";import{S as o}from"./Slider-CxZ45NUH.js";import"./iframe-CTnXOULQ.js";import"./preload-helper-PPVm8Dsz.js";const g={title:"@/ui-kit/forms/Slider",component:o},d=({children:r})=>{const t=i({defaultValues:{scale:"km"}});return e.jsx(m,{...t,children:e.jsx("form",{children:r})})},n={args:{name:"myField",scale:"km",onChange:()=>{}},decorators:[r=>e.jsx("div",{style:{padding:"2rem"},children:e.jsx(r,{})})]},s={args:{name:"myField",scale:"km"},decorators:[r=>e.jsx("div",{style:{width:300,height:300},children:e.jsx(d,{children:e.jsx(r,{})})})],render:r=>{const{register:t}=a();return e.jsx(o,{...r,...t("myField")})}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
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
}`,...n.parameters?.docs?.source}}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
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
}`,...s.parameters?.docs?.source}}};const x=["Default","WithinForm"];export{n as Default,s as WithinForm,x as __namedExportsOrder,g as default};
