import{j as e}from"./jsx-runtime-Ds4Wh7L8.js";import{o as d,c as u,a as h}from"./index.esm-B95tiOwK.js";import{r as v}from"./iframe-D26S0QAy.js";import{a as x,u as b,F as S}from"./index.esm-DO_qzhT2.js";import{S as i}from"./SelectAutocomplete-B2LWSjf_.js";import"./preload-helper-PPVm8Dsz.js";import"./index-B3C22wEj.js";import"./noop-BjFrJKj1.js";import"./FieldLayout-D7QYmx_v.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-help-blUMxBcv.js";import"./Button-CtvFBMqV.js";import"./stroke-pass-CALgybTM.js";import"./SvgIcon-BoCb1h_t.js";import"./Tooltip-CoMRaNQR.js";import"./Button.module-CY1ZDZvt.js";import"./types-yVZEaApa.js";import"./FieldError-DrFAmZz8.js";import"./stroke-error-DSZD431a.js";import"./index.module-B9KjvN69.js";import"./stroke-down-Co3p5GaP.js";const g=({children:r})=>{const t=b({defaultValues:{departement:"05"},resolver:d(u().shape({departement:h().required("Veuillez choisir un département dans la liste")})),mode:"onTouched"});return e.jsx(S,{...t,children:r})},p=[{value:"01",label:"Ain"},{value:"02",label:"Aisne"},{value:"03",label:"Allier"},{value:"04",label:"Alpes-de-Haute-Provence test de libellé très long"},{value:"05",label:"Hautes-Alpes"},{value:"06",label:"Alpes-Maritimes"},{value:"07",label:"Ardèche"},{value:"08",label:"Ardennes"},{value:"09",label:"Ariège"},{value:"10",label:"Aube"},{value:"11",label:"Aude"},{value:"12",label:"Aveyron"},{value:"13",label:"Bouches-du-Rhône"},{value:"14",label:"Calvados"},{value:"15",label:"Cantal"}],q={title:"@/ui-kit/forms/SelectAutocomplete",component:i},n={wrapper:{color:"#666",fontSize:"0.8rem",padding:"0 1rem",backgroundColor:"#f5f5f5",borderRadius:"0.2rem",border:"thin solid #e1e1e1",minHeight:"45px",marginBottom:"1rem",display:"flex",alignItems:"center"},pre:{display:"inline-block",padding:"0.5rem"}},a={args:{name:"departement",label:"Département",options:p,isOptional:!0}},o={args:{name:"departement",label:"Département",options:p,isOptional:!0,resetOnOpen:!1,value:"05"}},s={render:()=>{const[r,t]=v.useState("");return e.jsxs(e.Fragment,{children:[e.jsxs("div",{style:n.wrapper,children:["Search text value: ",e.jsx("pre",{style:n.pre,children:r})]}),e.jsx(i,{label:"Département",name:"departement",options:p,isOptional:!0,onSearch:m=>t(m)})]})}},l={decorators:[r=>e.jsx(g,{children:e.jsx(r,{})})],render:()=>{const{register:r,watch:t,formState:{errors:m}}=x(),c=t("departement");return e.jsxs(e.Fragment,{children:[e.jsxs("div",{style:n.wrapper,children:["Selected value in the form:"," ",e.jsx("pre",{style:n.pre,children:c})]}),e.jsx(i,{label:"Département",options:p,...r("departement"),error:m.departement?.message})]})}};a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    isOptional: true
  }
}`,...a.parameters?.docs?.source}}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    isOptional: true,
    resetOnOpen: false,
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

        <SelectAutocomplete label="Département" name="departement" options={options} isOptional={true} onSearch={text => setSearchText(text)} />
      </>;
  }
}`,...s.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
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
}`,...l.parameters?.docs?.source}}};const I=["Default","NoResetOnOpen","WithOnsearchTrigger","WithinFormValidation"];export{a as Default,o as NoResetOnOpen,s as WithOnsearchTrigger,l as WithinFormValidation,I as __namedExportsOrder,q as default};
