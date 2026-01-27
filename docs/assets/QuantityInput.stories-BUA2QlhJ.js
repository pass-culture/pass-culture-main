import{j as a}from"./jsx-runtime-C_uOM0Gm.js";import{a as _,u as j,F as w}from"./index.esm-B74CwnGv.js";import{r as i}from"./iframe-CTnXOULQ.js";import{C as S}from"./Checkbox-BYovAbr0.js";import{T as R}from"./TextInput-DOsfrCQI.js";import"./preload-helper-PPVm8Dsz.js";import"./index-TscbDd2H.js";import"./Asset-DEO5YOFe.js";import"./Tag-CZrfY-rG.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-CJiY4LCz.js";import"./FieldFooter-CL0tzobd.js";import"./full-error-BFAmjN4t.js";import"./index.module-DEHgy3-r.js";import"./FieldHeader-DxZ9joXq.js";import"./Tooltip-GJ5PEk5n.js";const p=({label:t="Quantité",name:n="quantity",onChange:u,onBlur:l,disabled:g,required:x,requiredIndicator:v,min:q=0,max:V=1e6,value:f,error:F,ariaLabel:I})=>{const Q=n,o=i.useRef(null),C=`${n}.unlimited`,b=i.useRef(null),s=f!==0&&!f,[r,y]=i.useState(s);i.useEffect(()=>{const h=document.activeElement===b.current;!r&&h&&o.current?.focus()},[r]),i.useEffect(()=>{r!==s&&y(s)},[s]);const E=e=>{e.target.value&&/[,.]/.test(e.target.value)&&(e.target.value=e.target.value.split(".")[0].split(",")[0]),u?.(e),y(e.target.value==="")},k=()=>{let e=`${q}`;r||(e=""),u?.({target:{value:e}}),o.current&&(o.current.value=e),y(h=>!h)},T=a.jsx(S,{ref:b,label:"Illimité",name:C,onChange:k,checked:r,disabled:g});return a.jsx(R,{ref:o,name:Q,label:t,required:x,requiredIndicator:v,disabled:g,type:"number",min:q,max:V,step:1,extension:T,onChange:E,onBlur:l,value:r?"":f?.toString()??"",error:F,"aria-label":I})};try{p.displayName="QuantityInput",p.__docgenInfo={description:`The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
An undefined quantity is meant to be interpreted as unlimited.`,displayName:"QuantityInput",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},requiredIndicator:{defaultValue:null,description:"",name:"requiredIndicator",required:!1,type:{name:"enum",value:[{value:'"symbol"'},{value:'"hidden"'},{value:'"explicit"'}]}},label:{defaultValue:{value:"Quantité"},description:"A label for the text input.",name:"label",required:!1,type:{name:"string"}},name:{defaultValue:{value:"quantity"},description:"The name of the input, mind what's being used in the form.",name:"name",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"A callback when the quantity changes.",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"A callback when the quantity text input is blurred.",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},value:{defaultValue:null,description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:"value",required:!1,type:{name:"number | null"}},min:{defaultValue:{value:"0"},description:"The minimum value allowed for the quantity. Make sure it matches validation schema.",name:"min",required:!1,type:{name:"number"}},max:{defaultValue:{value:"1000000"},description:"The maximum value allowed for the quantity. Make sure it matches validation schema.",name:"max",required:!1,type:{name:"number"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},ariaLabel:{defaultValue:null,description:"",name:"ariaLabel",required:!1,type:{name:"string"}}}}}catch{}const N=({children:t})=>{const n=j({defaultValues:{myField:100}});return a.jsx(w,{...n,children:a.jsx("form",{children:t})})},Y={title:"@/ui-kit/forms/QuantityInput",component:p},m={args:{name:"quantity",label:"Quantité"}},d={args:{name:"quantity",label:"Quantité",required:!0}},c={args:{name:"quantity",label:"Quantity",min:10},decorators:[t=>a.jsx(N,{children:a.jsx(t,{})})],render:t=>{const{setValue:n,watch:u}=_();return a.jsx(p,{...t,value:u("myField"),onChange:l=>{n("myField",l.target.value?Number(l.target.value):void 0)}})}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
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
}`,...c.parameters?.docs?.source}}};const Z=["Default","Required","WithinForm"];export{m as Default,d as Required,c as WithinForm,Z as __namedExportsOrder,Y as default};
