import{n as e}from"./rolldown-runtime-DkW27tQK.js";import{d as t}from"./iframe-DuB9xBT3.js";import{t as n}from"./jsx-runtime-DeHZSEgm.js";import{n as r,t as i}from"./TextInput-DjFf3tOv.js";import{n as a,t as o}from"./Checkbox-BR0dNGcU.js";import{i as s,o as c,s as l,t as u}from"./index.esm-CXnKW2PB.js";var d,f,p;function m(){return(m=e((()=>{d=t(),a(),r(),f=n(),p=({label:e=`Quantité`,name:t=`quantity`,onChange:n,onBlur:r,disabled:a,required:s,requiredIndicator:c,min:l=0,max:u=1e6,value:p,error:m,ariaLabel:h})=>{let g=t,_=(0,d.useRef)(null),v=`${t}.unlimited`,y=(0,d.useRef)(null),b=p!==0&&!p,[x,S]=(0,d.useState)(b);return(0,d.useEffect)(()=>{let e=document.activeElement===y.current;!x&&e&&_.current?.focus()},[x]),(0,d.useEffect)(()=>{x!==b&&S(b)},[b]),(0,f.jsx)(i,{ref:_,name:g,label:e,required:s,requiredIndicator:c,disabled:a,type:`number`,min:l,max:u,step:1,extension:(0,f.jsx)(o,{ref:y,label:`Illimité`,name:v,onChange:()=>{let e=`${l}`;x||(e=``),n?.({target:{value:e}}),_.current&&(_.current.value=e),S(e=>!e)},checked:x,disabled:a}),onChange:e=>{e.target.value&&/[,.]/.test(e.target.value)&&(e.target.value=e.target.value.split(`.`)[0].split(`,`)[0]),n?.(e),S(e.target.value===``)},onBlur:r,value:x?``:p?.toString()??``,error:m,"aria-label":h})};try{p.displayName=`QuantityInput`,p.__docgenInfo={description:`The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
An undefined quantity is meant to be interpreted as unlimited.`,displayName:`QuantityInput`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,methods:[],props:{disabled:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/TextInput/TextInput.tsx`,name:`TypeLiteral`}],description:``,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},required:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/TextInput/TextInput.tsx`,name:`TypeLiteral`}],description:``,name:`required`,required:!1,tags:{},type:{name:`boolean`}},requiredIndicator:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/TextInput/TextInput.tsx`,name:`TypeLiteral`}],description:``,name:`requiredIndicator`,required:!1,tags:{},type:{name:`enum`,raw:`RequiredIndicator`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}},label:{defaultValue:{value:`Quantité`},declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:`A label for the text input.`,name:`label`,required:!1,tags:{},type:{name:`string`}},name:{defaultValue:{value:`quantity`},declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:`The name of the input, mind what's being used in the form.`,name:`name`,required:!1,tags:{},type:{name:`string`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:`A callback when the quantity changes.`,name:`onChange`,required:!1,tags:{},type:{name:`ChangeEventHandler<HTMLInputElement, HTMLInputElement>`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:`A callback when the quantity text input is blurred.`,name:`onBlur`,required:!1,tags:{},type:{name:`FocusEventHandler<HTMLInputElement>`}},value:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:`value`,required:!1,tags:{},type:{name:`number | null`}},min:{defaultValue:{value:`0`},declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:`The minimum value allowed for the quantity. Make sure it matches validation schema.`,name:`min`,required:!1,tags:{},type:{name:`number`}},max:{defaultValue:{value:`1000000`},declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:`The maximum value allowed for the quantity. Make sure it matches validation schema.`,name:`max`,required:!1,tags:{},type:{name:`number`}},error:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:``,name:`error`,required:!1,tags:{},type:{name:`string`}},ariaLabel:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:``,name:`ariaLabel`,required:!1,tags:{},type:{name:`string`}}},tags:{example:`<QuantityInput
  label="Quantity"
  name="quantity"
  min={0}
  onChange={(value) => console.log(value)}
/>`}}}catch{}})))()}var h,g,_,v,y,b,x;function S(){return(S=e((()=>{s(),m(),h=n(),g=({children:e})=>{let t=c({defaultValues:{myField:100}});return(0,h.jsx)(u,{...t,children:(0,h.jsx)(`form`,{children:e})})},_={title:`@/ui-kit/forms/QuantityInput`,component:p},v={args:{name:`quantity`,label:`Quantité`}},y={args:{name:`quantity`,label:`Quantité`,required:!0}},b={args:{name:`quantity`,label:`Quantity`,min:10},decorators:[e=>(0,h.jsx)(g,{children:(0,h.jsx)(e,{})})],render:e=>{let{setValue:t,watch:n}=l();return(0,h.jsx)(p,{...e,value:n(`myField`),onChange:e=>{t(`myField`,e.target.value?Number(e.target.value):void 0)}})}},v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité'
  }
}`,...v.parameters?.docs?.source}}},y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    required: true
  }
}`,...y.parameters?.docs?.source}}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantity',
    min: 10
  },
  decorators: [(Story: any) => <Wrapper>
        <Story />
      </Wrapper>],
  render: (args: any) => {
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
}`,...b.parameters?.docs?.source}}},x=[`Default`,`Required`,`WithinForm`]})))()}S();export{v as Default,y as Required,b as WithinForm,x as __namedExportsOrder,_ as default};