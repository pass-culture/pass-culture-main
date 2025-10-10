import{j as a}from"./jsx-runtime-Cg5D_Ruf.js";import{a as N,u as j,F as E}from"./index.esm-0PuDciA2.js";import{c as k}from"./index-BfFe--5j.js";import{r as f,R as P}from"./iframe-B6l6sXAy.js";import{F as I}from"./FieldFooter-BMg-A4z8.js";import{i as g,f as D,F as _}from"./date-D2dEj49M.js";import"./preload-helper-PPVm8Dsz.js";import"./full-error-BFAmjN4t.js";import"./index.module-DK4RLnRr.js";import"./SvgIcon-ByN9JJrr.js";const x={"date-picker":"_date-picker_3qfh5_1","has-error":"_has-error_3qfh5_46"},d=f.forwardRef(({className:e,maxDate:r,minDate:n,id:u,hasError:m,...s},c)=>{const l=g(n)?D(n,_):void 0,p=g(r)?D(r,_):"2050-01-01";return a.jsx("input",{type:"date",min:l,max:p,id:u,ref:c,className:k(e,x["date-picker"],{[x["has-error"]]:m}),...s})});d.displayName="BaseDatePicker";try{d.displayName="BaseDatePicker",d.__docgenInfo={description:"",displayName:"BaseDatePicker",props:{maxDate:{defaultValue:null,description:"",name:"maxDate",required:!1,type:{name:"Date"}},minDate:{defaultValue:null,description:"",name:"minDate",required:!1,type:{name:"Date"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},hasError:{defaultValue:null,description:"",name:"hasError",required:!1,type:{name:"boolean"}}}}}catch{}const C="_label_243fh_1",b={label:C},t=P.forwardRef(({error:e,disabled:r,maxDate:n,minDate:u,onChange:m,required:s,onBlur:c,name:l,value:p,label:q,asterisk:V=!0,className:F},v)=>{const h=f.useId(),y=f.useId();return a.jsxs("div",{className:k(b["date-picker"],F),children:[a.jsxs("div",{children:[a.jsxs("label",{htmlFor:h,className:b.label,children:[q,s&&V?" *":""]}),a.jsx(d,{"data-testid":l,name:l,id:h,hasError:!!e,disabled:r,maxDate:n,minDate:u,onChange:m,"aria-required":s,onBlur:c,value:p,"aria-describedby":e?y:void 0,ref:v})]}),a.jsx(I,{error:e,errorId:y})]})});t.displayName="DatePicker";try{t.displayName="DatePicker",t.__docgenInfo={description:"",displayName:"DatePicker",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},maxDate:{defaultValue:null,description:"",name:"maxDate",required:!1,type:{name:"Date"}},name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},minDate:{defaultValue:null,description:"",name:"minDate",required:!1,type:{name:"Date"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},asterisk:{defaultValue:{value:"true"},description:"Whether or not to display the asterisk in the label when the field is required",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const B=({children:e})=>{const r=j({defaultValues:{group:"option1"}});return a.jsx(E,{...r,children:a.jsx("form",{children:e})})},U={title:"@/ui-kit/forms/DatePicker",component:t},o={args:{name:"date",label:"Date",value:"2025-11-22",onChange:()=>{}}},i={args:{label:"Date"},decorators:[e=>a.jsx(B,{children:a.jsx(e,{})})],render:e=>{const{register:r}=N();return a.jsx(t,{...e,...r("date")})}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'date',
    label: 'Date',
    value: '2025-11-22',
    onChange: () => {
      //    Control changes
    }
  }
}`,...o.parameters?.docs?.source}}};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
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
}`,...i.parameters?.docs?.source}}};const Y=["Default","WithinForm"];export{o as Default,i as WithinForm,Y as __namedExportsOrder,U as default};
