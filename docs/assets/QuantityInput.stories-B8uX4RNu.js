import{j as n}from"./jsx-runtime-DF2Pcvd1.js";import{u as z,a as O,F as P}from"./index.esm-BBvhERNj.js";import{c as G}from"./index-DeARc5FM.js";import{r as u}from"./index-B2-qRKKC.js";import{C as J}from"./Checkbox-ByXPbm6B.js";import{T as K}from"./TextInput-DielMoqq.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./Tag-DoB-Hjk-.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-DfLnDDE5.js";import"./BaseInput-BpSbbDCb.js";import"./FieldError-B3RhE53I.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-DKTgIOgC.js";import"./index.module-D7-Ko2QV.js";const X={"quantity-row":"_quantity-row_szr8k_1"},y=({label:e="Quantité",name:r="quantity",onChange:t,onBlur:s,disabled:q,className:N,required:A,asterisk:C,minimum:g=0,maximum:R=1e6,value:l,error:W,ariaLabel:H})=>{const M=r,o=u.useRef(null),B=`${r}.unlimited`,x=u.useRef(null),m=l!==0&&!l,[i,b]=u.useState(m);u.useEffect(()=>{var v;const h=document.activeElement===x.current;!i&&h&&((v=o.current)==null||v.focus())},[i]),u.useEffect(()=>{i!==m&&b(m)},[m]);const D=a=>{t==null||t(a),b(a.target.value==="")},U=()=>{let a=`${g}`;i||(a=""),t==null||t({target:{value:a}}),o.current&&(o.current.value=a),b(h=>!h)},$=n.jsx(J,{ref:x,label:"Illimité",name:B,onChange:U,checked:i,disabled:q});return n.jsx(K,{ref:o,className:G(X["quantity-row"],N),name:M,label:e,required:A,asterisk:C,disabled:q,type:"number",hasDecimal:!1,min:g,max:R,step:1,InputExtension:$,onChange:D,onBlur:s,value:i?"":l===0?"0":l||"",error:W,"aria-label":H})};try{y.displayName="QuantityInput",y.__docgenInfo={description:`The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
An undefined quantity is meant to be interpreted as unlimited.`,displayName:"QuantityInput",props:{className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},asterisk:{defaultValue:null,description:`A property to not displayed asterisk even if field is required
If this prop is provided, the asterisk will not be displayed`,name:"asterisk",required:!1,type:{name:"boolean"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},label:{defaultValue:{value:"Quantité"},description:"A label for the text input.",name:"label",required:!1,type:{name:"string"}},name:{defaultValue:{value:"quantity"},description:"The name of the input, mind what's being used in the form.",name:"name",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"A callback when the quantity changes.",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"A callback when the quantity text input is blurred.",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},value:{defaultValue:null,description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:"value",required:!1,type:{name:"number"}},minimum:{defaultValue:{value:"0"},description:"The minimum value allowed for the quantity. Make sure it matches validation schema.",name:"minimum",required:!1,type:{name:"number"}},maximum:{defaultValue:{value:"1000000"},description:"The maximum value allowed for the quantity. Make sure it matches validation schema.",name:"maximum",required:!1,type:{name:"number"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},ariaLabel:{defaultValue:null,description:"",name:"ariaLabel",required:!1,type:{name:"string"}}}}}catch{}const Y=({children:e})=>{const r=O({defaultValues:{myField:100}});return n.jsx(P,{...r,children:n.jsx("form",{children:e})})},fe={title:"@/ui-kit/formsV2/QuantityInput",component:y},d={args:{name:"quantity",label:"Quantité"}},c={args:{name:"quantity",label:"Quantité",smallLabel:!0}},p={args:{name:"quantity",label:"Quantité",required:!0}},f={args:{name:"quantity",label:"Quantity",minimum:10},decorators:[e=>n.jsx(Y,{children:n.jsx(e,{})})],render:e=>{const{setValue:r,watch:t}=z();return n.jsx(y,{...e,value:t("myField"),onChange:s=>{r("myField",s.target.value?Number(s.target.value):void 0)}})}};var V,k,Q;d.parameters={...d.parameters,docs:{...(V=d.parameters)==null?void 0:V.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité'
  }
}`,...(Q=(k=d.parameters)==null?void 0:k.docs)==null?void 0:Q.source}}};var F,E,I;c.parameters={...c.parameters,docs:{...(F=c.parameters)==null?void 0:F.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    smallLabel: true
  }
}`,...(I=(E=c.parameters)==null?void 0:E.docs)==null?void 0:I.source}}};var w,_,L;p.parameters={...p.parameters,docs:{...(w=p.parameters)==null?void 0:w.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    required: true
  }
}`,...(L=(_=p.parameters)==null?void 0:_.docs)==null?void 0:L.source}}};var S,T,j;f.parameters={...f.parameters,docs:{...(S=f.parameters)==null?void 0:S.docs,source:{originalSource:`{
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
}`,...(j=(T=f.parameters)==null?void 0:T.docs)==null?void 0:j.source}}};const ye=["Default","SmallLabel","Required","WithinForm"];export{d as Default,p as Required,c as SmallLabel,f as WithinForm,ye as __namedExportsOrder,fe as default};
