import{n as e}from"./rolldown-runtime-sJBDdmOt.js";import{f as t}from"./iframe-DDrY5Qix.js";import{t as n}from"./jsx-runtime-MKhVqBIO.js";import{n as r,t as i}from"./index.module-8q3bxDlY.js";import{n as a,r as o}from"./api-DtK7FMij.js";import{i as s,o as c,s as l,t as u}from"./index.esm-CLY0JHf6.js";import{a as d,i as f,n as p,r as m,t as h}from"./index.esm-CxmdVlrZ.js";import{n as g,t as _}from"./SelectAutocomplete-Bbk0RcPf.js";var v;function y(){return(y=e((()=>{v=e=>e.trim().toLowerCase().replace(/œ/g,`oe`).replace(/æ/g,`ae`).normalize(`NFD`).replace(/[^a-z0-9-\s]/g,``).replace(/\s+/g,` `)})))()}var b,x,S,C,w;function T(){return(T=e((()=>{b=t(),s(),r(),a(),y(),g(),x=n(),S=400,C=5,w=(0,b.forwardRef)(({label:e,description:t,suggestionLimit:n=C,onlyTypes:r,disabled:a=!1,className:s,onAddressChosen:c,error:u,name:d,onChange:f,onBlur:p,required:m=!0,requiredIndicator:h=`symbol`},g)=>{let y=l(),[w,T]=(0,b.useState)([]),E=(0,b.useRef)(new Map),D=(0,b.useRef)(null),O=(0,b.useCallback)(async e=>{if(e.trim().length<3)T([]);else try{let t=await o(e,{limit:n,onlyTypes:r});E.current=new Map(t.map(e=>[e.label,e])),T(t.map(({label:e})=>({value:e,label:e})))}catch{E.current=new Map,T([])}},[n,r]),k=i(e=>{O(e)},S),A=e=>v(e).replace(/[^\w ]/,``);return(0,b.useEffect)(()=>{D.current?.value&&O(D.current?.value)},[]),(0,b.useImperativeHandle)(g,()=>D.current),(0,x.jsx)(_,{name:d,label:e,options:w,description:t,onSearch:e=>{k(e)},onChange:e=>{f?.(e),y?.trigger(d);let t=E.current.get(e.target.value);t&&c?.(t)},onBlur:e=>{p?.(e);let t=E.current.get(e.target.value);t&&c?.(t)},searchInOptions:(e,t)=>e.filter(e=>A(t||``).split(` `).every(t=>A(e.label).includes(t))),disabled:a,className:s,ref:D,error:u,required:m,requiredIndicator:h})}),w.displayName=`AddressSelect`;try{w.displayName=`AddressSelect`,w.__docgenInfo={description:``,displayName:`AddressSelect`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,methods:[],props:{name:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Name of the field, used for form submission and accessibility`,name:`name`,required:!0,tags:{},type:{name:`string`}},label:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Label displayed above the input`,name:`label`,required:!0,tags:{},type:{name:`string | Element`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Called when the input value changes`,name:`onChange`,required:!1,tags:{},type:{name:`((event: CustomEvent<"change">) => void)`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Called when the input loses focus`,name:`onBlur`,required:!1,tags:{},type:{name:`((event: CustomEvent<"blur">) => void)`}},onAddressChosen:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Called when an address is chosen from the suggestions`,name:`onAddressChosen`,required:!1,tags:{},type:{name:`((data: AdresseData) => void)`}},disabled:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Disables the input and prevents interaction`,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},className:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Additional CSS class names`,name:`className`,required:!1,tags:{},type:{name:`string`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Helper text displayed below the input`,name:`description`,required:!1,tags:{},type:{name:`string`}},onlyTypes:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Filters the address suggestions by type (e.g., "municipality", "street")`,name:`onlyTypes`,required:!1,tags:{},type:{name:`FeaturePropertyType[]`}},error:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Error message to display`,name:`error`,required:!1,tags:{},type:{name:`string`}},suggestionLimit:{defaultValue:{value:`5`},declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Maximum number of address suggestions to display`,name:`suggestionLimit`,required:!1,tags:{},type:{name:`number`}},required:{defaultValue:{value:`true`},declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Indicates if the field is required`,name:`required`,required:!1,tags:{},type:{name:`boolean`}},requiredIndicator:{defaultValue:{value:`symbol`},declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:``,name:`requiredIndicator`,required:!1,tags:{},type:{name:`enum`,raw:`RequiredIndicator`,value:[{value:`"symbol"`},{value:`"explicit"`},{value:`"hidden"`}]}}},tags:{}}}catch{}})))()}var E,D,O,k,A,j,M,N,P,F,I;function L(){return(L=e((()=>{f(),s(),m(),T(),E=n(),D={title:`@/ui-kit/forms/AddressSelect`,component:w},O={wrapper:{color:`#666`,fontSize:`0.8rem`,padding:`1rem`,backgroundColor:`#f5f5f5`,borderRadius:`0.2rem`,border:`thin solid #e1e1e1`,minHeight:`45px`,marginBottom:`1rem`,display:`flex`,flexDirection:`column`,alignItems:`flex-start`},pre:{display:`inline-block`,padding:`0.5rem`}},k=({children:e})=>{let t=c({defaultValues:{addressText:`19 Rue de Toulouse 30000 Nîmes`,street:`19 Rue de Toulouse`,postalCode:`30000`,city:`Nîmes`,latitude:`43.828539`,longitude:`4.375801`,inseeCode:`30000`,banId:`30189_7810_00019`},resolver:d(h().shape({addressText:p().required(`Veuillez sélectionner une adresse valide`),street:p().default(``),postalCode:p().default(``),city:p().default(``),latitude:p().default(``),longitude:p().default(``),inseeCode:p().default(``),banId:p().default(``)})),mode:`onBlur`}),[n,r,i,a,o,s,l,f]=t.watch([`street`,`city`,`postalCode`,`latitude`,`longitude`,`addressText`,`inseeCode`,`banId`]);return(0,E.jsxs)(u,{...t,children:[(0,E.jsxs)(`div`,{style:O.wrapper,children:[`Selected value in the form: `,(0,E.jsx)(`br`,{}),(0,E.jsxs)(`pre`,{style:O.pre,children:[`addressText = `,s,(0,E.jsx)(`br`,{}),`street = `,n,(0,E.jsx)(`br`,{}),`city = `,r,(0,E.jsx)(`br`,{}),`postalCode = `,i,(0,E.jsx)(`br`,{}),`latitude = `,a,(0,E.jsx)(`br`,{}),`longitude = `,o,(0,E.jsx)(`br`,{}),`inseeCode = `,l,(0,E.jsx)(`br`,{}),`banId = `,f]})]}),(0,E.jsx)(`form`,{children:e})]})},A={args:{name:`addressText`,label:`Adresse postale`}},j={args:{name:`addressText`,label:`Adresse postale`,suggestionLimit:15,ref:e=>{e&&(e.defaultValue=`8 Rue`)}}},M={args:{name:`addressText`,label:`Adresse postale`,disabled:!0}},N={args:{name:`addressText`,label:`Adresse postale`,description:`Uniquement si vous souhaitez préciser l’adresse exacte`,required:!1}},P={args:{name:`cityName`,label:`Nom de la ville`,onlyTypes:[`municipality`],suggestionLimit:50}},F={decorators:[e=>(0,E.jsx)(k,{children:(0,E.jsx)(e,{})})],render:()=>{let{setValue:e,register:t,formState:{errors:n}}=l();return(0,E.jsx)(w,{label:`Adresse postale`,...t(`addressText`),error:n.addressText?.message,onAddressChosen:t=>{e(`street`,t.address),e(`postalCode`,t.postalCode),e(`city`,t.city),e(`latitude`,String(t.latitude)),e(`longitude`,String(t.longitude)),e(`banId`,t.id),e(`inseeCode`,t.inseeCode)}})}},I=[`Default`,`withLimitOf15Suggestions`,`Disabled`,`optionalWithDescription`,`onlyMunicipality`,`WithinFormValidation`],A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale'
  }
}`,...A.parameters?.docs?.source}}},j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
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
}`,...j.parameters?.docs?.source}}},M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    disabled: true
  }
}`,...M.parameters?.docs?.source}}},N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    description: 'Uniquement si vous souhaitez préciser l’adresse exacte',
    required: false
  }
}`,...N.parameters?.docs?.source}}},P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'cityName',
    label: 'Nom de la ville',
    onlyTypes: ['municipality'],
    suggestionLimit: 50
  }
}`,...P.parameters?.docs?.source}}},F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
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
}`,...F.parameters?.docs?.source}}}})))()}L();export{A as Default,M as Disabled,F as WithinFormValidation,I as __namedExportsOrder,D as default,P as onlyMunicipality,N as optionalWithDescription,j as withLimitOf15Suggestions};