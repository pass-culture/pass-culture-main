import{j as e}from"./jsx-runtime-BYYWji4R.js";import{u as p,a as u,F as g}from"./index.esm-ClDB96id.js";import{I as l}from"./IconRadio-C9YxZHMM.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./index-DeARc5FM.js";import"./Tooltip-BpKRYYrm.js";const v={title:"ui-kit/formsV2/IconRadio",component:l},h=({children:r})=>{const t=u({defaultValues:{myField:!0}});return e.jsx(g,{...t,children:e.jsx("form",{children:r})})},n={args:{label:"Radio input",name:"myField",icon:"A",checked:!1,onChange:()=>{}},decorators:[r=>e.jsx("div",{style:{padding:"2rem"},children:e.jsx(r,{})})]},o={args:{label:"Radio input",name:"myField",icon:"B"},decorators:[r=>e.jsx("div",{style:{padding:"2rem"},children:e.jsx(h,{children:e.jsx(r,{})})})],render:r=>{const{register:t}=p();return e.jsx(l,{...r,...t("myField")})}};var s,a,i;n.parameters={...n.parameters,docs:{...(s=n.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
}`,...(i=(a=n.parameters)==null?void 0:a.docs)==null?void 0:i.source}}};var d,m,c;o.parameters={...o.parameters,docs:{...(d=o.parameters)==null?void 0:d.docs,source:{originalSource:`{
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
}`,...(c=(m=o.parameters)==null?void 0:m.docs)==null?void 0:c.source}}};const b=["Default","WithinForm"];export{n as Default,o as WithinForm,b as __namedExportsOrder,v as default};
