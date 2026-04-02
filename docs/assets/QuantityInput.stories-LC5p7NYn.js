import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-CFgoRN3L.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./TextInput-xCR8fxat.js";import{t as i}from"./Checkbox-D6c8xwQR.js";import{a,o,t as s}from"./index.esm-D1mpJ_zV.js";var c=e(t(),1),l=n(),u=({label:e=`Quantité`,name:t=`quantity`,onChange:n,onBlur:a,disabled:o,required:s,requiredIndicator:u,min:d=0,max:f=1e6,value:p,error:m,ariaLabel:h})=>{let g=t,_=(0,c.useRef)(null),v=`${t}.unlimited`,y=(0,c.useRef)(null),b=p!==0&&!p,[x,S]=(0,c.useState)(b);return(0,c.useEffect)(()=>{let e=document.activeElement===y.current;!x&&e&&_.current?.focus()},[x]),(0,c.useEffect)(()=>{x!==b&&S(b)},[b]),(0,l.jsx)(r,{ref:_,name:g,label:e,required:s,requiredIndicator:u,disabled:o,type:`number`,min:d,max:f,step:1,extension:(0,l.jsx)(i,{ref:y,label:`Illimité`,name:v,onChange:()=>{let e=`${d}`;x||(e=``),n?.({target:{value:e}}),_.current&&(_.current.value=e),S(e=>!e)},checked:x,disabled:o}),onChange:e=>{e.target.value&&/[,.]/.test(e.target.value)&&(e.target.value=e.target.value.split(`.`)[0].split(`,`)[0]),n?.(e),S(e.target.value===``)},onBlur:a,value:x?``:p?.toString()??``,error:m,"aria-label":h})};try{u.displayName=`QuantityInput`,u.__docgenInfo={description:`The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
An undefined quantity is meant to be interpreted as unlimited.`,displayName:`QuantityInput`,props:{disabled:{defaultValue:null,description:``,name:`disabled`,required:!1,type:{name:`boolean`}},required:{defaultValue:null,description:``,name:`required`,required:!1,type:{name:`boolean`}},requiredIndicator:{defaultValue:null,description:``,name:`requiredIndicator`,required:!1,type:{name:`enum`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}},label:{defaultValue:{value:`Quantité`},description:`A label for the text input.`,name:`label`,required:!1,type:{name:`string`}},name:{defaultValue:{value:`quantity`},description:`The name of the input, mind what's being used in the form.`,name:`name`,required:!1,type:{name:`string`}},onChange:{defaultValue:null,description:`A callback when the quantity changes.`,name:`onChange`,required:!1,type:{name:`ChangeEventHandler<HTMLInputElement, HTMLInputElement>`}},onBlur:{defaultValue:null,description:`A callback when the quantity text input is blurred.`,name:`onBlur`,required:!1,type:{name:`FocusEventHandler<HTMLInputElement>`}},value:{defaultValue:null,description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:`value`,required:!1,type:{name:`number | null`}},min:{defaultValue:{value:`0`},description:`The minimum value allowed for the quantity. Make sure it matches validation schema.`,name:`min`,required:!1,type:{name:`number`}},max:{defaultValue:{value:`1000000`},description:`The maximum value allowed for the quantity. Make sure it matches validation schema.`,name:`max`,required:!1,type:{name:`number`}},error:{defaultValue:null,description:``,name:`error`,required:!1,type:{name:`string`}},ariaLabel:{defaultValue:null,description:``,name:`ariaLabel`,required:!1,type:{name:`string`}}}}}catch{}var d=({children:e})=>(0,l.jsx)(s,{...a({defaultValues:{myField:100}}),children:(0,l.jsx)(`form`,{children:e})}),f={title:`@/ui-kit/forms/QuantityInput`,component:u},p={args:{name:`quantity`,label:`Quantité`}},m={args:{name:`quantity`,label:`Quantité`,required:!0}},h={args:{name:`quantity`,label:`Quantity`,min:10},decorators:[e=>(0,l.jsx)(d,{children:(0,l.jsx)(e,{})})],render:e=>{let{setValue:t,watch:n}=o();return(0,l.jsx)(u,{...e,value:n(`myField`),onChange:e=>{t(`myField`,e.target.value?Number(e.target.value):void 0)}})}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité'
  }
}`,...p.parameters?.docs?.source}}},m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    required: true
  }
}`,...m.parameters?.docs?.source}}},h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
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
}`,...h.parameters?.docs?.source}}};var g=[`Default`,`Required`,`WithinForm`];export{p as Default,m as Required,h as WithinForm,g as __namedExportsOrder,f as default};