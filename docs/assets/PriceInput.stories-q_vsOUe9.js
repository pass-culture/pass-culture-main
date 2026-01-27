import{j as t}from"./jsx-runtime-C_uOM0Gm.js";import{R as N,r as u}from"./iframe-CTnXOULQ.js";import{C as T}from"./Checkbox-BYovAbr0.js";import{T as S}from"./TextInput-DOsfrCQI.js";import{a as W,u as U,F as D}from"./index.esm-B74CwnGv.js";import"./preload-helper-PPVm8Dsz.js";import"./index-TscbDd2H.js";import"./Asset-DEO5YOFe.js";import"./Tag-CZrfY-rG.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-CJiY4LCz.js";import"./FieldFooter-CL0tzobd.js";import"./full-error-BFAmjN4t.js";import"./index.module-DEHgy3-r.js";import"./FieldHeader-DxZ9joXq.js";import"./Tooltip-GJ5PEk5n.js";const d=N.forwardRef(({name:e,label:a,value:i,max:s,disabled:f,showFreeCheckbox:p,requiredIndicator:q="symbol",required:C=!0,error:k,description:I,currency:h="EUR",onChange:b,onBlur:P},V)=>{const g=u.useRef(null),E=`${e}.free`,x=u.useRef(null),w=i===0,[o,y]=u.useState(w),v=h==="XPF"?1:.01,R=h==="XPF"?"(en F)":"(en €)";u.useEffect(()=>{const n=document.activeElement===x.current;!o&&n&&g.current?.focus()},[o]);const j=r=>{const n=r.target.value;let F=n!==""?Number(n):void 0;p&&o&&(F=0),b?.({target:{valueAsNumber:F}}),p&&y(r.target.value==="0")},_=()=>{const r=!o;y(r);let n="";r&&(n="0"),b?.({target:{valueAsNumber:Number(n)}})},A=t.jsx(T,{ref:x,label:"Gratuit",checked:o,name:E,onChange:_,disabled:f});return t.jsx("div",{ref:V,children:t.jsx(S,{ref:g,autoComplete:"off",required:C,name:e,label:`${a} ${R}`,value:i?.toString()??"",type:"number",step:v,min:0,max:s,disabled:f,description:I,requiredIndicator:q,onChange:j,onBlur:P,onKeyDown:r=>{v===1&&/[,.]/.test(r.key)&&r.preventDefault()},error:k,...p?{extension:A}:{}})})});try{d.displayName="PriceInput",d.__docgenInfo={description:`The PriceInput component is a combination of a TextInput and a Checkbox to define prices.
It integrates with Formik for form state management and is used when an null price is meant to be interpreted as free.

---`,displayName:"PriceInput",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},name:{defaultValue:null,description:"The name of the input, mind what's being used in the form.",name:"name",required:!1,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},required:{defaultValue:{value:"true"},description:"",name:"required",required:!1,type:{name:"boolean"}},max:{defaultValue:null,description:"",name:"max",required:!1,type:{name:"string | number"}},label:{defaultValue:null,description:`A label for the input,
also used as the aria-label for the group.`,name:"label",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"A callback when the quantity changes.",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"A callback when the quantity text input is blurred.",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},value:{defaultValue:null,description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:"value",required:!1,type:{name:'number | ""'}},showFreeCheckbox:{defaultValue:null,description:'A flag to show the "Gratuit" checkbox.',name:"showFreeCheckbox",required:!1,type:{name:"boolean"}},requiredIndicator:{defaultValue:{value:"symbol"},description:"What type of required indicator is displayed",name:"requiredIndicator",required:!1,type:{name:"enum",value:[{value:'"symbol"'},{value:'"hidden"'},{value:'"explicit"'}]}},error:{defaultValue:null,description:`A custom error message to be displayed.
If this prop is provided, the error message will be displayed and the field will be marked as errored`,name:"error",required:!1,type:{name:"string"}},currency:{defaultValue:{value:"EUR"},description:"Currency to use to display currency icon",name:"currency",required:!1,type:{name:"enum",value:[{value:'"EUR"'},{value:'"XPF"'}]}}}}}catch{}const H=({children:e})=>{const a=U({defaultValues:{price:100}});return t.jsx(D,{...a,children:t.jsx("form",{children:e})})},ne={title:"@/ui-kit/forms/PriceInput",component:d},l={args:{name:"price",label:"Prix"}},c={args:{name:"price",label:"Prix",showFreeCheckbox:!0}},m={args:{name:"price",label:"Prix",currency:"EUR"},decorators:[e=>t.jsx(H,{children:t.jsx(e,{})})],render:e=>{const{setValue:a,watch:i}=W();return t.jsx(d,{...e,value:i("price"),onChange:s=>{a("price",s.target.value?Number(s.target.value):void 0)}})}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'price',
    label: 'Prix'
  }
}`,...l.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
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
}`,...m.parameters?.docs?.source}}};const ae=["Default","WithCheckbox","WithinForm"];export{l as Default,c as WithCheckbox,m as WithinForm,ae as __namedExportsOrder,ne as default};
