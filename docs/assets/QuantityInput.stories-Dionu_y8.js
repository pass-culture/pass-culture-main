import{a as e,n as t}from"./chunk-DnJy8xQt.js";import{S as n}from"./iframe-XvC5t-WH.js";import{t as r}from"./jsx-runtime-BGU0mfus.js";import{n as i,t as a}from"./TextInput-WfYiVbmS.js";import{n as o,t as s}from"./Checkbox-E-ZBQHHM.js";import{i as c,o as l,s as u,t as d}from"./index.esm-D6XZZnsd.js";var f,p,m,h=t((()=>{f=e(n(),1),o(),i(),p=r(),m=({label:e=`Quantité`,name:t=`quantity`,onChange:n,onBlur:r,disabled:i,required:o,requiredIndicator:c,min:l=0,max:u=1e6,value:d,error:m,ariaLabel:h})=>{let g=t,_=(0,f.useRef)(null),v=`${t}.unlimited`,y=(0,f.useRef)(null),b=d!==0&&!d,[x,S]=(0,f.useState)(b);return(0,f.useEffect)(()=>{let e=document.activeElement===y.current;!x&&e&&_.current?.focus()},[x]),(0,f.useEffect)(()=>{x!==b&&S(b)},[b]),(0,p.jsx)(a,{ref:_,name:g,label:e,required:o,requiredIndicator:c,disabled:i,type:`number`,min:l,max:u,step:1,extension:(0,p.jsx)(s,{ref:y,label:`Illimité`,name:v,onChange:()=>{let e=`${l}`;x||(e=``),n?.({target:{value:e}}),_.current&&(_.current.value=e),S(e=>!e)},checked:x,disabled:i}),onChange:e=>{e.target.value&&/[,.]/.test(e.target.value)&&(e.target.value=e.target.value.split(`.`)[0].split(`,`)[0]),n?.(e),S(e.target.value===``)},onBlur:r,value:x?``:d?.toString()??``,error:m,"aria-label":h})};try{m.displayName=`QuantityInput`,m.__docgenInfo={description:`The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
An undefined quantity is meant to be interpreted as unlimited.`,displayName:`QuantityInput`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,methods:[],props:{disabled:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/TextInput/TextInput.tsx`,name:`TypeLiteral`}],description:``,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},required:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/TextInput/TextInput.tsx`,name:`TypeLiteral`}],description:``,name:`required`,required:!1,tags:{},type:{name:`boolean`}},requiredIndicator:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/TextInput/TextInput.tsx`,name:`TypeLiteral`}],description:``,name:`requiredIndicator`,required:!1,tags:{},type:{name:`enum`,raw:`RequiredIndicator`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}},label:{defaultValue:{value:`Quantité`},declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:`A label for the text input.`,name:`label`,required:!1,tags:{},type:{name:`string`}},name:{defaultValue:{value:`quantity`},declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:`The name of the input, mind what's being used in the form.`,name:`name`,required:!1,tags:{},type:{name:`string`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:`A callback when the quantity changes.`,name:`onChange`,required:!1,tags:{},type:{name:`ChangeEventHandler<HTMLInputElement, HTMLInputElement>`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:`A callback when the quantity text input is blurred.`,name:`onBlur`,required:!1,tags:{},type:{name:`FocusEventHandler<HTMLInputElement>`}},value:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:`value`,required:!1,tags:{},type:{name:`number | null`}},min:{defaultValue:{value:`0`},declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:`The minimum value allowed for the quantity. Make sure it matches validation schema.`,name:`min`,required:!1,tags:{},type:{name:`number`}},max:{defaultValue:{value:`1000000`},declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:`The maximum value allowed for the quantity. Make sure it matches validation schema.`,name:`max`,required:!1,tags:{},type:{name:`number`}},error:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:``,name:`error`,required:!1,tags:{},type:{name:`string`}},ariaLabel:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/QuantityInput/QuantityInput.tsx`,name:`TypeLiteral`}],description:``,name:`ariaLabel`,required:!1,tags:{},type:{name:`string`}}},tags:{example:`<QuantityInput
  label="Quantity"
  name="quantity"
  min={0}
  onChange={(value) => console.log(value)}
/>`}}}catch{}})),g,_,v,y,b,x,S;t((()=>{c(),h(),g=r(),_=({children:e})=>(0,g.jsx)(d,{...l({defaultValues:{myField:100}}),children:(0,g.jsx)(`form`,{children:e})}),v={title:`@/ui-kit/forms/QuantityInput`,component:m},y={args:{name:`quantity`,label:`Quantité`}},b={args:{name:`quantity`,label:`Quantité`,required:!0}},x={args:{name:`quantity`,label:`Quantity`,min:10},decorators:[e=>(0,g.jsx)(_,{children:(0,g.jsx)(e,{})})],render:e=>{let{setValue:t,watch:n}=u();return(0,g.jsx)(m,{...e,value:n(`myField`),onChange:e=>{t(`myField`,e.target.value?Number(e.target.value):void 0)}})}},y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité'
  }
}`,...y.parameters?.docs?.source}}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'quantity',
    label: 'Quantité',
    required: true
  }
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
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
}`,...x.parameters?.docs?.source}}},S=[`Default`,`Required`,`WithinForm`]}))();export{y as Default,b as Required,x as WithinForm,S as __namedExportsOrder,v as default};