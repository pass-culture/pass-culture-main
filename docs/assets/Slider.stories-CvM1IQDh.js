import{j as e}from"./jsx-runtime-BYYWji4R.js";import{u,a as p,F as h}from"./index.esm-ClDB96id.js";import{S as c}from"./Slider-D8sIjjnx.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";const f={title:"ui-kit/Slider",component:c},g=({children:r})=>{const t=p({defaultValues:{scale:"km"}});return e.jsx(h,{...t,children:e.jsx("form",{children:r})})},n={args:{name:"myField",scale:"km",onChange:()=>{}},decorators:[r=>e.jsx("div",{style:{padding:"2rem"},children:e.jsx(r,{})})]},s={args:{name:"myField",scale:"km"},decorators:[r=>e.jsx("div",{style:{width:300,height:300},children:e.jsx(g,{children:e.jsx(r,{})})})],render:r=>{const{register:t}=u();return e.jsx(c,{...r,...t("myField")})}};var o,a,i;n.parameters={...n.parameters,docs:{...(o=n.parameters)==null?void 0:o.docs,source:{originalSource:`{
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
}`,...(i=(a=n.parameters)==null?void 0:a.docs)==null?void 0:i.source}}};var m,d,l;s.parameters={...s.parameters,docs:{...(m=s.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
}`,...(l=(d=s.parameters)==null?void 0:d.docs)==null?void 0:l.source}}};const k=["Default","WithinForm"];export{n as Default,s as WithinForm,k as __namedExportsOrder,f as default};
