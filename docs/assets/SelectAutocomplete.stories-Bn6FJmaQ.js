import{j as e}from"./jsx-runtime-Bceq0Pxv.js";import{o as u,c,a as b}from"./index.esm-9KyfWcA4.js";import{r as h}from"./iframe-D--VP42G.js";import{a as A,u as g,F as x}from"./index.esm-3WoXR_NJ.js";import{S as n}from"./SelectAutocomplete-CEeSBt0R.js";import"./preload-helper-PPVm8Dsz.js";import"./index-BFbtfYmv.js";import"./full-error-BFAmjN4t.js";import"./noop-BjFrJKj1.js";import"./SvgIcon-DHFuV8hN.js";import"./full-down-Cmbtr9nI.js";const j=({children:r})=>{const t=g({defaultValues:{departement:"05"},resolver:u(c().shape({departement:b().required("Veuillez choisir un département dans la liste")})),mode:"onTouched"});return e.jsx(x,{...t,children:r})},i=[{value:"01",label:"Ain",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"02",label:"Aisne"},{value:"03",label:"Allier",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"04",label:"Alpes-de-Haute-Provence test de libellé très long",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"05",label:"Hautes-Alpes",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"06",label:"Alpes-Maritimes",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"07",label:"Ardèche",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"08",label:"Ardennes",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"09",label:"Ariège",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"10",label:"Aube",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"11",label:"Aude",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"12",label:"Aveyron",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"13",label:"Bouches-du-Rhône",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"14",label:"Calvados",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},{value:"15",label:"Cantal",thumbUrl:"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"}],D={title:"@/ui-kit/forms/SelectAutocomplete",component:n},l={wrapper:{color:"#666",fontSize:"0.8rem",padding:"0 1rem",backgroundColor:"#f5f5f5",borderRadius:"0.2rem",border:"thin solid #e1e1e1",minHeight:"45px",marginBottom:"1rem",display:"flex",alignItems:"center"},pre:{display:"inline-block",padding:"0.5rem"}},a={args:{name:"departement",label:"Département",options:i,required:!1,shouldResetOnOpen:!0}},o={args:{name:"departement",label:"Département",options:i,required:!1,shouldResetOnOpen:!1,value:"05"}},s={render:()=>{const[r,t]=h.useState("");return e.jsxs(e.Fragment,{children:[e.jsxs("div",{style:l.wrapper,children:["Search text value: ",e.jsx("pre",{style:l.pre,children:r})]}),e.jsx(n,{label:"Département",name:"departement",options:i,required:!1,onSearch:m=>t(m)})]})}},p={decorators:[r=>e.jsx(j,{children:e.jsx(r,{})})],render:()=>{const{register:r,watch:t,formState:{errors:m}}=A(),d=t("departement");return e.jsxs(e.Fragment,{children:[e.jsxs("div",{style:l.wrapper,children:["Selected value in the form:"," ",e.jsx("pre",{style:l.pre,children:d})]}),e.jsx(n,{label:"Département",options:i,...r("departement"),error:m.departement?.message})]})}};a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    required: false,
    shouldResetOnOpen: true
  }
}`,...a.parameters?.docs?.source}}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    required: false,
    shouldResetOnOpen: false,
    value: '05'
  }
}`,...o.parameters?.docs?.source}}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [searchText, setSearchText] = useState('');
    return <>
        <div style={demoStyles['wrapper']}>
          Search text value: <pre style={demoStyles['pre']}>{searchText}</pre>
        </div>

        <SelectAutocomplete label="Département" name="departement" options={options} required={false} onSearch={text => setSearchText(text)} />
      </>;
  }
}`,...s.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  decorators: [(Story: any) => <FormWrapper>
        <Story />
      </FormWrapper>],
  render: () => {
    const {
      register,
      watch,
      formState: {
        errors
      }
      // eslint-disable-next-line react-hooks/rules-of-hooks
    } = useFormContext<WrapperFormValues>();
    const departement = watch('departement');
    return <>
        <div style={demoStyles['wrapper']}>
          Selected value in the form:{' '}
          <pre style={demoStyles['pre']}>{departement}</pre>
        </div>

        <SelectAutocomplete label="Département" options={options} {...register('departement')} error={errors.departement?.message} />
      </>;
  }
}`,...p.parameters?.docs?.source}}};const R=["Default","NoResetOnOpen","WithOnsearchTrigger","WithinFormValidation"];export{a as Default,o as NoResetOnOpen,s as WithOnsearchTrigger,p as WithinFormValidation,R as __namedExportsOrder,D as default};
