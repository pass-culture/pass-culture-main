import{i as e,s as t}from"./preload-helper-xPQekRTU.js";import{C as n}from"./iframe-BT7z-H6_.js";import{t as r}from"./jsx-runtime-CaZkqeYb.js";import{n as i,t as a}from"./index.module-BO2wPZaB.js";import{n as o,r as s}from"./api-B1XcSlQm.js";import{i as c,o as l,s as u,t as d}from"./index.esm-CgV7v29j.js";import{a as f,i as p,n as m,r as h,t as g}from"./index.esm-DIPWMN1O.js";import{n as _,t as v}from"./SelectAutocomplete-BdW87-mi.js";var y,b=e((()=>{y=e=>e.trim().toLowerCase().replace(/œ/g,`oe`).replace(/æ/g,`ae`).normalize(`NFD`).replace(/[^a-z0-9-\s]/g,``).replace(/\s+/g,` `)})),x,S,C,w,T,E=e((()=>{x=t(n(),1),c(),i(),o(),b(),_(),S=r(),C=400,w=5,T=(0,x.forwardRef)(({label:e,description:t,suggestionLimit:n=w,onlyTypes:r,disabled:i=!1,className:o,onAddressChosen:c,error:l,name:d,onChange:f,onBlur:p,required:m=!0,requiredIndicator:h=`symbol`},g)=>{let _=u(),[b,T]=(0,x.useState)([]),E=(0,x.useRef)(new Map),D=(0,x.useRef)(null),O=(0,x.useCallback)(async e=>{if(e.trim().length<3){T([]);return}try{let t=await s(e,{limit:n,onlyTypes:r});E.current=new Map(t.map(e=>[e.label,e])),T(t.map(({label:e})=>({value:e,label:e})))}catch{E.current=new Map,T([])}},[n,r]),k=a(e=>{O(e)},C),A=e=>y(e).replace(/[^\w ]/,``);return(0,x.useEffect)(()=>{D.current?.value&&O(D.current?.value)},[]),(0,x.useImperativeHandle)(g,()=>D.current),(0,S.jsx)(v,{name:d,label:e,options:b,description:t,onSearch:e=>{k(e)},onChange:e=>{f?.(e),_?.trigger(d);let t=E.current.get(e.target.value);t&&c?.(t)},onBlur:e=>{p?.(e);let t=E.current.get(e.target.value);t&&c?.(t)},searchInOptions:(e,t)=>e.filter(e=>A(t||``).split(` `).every(t=>A(e.label).includes(t))),disabled:i,className:o,ref:D,error:l,required:m,requiredIndicator:h})}),T.displayName=`AddressSelect`;try{T.displayName=`AddressSelect`,T.__docgenInfo={description:``,displayName:`AddressSelect`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,methods:[],props:{name:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Name of the field, used for form submission and accessibility`,name:`name`,required:!0,tags:{},type:{name:`string`}},label:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Label displayed above the input`,name:`label`,required:!0,tags:{},type:{name:`string | Element`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Called when the input value changes`,name:`onChange`,required:!1,tags:{},type:{name:`((event: CustomEvent<"change">) => void)`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Called when the input loses focus`,name:`onBlur`,required:!1,tags:{},type:{name:`((event: CustomEvent<"blur">) => void)`}},onAddressChosen:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Called when an address is chosen from the suggestions`,name:`onAddressChosen`,required:!1,tags:{},type:{name:`((data: AdresseData) => void)`}},disabled:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Disables the input and prevents interaction`,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},className:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Additional CSS class names`,name:`className`,required:!1,tags:{},type:{name:`string`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Helper text displayed below the input`,name:`description`,required:!1,tags:{},type:{name:`string`}},onlyTypes:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Filters the address suggestions by type (e.g., "municipality", "street")`,name:`onlyTypes`,required:!1,tags:{},type:{name:`FeaturePropertyType[]`}},error:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Error message to display`,name:`error`,required:!1,tags:{},type:{name:`string`}},suggestionLimit:{defaultValue:{value:`5`},declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Maximum number of address suggestions to display`,name:`suggestionLimit`,required:!1,tags:{},type:{name:`number`}},required:{defaultValue:{value:`true`},declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Indicates if the field is required`,name:`required`,required:!1,tags:{},type:{name:`boolean`}},requiredIndicator:{defaultValue:{value:`symbol`},declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:``,name:`requiredIndicator`,required:!1,tags:{},type:{name:`enum`,raw:`RequiredIndicator`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}}},tags:{}}}catch{}})),D,O,k,A,j,M,N,P,F,I,L;e((()=>{p(),c(),h(),E(),D=r(),O={title:`@/ui-kit/forms/AddressSelect`,component:T},k={wrapper:{color:`#666`,fontSize:`0.8rem`,padding:`1rem`,backgroundColor:`#f5f5f5`,borderRadius:`0.2rem`,border:`thin solid #e1e1e1`,minHeight:`45px`,marginBottom:`1rem`,display:`flex`,flexDirection:`column`,alignItems:`flex-start`},pre:{display:`inline-block`,padding:`0.5rem`}},A=({children:e})=>{let t=l({defaultValues:{addressText:`19 Rue de Toulouse 30000 Nîmes`,street:`19 Rue de Toulouse`,postalCode:`30000`,city:`Nîmes`,latitude:`43.828539`,longitude:`4.375801`,inseeCode:`30000`,banId:`30189_7810_00019`},resolver:f(g().shape({addressText:m().required(`Veuillez sélectionner une adresse valide`),street:m().default(``),postalCode:m().default(``),city:m().default(``),latitude:m().default(``),longitude:m().default(``),inseeCode:m().default(``),banId:m().default(``)})),mode:`onBlur`}),[n,r,i,a,o,s,c,u]=t.watch([`street`,`city`,`postalCode`,`latitude`,`longitude`,`addressText`,`inseeCode`,`banId`]);return(0,D.jsxs)(d,{...t,children:[(0,D.jsxs)(`div`,{style:k.wrapper,children:[`Selected value in the form: `,(0,D.jsx)(`br`,{}),(0,D.jsxs)(`pre`,{style:k.pre,children:[`addressText = `,s,(0,D.jsx)(`br`,{}),`street = `,n,(0,D.jsx)(`br`,{}),`city = `,r,(0,D.jsx)(`br`,{}),`postalCode = `,i,(0,D.jsx)(`br`,{}),`latitude = `,a,(0,D.jsx)(`br`,{}),`longitude = `,o,(0,D.jsx)(`br`,{}),`inseeCode = `,c,(0,D.jsx)(`br`,{}),`banId = `,u]})]}),(0,D.jsx)(`form`,{children:e})]})},j={args:{name:`addressText`,label:`Adresse postale`}},M={args:{name:`addressText`,label:`Adresse postale`,suggestionLimit:15,ref:e=>{e&&(e.defaultValue=`8 Rue`)}}},N={args:{name:`addressText`,label:`Adresse postale`,disabled:!0}},P={args:{name:`addressText`,label:`Adresse postale`,description:`Uniquement si vous souhaitez préciser l’adresse exacte`,required:!1}},F={args:{name:`cityName`,label:`Nom de la ville`,onlyTypes:[`municipality`],suggestionLimit:50}},I={decorators:[e=>(0,D.jsx)(A,{children:(0,D.jsx)(e,{})})],render:()=>{let{setValue:e,register:t,formState:{errors:n}}=u();return(0,D.jsx)(T,{label:`Adresse postale`,...t(`addressText`),error:n.addressText?.message,onAddressChosen:t=>{e(`street`,t.address),e(`postalCode`,t.postalCode),e(`city`,t.city),e(`latitude`,String(t.latitude)),e(`longitude`,String(t.longitude)),e(`banId`,t.id),e(`inseeCode`,t.inseeCode)}})}},j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale'
  }
}`,...j.parameters?.docs?.source}}},M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
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
}`,...M.parameters?.docs?.source}}},N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    disabled: true
  }
}`,...N.parameters?.docs?.source}}},P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    description: 'Uniquement si vous souhaitez préciser l’adresse exacte',
    required: false
  }
}`,...P.parameters?.docs?.source}}},F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'cityName',
    label: 'Nom de la ville',
    onlyTypes: ['municipality'],
    suggestionLimit: 50
  }
}`,...F.parameters?.docs?.source}}},I.parameters={...I.parameters,docs:{...I.parameters?.docs,source:{originalSource:`{
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
}`,...I.parameters?.docs?.source}}},L=[`Default`,`withLimitOf15Suggestions`,`Disabled`,`optionalWithDescription`,`onlyMunicipality`,`WithinFormValidation`]}))();export{j as Default,N as Disabled,I as WithinFormValidation,L as __namedExportsOrder,O as default,F as onlyMunicipality,P as optionalWithDescription,M as withLimitOf15Suggestions};