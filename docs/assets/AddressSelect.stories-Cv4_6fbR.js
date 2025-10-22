import{j as t}from"./jsx-runtime-NJaF6LrX.js";import{o as U,c as k,a as n}from"./index.esm-DxE86b4z.js";import{a as z,u as W,F as $}from"./index.esm-B-CTCB-x.js";import{r as u}from"./iframe-DjRYVsy-.js";import{c as P}from"./index.module-CU7G4Ycp.js";import{A as G}from"./api-B_YBcxQ2.js";import{S as H}from"./SelectAutocomplete-Bibwr425.js";import"./config-BqmKEuqZ.js";import"./preload-helper-PPVm8Dsz.js";import"./index-yH7QRrJI.js";import"./noop-BjFrJKj1.js";import"./FieldLayout-xa4sG1bb.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-help-blUMxBcv.js";import"./Button-Bx0rODR6.js";import"./stroke-pass-CALgybTM.js";import"./SvgIcon-dS0B0qpc.js";import"./Tooltip-Dx44cbyp.js";import"./Button.module-CY1ZDZvt.js";import"./types-yVZEaApa.js";import"./FieldError-DoiAfFog.js";import"./stroke-error-DSZD431a.js";import"./stroke-down-Co3p5GaP.js";const Q="https://api-adresse.data.gouv.fr",J=async(e,s,o)=>{if(!e.ok)throw new G({method:s,url:o},e,`Échec de la requête ${e.url}, code: ${e.status}`);return await e.json()};function E(e){return e.features.map(s=>({address:s.properties.name,city:s.properties.city,inseeCode:s.properties.citycode,id:s.properties.id,latitude:s.geometry.coordinates[1],longitude:s.geometry.coordinates[0],label:s.properties.label,postalCode:s.properties.postcode}))}const v={limit:5,onlyTypes:["housenumber","street"]},K=async(e,{limit:s=v.limit,onlyTypes:o=v.onlyTypes}=v)=>{const r=`${Q}/search/?limit=${s}&q=${e}`,l=await J(await fetch(r),"GET",r);if(!o)return E(l);const p={...l,features:l.features.filter(d=>o.includes(d.properties.type))};return E(p)},w=e=>X(e).replace(/[^\w ]/,""),X=e=>e.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,""),Y=400,Z=5,c=u.forwardRef(({label:e,description:s,suggestionLimit:o=Z,onlyTypes:r,disabled:l=!1,className:p,onAddressChosen:d,error:S,name:x,onChange:C,onBlur:j,value:q,isOptional:D},I)=>{const[V,N]=u.useState(""),[O,A]=u.useState([]),T=u.useRef(new Map),F=u.useRef(null),R=P(async()=>{if(V.trim().length<3){A([]);return}try{const a=await K(V,{limit:o,onlyTypes:r});T.current=new Map(a.map(i=>[i.label,i])),A(a.map(({label:i})=>({value:i,label:i})))}catch{T.current=new Map,A([])}},Y),L=(a,i)=>a.filter(M=>w(i||"").split(" ").every(B=>w(M.label).includes(B)));return u.useImperativeHandle(I,()=>F.current),t.jsx(H,{name:x,label:e,options:O,hideArrow:!0,resetOnOpen:!1,description:s,value:q,onSearch:a=>{N(a),R()},onChange:a=>{C?.(a);const i=T.current.get(a.target.value);i&&d?.(i)},onBlur:a=>{a.target.value.trim()===""&&d?.({id:"",address:"",city:"",label:"",latitude:"",longitude:"",postalCode:"",inseeCode:""}),j?.(a)},searchInOptions:L,disabled:l,className:p,ref:F,error:S,isOptional:D})});c.displayName="AddressSelect";try{c.displayName="AddressSelect",c.__docgenInfo={description:"",displayName:"AddressSelect",props:{name:{defaultValue:null,description:"Name of the field, used for form submission and accessibility",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"Label displayed above the input",name:"label",required:!0,type:{name:"string | Element"}},onChange:{defaultValue:null,description:"Called when the input value changes",name:"onChange",required:!1,type:{name:'((event: CustomEvent<"change">) => void)'}},onBlur:{defaultValue:null,description:"Called when the input loses focus",name:"onBlur",required:!1,type:{name:'((event: CustomEvent<"blur">) => void)'}},value:{defaultValue:null,description:"Value of the input",name:"value",required:!1,type:{name:"string"}},onAddressChosen:{defaultValue:null,description:"Called when an address is chosen from the suggestions",name:"onAddressChosen",required:!1,type:{name:"((data: AdresseData) => void)"}},disabled:{defaultValue:{value:"false"},description:"Disables the input and prevents interaction",name:"disabled",required:!1,type:{name:"boolean"}},className:{defaultValue:null,description:"Additional CSS class names",name:"className",required:!1,type:{name:"string"}},description:{defaultValue:null,description:"Helper text displayed below the input",name:"description",required:!1,type:{name:"string"}},onlyTypes:{defaultValue:null,description:'Filters the address suggestions by type (e.g., "municipality", "street")',name:"onlyTypes",required:!1,type:{name:"FeaturePropertyType[]"}},error:{defaultValue:null,description:"Error message to display",name:"error",required:!1,type:{name:"string"}},suggestionLimit:{defaultValue:{value:"5"},description:"Maximum number of address suggestions to display",name:"suggestionLimit",required:!1,type:{name:"number"}},isOptional:{defaultValue:null,description:"Indicates if the field is optional",name:"isOptional",required:!1,type:{name:"boolean"}}}}}catch{}const Fe={title:"@/ui-kit/forms/AddressSelect",component:c},_={wrapper:{color:"#666",fontSize:"0.8rem",padding:"1rem",backgroundColor:"#f5f5f5",borderRadius:"0.2rem",border:"thin solid #e1e1e1",minHeight:"45px",marginBottom:"1rem",display:"flex",flexDirection:"column",alignItems:"flex-start"},pre:{display:"inline-block",padding:"0.5rem"}},ee=({children:e})=>{const s=W({defaultValues:{addressText:"19 Rue de Toulouse 30000 Nîmes",street:"19 Rue de Toulouse",postalCode:"30000",city:"Nîmes",latitude:"43.828539",longitude:"4.375801",inseeCode:"30000",banId:"30189_7810_00019"},resolver:U(k().shape({addressText:n().required("Veuillez sélectionner une adresse valide"),street:n().default(""),postalCode:n().default(""),city:n().default(""),latitude:n().default(""),longitude:n().default(""),inseeCode:n().default(""),banId:n().default("")})),mode:"onBlur"}),[o,r,l,p,d,S,x,C]=s.watch(["street","city","postalCode","latitude","longitude","addressText","inseeCode","banId"]);return t.jsxs($,{...s,children:[t.jsxs("div",{style:_.wrapper,children:["Selected value in the form: ",t.jsx("br",{}),t.jsxs("pre",{style:_.pre,children:["addressText = ",S,t.jsx("br",{}),"street = ",o,t.jsx("br",{}),"city = ",r,t.jsx("br",{}),"postalCode = ",l,t.jsx("br",{}),"latitude = ",p,t.jsx("br",{}),"longitude = ",d,t.jsx("br",{}),"inseeCode = ",x,t.jsx("br",{}),"banId = ",C]})]}),t.jsx("form",{children:e})]})},m={args:{name:"addressText",label:"Adresse postale"}},f={args:{name:"addressText",label:"Adresse postale",suggestionLimit:15,ref:e=>(e&&(e.defaultValue="8 Rue"),e)}},g={args:{name:"addressText",label:"Adresse postale",disabled:!0}},y={args:{name:"addressText",label:"Adresse postale",description:"Uniquement si vous souhaitez préciser l’adresse exacte",isOptional:!0}},h={args:{name:"cityName",label:"Nom de la ville",onlyTypes:["municipality"],value:"Noisy",suggestionLimit:50}},b={decorators:[e=>t.jsx(ee,{children:t.jsx(e,{})})],render:()=>{const{setValue:e,register:s,formState:{errors:o}}=z();return t.jsx(c,{label:"Adresse postale",...s("addressText"),error:o.addressText?.message,onAddressChosen:r=>{e("street",r.address),e("postalCode",r.postalCode),e("city",r.city),e("latitude",String(r.latitude)),e("longitude",String(r.longitude)),e("banId",r.id),e("inseeCode",r.inseeCode)}})}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale'
  }
}`,...m.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    suggestionLimit: 15,
    ref: ref => {
      if (ref) {
        ref.defaultValue = '8 Rue';
      }
      return ref;
    }
  }
}`,...f.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    disabled: true
  }
}`,...g.parameters?.docs?.source}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    description: 'Uniquement si vous souhaitez préciser l’adresse exacte',
    isOptional: true
  }
}`,...y.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'cityName',
    label: 'Nom de la ville',
    onlyTypes: ['municipality'],
    value: 'Noisy',
    suggestionLimit: 50
  }
}`,...h.parameters?.docs?.source}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
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
}`,...b.parameters?.docs?.source}}};const Ee=["Default","withLimitOf15Suggestions","Disabled","optionalWithDescription","onlyMunicipality","WithinFormValidation"];export{m as Default,g as Disabled,b as WithinFormValidation,Ee as __namedExportsOrder,Fe as default,h as onlyMunicipality,y as optionalWithDescription,f as withLimitOf15Suggestions};
