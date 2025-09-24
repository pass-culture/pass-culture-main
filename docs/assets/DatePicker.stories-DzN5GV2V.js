import{j as a}from"./jsx-runtime-Cf8x2fCZ.js";import{u as F,a as j,F as v}from"./index.esm-D1X9ZzX-.js";import{c as x}from"./index-B0pXE9zJ.js";import{r as f,R as I}from"./index-QQMyt9Ur.js";import{i as h,f as D,F as _}from"./date-D2dEj49M.js";import{B as E}from"./BaseInput-B8c5gx_3.js";import{F as B}from"./FieldError-2mFOl_uD.js";import"./index-yBjzXJbu.js";import"./_commonjsHelpers-CqkleIqs.js";import"./stroke-search-dgesjRZH.js";import"./SvgIcon-B5V96DYN.js";import"./stroke-error-DSZD431a.js";const P={"date-picker":"_date-picker_1jm56_1"},u=f.forwardRef(({className:e,maxDate:r,minDate:l,id:m,...c},s)=>{const p=h(l)?D(l,_):void 0,t=h(r)?D(r,_):"2050-01-01";return a.jsx(E,{type:"date",min:p,max:t,id:m,ref:s,className:x(e,P["date-picker"]),...c})});u.displayName="BaseDatePicker";try{u.displayName="BaseDatePicker",u.__docgenInfo={description:"",displayName:"BaseDatePicker",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},id:{defaultValue:null,description:"",name:"id",required:!1,type:{name:"string"}},hasError:{defaultValue:null,description:"",name:"hasError",required:!1,type:{name:"boolean"}},leftIcon:{defaultValue:null,description:"",name:"leftIcon",required:!1,type:{name:"string"}},rightButton:{defaultValue:null,description:"",name:"rightButton",required:!1,type:{name:"(() => Element)"}},rightIcon:{defaultValue:null,description:"",name:"rightIcon",required:!1,type:{name:"string"}},maxDate:{defaultValue:null,description:"",name:"maxDate",required:!1,type:{name:"Date"}},minDate:{defaultValue:null,description:"",name:"minDate",required:!1,type:{name:"Date"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}}}}}catch{}const C="_label_1xrff_1",R="_error_1xrff_6",i={label:C,error:R},n=I.forwardRef(({error:e,disabled:r,maxDate:l,minDate:m,onChange:c,required:s,onBlur:p,name:t,value:q,label:V,asterisk:b=!0,className:k},N)=>{const y=f.useId(),g=f.useId();return a.jsxs("div",{className:x(i["date-picker"],k),children:[a.jsxs("div",{className:i["date-picker-field"],children:[a.jsxs("label",{htmlFor:y,className:i.label,children:[V,s&&b?" *":""]}),a.jsx(u,{"data-testid":t,name:t,id:y,hasError:!!e,disabled:r,maxDate:l,minDate:m,onChange:c,"aria-required":s,onBlur:p,value:q,"aria-describedby":e?g:void 0,ref:N})]}),a.jsx("div",{role:"alert",id:g,children:e&&a.jsx(B,{name:t,className:i.error,children:e})})]})});n.displayName="DatePicker";try{n.displayName="DatePicker",n.__docgenInfo={description:"",displayName:"DatePicker",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},maxDate:{defaultValue:null,description:"",name:"maxDate",required:!1,type:{name:"Date"}},name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},minDate:{defaultValue:null,description:"",name:"minDate",required:!1,type:{name:"Date"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},asterisk:{defaultValue:{value:"true"},description:"Whether or not to display the asterisk in the label when the field is required",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const W=({children:e})=>{const r=j({defaultValues:{group:"option1"}});return a.jsx(v,{...r,children:a.jsx("form",{children:e})})},G={title:"@/ui-kit/forms/DatePicker",component:n},o={args:{name:"date",label:"Date",value:"2025-11-22",onChange:()=>{}}},d={args:{label:"Date"},decorators:[e=>a.jsx(W,{children:a.jsx(e,{})})],render:e=>{const{register:r}=F();return a.jsx(n,{...e,...r("date")})}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'date',
    label: 'Date',
    value: '2025-11-22',
    onChange: () => {
      //    Control changes
    }
  }
}`,...o.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
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
}`,...d.parameters?.docs?.source}}};const J=["Default","WithinForm"];export{o as Default,d as WithinForm,J as __namedExportsOrder,G as default};
