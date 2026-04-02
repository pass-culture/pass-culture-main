import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-DhrfSMI3.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./index.module-DUX1jt65.js";import{n as i}from"./api-DKBp4NIB.js";import{a,o,t as s}from"./index.esm-i0alUlJM.js";import{n as c,r as l,t as u}from"./index.esm-d2_mjT5L.js";import{t as d}from"./SelectAutocomplete-tdkeOXrq.js";var f=e(t(),1),p=e=>e.trim().toLowerCase().replace(/œ/g,`oe`).replace(/æ/g,`ae`).normalize(`NFD`).replace(/[^a-z0-9-\s]/g,``).replace(/\s+/g,` `),m=n(),h=400,g=5,_=(0,f.forwardRef)(({label:e,description:t,suggestionLimit:n=g,onlyTypes:a,disabled:o=!1,className:s,onAddressChosen:c,error:l,name:u,onChange:_,onBlur:v,required:y=!0},b)=>{let[x,S]=(0,f.useState)([]),C=(0,f.useRef)(new Map),w=(0,f.useRef)(null),T=(0,f.useCallback)(async e=>{if(e.trim().length<3){S([]);return}try{let t=await i(e,{limit:n,onlyTypes:a});C.current=new Map(t.map(e=>[e.label,e])),S(t.map(({label:e})=>({value:e,label:e})))}catch{C.current=new Map,S([])}},[n,a]),E=r(e=>{T(e)},h),D=e=>p(e).replace(/[^\w ]/,``);return(0,f.useEffect)(()=>{w.current?.value&&T(w.current?.value)},[]),(0,f.useImperativeHandle)(b,()=>w.current),(0,m.jsx)(d,{name:u,label:e,options:x,description:t,onSearch:e=>{E(e)},onChange:e=>{_?.(e);let t=C.current.get(e.target.value);t&&c?.(t)},onBlur:e=>{v?.(e);let t=C.current.get(e.target.value);t&&c?.(t)},searchInOptions:(e,t)=>e.filter(e=>D(t||``).split(` `).every(t=>D(e.label).includes(t))),disabled:o,className:s,ref:w,error:l,required:y})});_.displayName=`AddressSelect`;try{_.displayName=`AddressSelect`,_.__docgenInfo={description:``,displayName:`AddressSelect`,props:{name:{defaultValue:null,description:`Name of the field, used for form submission and accessibility`,name:`name`,required:!0,type:{name:`string`}},label:{defaultValue:null,description:`Label displayed above the input`,name:`label`,required:!0,type:{name:`string | Element`}},onChange:{defaultValue:null,description:`Called when the input value changes`,name:`onChange`,required:!1,type:{name:`((event: CustomEvent<"change">) => void)`}},onBlur:{defaultValue:null,description:`Called when the input loses focus`,name:`onBlur`,required:!1,type:{name:`((event: CustomEvent<"blur">) => void)`}},onAddressChosen:{defaultValue:null,description:`Called when an address is chosen from the suggestions`,name:`onAddressChosen`,required:!1,type:{name:`((data: AdresseData) => void)`}},disabled:{defaultValue:{value:`false`},description:`Disables the input and prevents interaction`,name:`disabled`,required:!1,type:{name:`boolean`}},className:{defaultValue:null,description:`Additional CSS class names`,name:`className`,required:!1,type:{name:`string`}},description:{defaultValue:null,description:`Helper text displayed below the input`,name:`description`,required:!1,type:{name:`string`}},onlyTypes:{defaultValue:null,description:`Filters the address suggestions by type (e.g., "municipality", "street")`,name:`onlyTypes`,required:!1,type:{name:`FeaturePropertyType[]`}},error:{defaultValue:null,description:`Error message to display`,name:`error`,required:!1,type:{name:`string`}},suggestionLimit:{defaultValue:{value:`5`},description:`Maximum number of address suggestions to display`,name:`suggestionLimit`,required:!1,type:{name:`number`}},required:{defaultValue:{value:`true`},description:`Indicates if the field is required`,name:`required`,required:!1,type:{name:`boolean`}}}}}catch{}var v={title:`@/ui-kit/forms/AddressSelect`,component:_},y={wrapper:{color:`#666`,fontSize:`0.8rem`,padding:`1rem`,backgroundColor:`#f5f5f5`,borderRadius:`0.2rem`,border:`thin solid #e1e1e1`,minHeight:`45px`,marginBottom:`1rem`,display:`flex`,flexDirection:`column`,alignItems:`flex-start`},pre:{display:`inline-block`,padding:`0.5rem`}},b=({children:e})=>{let t=a({defaultValues:{addressText:`19 Rue de Toulouse 30000 Nîmes`,street:`19 Rue de Toulouse`,postalCode:`30000`,city:`Nîmes`,latitude:`43.828539`,longitude:`4.375801`,inseeCode:`30000`,banId:`30189_7810_00019`},resolver:l(u().shape({addressText:c().required(`Veuillez sélectionner une adresse valide`),street:c().default(``),postalCode:c().default(``),city:c().default(``),latitude:c().default(``),longitude:c().default(``),inseeCode:c().default(``),banId:c().default(``)})),mode:`onBlur`}),[n,r,i,o,d,f,p,h]=t.watch([`street`,`city`,`postalCode`,`latitude`,`longitude`,`addressText`,`inseeCode`,`banId`]);return(0,m.jsxs)(s,{...t,children:[(0,m.jsxs)(`div`,{style:y.wrapper,children:[`Selected value in the form: `,(0,m.jsx)(`br`,{}),(0,m.jsxs)(`pre`,{style:y.pre,children:[`addressText = `,f,(0,m.jsx)(`br`,{}),`street = `,n,(0,m.jsx)(`br`,{}),`city = `,r,(0,m.jsx)(`br`,{}),`postalCode = `,i,(0,m.jsx)(`br`,{}),`latitude = `,o,(0,m.jsx)(`br`,{}),`longitude = `,d,(0,m.jsx)(`br`,{}),`inseeCode = `,p,(0,m.jsx)(`br`,{}),`banId = `,h]})]}),(0,m.jsx)(`form`,{children:e})]})},x={args:{name:`addressText`,label:`Adresse postale`}},S={args:{name:`addressText`,label:`Adresse postale`,suggestionLimit:15,ref:e=>{e&&(e.defaultValue=`8 Rue`)}}},C={args:{name:`addressText`,label:`Adresse postale`,disabled:!0}},w={args:{name:`addressText`,label:`Adresse postale`,description:`Uniquement si vous souhaitez préciser l’adresse exacte`,required:!1}},T={args:{name:`cityName`,label:`Nom de la ville`,onlyTypes:[`municipality`],suggestionLimit:50}},E={decorators:[e=>(0,m.jsx)(b,{children:(0,m.jsx)(e,{})})],render:()=>{let{setValue:e,register:t,formState:{errors:n}}=o();return(0,m.jsx)(_,{label:`Adresse postale`,...t(`addressText`),error:n.addressText?.message,onAddressChosen:t=>{e(`street`,t.address),e(`postalCode`,t.postalCode),e(`city`,t.city),e(`latitude`,String(t.latitude)),e(`longitude`,String(t.longitude)),e(`banId`,t.id),e(`inseeCode`,t.inseeCode)}})}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale'
  }
}`,...x.parameters?.docs?.source}}},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    suggestionLimit: 15,
    ref: ref => {
      if (ref) {
        ref.defaultValue = '8 Rue';
      }
    }
  }
}`,...S.parameters?.docs?.source}}},C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    disabled: true
  }
}`,...C.parameters?.docs?.source}}},w.parameters={...w.parameters,docs:{...w.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    description: 'Uniquement si vous souhaitez préciser l’adresse exacte',
    required: false
  }
}`,...w.parameters?.docs?.source}}},T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'cityName',
    label: 'Nom de la ville',
    onlyTypes: ['municipality'],
    suggestionLimit: 50
  }
}`,...T.parameters?.docs?.source}}},E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
  decorators: [(Story: any) => <FormWrapper>
        <Story />
      </FormWrapper>],
  render: () => {
    const {
      setValue,
      register,
      formState: {
        errors
      }
      // eslint-disable-next-line react-hooks/rules-of-hooks
    } = useFormContext<AddressFormValues>();
    return <AddressSelect label="Adresse postale" {...register('addressText')} error={errors.addressText?.message} onAddressChosen={addressData => {
      setValue('street', addressData.address);
      setValue('postalCode', addressData.postalCode);
      setValue('city', addressData.city);
      setValue('latitude', String(addressData.latitude));
      setValue('longitude', String(addressData.longitude));
      setValue('banId', addressData.id);
      setValue('inseeCode', addressData.inseeCode);
    }} />;
  }
}`,...E.parameters?.docs?.source}}};var D=[`Default`,`withLimitOf15Suggestions`,`Disabled`,`optionalWithDescription`,`onlyMunicipality`,`WithinFormValidation`];export{x as Default,C as Disabled,E as WithinFormValidation,D as __namedExportsOrder,v as default,T as onlyMunicipality,w as optionalWithDescription,S as withLimitOf15Suggestions};