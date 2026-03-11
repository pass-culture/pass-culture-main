import{j as a}from"./jsx-runtime-u17CrQMm.js";import{a as k,u as F,F as j}from"./index.esm-DnEDBkfk.js";import{r as f,R as N}from"./iframe-D71W6Em8.js";import{F as E}from"./FieldFooter-CcSUzVc9.js";import{c as I}from"./index-CtOv_S0D.js";import{i as h,f as D,a as _}from"./date-CrU56jqV.js";import"./preload-helper-PPVm8Dsz.js";import"./full-error-BFAmjN4t.js";import"./index.module-DiBD0ha9.js";import"./SvgIcon-DuZPzNRk.js";const x={"date-picker":"_date-picker_ogfoh_2","has-error":"_has-error_ogfoh_47"},d=f.forwardRef(({className:e,maxDate:r,minDate:n,id:u,hasError:m,...s},c)=>{const l=h(n)?D(n,_):void 0,p=h(r)?D(r,_):"2050-01-01";return a.jsx("input",{type:"date",min:l,max:p,id:u,ref:c,className:I(e,x["date-picker"],{[x["has-error"]]:m}),...s})});d.displayName="BaseDatePicker";try{d.displayName="BaseDatePicker",d.__docgenInfo={description:"",displayName:"BaseDatePicker",props:{maxDate:{defaultValue:null,description:"",name:"maxDate",required:!1,type:{name:"Date"}},minDate:{defaultValue:null,description:"",name:"minDate",required:!1,type:{name:"Date"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},hasError:{defaultValue:null,description:"",name:"hasError",required:!1,type:{name:"boolean"}}}}}catch{}const P="_label_243fh_1",C={label:P},t=N.forwardRef(({error:e,disabled:r,maxDate:n,minDate:u,onChange:m,required:s,onBlur:c,name:l,value:p,label:b,requiredIndicator:q="symbol",className:v},V)=>{const y=f.useId(),g=f.useId();return a.jsxs("div",{className:v,children:[a.jsxs("div",{children:[a.jsxs("label",{htmlFor:y,className:C.label,children:[b,s&&q==="symbol"?a.jsx(a.Fragment,{children:" *"}):""]}),a.jsx(d,{"data-testid":l,name:l,id:y,hasError:!!e,disabled:r,maxDate:n,minDate:u,onChange:m,"aria-required":s,onBlur:c,value:p,"aria-describedby":e?g:void 0,ref:V})]}),a.jsx(E,{error:e,errorId:g})]})});t.displayName="DatePicker";try{t.displayName="DatePicker",t.__docgenInfo={description:"",displayName:"DatePicker",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},maxDate:{defaultValue:null,description:"",name:"maxDate",required:!1,type:{name:"Date"}},name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},minDate:{defaultValue:null,description:"",name:"minDate",required:!1,type:{name:"Date"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement, HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},requiredIndicator:{defaultValue:{value:"symbol"},description:"What type of required indicator is displayed",name:"requiredIndicator",required:!1,type:{name:"enum",value:[{value:'"symbol"'},{value:'"hidden"'},{value:'"explicit"'}]}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const B=({children:e})=>{const r=F({defaultValues:{group:"option1"}});return a.jsx(j,{...r,children:a.jsx("form",{children:e})})},U={title:"@/ui-kit/forms/DatePicker",component:t},o={args:{name:"date",label:"Date",value:"2025-11-22",onChange:()=>{}}},i={args:{label:"Date"},decorators:[e=>a.jsx(B,{children:a.jsx(e,{})})],render:e=>{const{register:r}=k();return a.jsx(t,{...e,...r("date")})}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
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
