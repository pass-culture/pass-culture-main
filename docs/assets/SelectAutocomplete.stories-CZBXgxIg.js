import{j as e}from"./jsx-runtime-CDgzsi4D.js";import{o as c,c as u,a as h}from"./index.esm-Df8qV1S9.js";import{r as v}from"./iframe-BwUSJ71n.js";import{a as x,u as b,F as S}from"./index.esm-fSgWsKZU.js";import{S as i}from"./SelectAutocomplete-BdiHoxQy.js";import"./preload-helper-PPVm8Dsz.js";import"./index-CvE4PFvh.js";import"./noop-BjFrJKj1.js";import"./FieldLayout-DJ2bEbqv.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-help-blUMxBcv.js";import"./Button-pabQ-211.js";import"./stroke-pass-CALgybTM.js";import"./SvgIcon-ea64-BdU.js";import"./Tooltip-DaUk3qQb.js";import"./Button.module-CY1ZDZvt.js";import"./types-yVZEaApa.js";import"./FieldError-CZp2lrZT.js";import"./stroke-error-DSZD431a.js";import"./index.module-C5uAqyKZ.js";import"./full-down-Cmbtr9nI.js";const f=({children:r})=>{const t=b({defaultValues:{departement:"05"},resolver:c(u().shape({departement:h().required("Veuillez choisir un département dans la liste")})),mode:"onTouched"});return e.jsx(S,{...t,children:r})},p=[{value:"01",label:"Ain"},{value:"02",label:"Aisne"},{value:"03",label:"Allier"},{value:"04",label:"Alpes-de-Haute-Provence test de libellé très long"},{value:"05",label:"Hautes-Alpes"},{value:"06",label:"Alpes-Maritimes"},{value:"07",label:"Ardèche"},{value:"08",label:"Ardennes"},{value:"09",label:"Ariège"},{value:"10",label:"Aube"},{value:"11",label:"Aude"},{value:"12",label:"Aveyron"},{value:"13",label:"Bouches-du-Rhône"},{value:"14",label:"Calvados"},{value:"15",label:"Cantal"}],$={title:"@/ui-kit/forms/SelectAutocomplete",component:i},n={wrapper:{color:"#666",fontSize:"0.8rem",padding:"0 1rem",backgroundColor:"#f5f5f5",borderRadius:"0.2rem",border:"thin solid #e1e1e1",minHeight:"45px",marginBottom:"1rem",display:"flex",alignItems:"center"},pre:{display:"inline-block",padding:"0.5rem"}},a={args:{name:"departement",label:"Département",options:p,required:!1,shouldResetOnOpen:!0}},s={args:{name:"departement",label:"Département",options:p,required:!1,shouldResetOnOpen:!1,value:"05"}},o={render:()=>{const[r,t]=v.useState("");return e.jsxs(e.Fragment,{children:[e.jsxs("div",{style:n.wrapper,children:["Search text value: ",e.jsx("pre",{style:n.pre,children:r})]}),e.jsx(i,{label:"Département",name:"departement",options:p,required:!1,onSearch:m=>t(m)})]})}},l={decorators:[r=>e.jsx(f,{children:e.jsx(r,{})})],render:()=>{const{register:r,watch:t,formState:{errors:m}}=x(),d=t("departement");return e.jsxs(e.Fragment,{children:[e.jsxs("div",{style:n.wrapper,children:["Selected value in the form:"," ",e.jsx("pre",{style:n.pre,children:d})]}),e.jsx(i,{label:"Département",options:p,...r("departement"),error:m.departement?.message})]})}};a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    required: false,
    shouldResetOnOpen: true
  }
}`,...a.parameters?.docs?.source}}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    required: false,
    shouldResetOnOpen: false,
    value: '05'
  }
}`,...s.parameters?.docs?.source}}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
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
}`,...o.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
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
}`,...l.parameters?.docs?.source}}};const I=["Default","NoResetOnOpen","WithOnsearchTrigger","WithinFormValidation"];export{a as Default,s as NoResetOnOpen,o as WithOnsearchTrigger,l as WithinFormValidation,I as __namedExportsOrder,$ as default};
