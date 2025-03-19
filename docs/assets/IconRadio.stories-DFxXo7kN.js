import{j as e}from"./jsx-runtime-CfatFE5O.js";import{u as b,a as j,F as R}from"./index.esm-DECH_zav.js";import{c as k}from"./index-DeARc5FM.js";import{r as c}from"./index-ClcD9ViR.js";import{T as I}from"./Tooltip-Bh4x5Y8V.js";import"./_commonjsHelpers-Cpj98o6Y.js";const a={"icon-radio":"_icon-radio_efovz_1","icon-radio-input":"_icon-radio-input_efovz_8","icon-radio-input-icon":"_icon-radio-input-icon_efovz_23","icon-radio-input-checked":"_icon-radio-input-checked_efovz_41","icon-radio-icon":"_icon-radio-icon_efovz_48","icon-radio-label":"_icon-radio-label_efovz_54"},o=c.forwardRef(({name:n,label:r,icon:_,hasError:d,checked:s,disabled:g,onChange:x,onBlur:v},F)=>{const l=c.useId();return e.jsxs("div",{className:a["icon-radio"],children:[e.jsx("label",{htmlFor:l,className:a["icon-radio-label"],children:r}),e.jsx("div",{className:a["icon-radio-icon"],children:_}),e.jsx(I,{content:r,children:e.jsx("input",{type:"radio",id:l,className:k(a["icon-radio-input"],{[a["has-error"]]:d,[a["icon-radio-input-checked"]]:s}),"aria-invalid":d,checked:s,disabled:g,name:n,onChange:x,onBlur:v,ref:F})})]})});o.displayName="IconRadio";try{o.displayName="IconRadio",o.__docgenInfo={description:"",displayName:"IconRadio",props:{name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string"}},icon:{defaultValue:null,description:"",name:"icon",required:!0,type:{name:"string | Element"}},hasError:{defaultValue:null,description:"",name:"hasError",required:!1,type:{name:"boolean"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},checked:{defaultValue:null,description:"",name:"checked",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}}}}}catch{}const W={title:"ui-kit/formsV2/IconRadio",component:o},V=({children:n})=>{const r=j({defaultValues:{myField:!0}});return e.jsx(R,{...r,children:e.jsx("form",{children:n})})},i={args:{label:"Radio input",name:"myField",icon:"A",checked:!1,onChange:()=>{}},decorators:[n=>e.jsx("div",{style:{padding:"2rem"},children:e.jsx(n,{})})]},t={args:{label:"Radio input",name:"myField",icon:"B"},decorators:[n=>e.jsx("div",{style:{padding:"2rem"},children:e.jsx(V,{children:e.jsx(n,{})})})],render:n=>{const{register:r}=b();return e.jsx(o,{...n,...r("myField")})}};var u,m,p;i.parameters={...i.parameters,docs:{...(u=i.parameters)==null?void 0:u.docs,source:{originalSource:`{
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
}`,...(p=(m=i.parameters)==null?void 0:m.docs)==null?void 0:p.source}}};var f,h,y;t.parameters={...t.parameters,docs:{...(f=t.parameters)==null?void 0:f.docs,source:{originalSource:`{
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
}`,...(y=(h=t.parameters)==null?void 0:h.docs)==null?void 0:y.source}}};const B=["Default","WithinForm"];export{i as Default,t as WithinForm,B as __namedExportsOrder,W as default};
