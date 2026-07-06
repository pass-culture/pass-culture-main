import{i as e,s as t}from"./preload-helper-xPQekRTU.js";import{C as n}from"./iframe-BCMqugAg.js";import{t as r}from"./jsx-runtime-CaZkqeYb.js";import{n as i,t as a}from"./TextInput-CBF-mEqQ.js";import{n as o,t as s}from"./Checkbox-BGseY5Mp.js";import{i as c,o as l,s as u,t as d}from"./index.esm-CS4hCA_n.js";var f,p,m,h=e((()=>{f=t(n(),1),o(),i(),p=r(),m=f.forwardRef(({name:e,label:t,disabled:n,requiredIndicator:r=`symbol`,required:i=!0,error:o,max:c,description:l,currency:u=`EUR`,value:d,showFreeCheckbox:m,onChange:h,onBlur:g},_)=>{let v=(0,f.useRef)(null),y=`${e}.free`,b=d===0||d===`0`,x=u===`XPF`?1:.01,S=u===`XPF`?`(en F)`:`(en €)`,C=(0,p.jsx)(s,{ref:v,label:`Gratuit`,checked:b,name:y,onChange:t=>{let n=t.target.checked?0:``;h?.({...t,target:{...t.target,name:e,value:n}})},disabled:n});return(0,p.jsx)(a,{ref:_,name:e,disabled:n||b,label:`${t} ${S}`,error:o,step:x,min:0,max:c,type:`number`,required:i,description:l,requiredIndicator:r,autoComplete:`off`,onChange:h,onBlur:g,onKeyDown:e=>{x===1&&/[,.]/.test(e.key)&&e.preventDefault()},...m?{extension:C}:{}},String(b))});try{m.displayName=`PriceInput`,m.__docgenInfo={description:`The PriceInput component is a combination of a TextInput and a Checkbox to define prices.
It integrates with Formik for form state management and is used when an null price is meant to be interpreted as free.

---`,displayName:`PriceInput`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/form/PriceInput/PriceInput.tsx`,methods:[],props:{disabled:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/TextInput/TextInput.tsx`,name:`TypeLiteral`}],description:``,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},name:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/TextInput/TextInput.tsx`,name:`TypeLiteral`},{fileName:`pro/src/ui-kit/form/PriceInput/PriceInput.tsx`,name:`TypeLiteral`}],description:`The name of the input, mind what's being used in the form.`,name:`name`,required:!1,tags:{},type:{name:`string`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/TextInput/TextInput.tsx`,name:`TypeLiteral`},{fileName:`pro/src/ui-kit/form/PriceInput/PriceInput.tsx`,name:`TypeLiteral`}],description:``,name:`description`,required:!1,tags:{},type:{name:`string`}},required:{defaultValue:{value:`true`},declarations:[{fileName:`pro/src/design-system/TextInput/TextInput.tsx`,name:`TypeLiteral`}],description:``,name:`required`,required:!1,tags:{},type:{name:`boolean`}},max:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/TextInput/TextInput.tsx`,name:`TypeLiteral`}],description:``,name:`max`,required:!1,tags:{},type:{name:`string | number`}},label:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/PriceInput/PriceInput.tsx`,name:`TypeLiteral`}],description:`A label for the input,
also used as the aria-label for the group.`,name:`label`,required:!0,tags:{},type:{name:`string`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/PriceInput/PriceInput.tsx`,name:`TypeLiteral`}],description:`A callback when the quantity changes.`,name:`onChange`,required:!1,tags:{},type:{name:`ChangeEventHandler<HTMLInputElement, HTMLInputElement>`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/PriceInput/PriceInput.tsx`,name:`TypeLiteral`}],description:`A callback when the quantity text input is blurred.`,name:`onBlur`,required:!1,tags:{},type:{name:`FocusEventHandler<HTMLInputElement>`}},value:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/PriceInput/PriceInput.tsx`,name:`TypeLiteral`}],description:"The quantity value. Should be `undefined` if the quantity is unlimited.",name:`value`,required:!1,tags:{},type:{name:`string | number | null`}},showFreeCheckbox:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/PriceInput/PriceInput.tsx`,name:`TypeLiteral`}],description:`A flag to show the "Gratuit" checkbox.`,name:`showFreeCheckbox`,required:!1,tags:{},type:{name:`boolean`}},requiredIndicator:{defaultValue:{value:`symbol`},declarations:[{fileName:`pro/src/ui-kit/form/PriceInput/PriceInput.tsx`,name:`TypeLiteral`}],description:`What type of required indicator is displayed`,name:`requiredIndicator`,required:!1,tags:{},type:{name:`enum`,raw:`RequiredIndicator`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}},error:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/PriceInput/PriceInput.tsx`,name:`TypeLiteral`}],description:`A custom error message to be displayed.
If this prop is provided, the error message will be displayed and the field will be marked as errored`,name:`error`,required:!1,tags:{},type:{name:`string`}},currency:{defaultValue:{value:`EUR`},declarations:[{fileName:`pro/src/ui-kit/form/PriceInput/PriceInput.tsx`,name:`TypeLiteral`}],description:`Currency to use to display currency icon`,name:`currency`,required:!1,tags:{default:`EUR`},type:{name:`enum`,raw:`Currency`,value:[{value:`"EUR"`},{value:`"XPF"`}]}}},tags:{param:`props - The props for the PriceInput component.`,returns:`The rendered PriceInput component.`,example:`<PriceInput
 label="Price"
 name="price"
 max={100}
/>`}}}catch{}})),g,_,v,y,b,x,S;e((()=>{h(),c(),g=r(),_=({children:e})=>(0,g.jsx)(d,{...l({defaultValues:{price:100}}),children:(0,g.jsx)(`form`,{children:e})}),v={title:`@/ui-kit/forms/PriceInput`,component:m},y={args:{name:`price`,label:`Prix`}},b={args:{name:`price`,label:`Prix`,showFreeCheckbox:!0}},x={args:{name:`price`,label:`Prix`,currency:`EUR`},decorators:[e=>(0,g.jsx)(_,{children:(0,g.jsx)(e,{})})],render:e=>{let{setValue:t,watch:n}=u();return(0,g.jsx)(m,{...e,value:n(`price`),onChange:e=>{t(`price`,e.target.value?Number(e.target.value):void 0)}})}},y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'price',
    label: 'Prix'
  }
}`,...y.parameters?.docs?.source}}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'price',
    label: 'Prix',
    showFreeCheckbox: true
  }
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'price',
    label: 'Prix',
    currency: 'EUR'
  },
  decorators: [(Story: any) => <Wrapper>
        <Story />
      </Wrapper>],
  render: (args: any) => {
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
}`,...x.parameters?.docs?.source}}},S=[`Default`,`WithCheckbox`,`WithinForm`]}))();export{y as Default,b as WithCheckbox,x as WithinForm,S as __namedExportsOrder,v as default};