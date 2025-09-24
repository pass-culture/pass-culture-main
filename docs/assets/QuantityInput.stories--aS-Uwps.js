import{j as a}from"./jsx-runtime-Cf8x2fCZ.js";import{u as S,a as T,F as j}from"./index.esm-D1X9ZzX-.js";import{c as N}from"./index-B0pXE9zJ.js";import{r as i}from"./index-QQMyt9Ur.js";import{C as A}from"./Checkbox-8jeYcLLy.js";import{T as R}from"./TextInput-C-6M7uLs.js";import"./index-yBjzXJbu.js";import"./_commonjsHelpers-CqkleIqs.js";import"./Tag-DpLUbPXr.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-B5V96DYN.js";import"./BaseInput-B8c5gx_3.js";import"./stroke-search-dgesjRZH.js";import"./FieldError-2mFOl_uD.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-CCjrqBrG.js";import"./index.module-DTkZ18fI.js";const W={"quantity-row":"_quantity-row_szr8k_1"},f=({label:e="Quantité",name:n="quantity",onChange:u,onBlur:l,disabled:q,className:v,required:k,asterisk:Q,minimum:g=0,maximum:V=1e6,value:y,error:F,ariaLabel:E})=>{const I=n,s=i.useRef(null),C=`${n}.unlimited`,x=i.useRef(null),o=y!==0&&!y,[r,h]=i.useState(o);i.useEffect(()=>{const b=document.activeElement===x.current;!r&&b&&s.current?.focus()},[r]),i.useEffect(()=>{r!==o&&h(o)},[o]);const w=t=>{u?.(t),h(t.target.value==="")},_=()=>{let t=`${g}`;r||(t=""),u?.({target:{value:t}}),s.current&&(s.current.value=t),h(b=>!b)},L=a.jsx(A,{ref:x,label:"Illimité",name:C,onChange:_,checked:r,disabled:q});return a.jsx(R,{ref:s,className:N(W["quantity-row"],v),name:I,label:e,required:k,asterisk:Q,disabled:q,type:"number",hasDecimal:!1,min:g,max:V,step:1,InputExtension:L,onChange:w,onBlur:l,value:r?"":y??"",error:F,"aria-label":E})};try{f.displayName="QuantityInput",f.__docgenInfo={description:`The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
An undefined quantity is meant to be interpreted as unlimited.`,displayName:"QuantityInput",props:{className:{defaultValue:null,description:`A custom class for the field layout,
where label, description, input, and footer are displayed.`,name:"className",required:!1,type:{name:"string"}},asterisk:{defaultValue:null,description:`A property to not displayed asterisk even if field is required
If this prop is provided, the asterisk will not be displayed`,name:"asterisk",required:!1,type:{name:"boolean"}},smallLabel:{defaultValue:null,description:"A flag to display a smaller label.",name:"smallLabel",required:!1,type:{name:"boolean"}},label:{defaultValue:{value:"Quantité"},description:"A label for the text input.",name:"label",required:!1,type:{name:"string"}},name:{defaultValue:{value:"quantity"},description:"The name of the input, mind what's being used in the form.",name:"name",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"A callback when the quantity changes.",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"A callback when the quantity text input is blurred.",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},value:{defaultValue:null,description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:"value",required:!1,type:{name:"number | null"}},minimum:{defaultValue:{value:"0"},description:"The minimum value allowed for the quantity. Make sure it matches validation schema.",name:"minimum",required:!1,type:{name:"number"}},maximum:{defaultValue:{value:"1000000"},description:"The maximum value allowed for the quantity. Make sure it matches validation schema.",name:"maximum",required:!1,type:{name:"number"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},ariaLabel:{defaultValue:null,description:"",name:"ariaLabel",required:!1,type:{name:"string"}}}}}catch{}const H=({children:e})=>{const n=T({defaultValues:{myField:100}});return a.jsx(j,{...n,children:a.jsx("form",{children:e})})},ne={title:"@/ui-kit/forms/QuantityInput",component:f},m={args:{name:"quantity",label:"Quantité"}},d={args:{name:"quantity",label:"Quantité",smallLabel:!0}},c={args:{name:"quantity",label:"Quantité",required:!0}},p={args:{name:"quantity",label:"Quantity",minimum:10},decorators:[e=>a.jsx(H,{children:a.jsx(e,{})})],render:e=>{const{setValue:n,watch:u}=S();return a.jsx(f,{...e,value:u("myField"),onChange:l=>{n("myField",l.target.value?Number(l.target.value):void 0)}})}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité'
  }
}`,...m.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    smallLabel: true
  }
}`,...d.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    required: true
  }
}`,...c.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
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
}`,...p.parameters?.docs?.source}}};const re=["Default","SmallLabel","Required","WithinForm"];export{m as Default,c as Required,d as SmallLabel,p as WithinForm,re as __namedExportsOrder,ne as default};
