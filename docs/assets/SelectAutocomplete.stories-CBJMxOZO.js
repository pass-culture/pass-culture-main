import{n as e}from"./rolldown-runtime-DkW27tQK.js";import{d as t}from"./iframe-D81rFjU2.js";import{t as n}from"./jsx-runtime-DeHZSEgm.js";import{i as r,o as i,s as a,t as o}from"./index.esm-Dzpau52a.js";import{a as s,i as c,n as l,r as u,t as d}from"./index.esm-iuNOH-F2.js";import{n as f,t as p}from"./SelectAutocomplete-CP5hhTO_.js";var m,h,g,_,v,y,b,x,S,C,w;function T(){return(T=e((()=>{c(),m=t(),r(),u(),f(),h=n(),g=({children:e})=>{let t=i({defaultValues:{departement:`05`},resolver:s(d().shape({departement:l().required(`Veuillez choisir un département dans la liste`)})),mode:`onTouched`});return(0,h.jsx)(o,{...t,children:e})},_=[{value:`01`,label:`Ain`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`02`,label:`Aisne`},{value:`03`,label:`Allier`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`04`,label:`Alpes-de-Haute-Provence test de libellé très long`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`05`,label:`Hautes-Alpes`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`06`,label:`Alpes-Maritimes`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`07`,label:`Ardèche`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`08`,label:`Ardennes`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`09`,label:`Ariège`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`10`,label:`Aube`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`11`,label:`Aude`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`12`,label:`Aveyron`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`13`,label:`Bouches-du-Rhône`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`14`,label:`Calvados`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`15`,label:`Cantal`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`}],v={title:`@/ui-kit/forms/SelectAutocomplete`,component:p},y={wrapper:{color:`#666`,fontSize:`0.8rem`,padding:`0 1rem`,backgroundColor:`#f5f5f5`,borderRadius:`0.2rem`,border:`thin solid #e1e1e1`,minHeight:`45px`,marginBottom:`1rem`,display:`flex`,alignItems:`center`},pre:{display:`inline-block`,padding:`0.5rem`}},b={args:{name:`departement`,label:`Département`,options:_,required:!1,shouldResetOnOpen:!0}},x={args:{name:`departement`,label:`Département`,options:_,required:!1,shouldResetOnOpen:!1,value:`05`}},S={render:()=>{let[e,t]=(0,m.useState)(``);return(0,h.jsxs)(h.Fragment,{children:[(0,h.jsxs)(`div`,{style:y.wrapper,children:[`Search text value: `,(0,h.jsx)(`pre`,{style:y.pre,children:e})]}),(0,h.jsx)(p,{label:`Département`,name:`departement`,options:_,required:!1,onSearch:e=>t(e)})]})}},C={decorators:[e=>(0,h.jsx)(g,{children:(0,h.jsx)(e,{})})],render:()=>{let{register:e,watch:t,formState:{errors:n}}=a(),r=t(`departement`);return(0,h.jsxs)(h.Fragment,{children:[(0,h.jsxs)(`div`,{style:y.wrapper,children:[`Selected value in the form:`,` `,(0,h.jsx)(`pre`,{style:y.pre,children:r})]}),(0,h.jsx)(p,{label:`Département`,options:_,...e(`departement`),error:n.departement?.message})]})}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    required: false,
    shouldResetOnOpen: true
  }
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    required: false,
    shouldResetOnOpen: false,
    value: '05'
  }
}`,...x.parameters?.docs?.source}}},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  render: () => {
    const [searchText, setSearchText] = useState('');
    return <>
        <div style={demoStyles['wrapper']}>
          Search text value: <pre style={demoStyles['pre']}>{searchText}</pre>
        </div>

        <SelectAutocomplete label="Département" name="departement" options={options} required={false} onSearch={text => setSearchText(text)} />
      </>;
  }
}`,...S.parameters?.docs?.source}}},C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`{
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
}`,...C.parameters?.docs?.source}}},w=[`Default`,`NoResetOnOpen`,`WithOnsearchTrigger`,`WithinFormValidation`]})))()}T();export{b as Default,x as NoResetOnOpen,S as WithOnsearchTrigger,C as WithinFormValidation,w as __namedExportsOrder,v as default};