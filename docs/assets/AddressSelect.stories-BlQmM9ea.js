import{j as s}from"./jsx-runtime-CrQix9pG.js";import{o as U,c as k,a as n}from"./index.esm-BUAjuamB.js";import{a as z,u as W,F as $}from"./index.esm-BGboK4dZ.js";import{r as u}from"./iframe-CLYsrNTt.js";import{c as P}from"./index.module-CjmmisF-.js";import{A as G}from"./api-CqquuWXJ.js";import{S as H}from"./SelectAutocomplete-xklTW468.js";import"./config-BqmKEuqZ.js";import"./store-By_GZN47.js";import"./logout-BW_kIPCp.js";import"./preload-helper-PPVm8Dsz.js";import"./index-GE5Gqg2M.js";import"./noop-BjFrJKj1.js";import"./FieldLayout-OePBce3b.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-help-blUMxBcv.js";import"./Button-DEIgSCvy.js";import"./stroke-pass-CALgybTM.js";import"./SvgIcon-Ce4RdEWU.js";import"./Tooltip-fPtaBLPu.js";import"./Button.module-CY1ZDZvt.js";import"./types-yVZEaApa.js";import"./FieldError-VF4WR9Y7.js";import"./stroke-error-DSZD431a.js";import"./full-down-Cmbtr9nI.js";import"./useAppDispatch-Bv0z3sUD.js";import"./useNotification-DnIN7Mv1.js";const Q="https://data.geopf.fr",J=async(e,r,o)=>{if(!e.ok)throw new G({method:r,url:o},e,`Échec de la requête ${e.url}, code: ${e.status}`);return await e.json()};function q(e){return e.features.map(r=>({address:r.properties.name,city:r.properties.city,inseeCode:r.properties.citycode,id:r.properties.id,latitude:r.geometry.coordinates[1],longitude:r.geometry.coordinates[0],label:r.properties.label,postalCode:r.properties.postcode}))}const v={limit:5,onlyTypes:["housenumber","street"]},K=async(e,{limit:r=v.limit,onlyTypes:o=v.onlyTypes}=v)=>{const t=`${Q}/geocodage/search/?limit=${r}&q=${e}`,l=await J(await fetch(t),"GET",t);if(!o)return q(l);const p={...l,features:l.features.filter(d=>o.includes(d.properties.type))};return q(p)},E=e=>X(e).replace(/[^\w ]/,""),X=e=>e.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,""),Y=400,Z=5,c=u.forwardRef(({label:e,description:r,suggestionLimit:o=Z,onlyTypes:t,disabled:l=!1,className:p,onAddressChosen:d,error:S,name:x,onChange:C,onBlur:w,value:j,required:D=!0},I)=>{const[V,N]=u.useState(""),[R,A]=u.useState([]),T=u.useRef(new Map),F=u.useRef(null),L=P(async()=>{if(V.trim().length<3){A([]);return}try{const a=await K(V,{limit:o,onlyTypes:t});T.current=new Map(a.map(i=>[i.label,i])),A(a.map(({label:i})=>({value:i,label:i})))}catch{T.current=new Map,A([])}},Y),O=(a,i)=>a.filter(M=>E(i||"").split(" ").every(B=>E(M.label).includes(B)));return u.useImperativeHandle(I,()=>F.current),s.jsx(H,{name:x,label:e,options:R,resetOnOpen:!1,description:r,value:j,onSearch:a=>{N(a),L()},onChange:a=>{C?.(a);const i=T.current.get(a.target.value);i&&d?.(i)},onBlur:a=>{a.target.value.trim()===""&&d?.({id:"",address:"",city:"",label:"",latitude:"",longitude:"",postalCode:"",inseeCode:""}),w?.(a)},searchInOptions:O,disabled:l,className:p,ref:F,error:S,required:D})});c.displayName="AddressSelect";try{c.displayName="AddressSelect",c.__docgenInfo={description:"",displayName:"AddressSelect",props:{name:{defaultValue:null,description:"Name of the field, used for form submission and accessibility",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"Label displayed above the input",name:"label",required:!0,type:{name:"string | Element"}},onChange:{defaultValue:null,description:"Called when the input value changes",name:"onChange",required:!1,type:{name:'((event: CustomEvent<"change">) => void)'}},onBlur:{defaultValue:null,description:"Called when the input loses focus",name:"onBlur",required:!1,type:{name:'((event: CustomEvent<"blur">) => void)'}},value:{defaultValue:null,description:"Value of the input",name:"value",required:!1,type:{name:"string"}},onAddressChosen:{defaultValue:null,description:"Called when an address is chosen from the suggestions",name:"onAddressChosen",required:!1,type:{name:"((data: AdresseData) => void)"}},disabled:{defaultValue:{value:"false"},description:"Disables the input and prevents interaction",name:"disabled",required:!1,type:{name:"boolean"}},className:{defaultValue:null,description:"Additional CSS class names",name:"className",required:!1,type:{name:"string"}},description:{defaultValue:null,description:"Helper text displayed below the input",name:"description",required:!1,type:{name:"string"}},onlyTypes:{defaultValue:null,description:'Filters the address suggestions by type (e.g., "municipality", "street")',name:"onlyTypes",required:!1,type:{name:"FeaturePropertyType[]"}},error:{defaultValue:null,description:"Error message to display",name:"error",required:!1,type:{name:"string"}},suggestionLimit:{defaultValue:{value:"5"},description:"Maximum number of address suggestions to display",name:"suggestionLimit",required:!1,type:{name:"number"}},required:{defaultValue:{value:"true"},description:"Indicates if the field is required",name:"required",required:!1,type:{name:"boolean"}}}}}catch{}const we={title:"@/ui-kit/forms/AddressSelect",component:c},_={wrapper:{color:"#666",fontSize:"0.8rem",padding:"1rem",backgroundColor:"#f5f5f5",borderRadius:"0.2rem",border:"thin solid #e1e1e1",minHeight:"45px",marginBottom:"1rem",display:"flex",flexDirection:"column",alignItems:"flex-start"},pre:{display:"inline-block",padding:"0.5rem"}},ee=({children:e})=>{const r=W({defaultValues:{addressText:"19 Rue de Toulouse 30000 Nîmes",street:"19 Rue de Toulouse",postalCode:"30000",city:"Nîmes",latitude:"43.828539",longitude:"4.375801",inseeCode:"30000",banId:"30189_7810_00019"},resolver:U(k().shape({addressText:n().required("Veuillez sélectionner une adresse valide"),street:n().default(""),postalCode:n().default(""),city:n().default(""),latitude:n().default(""),longitude:n().default(""),inseeCode:n().default(""),banId:n().default("")})),mode:"onBlur"}),[o,t,l,p,d,S,x,C]=r.watch(["street","city","postalCode","latitude","longitude","addressText","inseeCode","banId"]);return s.jsxs($,{...r,children:[s.jsxs("div",{style:_.wrapper,children:["Selected value in the form: ",s.jsx("br",{}),s.jsxs("pre",{style:_.pre,children:["addressText = ",S,s.jsx("br",{}),"street = ",o,s.jsx("br",{}),"city = ",t,s.jsx("br",{}),"postalCode = ",l,s.jsx("br",{}),"latitude = ",p,s.jsx("br",{}),"longitude = ",d,s.jsx("br",{}),"inseeCode = ",x,s.jsx("br",{}),"banId = ",C]})]}),s.jsx("form",{children:e})]})},m={args:{name:"addressText",label:"Adresse postale"}},f={args:{name:"addressText",label:"Adresse postale",suggestionLimit:15,ref:e=>(e&&(e.defaultValue="8 Rue"),e)}},g={args:{name:"addressText",label:"Adresse postale",disabled:!0}},y={args:{name:"addressText",label:"Adresse postale",description:"Uniquement si vous souhaitez préciser l’adresse exacte",required:!1}},h={args:{name:"cityName",label:"Nom de la ville",onlyTypes:["municipality"],value:"Noisy",suggestionLimit:50}},b={decorators:[e=>s.jsx(ee,{children:s.jsx(e,{})})],render:()=>{const{setValue:e,register:r,formState:{errors:o}}=z();return s.jsx(c,{label:"Adresse postale",...r("addressText"),error:o.addressText?.message,onAddressChosen:t=>{e("street",t.address),e("postalCode",t.postalCode),e("city",t.city),e("latitude",String(t.latitude)),e("longitude",String(t.longitude)),e("banId",t.id),e("inseeCode",t.inseeCode)}})}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
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
    required: false
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
}`,...b.parameters?.docs?.source}}};const je=["Default","withLimitOf15Suggestions","Disabled","optionalWithDescription","onlyMunicipality","WithinFormValidation"];export{m as Default,g as Disabled,b as WithinFormValidation,je as __namedExportsOrder,we as default,h as onlyMunicipality,y as optionalWithDescription,f as withLimitOf15Suggestions};
