import{j as t}from"./jsx-runtime-CHY4GNiZ.js";import{o as M,c as k,a as i}from"./index.esm-TqU1oRuM.js";import{a as z,u as B,F as U}from"./index.esm-EESTyOja.js";import{r as u}from"./iframe-UAYo8ewY.js";import{c as W}from"./index.module-BW7CMJeg.js";import{A as $}from"./api-BqNMOD2c.js";import{S as P}from"./SelectAutocomplete-B6H87W8x.js";import"./store-DbzJj_LB.js";import"./SnackBar-DsZ9_7iB.js";import"./preload-helper-PPVm8Dsz.js";import"./exports-XRHBct3C.js";import"./index-DOMnZ_As.js";import"./full-error-BFAmjN4t.js";import"./noop-BjFrJKj1.js";import"./SvgIcon-CjqE4XIa.js";import"./full-down-Cmbtr9nI.js";import"./date-CrU56jqV.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-validate-CbMNulkZ.js";import"./useMediaQuery-BK6GmpgR.js";const G="https://data.geopf.fr",H=async(e,s,o)=>{if(!e.ok)throw new $({method:s,url:o},e,`Échec de la requête ${e.url}, code: ${e.status}`);return await e.json()};function w(e){return e.features.map(s=>({address:s.properties.name,city:s.properties.city,inseeCode:s.properties.citycode,id:s.properties.id,latitude:s.geometry.coordinates[1],longitude:s.geometry.coordinates[0],label:s.properties.label,postalCode:s.properties.postcode}))}const E={limit:5,onlyTypes:["housenumber","street"]},Q=async(e,{limit:s=E.limit,onlyTypes:o=E.onlyTypes}=E)=>{const a=`${G}/geocodage/search/?limit=${s}&q=${e}`,d=await H(await fetch(a),"GET",a);if(!o)return w(d);const p={...d,features:d.features.filter(c=>o.includes(c.properties.type))};return w(p)},J=e=>e.trim().toLowerCase().replace(/œ/g,"oe").replace(/æ/g,"ae").normalize("NFD").replace(/[^a-z0-9-\s]/g,"").replace(/\s+/g," "),K=400,X=5,m=u.forwardRef(({label:e,description:s,suggestionLimit:o=X,onlyTypes:a,disabled:d=!1,className:p,onAddressChosen:c,error:A,name:T,onChange:V,onBlur:j,required:D=!0},I)=>{const[N,v]=u.useState([]),f=u.useRef(new Map),g=u.useRef(null),q=u.useCallback(async r=>{if(r.trim().length<3){v([]);return}try{const n=await Q(r,{limit:o,onlyTypes:a});f.current=new Map(n.map(l=>[l.label,l])),v(n.map(({label:l})=>({value:l,label:l})))}catch{f.current=new Map,v([])}},[o,a]),R=W(r=>{q(r)},K),_=r=>J(r).replace(/[^\w ]/,""),L=(r,n)=>r.filter(l=>_(n||"").split(" ").every(O=>_(l.label).includes(O)));return u.useEffect(()=>{g.current?.value&&q(g.current?.value)},[]),u.useImperativeHandle(I,()=>g.current),t.jsx(P,{name:T,label:e,options:N,description:s,onSearch:r=>{R(r)},onChange:r=>{V?.(r);const n=f.current.get(r.target.value);n&&c?.(n)},onBlur:r=>{j?.(r);const n=f.current.get(r.target.value);n&&c?.(n)},searchInOptions:L,disabled:d,className:p,ref:g,error:A,required:D})});m.displayName="AddressSelect";try{m.displayName="AddressSelect",m.__docgenInfo={description:"",displayName:"AddressSelect",props:{name:{defaultValue:null,description:"Name of the field, used for form submission and accessibility",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"Label displayed above the input",name:"label",required:!0,type:{name:"string | Element"}},onChange:{defaultValue:null,description:"Called when the input value changes",name:"onChange",required:!1,type:{name:'((event: CustomEvent<"change">) => void)'}},onBlur:{defaultValue:null,description:"Called when the input loses focus",name:"onBlur",required:!1,type:{name:'((event: CustomEvent<"blur">) => void)'}},onAddressChosen:{defaultValue:null,description:"Called when an address is chosen from the suggestions",name:"onAddressChosen",required:!1,type:{name:"((data: AdresseData) => void)"}},disabled:{defaultValue:{value:"false"},description:"Disables the input and prevents interaction",name:"disabled",required:!1,type:{name:"boolean"}},className:{defaultValue:null,description:"Additional CSS class names",name:"className",required:!1,type:{name:"string"}},description:{defaultValue:null,description:"Helper text displayed below the input",name:"description",required:!1,type:{name:"string"}},onlyTypes:{defaultValue:null,description:'Filters the address suggestions by type (e.g., "municipality", "street")',name:"onlyTypes",required:!1,type:{name:"FeaturePropertyType[]"}},error:{defaultValue:null,description:"Error message to display",name:"error",required:!1,type:{name:"string"}},suggestionLimit:{defaultValue:{value:"5"},description:"Maximum number of address suggestions to display",name:"suggestionLimit",required:!1,type:{name:"number"}},required:{defaultValue:{value:"true"},description:"Indicates if the field is required",name:"required",required:!1,type:{name:"boolean"}}}}}catch{}const Se={title:"@/ui-kit/forms/AddressSelect",component:m},F={wrapper:{color:"#666",fontSize:"0.8rem",padding:"1rem",backgroundColor:"#f5f5f5",borderRadius:"0.2rem",border:"thin solid #e1e1e1",minHeight:"45px",marginBottom:"1rem",display:"flex",flexDirection:"column",alignItems:"flex-start"},pre:{display:"inline-block",padding:"0.5rem"}},Y=({children:e})=>{const s=B({defaultValues:{addressText:"19 Rue de Toulouse 30000 Nîmes",street:"19 Rue de Toulouse",postalCode:"30000",city:"Nîmes",latitude:"43.828539",longitude:"4.375801",inseeCode:"30000",banId:"30189_7810_00019"},resolver:M(k().shape({addressText:i().required("Veuillez sélectionner une adresse valide"),street:i().default(""),postalCode:i().default(""),city:i().default(""),latitude:i().default(""),longitude:i().default(""),inseeCode:i().default(""),banId:i().default("")})),mode:"onBlur"}),[o,a,d,p,c,A,T,V]=s.watch(["street","city","postalCode","latitude","longitude","addressText","inseeCode","banId"]);return t.jsxs(U,{...s,children:[t.jsxs("div",{style:F.wrapper,children:["Selected value in the form: ",t.jsx("br",{}),t.jsxs("pre",{style:F.pre,children:["addressText = ",A,t.jsx("br",{}),"street = ",o,t.jsx("br",{}),"city = ",a,t.jsx("br",{}),"postalCode = ",d,t.jsx("br",{}),"latitude = ",p,t.jsx("br",{}),"longitude = ",c,t.jsx("br",{}),"inseeCode = ",T,t.jsx("br",{}),"banId = ",V]})]}),t.jsx("form",{children:e})]})},y={args:{name:"addressText",label:"Adresse postale"}},b={args:{name:"addressText",label:"Adresse postale",suggestionLimit:15,ref:e=>(e&&(e.defaultValue="8 Rue"),e)}},h={args:{name:"addressText",label:"Adresse postale",disabled:!0}},x={args:{name:"addressText",label:"Adresse postale",description:"Uniquement si vous souhaitez préciser l’adresse exacte",required:!1}},S={args:{name:"cityName",label:"Nom de la ville",onlyTypes:["municipality"],suggestionLimit:50}},C={decorators:[e=>t.jsx(Y,{children:t.jsx(e,{})})],render:()=>{const{setValue:e,register:s,formState:{errors:o}}=z();return t.jsx(m,{label:"Adresse postale",...s("addressText"),error:o.addressText?.message,onAddressChosen:a=>{e("street",a.address),e("postalCode",a.postalCode),e("city",a.city),e("latitude",String(a.latitude)),e("longitude",String(a.longitude)),e("banId",a.id),e("inseeCode",a.inseeCode)}})}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale'
  }
}`,...y.parameters?.docs?.source}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
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
}`,...b.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    disabled: true
  }
}`,...h.parameters?.docs?.source}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    description: 'Uniquement si vous souhaitez préciser l’adresse exacte',
    required: false
  }
}`,...x.parameters?.docs?.source}}};S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'cityName',
    label: 'Nom de la ville',
    onlyTypes: ['municipality'],
    suggestionLimit: 50
  }
}`,...S.parameters?.docs?.source}}};C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`{
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
}`,...C.parameters?.docs?.source}}};const Ce=["Default","withLimitOf15Suggestions","Disabled","optionalWithDescription","onlyMunicipality","WithinFormValidation"];export{y as Default,h as Disabled,C as WithinFormValidation,Ce as __namedExportsOrder,Se as default,S as onlyMunicipality,x as optionalWithDescription,b as withLimitOf15Suggestions};
