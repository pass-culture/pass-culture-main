import{j as a}from"./jsx-runtime-HI5-WoeL.js";import{a as v,u as j,F as E}from"./index.esm-CJHVCrWc.js";import{c as k}from"./index-DYIUYS_O.js";import{r as y,R as P}from"./iframe-C_eLJ2d6.js";import{i as g,f as D,F as x}from"./date-D2dEj49M.js";import{F as I}from"./FieldError-Dk-jcP1s.js";import"./preload-helper-PPVm8Dsz.js";import"./stroke-error-DSZD431a.js";import"./SvgIcon-BwFU88HS.js";const b={"date-picker":"_date-picker_m6003_1","has-error":"_has-error_m6003_46"},u=y.forwardRef(({className:e,maxDate:r,minDate:s,id:c,hasError:m,...l},p)=>{const t=g(s)?D(s,x):void 0,f=g(r)?D(r,x):"2050-01-01";return a.jsx("input",{type:"date",min:t,max:f,id:c,ref:p,className:k(e,b["date-picker"],{[b["has-error"]]:m}),...l})});u.displayName="BaseDatePicker";try{u.displayName="BaseDatePicker",u.__docgenInfo={description:"",displayName:"BaseDatePicker",props:{maxDate:{defaultValue:null,description:"",name:"maxDate",required:!1,type:{name:"Date"}},minDate:{defaultValue:null,description:"",name:"minDate",required:!1,type:{name:"Date"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},hasError:{defaultValue:null,description:"",name:"hasError",required:!1,type:{name:"boolean"}}}}}catch{}const C="_label_1xrff_1",B="_error_1xrff_6",o={label:C,error:B},n=P.forwardRef(({error:e,disabled:r,maxDate:s,minDate:c,onChange:m,required:l,onBlur:p,name:t,value:f,label:q,asterisk:V=!0,className:F},N)=>{const h=y.useId(),_=y.useId();return a.jsxs("div",{className:k(o["date-picker"],F),children:[a.jsxs("div",{className:o["date-picker-field"],children:[a.jsxs("label",{htmlFor:h,className:o.label,children:[q,l&&V?" *":""]}),a.jsx(u,{"data-testid":t,name:t,id:h,hasError:!!e,disabled:r,maxDate:s,minDate:c,onChange:m,"aria-required":l,onBlur:p,value:f,"aria-describedby":e?_:void 0,ref:N})]}),a.jsx("div",{role:"alert",id:_,children:e&&a.jsx(I,{name:t,className:o.error,children:e})})]})});n.displayName="DatePicker";try{n.displayName="DatePicker",n.__docgenInfo={description:"",displayName:"DatePicker",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},maxDate:{defaultValue:null,description:"",name:"maxDate",required:!1,type:{name:"Date"}},name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},minDate:{defaultValue:null,description:"",name:"minDate",required:!1,type:{name:"Date"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},asterisk:{defaultValue:{value:"true"},description:"Whether or not to display the asterisk in the label when the field is required",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const R=({children:e})=>{const r=j({defaultValues:{group:"option1"}});return a.jsx(E,{...r,children:a.jsx("form",{children:e})})},U={title:"@/ui-kit/forms/DatePicker",component:n},i={args:{name:"date",label:"Date",value:"2025-11-22",onChange:()=>{}}},d={args:{label:"Date"},decorators:[e=>a.jsx(R,{children:a.jsx(e,{})})],render:e=>{const{register:r}=v();return a.jsx(n,{...e,...r("date")})}};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'date',
    label: 'Date',
    value: '2025-11-22',
    onChange: () => {
      //    Control changes
    }
  }
}`,...i.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
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
}`,...d.parameters?.docs?.source}}};const Y=["Default","WithinForm"];export{i as Default,d as WithinForm,Y as __namedExportsOrder,U as default};
