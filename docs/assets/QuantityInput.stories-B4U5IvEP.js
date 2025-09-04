import{j as n}from"./jsx-runtime-DF2Pcvd1.js";import{u as z,a as O,F as P}from"./index.esm-BBvhERNj.js";import{c as G}from"./index-DeARc5FM.js";import{r as u}from"./index-B2-qRKKC.js";import{C as J}from"./Checkbox-DcgCepTx.js";import{T as K}from"./TextInput-BXnJurHW.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./Tag-DoB-Hjk-.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-DfLnDDE5.js";import"./BaseInput-JKfrEs2s.js";import"./stroke-search-dgesjRZH.js";import"./FieldError-B3RhE53I.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-Cg7wcWeq.js";import"./index.module-BDmDBTbR.js";const X={"quantity-row":"_quantity-row_szr8k_1"},f=({label:e="Quantité",name:r="quantity",onChange:t,onBlur:l,disabled:q,className:N,required:A,asterisk:C,minimum:g=0,maximum:R=1e6,value:y,error:W,ariaLabel:H})=>{const M=r,s=u.useRef(null),B=`${r}.unlimited`,x=u.useRef(null),o=y!==0&&!y,[i,b]=u.useState(o);u.useEffect(()=>{var v;const h=document.activeElement===x.current;!i&&h&&((v=s.current)==null||v.focus())},[i]),u.useEffect(()=>{i!==o&&b(o)},[o]);const D=a=>{t==null||t(a),b(a.target.value==="")},U=()=>{let a=`${g}`;i||(a=""),t==null||t({target:{value:a}}),s.current&&(s.current.value=a),b(h=>!h)},$=n.jsx(J,{ref:x,label:"Illimité",name:B,onChange:U,checked:i,disabled:q});return n.jsx(K,{ref:s,className:G(X["quantity-row"],N),name:M,label:e,required:A,asterisk:C,disabled:q,type:"number",hasDecimal:!1,min:g,max:R,step:1,InputExtension:$,onChange:D,onBlur:l,value:i?"":y??"",error:W,"aria-label":H})};try{f.displayName="QuantityInput",f.__docgenInfo={description:`The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
An undefined quantity is meant to be interpreted as unlimited.`,displayName:"QuantityInput",props:{className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},asterisk:{defaultValue:null,description:`A property to not displayed asterisk even if field is required
If this prop is provided, the asterisk will not be displayed`,name:"asterisk",required:!1,type:{name:"boolean"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},label:{defaultValue:{value:"Quantité"},description:"A label for the text input.",name:"label",required:!1,type:{name:"string"}},name:{defaultValue:{value:"quantity"},description:"The name of the input, mind what's being used in the form.",name:"name",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"A callback when the quantity changes.",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"A callback when the quantity text input is blurred.",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},value:{defaultValue:null,description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:"value",required:!1,type:{name:"number | null"}},minimum:{defaultValue:{value:"0"},description:"The minimum value allowed for the quantity. Make sure it matches validation schema.",name:"minimum",required:!1,type:{name:"number"}},maximum:{defaultValue:{value:"1000000"},description:"The maximum value allowed for the quantity. Make sure it matches validation schema.",name:"maximum",required:!1,type:{name:"number"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},ariaLabel:{defaultValue:null,description:"",name:"ariaLabel",required:!1,type:{name:"string"}}}}}catch{}const Y=({children:e})=>{const r=O({defaultValues:{myField:100}});return n.jsx(P,{...r,children:n.jsx("form",{children:e})})},ye={title:"@/ui-kit/forms/QuantityInput",component:f},m={args:{name:"quantity",label:"Quantité"}},d={args:{name:"quantity",label:"Quantité",smallLabel:!0}},c={args:{name:"quantity",label:"Quantité",required:!0}},p={args:{name:"quantity",label:"Quantity",minimum:10},decorators:[e=>n.jsx(Y,{children:n.jsx(e,{})})],render:e=>{const{setValue:r,watch:t}=z();return n.jsx(f,{...e,value:t("myField"),onChange:l=>{r("myField",l.target.value?Number(l.target.value):void 0)}})}};var k,Q,V;m.parameters={...m.parameters,docs:{...(k=m.parameters)==null?void 0:k.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité'
  }
}`,...(V=(Q=m.parameters)==null?void 0:Q.docs)==null?void 0:V.source}}};var F,E,I;d.parameters={...d.parameters,docs:{...(F=d.parameters)==null?void 0:F.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    smallLabel: true
  }
}`,...(I=(E=d.parameters)==null?void 0:E.docs)==null?void 0:I.source}}};var w,_,L;c.parameters={...c.parameters,docs:{...(w=c.parameters)==null?void 0:w.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    required: true
  }
}`,...(L=(_=c.parameters)==null?void 0:_.docs)==null?void 0:L.source}}};var S,T,j;p.parameters={...p.parameters,docs:{...(S=p.parameters)==null?void 0:S.docs,source:{originalSource:`{
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
}`,...(j=(T=p.parameters)==null?void 0:T.docs)==null?void 0:j.source}}};const be=["Default","SmallLabel","Required","WithinForm"];export{m as Default,c as Required,d as SmallLabel,p as WithinForm,be as __namedExportsOrder,ye as default};
