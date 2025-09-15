import{j as e}from"./jsx-runtime-Cf8x2fCZ.js";import{u as a,a as i,F as d}from"./index.esm-K9mStD-T.js";import{I as s}from"./IconRadio-BGTw8ys5.js";import"./index-yBjzXJbu.js";import"./index-QQMyt9Ur.js";import"./_commonjsHelpers-CqkleIqs.js";import"./index-B0pXE9zJ.js";import"./Tooltip-Du1ylKtn.js";const x={title:"@/ui-kit/forms/IconRadio",component:s},m=({children:r})=>{const t=i({defaultValues:{myField:!0}});return e.jsx(d,{...t,children:e.jsx("form",{children:r})})},n={args:{label:"Radio input",name:"myField",icon:"A",checked:!1,onChange:()=>{}},decorators:[r=>e.jsx("div",{style:{padding:"2rem"},children:e.jsx(r,{})})]},o={args:{label:"Radio input",name:"myField",icon:"B"},decorators:[r=>e.jsx("div",{style:{padding:"2rem"},children:e.jsx(m,{children:e.jsx(r,{})})})],render:r=>{const{register:t}=a();return e.jsx(s,{...r,...t("myField")})}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
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
}`,...n.parameters?.docs?.source}}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
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
}`,...o.parameters?.docs?.source}}};const f=["Default","WithinForm"];export{n as Default,o as WithinForm,f as __namedExportsOrder,x as default};
