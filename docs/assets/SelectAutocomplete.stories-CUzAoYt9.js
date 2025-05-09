import{j as e}from"./jsx-runtime-BYYWji4R.js";import{o as j,c as D,a as T}from"./index.esm-BWN7Uh-k.js";import{r as k}from"./index-ClcD9ViR.js";import{u as w,a as W,F as V}from"./index.esm-BuPb1Mi7.js";import{S as i}from"./SelectAutocomplete-9fcaqzn9.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./index-DeARc5FM.js";import"./BaseInput-BI1b_EYZ.js";import"./SvgIcon-CyWUmZpn.js";import"./FieldLayout-B7vRs_OG.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-help-blUMxBcv.js";import"./Button-Cva4CQSi.js";import"./stroke-pass-CALgybTM.js";import"./Tooltip-BpKRYYrm.js";import"./Button.module-BsO1-3k4.js";import"./types-yVZEaApa.js";import"./FieldError-azuIsM2E.js";import"./stroke-error-DSZD431a.js";import"./FieldLayoutCharacterCount-Bc4HS3VB.js";import"./index.module-DF6qn1Ex.js";import"./stroke-down-Co3p5GaP.js";const C=({children:r})=>{const t=W({defaultValues:{departement:"05"},resolver:j(D().shape({departement:T().required("Veuillez choisir un département dans la liste")})),mode:"onTouched"});return e.jsx(V,{...t,children:r})},p=[{value:"01",label:"Ain"},{value:"02",label:"Aisne"},{value:"03",label:"Allier"},{value:"04",label:"Alpes-de-Haute-Provence test de libellé très long"},{value:"05",label:"Hautes-Alpes"},{value:"06",label:"Alpes-Maritimes"},{value:"07",label:"Ardèche"},{value:"08",label:"Ardennes"},{value:"09",label:"Ariège"},{value:"10",label:"Aube"},{value:"11",label:"Aude"},{value:"12",label:"Aveyron"},{value:"13",label:"Bouches-du-Rhône"},{value:"14",label:"Calvados"},{value:"15",label:"Cantal"}],te={title:"ui-kit/formsV2/SelectAutocomplete",component:i},n={wrapper:{color:"#666",fontSize:"0.8rem",padding:"0 1rem",backgroundColor:"#f5f5f5",borderRadius:"0.2rem",border:"thin solid #e1e1e1",minHeight:"45px",marginBottom:"1rem",display:"flex",alignItems:"center"},pre:{display:"inline-block",padding:"0.5rem"}},a={args:{name:"departement",label:"Département",options:p,isOptional:!0}},o={args:{name:"departement",label:"Département",options:p,isOptional:!0,resetOnOpen:!1,value:"05"}},s={render:()=>{const[r,t]=k.useState("");return e.jsxs(e.Fragment,{children:[e.jsxs("div",{style:n.wrapper,children:["Search text value: ",e.jsx("pre",{style:n.pre,children:r})]}),e.jsx(i,{label:"Département",name:"departement",options:p,isOptional:!0,onSearch:m=>t(m)})]})}},l={decorators:[r=>e.jsx(C,{children:e.jsx(r,{})})],render:()=>{var c;const{register:r,watch:t,formState:{errors:m}}=w(),F=t("departement");return e.jsxs(e.Fragment,{children:[e.jsxs("div",{style:n.wrapper,children:["Selected value in the form:"," ",e.jsx("pre",{style:n.pre,children:F})]}),e.jsx(i,{label:"Département",options:p,...r("departement"),error:(c=m.departement)==null?void 0:c.message})]})}};var d,u,h;a.parameters={...a.parameters,docs:{...(d=a.parameters)==null?void 0:d.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    isOptional: true
  }
}`,...(h=(u=a.parameters)==null?void 0:u.docs)==null?void 0:h.source}}};var v,x,b;o.parameters={...o.parameters,docs:{...(v=o.parameters)==null?void 0:v.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    isOptional: true,
    resetOnOpen: false,
    value: '05'
  }
}`,...(b=(x=o.parameters)==null?void 0:x.docs)==null?void 0:b.source}}};var S,g,f;s.parameters={...s.parameters,docs:{...(S=s.parameters)==null?void 0:S.docs,source:{originalSource:`{
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
}`,...(f=(g=s.parameters)==null?void 0:g.docs)==null?void 0:f.source}}};var y,A,O;l.parameters={...l.parameters,docs:{...(y=l.parameters)==null?void 0:y.docs,source:{originalSource:`{
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
}`,...(O=(A=l.parameters)==null?void 0:A.docs)==null?void 0:O.source}}};const ae=["Default","NoResetOnOpen","WithOnsearchTrigger","WithinFormValidation"];export{a as Default,o as NoResetOnOpen,s as WithOnsearchTrigger,l as WithinFormValidation,ae as __namedExportsOrder,te as default};
