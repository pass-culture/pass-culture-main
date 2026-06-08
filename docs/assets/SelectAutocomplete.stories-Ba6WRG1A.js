import{i as e,s as t}from"./preload-helper-xPQekRTU.js";import{C as n}from"./iframe-CZzvhLX9.js";import{t as r}from"./jsx-runtime-CaZkqeYb.js";import{i,o as a,s as o,t as s}from"./index.esm-BQj_Ynve.js";import{a as c,i as l,n as u,r as d,t as f}from"./index.esm-Dijz0Qhd.js";import{n as p,t as m}from"./SelectAutocomplete-DZo-AGLF.js";var h,g,_,v,y,b,x,S,C,w,T;e((()=>{l(),h=t(n(),1),i(),d(),p(),g=r(),_=({children:e})=>(0,g.jsx)(s,{...a({defaultValues:{departement:`05`},resolver:c(f().shape({departement:u().required(`Veuillez choisir un département dans la liste`)})),mode:`onTouched`}),children:e}),v=[{value:`01`,label:`Ain`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`02`,label:`Aisne`},{value:`03`,label:`Allier`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`04`,label:`Alpes-de-Haute-Provence test de libellé très long`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`05`,label:`Hautes-Alpes`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`06`,label:`Alpes-Maritimes`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`07`,label:`Ardèche`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`08`,label:`Ardennes`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`09`,label:`Ariège`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`10`,label:`Aube`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`11`,label:`Aude`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`12`,label:`Aveyron`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`13`,label:`Bouches-du-Rhône`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`14`,label:`Calvados`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`15`,label:`Cantal`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`}],y={title:`@/ui-kit/forms/SelectAutocomplete`,component:m},b={wrapper:{color:`#666`,fontSize:`0.8rem`,padding:`0 1rem`,backgroundColor:`#f5f5f5`,borderRadius:`0.2rem`,border:`thin solid #e1e1e1`,minHeight:`45px`,marginBottom:`1rem`,display:`flex`,alignItems:`center`},pre:{display:`inline-block`,padding:`0.5rem`}},x={args:{name:`departement`,label:`Département`,options:v,required:!1,shouldResetOnOpen:!0}},S={args:{name:`departement`,label:`Département`,options:v,required:!1,shouldResetOnOpen:!1,value:`05`}},C={render:()=>{let[e,t]=(0,h.useState)(``);return(0,g.jsxs)(g.Fragment,{children:[(0,g.jsxs)(`div`,{style:b.wrapper,children:[`Search text value: `,(0,g.jsx)(`pre`,{style:b.pre,children:e})]}),(0,g.jsx)(m,{label:`Département`,name:`departement`,options:v,required:!1,onSearch:e=>t(e)})]})}},w={decorators:[e=>(0,g.jsx)(_,{children:(0,g.jsx)(e,{})})],render:()=>{let{register:e,watch:t,formState:{errors:n}}=o(),r=t(`departement`);return(0,g.jsxs)(g.Fragment,{children:[(0,g.jsxs)(`div`,{style:b.wrapper,children:[`Selected value in the form:`,` `,(0,g.jsx)(`pre`,{style:b.pre,children:r})]}),(0,g.jsx)(m,{label:`Département`,options:v,...e(`departement`),error:n.departement?.message})]})}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    required: false,
    shouldResetOnOpen: true
  }
}`,...x.parameters?.docs?.source}}},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    required: false,
    shouldResetOnOpen: false,
    value: '05'
  }
}`,...S.parameters?.docs?.source}}},C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`{
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
}`,...C.parameters?.docs?.source}}},w.parameters={...w.parameters,docs:{...w.parameters?.docs,source:{originalSource:`{
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
}`,...w.parameters?.docs?.source}}},T=[`Default`,`NoResetOnOpen`,`WithOnsearchTrigger`,`WithinFormValidation`]}))();export{x as Default,S as NoResetOnOpen,C as WithOnsearchTrigger,w as WithinFormValidation,T as __namedExportsOrder,y as default};