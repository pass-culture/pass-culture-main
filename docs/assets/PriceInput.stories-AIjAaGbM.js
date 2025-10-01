import{j as n}from"./jsx-runtime-696WI-R9.js";import{R as _,r as l}from"./iframe-DC-pzFJj.js";import{C as N}from"./Checkbox-C-qC8Zr6.js";import{T}from"./TextInput-B6Iahbp0.js";import{a as S,u as W,F as U}from"./index.esm-DRfGFkqR.js";import"./preload-helper-PPVm8Dsz.js";import"./index-DrsUujRR.js";import"./Tag-BlE21ldy.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-DwZRSni_.js";import"./FieldFooter-rM_I5qiT.js";import"./full-error-BFAmjN4t.js";import"./index.module-YuqhVSmR.js";import"./FieldHeader-C7G-Cfls.js";import"./Tooltip-Dn5-X8JA.js";const p=_.forwardRef(({name:e,label:a,value:s,max:i,disabled:f,showFreeCheckbox:d,hideAsterisk:h=!1,error:k,description:P,currency:b="EUR",onChange:g,onBlur:q},E)=>{const x=l.useRef(null),I=`${e}.free`,y=l.useRef(null),V=s===0,[o,v]=l.useState(V),F=b==="XPF"?1:.01,w=b==="XPF"?"(en F)":"(en €)";l.useEffect(()=>{const t=document.activeElement===y.current;!o&&t&&x.current?.focus()},[o]);const R=r=>{const t=r.target.value;let C=t!==""?Number(t):void 0;d&&o&&(C=0),g?.({target:{valueAsNumber:C}}),d&&v(r.target.value==="0")},j=()=>{const r=!o;v(r);let t="";r&&(t="0"),g?.({target:{valueAsNumber:Number(t)}})},A=n.jsx(N,{ref:y,label:"Gratuit",checked:o,name:I,onChange:j,disabled:f});return n.jsx("div",{ref:E,children:n.jsx(T,{ref:x,autoComplete:"off",required:!h,name:e,label:`${a} ${w}`,value:s?.toString()??"",type:"number",step:F,min:0,max:i,disabled:f,description:P,asterisk:!h,onChange:R,onBlur:q,onKeyDown:r=>{F===1&&/[,.]/.test(r.key)&&r.preventDefault()},error:k,...d?{extension:A}:{}})})});try{p.displayName="PriceInput",p.__docgenInfo={description:`The PriceInput component is a combination of a TextInput and a Checkbox to define prices.
It integrates with Formik for form state management and is used when an null price is meant to be interpreted as free.

---`,displayName:"PriceInput",props:{description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},name:{defaultValue:null,description:"The name of the input, mind what's being used in the form.",name:"name",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},max:{defaultValue:null,description:"",name:"max",required:!1,type:{name:"string | number"}},label:{defaultValue:null,description:`A label for the input,
also used as the aria-label for the group.`,name:"label",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"A callback when the quantity changes.",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"A callback when the quantity text input is blurred.",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},value:{defaultValue:null,description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:"value",required:!1,type:{name:'number | ""'}},showFreeCheckbox:{defaultValue:null,description:'A flag to show the "Gratuit" checkbox.',name:"showFreeCheckbox",required:!1,type:{name:"boolean"}},hideAsterisk:{defaultValue:{value:"false"},description:"",name:"hideAsterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:`A custom error message to be displayed.
If this prop is provided, the error message will be displayed and the field will be marked as errored`,name:"error",required:!1,type:{name:"string"}},currency:{defaultValue:{value:"EUR"},description:"Currency to use to display currency icon",name:"currency",required:!1,type:{name:"enum",value:[{value:'"EUR"'},{value:'"XPF"'}]}}}}}catch{}const D=({children:e})=>{const a=W({defaultValues:{price:100}});return n.jsx(U,{...a,children:n.jsx("form",{children:e})})},re={title:"@/ui-kit/forms/PriceInput",component:p},u={args:{name:"price",label:"Prix"}},c={args:{name:"price",label:"Prix",showFreeCheckbox:!0}},m={args:{name:"price",label:"Prix",currency:"EUR"},decorators:[e=>n.jsx(D,{children:n.jsx(e,{})})],render:e=>{const{setValue:a,watch:s}=S();return n.jsx(p,{...e,value:s("price"),onChange:i=>{a("price",i.target.value?Number(i.target.value):void 0)}})}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'price',
    label: 'Prix'
  }
}`,...u.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'price',
    label: 'Prix',
    showFreeCheckbox: true
  }
}`,...c.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'price',
    label: 'Prix',
    currency: 'EUR'
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
      price?: number;
    }>();
    return <PriceInput {...args} value={watch('price')} onChange={e => {
      setValue('price', e.target.value ? Number(e.target.value) : undefined);
    }} />;
  }
}`,...m.parameters?.docs?.source}}};const ne=["Default","WithCheckbox","WithinForm"];export{u as Default,c as WithCheckbox,m as WithinForm,ne as __namedExportsOrder,re as default};
