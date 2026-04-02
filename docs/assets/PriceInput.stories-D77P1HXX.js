import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-zMGudiS2.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./TextInput-Dy9_9upv.js";import{t as i}from"./Checkbox-B3X4hqJJ.js";import{a,o,t as s}from"./index.esm-0vXoC-Ep.js";var c=e(t(),1),l=n(),u=c.forwardRef(({name:e,label:t,value:n,max:a,disabled:o,showFreeCheckbox:s,requiredIndicator:u=`symbol`,required:d=!0,error:f,description:p,currency:m=`EUR`,onChange:h,onBlur:g},_)=>{let v=(0,c.useRef)(null),y=`${e}.free`,b=(0,c.useRef)(null),[x,S]=(0,c.useState)(n===0),C=m===`XPF`?1:.01,w=m===`XPF`?`(en F)`:`(en €)`;(0,c.useEffect)(()=>{let e=document.activeElement===b.current;!x&&e&&v.current?.focus()},[x]);let T=e=>{let t=e.target.value,n=t===``?void 0:Number(t);s&&x&&(n=0),h?.({target:{valueAsNumber:n}}),s&&S(e.target.value===`0`)},E=(0,l.jsx)(i,{ref:b,label:`Gratuit`,checked:x,name:y,onChange:()=>{let e=!x;S(e);let t=``;e&&(t=`0`),h?.({target:{valueAsNumber:Number(t)}})},disabled:o});return(0,l.jsx)(`div`,{ref:_,children:(0,l.jsx)(r,{ref:v,autoComplete:`off`,required:d,name:e,label:`${t} ${w}`,value:n?.toString()??``,type:`number`,step:C,min:0,max:a,disabled:o,description:p,requiredIndicator:u,onChange:T,onBlur:g,onKeyDown:e=>{C===1&&/[,.]/.test(e.key)&&e.preventDefault()},error:f,...s?{extension:E}:{}})})});try{u.displayName=`PriceInput`,u.__docgenInfo={description:`The PriceInput component is a combination of a TextInput and a Checkbox to define prices.
It integrates with Formik for form state management and is used when an null price is meant to be interpreted as free.

---`,displayName:`PriceInput`,props:{disabled:{defaultValue:null,description:``,name:`disabled`,required:!1,type:{name:`boolean`}},name:{defaultValue:null,description:`The name of the input, mind what's being used in the form.`,name:`name`,required:!1,type:{name:`string`}},description:{defaultValue:null,description:``,name:`description`,required:!1,type:{name:`string`}},required:{defaultValue:{value:`true`},description:``,name:`required`,required:!1,type:{name:`boolean`}},max:{defaultValue:null,description:``,name:`max`,required:!1,type:{name:`string | number`}},label:{defaultValue:null,description:`A label for the input,
also used as the aria-label for the group.`,name:`label`,required:!0,type:{name:`string`}},onChange:{defaultValue:null,description:`A callback when the quantity changes.`,name:`onChange`,required:!1,type:{name:`ChangeEventHandler<HTMLInputElement, HTMLInputElement>`}},onBlur:{defaultValue:null,description:`A callback when the quantity text input is blurred.`,name:`onBlur`,required:!1,type:{name:`FocusEventHandler<HTMLInputElement>`}},value:{defaultValue:null,description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:`value`,required:!1,type:{name:`number | ""`}},showFreeCheckbox:{defaultValue:null,description:`A flag to show the "Gratuit" checkbox.`,name:`showFreeCheckbox`,required:!1,type:{name:`boolean`}},requiredIndicator:{defaultValue:{value:`symbol`},description:`What type of required indicator is displayed`,name:`requiredIndicator`,required:!1,type:{name:`enum`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}},error:{defaultValue:null,description:`A custom error message to be displayed.
If this prop is provided, the error message will be displayed and the field will be marked as errored`,name:`error`,required:!1,type:{name:`string`}},currency:{defaultValue:{value:`EUR`},description:`Currency to use to display currency icon`,name:`currency`,required:!1,type:{name:`enum`,value:[{value:`"EUR"`},{value:`"XPF"`}]}}}}}catch{}var d=({children:e})=>(0,l.jsx)(s,{...a({defaultValues:{price:100}}),children:(0,l.jsx)(`form`,{children:e})}),f={title:`@/ui-kit/forms/PriceInput`,component:u},p={args:{name:`price`,label:`Prix`}},m={args:{name:`price`,label:`Prix`,showFreeCheckbox:!0}},h={args:{name:`price`,label:`Prix`,currency:`EUR`},decorators:[e=>(0,l.jsx)(d,{children:(0,l.jsx)(e,{})})],render:e=>{let{setValue:t,watch:n}=o();return(0,l.jsx)(u,{...e,value:n(`price`),onChange:e=>{t(`price`,e.target.value?Number(e.target.value):void 0)}})}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'price',
    label: 'Prix'
  }
}`,...p.parameters?.docs?.source}}},m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'price',
    label: 'Prix',
    showFreeCheckbox: true
  }
}`,...m.parameters?.docs?.source}}},h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
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
}`,...h.parameters?.docs?.source}}};var g=[`Default`,`WithCheckbox`,`WithinForm`];export{p as Default,m as WithCheckbox,h as WithinForm,g as __namedExportsOrder,f as default};