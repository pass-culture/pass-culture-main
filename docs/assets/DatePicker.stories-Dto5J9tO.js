import{j as e}from"./jsx-runtime-BYYWji4R.js";import{u as v,a as N,F as E}from"./index.esm-nHDMj4MR.js";import{c as C}from"./index-DeARc5FM.js";import{R as P,r as m}from"./index-ClcD9ViR.js";import{B as I}from"./BaseDatePicker-D7a-LOU-.js";import{F as W}from"./FieldError-ky1_Lcaw.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./date-B2aPeOvv.js";import"./BaseInput-BI1b_EYZ.js";import"./SvgIcon-CyWUmZpn.js";import"./stroke-error-DSZD431a.js";const B="_label_1kw3x_1",R="_error_1kw3x_6",n={label:B,error:R},t=P.forwardRef(({error:r,disabled:a,maxDate:x,minDate:b,onChange:D,required:o,onBlur:k,name:i,value:_,label:q,asterisk:V=!0,className:j},F)=>{const d=m.useId(),u=m.useId();return e.jsxs("div",{className:C(n["date-picker"],j),children:[e.jsxs("div",{className:n["date-picker-field"],children:[e.jsxs("label",{htmlFor:d,className:n.label,children:[q,o&&V?" *":""]}),e.jsx(I,{name:i,id:d,hasError:!!r,disabled:a,maxDate:x,minDate:b,onChange:D,"aria-required":o,onBlur:k,value:_,"aria-describedby":u,ref:F})]}),e.jsx("div",{role:"alert",id:u,children:r&&e.jsx(W,{name:i,className:n.error,children:r})})]})});t.displayName="DatePicker";try{t.displayName="DatePicker",t.__docgenInfo={description:"",displayName:"DatePicker",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},maxDate:{defaultValue:null,description:"",name:"maxDate",required:!1,type:{name:"Date"}},name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},minDate:{defaultValue:null,description:"",name:"minDate",required:!1,type:{name:"Date"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},asterisk:{defaultValue:{value:"true"},description:"Whether or not to display the asterisk in the label when the field is required",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const w=({children:r})=>{const a=N({defaultValues:{group:"option1"}});return e.jsx(E,{...a,children:e.jsx("form",{children:r})})},K={title:"ui-kit/formsV2/DatePicker",component:t},s={args:{name:"date",label:"Date",value:"2025-11-22",onChange:()=>{}}},l={args:{label:"Date"},decorators:[r=>e.jsx(w,{children:e.jsx(r,{})})],render:r=>{const{register:a}=v();return e.jsx(t,{...r,...a("date")})}};var c,p,f;s.parameters={...s.parameters,docs:{...(c=s.parameters)==null?void 0:c.docs,source:{originalSource:`{
  args: {
    name: 'date',
    label: 'Date',
    value: '2025-11-22',
    onChange: () => {
      //    Control changes
    }
  }
}`,...(f=(p=s.parameters)==null?void 0:p.docs)==null?void 0:f.source}}};var h,g,y;l.parameters={...l.parameters,docs:{...(h=l.parameters)==null?void 0:h.docs,source:{originalSource:`{
  args: {
    label: 'Date'
  },
  decorators: [(Story: any) => <Wrapper>
        <Story />
      </Wrapper>],
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const {
      register
    } = useFormContext<{
      date: string;
    }>();
    return <DatePicker {...args} {...register('date')} />;
  }
}`,...(y=(g=l.parameters)==null?void 0:g.docs)==null?void 0:y.source}}};const Q=["Default","WithinForm"];export{s as Default,l as WithinForm,Q as __namedExportsOrder,K as default};
