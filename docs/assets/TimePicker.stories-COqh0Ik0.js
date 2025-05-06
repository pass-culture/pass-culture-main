import{j as e}from"./jsx-runtime-BYYWji4R.js";import{u as V,a as v,F as N}from"./index.esm-Z2NZos4s.js";import{c as E}from"./index-DeARc5FM.js";import{r as i}from"./index-ClcD9ViR.js";import{F as T}from"./FieldError-azuIsM2E.js";import{B as C}from"./BaseTimePicker-a0anDuVv.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./stroke-error-DSZD431a.js";import"./SvgIcon-CyWUmZpn.js";import"./BaseInput-BI1b_EYZ.js";const P="_label_1kw3x_1",S="_error_1kw3x_6",t={label:P,error:S},n=i.forwardRef(({name:r,className:a,disabled:b,label:x,required:d,asterisk:k=!0,error:l,value:_,onChange:j,onBlur:q},F)=>{const m=i.useId(),u=i.useId();return e.jsxs("div",{className:E(t["time-picker"],a),children:[e.jsxs("div",{className:t["time-picker-field"],children:[e.jsxs("label",{htmlFor:m,className:t.label,children:[x,d&&k?" *":""]}),e.jsx(C,{hasError:!!l,disabled:b,"aria-required":d,value:_,ref:F,onChange:j,onBlur:q,name:r,id:m,"aria-describedby":u})]}),e.jsx("div",{role:"alert",id:u,children:l&&e.jsx(T,{name:r,className:t.error,children:l})})]})});n.displayName="TimePicker";try{n.displayName="TimePicker",n.__docgenInfo={description:"",displayName:"TimePicker",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},asterisk:{defaultValue:{value:"true"},description:"Whether or not to display the asterisk in the label when the field is required",name:"asterisk",required:!1,type:{name:"boolean"}},name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}}}}}catch{}const I=({children:r})=>{const a=v({defaultValues:{group:"option1"}});return e.jsx(N,{...a,children:e.jsx("form",{children:r})})},z={title:"ui-kit/formsV2/TimePicker",component:n},s={args:{label:"Select an option",value:"22:11",onChange:()=>{}}},o={args:{label:"Select a time"},decorators:[r=>e.jsx(I,{children:e.jsx(r,{})})],render:r=>{const{register:a}=V();return e.jsx(n,{...r,...a("time")})}};var c,p,f;s.parameters={...s.parameters,docs:{...(c=s.parameters)==null?void 0:c.docs,source:{originalSource:`{
  args: {
    label: 'Select an option',
    value: '22:11',
    onChange: () => {
      //    Control changes
    }
  }
}`,...(f=(p=s.parameters)==null?void 0:p.docs)==null?void 0:f.source}}};var h,g,y;o.parameters={...o.parameters,docs:{...(h=o.parameters)==null?void 0:h.docs,source:{originalSource:`{
  args: {
    label: 'Select a time'
  },
  decorators: [Story => <Wrapper>
        <Story />
      </Wrapper>],
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const {
      register
    } = useFormContext<{
      time: string;
    }>();
    return <TimePicker {...args} {...register('time')} />;
  }
}`,...(y=(g=o.parameters)==null?void 0:g.docs)==null?void 0:y.source}}};const A=["Default","WithinForm"];export{s as Default,o as WithinForm,A as __namedExportsOrder,z as default};
