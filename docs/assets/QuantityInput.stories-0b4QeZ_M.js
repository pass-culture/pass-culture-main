import{j as a}from"./jsx-runtime-XCRBpYO9.js";import{a as _,u as j,F as w}from"./index.esm-D59e2sCt.js";import{r as i}from"./iframe-DJLfoGTR.js";import{C as S}from"./Checkbox-CoIkAoih.js";import{T as R}from"./TextInput-BsDHVIa6.js";import"./preload-helper-PPVm8Dsz.js";import"./index-_b2EKpCM.js";import"./Tag-CxE8OUMz.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-B_jOQ3or.js";import"./full-error-BFAmjN4t.js";import"./index.module-CI_jRAaR.js";import"./Tooltip-Crh5A-3O.js";const p=({label:t="Quantité",name:n="quantity",onChange:u,onBlur:l,disabled:g,required:x,asterisk:v,min:b=0,max:V=1e6,value:f,error:F,ariaLabel:Q})=>{const k=n,s=i.useRef(null),C=`${n}.unlimited`,q=i.useRef(null),o=f!==0&&!f,[r,y]=i.useState(o);i.useEffect(()=>{const h=document.activeElement===q.current;!r&&h&&s.current?.focus()},[r]),i.useEffect(()=>{r!==o&&y(o)},[o]);const E=e=>{e.target.value&&/[,.]/.test(e.target.value)&&(e.target.value=e.target.value.split(".")[0].split(",")[0]),u?.(e),y(e.target.value==="")},I=()=>{let e=`${b}`;r||(e=""),u?.({target:{value:e}}),s.current&&(s.current.value=e),y(h=>!h)},T=a.jsx(S,{ref:q,label:"Illimité",name:C,onChange:I,checked:r,disabled:g});return a.jsx(R,{ref:s,name:k,label:t,required:x,asterisk:v,disabled:g,type:"number",min:b,max:V,step:1,extension:T,onChange:E,onBlur:l,value:r?"":f?.toString()??"",error:F,"aria-label":Q})};try{p.displayName="QuantityInput",p.__docgenInfo={description:`The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
An undefined quantity is meant to be interpreted as unlimited.`,displayName:"QuantityInput",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:null,description:"",name:"asterisk",required:!1,type:{name:"boolean"}},label:{defaultValue:{value:"Quantité"},description:"A label for the text input.",name:"label",required:!1,type:{name:"string"}},name:{defaultValue:{value:"quantity"},description:"The name of the input, mind what's being used in the form.",name:"name",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"A callback when the quantity changes.",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"A callback when the quantity text input is blurred.",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},value:{defaultValue:null,description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:"value",required:!1,type:{name:"number | null"}},min:{defaultValue:{value:"0"},description:"The minimum value allowed for the quantity. Make sure it matches validation schema.",name:"min",required:!1,type:{name:"number"}},max:{defaultValue:{value:"1000000"},description:"The maximum value allowed for the quantity. Make sure it matches validation schema.",name:"max",required:!1,type:{name:"number"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},ariaLabel:{defaultValue:null,description:"",name:"ariaLabel",required:!1,type:{name:"string"}}}}}catch{}const N=({children:t})=>{const n=j({defaultValues:{myField:100}});return a.jsx(w,{...n,children:a.jsx("form",{children:t})})},J={title:"@/ui-kit/forms/QuantityInput",component:p},m={args:{name:"quantity",label:"Quantité"}},d={args:{name:"quantity",label:"Quantité",required:!0}},c={args:{name:"quantity",label:"Quantity",min:10},decorators:[t=>a.jsx(N,{children:a.jsx(t,{})})],render:t=>{const{setValue:n,watch:u}=_();return a.jsx(p,{...t,value:u("myField"),onChange:l=>{n("myField",l.target.value?Number(l.target.value):void 0)}})}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité'
  }
}`,...m.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    required: true
  }
}`,...d.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantity',
    min: 10
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
}`,...c.parameters?.docs?.source}}};const K=["Default","Required","WithinForm"];export{m as Default,d as Required,c as WithinForm,K as __namedExportsOrder,J as default};
