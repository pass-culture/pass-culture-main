import{n as e,r as t}from"./rolldown-runtime-DkW27tQK.js";import{d as n}from"./iframe-QbuQVDmM.js";import{t as r}from"./jsx-runtime-DeHZSEgm.js";import{n as i,t as a}from"./index.module-BTUT1InF.js";import{i as o,n as s,r as c}from"./api-gm8QNyF3.js";import{i as l,o as u,s as d,t as f}from"./index.esm-Dxi1Ye1t.js";import{a as p,i as m,n as h,r as g,t as _}from"./index.esm-B3mw-jZS.js";import{n as v,t as y}from"./SelectAutocomplete-UU2tiFN_.js";var b;function x(){return(x=e((()=>{b=`https://data.geopf.fr`})))()}function S(e){return e.features.map(e=>({address:e.properties.name,city:e.properties.city,inseeCode:e.properties.citycode,id:e.properties.id,latitude:e.geometry.coordinates[1],longitude:e.geometry.coordinates[0],label:e.properties.label,postalCode:e.properties.postcode}))}var C,w,T;function E(){return(E=e((()=>{o(),x(),C=async(e,t,n)=>{if(!e.ok)throw new c({method:t,url:n},e,`Échec de la requête ${e.url}, code: ${e.status}`);return await e.json()},w={limit:5,onlyTypes:[`housenumber`,`street`]},T=async(e,{limit:t=w.limit,onlyTypes:n=w.onlyTypes}=w)=>{let r=`${b}/geocodage/search/?limit=${t}&q=${e}`,i=await C(await fetch(r),`GET`,r);return S(n?{...i,features:i.features.filter(e=>n.includes(e.properties.type))}:i)}})))()}var D;function O(){return(O=e((()=>{D=e=>e.trim().toLowerCase().replace(/œ/g,`oe`).replace(/æ/g,`ae`).normalize(`NFD`).replace(/[^a-z0-9-\s]/g,``).replace(/\s+/g,` `)})))()}var k,A,j,M,N;function P(){return(P=e((()=>{k=n(),l(),i(),s(),O(),v(),A=r(),j=400,M=5,N=(0,k.forwardRef)(({label:e,description:t,suggestionLimit:n=M,onlyTypes:r,disabled:i=!1,className:o,onAddressChosen:s,error:c,name:l,onChange:u,onBlur:f,required:p=!0,requiredIndicator:m=`symbol`},h)=>{let g=d(),[_,v]=(0,k.useState)([]),b=(0,k.useRef)(new Map),x=(0,k.useRef)(null),S=(0,k.useCallback)(async e=>{if(e.trim().length<3){v([]);return}try{let t=await T(e,{limit:n,onlyTypes:r});b.current=new Map(t.map(e=>[e.label,e])),v(t.map(({label:e})=>({value:e,label:e})))}catch{b.current=new Map,v([])}},[n,r]),C=a(e=>{S(e)},j),w=e=>D(e).replace(/[^\w ]/,``);return(0,k.useEffect)(()=>{x.current?.value&&S(x.current?.value)},[]),(0,k.useImperativeHandle)(h,()=>x.current),(0,A.jsx)(y,{name:l,label:e,options:_,description:t,onSearch:e=>{C(e)},onChange:e=>{u?.(e),g?.trigger(l);let t=b.current.get(e.target.value);t&&s?.(t)},onBlur:e=>{f?.(e);let t=b.current.get(e.target.value);t&&s?.(t)},searchInOptions:(e,t)=>e.filter(e=>w(t||``).split(` `).every(t=>w(e.label).includes(t))),disabled:i,className:o,ref:x,error:c,required:p,requiredIndicator:m})}),N.displayName=`AddressSelect`;try{N.displayName=`AddressSelect`,N.__docgenInfo={description:``,displayName:`AddressSelect`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,methods:[],props:{name:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Name of the field, used for form submission and accessibility`,name:`name`,required:!0,tags:{},type:{name:`string`}},label:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Label displayed above the input`,name:`label`,required:!0,tags:{},type:{name:`string | Element`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Called when the input value changes`,name:`onChange`,required:!1,tags:{},type:{name:`((event: CustomEvent<"change">) => void)`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Called when the input loses focus`,name:`onBlur`,required:!1,tags:{},type:{name:`((event: CustomEvent<"blur">) => void)`}},onAddressChosen:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Called when an address is chosen from the suggestions`,name:`onAddressChosen`,required:!1,tags:{},type:{name:`((data: AdresseData) => void)`}},disabled:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Disables the input and prevents interaction`,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},className:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Additional CSS class names`,name:`className`,required:!1,tags:{},type:{name:`string`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Helper text displayed below the input`,name:`description`,required:!1,tags:{},type:{name:`string`}},onlyTypes:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Filters the address suggestions by type (e.g., "municipality", "street")`,name:`onlyTypes`,required:!1,tags:{},type:{name:`FeaturePropertyType[]`}},error:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Error message to display`,name:`error`,required:!1,tags:{},type:{name:`string`}},suggestionLimit:{defaultValue:{value:`5`},declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Maximum number of address suggestions to display`,name:`suggestionLimit`,required:!1,tags:{},type:{name:`number`}},required:{defaultValue:{value:`true`},declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:`Indicates if the field is required`,name:`required`,required:!1,tags:{},type:{name:`boolean`}},requiredIndicator:{defaultValue:{value:`symbol`},declarations:[{fileName:`pro/src/ui-kit/form/AddressSelect/AddressSelect.tsx`,name:`TypeLiteral`}],description:``,name:`requiredIndicator`,required:!1,tags:{},type:{name:`enum`,raw:`RequiredIndicator`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}}},tags:{}}}catch{}})))()}var F=t({Default:()=>B,Disabled:()=>H,WithinFormValidation:()=>G,__namedExportsOrder:()=>K,default:()=>L,onlyMunicipality:()=>W,optionalWithDescription:()=>U,withLimitOf15Suggestions:()=>V}),I,L,R,z,B,V,H,U,W,G,K;function q(){return(q=e((()=>{m(),l(),g(),P(),I=r(),L={title:`@/ui-kit/forms/AddressSelect`,component:N},R={wrapper:{color:`#666`,fontSize:`0.8rem`,padding:`1rem`,backgroundColor:`#f5f5f5`,borderRadius:`0.2rem`,border:`thin solid #e1e1e1`,minHeight:`45px`,marginBottom:`1rem`,display:`flex`,flexDirection:`column`,alignItems:`flex-start`},pre:{display:`inline-block`,padding:`0.5rem`}},z=({children:e})=>{let t=u({defaultValues:{addressText:`19 Rue de Toulouse 30000 Nîmes`,street:`19 Rue de Toulouse`,postalCode:`30000`,city:`Nîmes`,latitude:`43.828539`,longitude:`4.375801`,inseeCode:`30000`,banId:`30189_7810_00019`},resolver:p(_().shape({addressText:h().required(`Veuillez sélectionner une adresse valide`),street:h().default(``),postalCode:h().default(``),city:h().default(``),latitude:h().default(``),longitude:h().default(``),inseeCode:h().default(``),banId:h().default(``)})),mode:`onBlur`}),[n,r,i,a,o,s,c,l]=t.watch([`street`,`city`,`postalCode`,`latitude`,`longitude`,`addressText`,`inseeCode`,`banId`]);return(0,I.jsxs)(f,{...t,children:[(0,I.jsxs)(`div`,{style:R.wrapper,children:[`Selected value in the form: `,(0,I.jsx)(`br`,{}),(0,I.jsxs)(`pre`,{style:R.pre,children:[`addressText = `,s,(0,I.jsx)(`br`,{}),`street = `,n,(0,I.jsx)(`br`,{}),`city = `,r,(0,I.jsx)(`br`,{}),`postalCode = `,i,(0,I.jsx)(`br`,{}),`latitude = `,a,(0,I.jsx)(`br`,{}),`longitude = `,o,(0,I.jsx)(`br`,{}),`inseeCode = `,c,(0,I.jsx)(`br`,{}),`banId = `,l]})]}),(0,I.jsx)(`form`,{children:e})]})},B={args:{name:`addressText`,label:`Adresse postale`}},V={args:{name:`addressText`,label:`Adresse postale`,suggestionLimit:15,ref:e=>{e&&(e.defaultValue=`8 Rue`)}}},H={args:{name:`addressText`,label:`Adresse postale`,disabled:!0}},U={args:{name:`addressText`,label:`Adresse postale`,description:`Uniquement si vous souhaitez préciser l’adresse exacte`,required:!1}},W={args:{name:`cityName`,label:`Nom de la ville`,onlyTypes:[`municipality`],suggestionLimit:50}},G={decorators:[e=>(0,I.jsx)(z,{children:(0,I.jsx)(e,{})})],render:()=>{let{setValue:e,register:t,formState:{errors:n}}=d();return(0,I.jsx)(N,{label:`Adresse postale`,...t(`addressText`),error:n.addressText?.message,onAddressChosen:t=>{e(`street`,t.address),e(`postalCode`,t.postalCode),e(`city`,t.city),e(`latitude`,String(t.latitude)),e(`longitude`,String(t.longitude)),e(`banId`,t.id),e(`inseeCode`,t.inseeCode)}})}},B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale'
  }
}`,...B.parameters?.docs?.source}}},V.parameters={...V.parameters,docs:{...V.parameters?.docs,source:{originalSource:`{
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
}`,...V.parameters?.docs?.source}}},H.parameters={...H.parameters,docs:{...H.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    disabled: true
  }
}`,...H.parameters?.docs?.source}}},U.parameters={...U.parameters,docs:{...U.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    description: 'Uniquement si vous souhaitez préciser l’adresse exacte',
    required: false
  }
}`,...U.parameters?.docs?.source}}},W.parameters={...W.parameters,docs:{...W.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'cityName',
    label: 'Nom de la ville',
    onlyTypes: ['municipality'],
    suggestionLimit: 50
  }
}`,...W.parameters?.docs?.source}}},G.parameters={...G.parameters,docs:{...G.parameters?.docs,source:{originalSource:`{
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
}`,...G.parameters?.docs?.source}}},K=[`Default`,`withLimitOf15Suggestions`,`Disabled`,`optionalWithDescription`,`onlyMunicipality`,`WithinFormValidation`]})))()}export{q as n,E as r,F as t};