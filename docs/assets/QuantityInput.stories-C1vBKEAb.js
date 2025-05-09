import{j as n}from"./jsx-runtime-BYYWji4R.js";import{u as $,a as z,F as O}from"./index.esm-BuPb1Mi7.js";import{c as P}from"./index-DeARc5FM.js";import{r as o}from"./index-ClcD9ViR.js";import{B as G}from"./BaseCheckbox-yx2QTGF8.js";import{T as J}from"./TextInput-DUFoZnSR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./SvgIcon-CyWUmZpn.js";import"./BaseInput-BI1b_EYZ.js";import"./FieldError-azuIsM2E.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-Bc4HS3VB.js";import"./index.module-DF6qn1Ex.js";const K={"quantity-row":"_quantity-row_szr8k_1"},f=({label:e="Quantité",name:r="quantity",onChange:t,onBlur:u,disabled:h,className:N,required:L,asterisk:A,minimum:b=0,maximum:R=1e6,value:s,error:C})=>{const B=r,l=o.useRef(null),W=`${r}.unlimited`,q=o.useRef(null),H=s!==0&&!s,[i,x]=o.useState(H);o.useEffect(()=>{var g;const y=document.activeElement===q.current;!i&&y&&((g=l.current)==null||g.focus())},[i]);const M=a=>{t==null||t(a),x(a.target.value==="")},D=()=>{let a=`${b}`;i||(a=""),t==null||t({target:{value:a}}),l.current&&(l.current.value=a),x(y=>!y)},U=n.jsx(G,{ref:q,label:"Illimité",name:W,onChange:D,checked:i,disabled:h});return n.jsx(J,{ref:l,className:P(K["quantity-row"],N),name:B,label:e,required:L,asterisk:A,disabled:h,type:"number",hasDecimal:!1,min:b,max:R,step:1,InputExtension:U,onChange:M,onBlur:u,value:i?"":s===0?"0":s||"",error:C})};try{f.displayName="QuantityInput",f.__docgenInfo={description:`The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
An undefined quantity is meant to be interpreted as unlimited.`,displayName:"QuantityInput",props:{className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:null,description:`A property to not displayed asterisk even if field is required
If this prop is provided, the asterisk will not be displayed`,name:"asterisk",required:!1,type:{name:"boolean"}},label:{defaultValue:{value:"Quantité"},description:"A label for the text input.",name:"label",required:!1,type:{name:"string"}},name:{defaultValue:{value:"quantity"},description:"The name of the input, mind what's being used in the form.",name:"name",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"A callback when the quantity changes.",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"A callback when the quantity text input is blurred.",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},value:{defaultValue:null,description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:"value",required:!1,type:{name:"number"}},minimum:{defaultValue:{value:"0"},description:"The minimum value allowed for the quantity. Make sure it matches validation schema.",name:"minimum",required:!1,type:{name:"number"}},maximum:{defaultValue:{value:"1000000"},description:"The maximum value allowed for the quantity. Make sure it matches validation schema.",name:"maximum",required:!1,type:{name:"number"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}}}}}catch{}const X=({children:e})=>{const r=z({defaultValues:{myField:100}});return n.jsx(O,{...r,children:n.jsx("form",{children:e})})},de={title:"ui-kit/formsV2/QuantityInput",component:f},m={args:{name:"quantity",label:"Quantité"}},d={args:{name:"quantity",label:"Quantité",smallLabel:!0}},c={args:{name:"quantity",label:"Quantité",required:!0}},p={args:{name:"quantity",label:"Quantity",minimum:10},decorators:[e=>n.jsx(X,{children:n.jsx(e,{})})],render:e=>{const{setValue:r,watch:t}=$();return n.jsx(f,{...e,value:t("myField"),onChange:u=>{r("myField",u.target.value?Number(u.target.value):void 0)}})}};var v,k,Q;m.parameters={...m.parameters,docs:{...(v=m.parameters)==null?void 0:v.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité'
  }
}`,...(Q=(k=m.parameters)==null?void 0:k.docs)==null?void 0:Q.source}}};var V,F,I;d.parameters={...d.parameters,docs:{...(V=d.parameters)==null?void 0:V.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    smallLabel: true
  }
}`,...(I=(F=d.parameters)==null?void 0:F.docs)==null?void 0:I.source}}};var E,w,_;c.parameters={...c.parameters,docs:{...(E=c.parameters)==null?void 0:E.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    required: true
  }
}`,...(_=(w=c.parameters)==null?void 0:w.docs)==null?void 0:_.source}}};var S,T,j;p.parameters={...p.parameters,docs:{...(S=p.parameters)==null?void 0:S.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantity',
    minimum: 10
  },
  decorators: [(Story: any) => <Wrapper>
        <Story />
      </Wrapper>],
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const {
      setValue,
      watch
    } = useFormContext<{
      myField?: number;
    }>();
    return <QuantityInput {...args} value={watch('myField')} onChange={e => {
      setValue('myField', e.target.value ? Number(e.target.value) : undefined);
    }}></QuantityInput>;
  }
}`,...(j=(T=p.parameters)==null?void 0:T.docs)==null?void 0:j.source}}};const ce=["Default","SmallLabel","Required","WithinForm"];export{m as Default,c as Required,d as SmallLabel,p as WithinForm,ce as __namedExportsOrder,de as default};
