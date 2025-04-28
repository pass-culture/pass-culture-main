import{j as x}from"./jsx-runtime-BYYWji4R.js";import{r as l}from"./index-ClcD9ViR.js";import{B}from"./BaseCheckbox-DKrWbv5n.js";import{T as F}from"./TextInput-CVZu0z03.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./index-DeARc5FM.js";import"./SvgIcon-CyWUmZpn.js";import"./BaseInput-BrnVefEj.js";import"./FieldError-azuIsM2E.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-Bc4HS3VB.js";import"./index.module-DF6qn1Ex.js";const H={"input-layout-small-label":"_input-layout-small-label_kaqxt_1"},o=({label:m="Quantité",name:c="quantity",onChange:a,disabled:d,className:T,isLabelHidden:N,required:p,min:f="0",smallLabel:R})=>{var h,q;const S=c,t=l.useRef(null),A=`${c}.unlimited`,y=l.useRef(null),C=((h=t.current)==null?void 0:h.value)===""||((q=t.current)==null?void 0:q.value)===void 0,[i,b]=l.useState(C);l.useEffect(()=>{var g;const e=document.activeElement===y.current;!i&&e&&((g=t.current)==null||g.focus())},[i]);const j=n=>{const e=n.target.value||"";b(e===""),a==null||a(e)},D=()=>{const n=!i;b(n);let e=f;n&&(e=""),a?a(e):t.current&&(t.current.value=e)},U=x.jsx(B,{ref:y,label:"Illimité",name:A,onChange:D,checked:i,disabled:d});return x.jsx(F,{ref:t,className:T,labelClassName:R?H["input-layout-small-label"]:"",name:S,label:m,required:p,asterisk:p,disabled:d,type:"number",hasDecimal:!1,min:f,max:1e6,isLabelHidden:N,step:1,InputExtension:U,onChange:j})};try{o.displayName="QuantityInput",o.__docgenInfo={description:`The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
It integrates with for form state management and is used when an undefined quantity is meant to be interpreted as unlimited.`,displayName:"QuantityInput",props:{className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},isLabelHidden:{defaultValue:null,description:`A flag to hide the label.
To be used with caution, as it can affect accessibility.
Do not use it if the label is mandatory, placeholder is not
a substitute for a label.`,name:"isLabelHidden",required:!1,type:{name:"boolean"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},label:{defaultValue:{value:"Quantité"},description:"A label for the input, also used as the aria-label for the group.",name:"label",required:!1,type:{name:"string"}},name:{defaultValue:{value:"quantity"},description:"The name of the input, mind what's being used in the form.",name:"name",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:`A callback when the quantity changes.
If not provided, the value will be set in the form, otherwise, setFieldValue must be called manually.
This is to support custom logic when the quantity changes.`,name:"onChange",required:!1,type:{name:"((quantity: string) => void)"}},min:{defaultValue:{value:"0"},description:"The minimum value allowed for the quantity. Make sure it matches validation schema.",name:"min",required:!1,type:{name:"string"}}}}}catch{}const ee={title:"ui-kit/formsV2/QuantityInput",component:o},s={args:{name:"quantity",label:"Quantité"}},r={args:{name:"quantity",label:"Quantité",smallLabel:!0}},u={args:{name:"quantity",label:"Quantité",required:!0}};var v,I,Q;s.parameters={...s.parameters,docs:{...(v=s.parameters)==null?void 0:v.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité'
  }
}`,...(Q=(I=s.parameters)==null?void 0:I.docs)==null?void 0:Q.source}}};var _,V,E;r.parameters={...r.parameters,docs:{...(_=r.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    smallLabel: true
  }
}`,...(E=(V=r.parameters)==null?void 0:V.docs)==null?void 0:E.source}}};var k,w,L;u.parameters={...u.parameters,docs:{...(k=u.parameters)==null?void 0:k.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    required: true
  }
}`,...(L=(w=u.parameters)==null?void 0:w.docs)==null?void 0:L.source}}};const te=["Default","SmallLabel","Required"];export{s as Default,u as Required,r as SmallLabel,te as __namedExportsOrder,ee as default};
