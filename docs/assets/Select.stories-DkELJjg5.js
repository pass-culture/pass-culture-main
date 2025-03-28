import{j as a}from"./jsx-runtime-BYYWji4R.js";import{u as I,F as h}from"./formik.esm-DUQIEGuZ.js";import{r as v}from"./index-ClcD9ViR.js";import{F as A}from"./FieldLayout-DzywnLcX.js";import{S as w,a as B}from"./SelectInput-CYMevzua.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./index-DeARc5FM.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-help-blUMxBcv.js";import"./Button-BRSat9jc.js";import"./stroke-pass-CALgybTM.js";import"./SvgIcon-CyWUmZpn.js";import"./Tooltip-BU5AxWXW.js";import"./Button.module-D8O89sdf.js";import"./types-DjX_gQD6.js";import"./FieldError-azuIsM2E.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-Bf7ZM7Vi.js";import"./full-down-Cmbtr9nI.js";const u=({name:e,defaultOption:V=null,options:S,className:q,isOptional:d=!1,disabled:k,label:x,smallLabel:L,description:i,inline:C,onChange:o,isLabelHidden:F,classNameLabel:_,classNameFooter:O,hideAsterisk:j,...E})=>{const[s,t]=I({name:e,type:"select"}),N=v.useCallback(l=>{s.onChange(l),o&&o(l)},[s,o]);return a.jsxs(A,{className:q,error:t.error,isOptional:d,label:x,name:e,showError:t.touched&&!!t.error,smallLabel:L,inline:C,isLabelHidden:F,classNameLabel:_,classNameFooter:O,hideAsterisk:j,children:[a.jsx(w,{disabled:k,hasError:t.touched&&!!t.error,hasDescription:i!==void 0,options:S,defaultOption:V,"aria-required":!d,...s,...E,onChange:l=>N(l),variant:B.FORM}),i&&a.jsx("span",{children:i})]})};try{u.displayName="Select",u.__docgenInfo={description:"",displayName:"Select",props:{label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string | Element"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},maxLength:{defaultValue:null,description:"",name:"maxLength",required:!1,type:{name:"number"}},isLabelHidden:{defaultValue:null,description:`A flag to hide the label.
To be used with caution, as it can affect accessibility.
Do not use it if the label is mandatory, placeholder is not
a substitute for a label.`,name:"isLabelHidden",required:!1,type:{name:"boolean"}},hasLabelLineBreak:{defaultValue:null,description:"",name:"hasLabelLineBreak",required:!1,type:{name:"boolean"}},isOptional:{defaultValue:{value:"false"},description:`A flag to indicate that the field is optional.
It will display an asterisk next to the label.`,name:"isOptional",required:!1,type:{name:"boolean"}},hideAsterisk:{defaultValue:null,description:`Can be false only when it's the only field in a form and it's mandatory,
or when all fields are mandatory and the form indicates that all fields are mandatory`,name:"hideAsterisk",required:!1,type:{name:"boolean"}},classNameLabel:{defaultValue:null,description:"",name:"classNameLabel",required:!1,type:{name:"string"}},classNameFooter:{defaultValue:null,description:`A custom class for the footer,
where errors and character count are displayed.`,name:"classNameFooter",required:!1,type:{name:"string"}},classNameInput:{defaultValue:null,description:"",name:"classNameInput",required:!1,type:{name:"string"}},filterVariant:{defaultValue:null,description:"",name:"filterVariant",required:!1,type:{name:"boolean"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},inline:{defaultValue:null,description:"",name:"inline",required:!1,type:{name:"boolean"}},clearButtonProps:{defaultValue:null,description:"",name:"clearButtonProps",required:!1,type:{name:'(ButtonHTMLAttributes<HTMLButtonElement> & { tooltip: string; display?: "clear" | "close"; })'}},ErrorDetails:{defaultValue:null,description:"",name:"ErrorDetails",required:!1,type:{name:"ReactNode"}},defaultOption:{defaultValue:{value:"null"},description:"",name:"defaultOption",required:!1,type:{name:"SelectOption | null"}},options:{defaultValue:null,description:"",name:"options",required:!0,type:{name:"SelectOption[]"}}}}}catch{}const le={title:"ui-kit/forms/Select",component:u},g=[{value:"cinema",label:"Cinéma"},{value:"theatre",label:"Théatre"},{value:"musique",label:"Musique"}],r={args:{label:"Catégorie",options:g,disabled:!1,name:"select"},decorators:[e=>a.jsx(h,{initialValues:{category:"theatre"},onSubmit:()=>{},children:a.jsx(e,{})})]},n={args:{label:"Catégorie",options:g,disabled:!1,name:"select",description:"super select inline"},decorators:[e=>a.jsx(h,{initialValues:{category:"theatre"},onSubmit:()=>{},children:a.jsx(e,{})})]};var m,c,p;r.parameters={...r.parameters,docs:{...(m=r.parameters)==null?void 0:m.docs,source:{originalSource:`{
  args: {
    label: 'Catégorie',
    options: mockCategoriesOptions,
    disabled: false,
    name: 'select'
  },
  decorators: [Story => <Formik initialValues={{
    category: 'theatre'
  }} onSubmit={() => {}}>
        <Story />
      </Formik>]
}`,...(p=(c=r.parameters)==null?void 0:c.docs)==null?void 0:p.source}}};var f,b,y;n.parameters={...n.parameters,docs:{...(f=n.parameters)==null?void 0:f.docs,source:{originalSource:`{
  args: {
    label: 'Catégorie',
    options: mockCategoriesOptions,
    disabled: false,
    name: 'select',
    description: 'super select inline'
  },
  decorators: [Story => <Formik initialValues={{
    category: 'theatre'
  }} onSubmit={() => {}}>
        <Story />
      </Formik>]
}`,...(y=(b=n.parameters)==null?void 0:b.docs)==null?void 0:y.source}}};const re=["Default","SelectInline"];export{r as Default,n as SelectInline,re as __namedExportsOrder,le as default};
