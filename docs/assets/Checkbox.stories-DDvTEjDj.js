import{j as r}from"./jsx-runtime-BYYWji4R.js";import{u as d,a as u,F as h}from"./index.esm-BuPb1Mi7.js";import{C as p}from"./Checkbox-CW9D5kuq.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./index-DeARc5FM.js";import"./BaseCheckbox-yx2QTGF8.js";import"./SvgIcon-CyWUmZpn.js";import"./FieldError-azuIsM2E.js";import"./stroke-error-DSZD431a.js";const S={title:"ui-kit/formsV2/Checkbox",component:p},b=({children:e})=>{const t=u({defaultValues:{myField:!0}});return r.jsx(h,{...t,children:r.jsx("form",{children:e})})},o={args:{label:"Accessible",name:"accessibility",checked:!0,onChange:()=>{}}},s={args:{label:"Accessible"},decorators:[e=>r.jsx(b,{children:r.jsx(e,{})})],render:e=>{const{register:t}=d();return r.jsx(p,{...e,...t("myField")})}};var n,a,c;o.parameters={...o.parameters,docs:{...(n=o.parameters)==null?void 0:n.docs,source:{originalSource:`{
  args: {
    label: 'Accessible',
    name: 'accessibility',
    checked: true,
    onChange: () => {
      //  Control the result here with e.target.checked
    }
  }
}`,...(c=(a=o.parameters)==null?void 0:a.docs)==null?void 0:c.source}}};var i,m,l;s.parameters={...s.parameters,docs:{...(i=s.parameters)==null?void 0:i.docs,source:{originalSource:`{
  args: {
    label: 'Accessible'
  },
  decorators: [Story => <Wrapper>
        <Story />
      </Wrapper>],
  render: args => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const {
      register
    } = useFormContext<{
      myField: boolean;
    }>();
    return <Checkbox {...args} {...register('myField')} />;
  }
}`,...(l=(m=s.parameters)==null?void 0:m.docs)==null?void 0:l.source}}};const D=["Default","WithinForm"];export{o as Default,s as WithinForm,D as __namedExportsOrder,S as default};
