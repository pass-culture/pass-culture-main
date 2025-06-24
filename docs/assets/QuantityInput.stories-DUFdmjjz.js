import{j as n}from"./jsx-runtime-BYYWji4R.js";import{u as $,a as z,F as O}from"./index.esm-ClDB96id.js";import{c as P}from"./index-DeARc5FM.js";import{r as u}from"./index-ClcD9ViR.js";import{C as G}from"./Checkbox-BsDe44fA.js";import{T as J}from"./TextInput-CZOlu6xY.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./Tag-CQO0EYV8.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-CyWUmZpn.js";import"./BaseInput-BI1b_EYZ.js";import"./FieldError-ky1_Lcaw.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-Cf20ddBy.js";import"./index.module-D0awDY1b.js";const K={"quantity-row":"_quantity-row_szr8k_1"},y=({label:e="Quantité",name:r="quantity",onChange:t,onBlur:s,disabled:q,className:L,required:A,asterisk:C,minimum:x=0,maximum:R=1e6,value:l,error:W})=>{const H=r,o=u.useRef(null),M=`${r}.unlimited`,g=u.useRef(null),m=l!==0&&!l,[i,h]=u.useState(m);u.useEffect(()=>{var v;const b=document.activeElement===g.current;!i&&b&&((v=o.current)==null||v.focus())},[i]),u.useEffect(()=>{i!==m&&h(m)},[m]);const B=a=>{t==null||t(a),h(a.target.value==="")},D=()=>{let a=`${x}`;i||(a=""),t==null||t({target:{value:a}}),o.current&&(o.current.value=a),h(b=>!b)},U=n.jsx(G,{ref:g,label:"Illimité",name:M,onChange:D,checked:i,disabled:q});return n.jsx(J,{ref:o,className:P(K["quantity-row"],L),name:H,label:e,required:A,asterisk:C,disabled:q,type:"number",hasDecimal:!1,min:x,max:R,step:1,InputExtension:U,onChange:B,onBlur:s,value:i?"":l===0?"0":l||"",error:W})};try{y.displayName="QuantityInput",y.__docgenInfo={description:`The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
An undefined quantity is meant to be interpreted as unlimited.`,displayName:"QuantityInput",props:{className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:null,description:`A property to not displayed asterisk even if field is required
If this prop is provided, the asterisk will not be displayed`,name:"asterisk",required:!1,type:{name:"boolean"}},label:{defaultValue:{value:"Quantité"},description:"A label for the text input.",name:"label",required:!1,type:{name:"string"}},name:{defaultValue:{value:"quantity"},description:"The name of the input, mind what's being used in the form.",name:"name",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"A callback when the quantity changes.",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"A callback when the quantity text input is blurred.",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},value:{defaultValue:null,description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:"value",required:!1,type:{name:"number"}},minimum:{defaultValue:{value:"0"},description:"The minimum value allowed for the quantity. Make sure it matches validation schema.",name:"minimum",required:!1,type:{name:"number"}},maximum:{defaultValue:{value:"1000000"},description:"The maximum value allowed for the quantity. Make sure it matches validation schema.",name:"maximum",required:!1,type:{name:"number"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}}}}}catch{}const X=({children:e})=>{const r=z({defaultValues:{myField:100}});return n.jsx(O,{...r,children:n.jsx("form",{children:e})})},pe={title:"ui-kit/formsV2/QuantityInput",component:y},d={args:{name:"quantity",label:"Quantité"}},c={args:{name:"quantity",label:"Quantité",smallLabel:!0}},p={args:{name:"quantity",label:"Quantité",required:!0}},f={args:{name:"quantity",label:"Quantity",minimum:10},decorators:[e=>n.jsx(X,{children:n.jsx(e,{})})],render:e=>{const{setValue:r,watch:t}=$();return n.jsx(y,{...e,value:t("myField"),onChange:s=>{r("myField",s.target.value?Number(s.target.value):void 0)}})}};var k,Q,V;d.parameters={...d.parameters,docs:{...(k=d.parameters)==null?void 0:k.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité'
  }
}`,...(V=(Q=d.parameters)==null?void 0:Q.docs)==null?void 0:V.source}}};var F,E,I;c.parameters={...c.parameters,docs:{...(F=c.parameters)==null?void 0:F.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    smallLabel: true
  }
}`,...(I=(E=c.parameters)==null?void 0:E.docs)==null?void 0:I.source}}};var w,_,S;p.parameters={...p.parameters,docs:{...(w=p.parameters)==null?void 0:w.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    required: true
  }
}`,...(S=(_=p.parameters)==null?void 0:_.docs)==null?void 0:S.source}}};var T,j,N;f.parameters={...f.parameters,docs:{...(T=f.parameters)==null?void 0:T.docs,source:{originalSource:`{
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
}`,...(N=(j=f.parameters)==null?void 0:j.docs)==null?void 0:N.source}}};const fe=["Default","SmallLabel","Required","WithinForm"];export{d as Default,p as Required,c as SmallLabel,f as WithinForm,fe as __namedExportsOrder,pe as default};
