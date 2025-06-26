import{j as e}from"./jsx-runtime-BYYWji4R.js";import{u as N,a as E,F as S}from"./index.esm-ClDB96id.js";import{c}from"./index-DeARc5FM.js";import{r as o}from"./index-ClcD9ViR.js";import{F as C}from"./FieldError-ky1_Lcaw.js";import{B as P}from"./BaseTimePicker-BIr0ruU0.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./stroke-error-DSZD431a.js";import"./SvgIcon-CyWUmZpn.js";import"./BaseInput-BI1b_EYZ.js";const I="_label_rjwrd_1",L="_error_rjwrd_6",n={label:I,error:L,"visually-hidden":"_visually-hidden_rjwrd_10"},t=o.forwardRef(({name:r,className:a,disabled:x,label:_,required:d,asterisk:j=!0,error:l,value:k,onChange:q,onBlur:v,suggestedTimeList:V,isLabelHidden:F=!1},T)=>{const u=o.useId(),m=o.useId();return e.jsxs("div",{className:c(n["time-picker"],a),children:[e.jsxs("div",{className:n["time-picker-field"],children:[e.jsxs("label",{htmlFor:u,className:c(n.label,{[n["visually-hidden"]]:F}),children:[_,d&&j?" *":""]}),e.jsx(P,{hasError:!!l,disabled:x,"aria-required":d,value:k,ref:T,onChange:q,onBlur:v,name:r,id:u,"aria-describedby":m,suggestedTimeList:V})]}),e.jsx("div",{role:"alert",id:m,children:l&&e.jsx(C,{name:r,className:n.error,children:l})})]})});t.displayName="TimePicker";try{t.displayName="TimePicker",t.__docgenInfo={description:"",displayName:"TimePicker",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},asterisk:{defaultValue:{value:"true"},description:"Whether or not to display the asterisk in the label when the field is required",name:"asterisk",required:!1,type:{name:"boolean"}},name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!1,type:{name:"ReactNode"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},suggestedTimeList:{defaultValue:null,description:"",name:"suggestedTimeList",required:!1,type:{name:"SuggestedTimeList"}},isLabelHidden:{defaultValue:{value:"false"},description:"",name:"isLabelHidden",required:!1,type:{name:"boolean"}}}}}catch{}const H=({children:r})=>{const a=E({defaultValues:{group:"option1"}});return e.jsx(S,{...a,children:e.jsx("form",{children:r})})},G={title:"ui-kit/formsV2/TimePicker",component:t},s={args:{label:"Select an option",value:"22:11",onChange:()=>{}}},i={args:{label:"Select a time"},decorators:[r=>e.jsx(H,{children:e.jsx(r,{})})],render:r=>{const{register:a}=N();return e.jsx(t,{...r,...a("time")})}};var p,f,g;s.parameters={...s.parameters,docs:{...(p=s.parameters)==null?void 0:p.docs,source:{originalSource:`{
  args: {
    label: 'Select an option',
    value: '22:11',
    onChange: () => {
      //    Control changes
    }
  }
}`,...(g=(f=s.parameters)==null?void 0:f.docs)==null?void 0:g.source}}};var h,y,b;i.parameters={...i.parameters,docs:{...(h=i.parameters)==null?void 0:h.docs,source:{originalSource:`{
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
}`,...(b=(y=i.parameters)==null?void 0:y.docs)==null?void 0:b.source}}};const J=["Default","WithinForm"];export{s as Default,i as WithinForm,J as __namedExportsOrder,G as default};
