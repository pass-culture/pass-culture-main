import{j as n}from"./jsx-runtime-BYYWji4R.js";import{u as I,F as M}from"./formik.esm-DUQIEGuZ.js";import{F as O}from"./FieldLayout-UMugZa6s.js";import{B as R}from"./BaseTimePicker-AXhTMnvs.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./index-DeARc5FM.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-help-blUMxBcv.js";import"./Button-EowvGHPD.js";import"./stroke-pass-CALgybTM.js";import"./SvgIcon-CyWUmZpn.js";import"./Tooltip-BU5AxWXW.js";import"./Button.module-CvVdqb9Z.js";import"./types-DjX_gQD6.js";import"./FieldError-azuIsM2E.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-Bf7ZM7Vi.js";import"./BaseInput-wU_9nUoO.js";const o=({name:e,className:B,classNameLabel:N,classNameFooter:S,classNameInput:_,disabled:P,label:F,isLabelHidden:A=!1,smallLabel:E,clearButtonProps:H,filterVariant:W,isOptional:m=!1,min:w,suggestedTimeList:C,hideAsterisk:j=!1})=>{const[v,a]=I({name:e,type:"text"}),D=a.touched&&!!a.error;return n.jsx(O,{className:B,error:a.error,label:F,isLabelHidden:A,name:e,showError:D,smallLabel:E,classNameLabel:N,classNameFooter:S,classNameInput:_,clearButtonProps:H,isOptional:m,hideAsterisk:j,children:n.jsx(R,{...v,hasError:a.touched&&!!a.error,filterVariant:W,disabled:P,"aria-required":!m,min:w,suggestedTimeList:C})})};try{o.displayName="TimePicker",o.__docgenInfo={description:"",displayName:"TimePicker",props:{label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string | Element"}},name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},maxLength:{defaultValue:null,description:"",name:"maxLength",required:!1,type:{name:"number"}},isLabelHidden:{defaultValue:{value:"false"},description:`A flag to hide the label.
To be used with caution, as it can affect accessibility.
Do not use it if the label is mandatory, placeholder is not
a substitute for a label.`,name:"isLabelHidden",required:!1,type:{name:"boolean"}},hasLabelLineBreak:{defaultValue:null,description:"",name:"hasLabelLineBreak",required:!1,type:{name:"boolean"}},isOptional:{defaultValue:{value:"false"},description:`A flag to indicate that the field is optional.
It will display an asterisk next to the label.`,name:"isOptional",required:!1,type:{name:"boolean"}},hideAsterisk:{defaultValue:{value:"false"},description:`Can be false only when it's the only field in a form and it's mandatory,
or when all fields are mandatory and the form indicates that all fields are mandatory`,name:"hideAsterisk",required:!1,type:{name:"boolean"}},className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},classNameLabel:{defaultValue:null,description:"",name:"classNameLabel",required:!1,type:{name:"string"}},classNameFooter:{defaultValue:null,description:`A custom class for the footer,
where errors and character count are displayed.`,name:"classNameFooter",required:!1,type:{name:"string"}},classNameInput:{defaultValue:null,description:"",name:"classNameInput",required:!1,type:{name:"string"}},filterVariant:{defaultValue:null,description:"",name:"filterVariant",required:!1,type:{name:"boolean"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},inline:{defaultValue:null,description:"",name:"inline",required:!1,type:{name:"boolean"}},clearButtonProps:{defaultValue:null,description:"",name:"clearButtonProps",required:!1,type:{name:'(ButtonHTMLAttributes<HTMLButtonElement> & { tooltip: string; display?: "clear" | "close"; })'}},ErrorDetails:{defaultValue:null,description:"",name:"ErrorDetails",required:!1,type:{name:"ReactNode"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},dateTime:{defaultValue:null,description:"",name:"dateTime",required:!1,type:{name:"Date"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:'"" | Date | null'}},min:{defaultValue:null,description:"",name:"min",required:!1,type:{name:"string"}},suggestedTimeList:{defaultValue:null,description:"",name:"suggestedTimeList",required:!1,type:{name:"SuggestedTimeList"}}}}}catch{}const ue={title:"ui-kit/forms/TimePicker",component:o,decorators:[e=>n.jsx(M,{initialValues:{time:null},onSubmit:()=>{},children:n.jsx(e,{})})]},r={args:{name:"time",label:"Horaire",clearButtonProps:{tooltip:"Supprimer l'horaire",onClick:()=>alert("Clear !")}}},t={args:{name:"time"}},i={args:{name:"time",label:"Horaire"}},l={args:{name:"time",filterVariant:!0}},s={args:{name:"time",suggestedTimeList:{}}};var u,d,p;r.parameters={...r.parameters,docs:{...(u=r.parameters)==null?void 0:u.docs,source:{originalSource:`{
  args: {
    name: 'time',
    label: 'Horaire',
    clearButtonProps: {
      tooltip: "Supprimer l'horaire",
      onClick: () => alert('Clear !')
    }
  }
}`,...(p=(d=r.parameters)==null?void 0:d.docs)==null?void 0:p.source}}};var c,f,g;t.parameters={...t.parameters,docs:{...(c=t.parameters)==null?void 0:c.docs,source:{originalSource:`{
  args: {
    name: 'time'
  }
}`,...(g=(f=t.parameters)==null?void 0:f.docs)==null?void 0:g.source}}};var b,h,y;i.parameters={...i.parameters,docs:{...(b=i.parameters)==null?void 0:b.docs,source:{originalSource:`{
  args: {
    name: 'time',
    label: 'Horaire'
  }
}`,...(y=(h=i.parameters)==null?void 0:h.docs)==null?void 0:y.source}}};var V,L,q;l.parameters={...l.parameters,docs:{...(V=l.parameters)==null?void 0:V.docs,source:{originalSource:`{
  args: {
    name: 'time',
    filterVariant: true
  }
}`,...(q=(L=l.parameters)==null?void 0:L.docs)==null?void 0:q.source}}};var T,k,x;s.parameters={...s.parameters,docs:{...(T=s.parameters)==null?void 0:T.docs,source:{originalSource:`{
  args: {
    name: 'time',
    suggestedTimeList: {}
  }
}`,...(x=(k=s.parameters)==null?void 0:k.docs)==null?void 0:x.source}}};const de=["WithClearButton","WithoutLabel","WithLabel","FilterVariant","WithoutSuggestList"];export{l as FilterVariant,r as WithClearButton,i as WithLabel,t as WithoutLabel,s as WithoutSuggestList,de as __namedExportsOrder,ue as default};
