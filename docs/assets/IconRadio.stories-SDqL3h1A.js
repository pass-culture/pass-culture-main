import{j as e}from"./jsx-runtime-DOJuJR3k.js";import{a,u as i,F as d}from"./index.esm-DC5Tw2DH.js";import{I as s}from"./IconRadio-DLtT67c1.js";import"./iframe-DLFo3C28.js";import"./preload-helper-PPVm8Dsz.js";import"./index-D3suXIEZ.js";import"./Tooltip-C9h188At.js";const F={title:"@/ui-kit/forms/IconRadio",component:s},m=({children:r})=>{const t=i({defaultValues:{myField:!0}});return e.jsx(d,{...t,children:e.jsx("form",{children:r})})},n={args:{label:"Radio input",name:"myField",icon:"A",checked:!1,onChange:()=>{}},decorators:[r=>e.jsx("div",{style:{padding:"2rem"},children:e.jsx(r,{})})]},o={args:{label:"Radio input",name:"myField",icon:"B"},decorators:[r=>e.jsx("div",{style:{padding:"2rem"},children:e.jsx(m,{children:e.jsx(r,{})})})],render:r=>{const{register:t}=a();return e.jsx(s,{...r,...t("myField")})}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
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
}`,...o.parameters?.docs?.source}}};const x=["Default","WithinForm"];export{n as Default,o as WithinForm,x as __namedExportsOrder,F as default};
