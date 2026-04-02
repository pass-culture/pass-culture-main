import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-9pzI0JWU.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{a as r,o as i,t as a}from"./index.esm-B9kbvG9l.js";import{n as o,r as s,t as c}from"./index.esm-qly5As8F.js";import{t as l}from"./SelectAutocomplete-knA--e4c.js";var u=e(t(),1),d=n(),f=({children:e})=>(0,d.jsx)(a,{...r({defaultValues:{departement:`05`},resolver:s(c().shape({departement:o().required(`Veuillez choisir un département dans la liste`)})),mode:`onTouched`}),children:e}),p=[{value:`01`,label:`Ain`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`02`,label:`Aisne`},{value:`03`,label:`Allier`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`04`,label:`Alpes-de-Haute-Provence test de libellé très long`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`05`,label:`Hautes-Alpes`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`06`,label:`Alpes-Maritimes`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`07`,label:`Ardèche`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`08`,label:`Ardennes`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`09`,label:`Ariège`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`10`,label:`Aube`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`11`,label:`Aude`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`12`,label:`Aveyron`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`13`,label:`Bouches-du-Rhône`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`14`,label:`Calvados`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`},{value:`15`,label:`Cantal`,thumbUrl:`https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg`}],m={title:`@/ui-kit/forms/SelectAutocomplete`,component:l},h={wrapper:{color:`#666`,fontSize:`0.8rem`,padding:`0 1rem`,backgroundColor:`#f5f5f5`,borderRadius:`0.2rem`,border:`thin solid #e1e1e1`,minHeight:`45px`,marginBottom:`1rem`,display:`flex`,alignItems:`center`},pre:{display:`inline-block`,padding:`0.5rem`}},g={args:{name:`departement`,label:`Département`,options:p,required:!1,shouldResetOnOpen:!0}},_={args:{name:`departement`,label:`Département`,options:p,required:!1,shouldResetOnOpen:!1,value:`05`}},v={render:()=>{let[e,t]=(0,u.useState)(``);return(0,d.jsxs)(d.Fragment,{children:[(0,d.jsxs)(`div`,{style:h.wrapper,children:[`Search text value: `,(0,d.jsx)(`pre`,{style:h.pre,children:e})]}),(0,d.jsx)(l,{label:`Département`,name:`departement`,options:p,required:!1,onSearch:e=>t(e)})]})}},y={decorators:[e=>(0,d.jsx)(f,{children:(0,d.jsx)(e,{})})],render:()=>{let{register:e,watch:t,formState:{errors:n}}=i(),r=t(`departement`);return(0,d.jsxs)(d.Fragment,{children:[(0,d.jsxs)(`div`,{style:h.wrapper,children:[`Selected value in the form:`,` `,(0,d.jsx)(`pre`,{style:h.pre,children:r})]}),(0,d.jsx)(l,{label:`Département`,options:p,...e(`departement`),error:n.departement?.message})]})}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    required: false,
    shouldResetOnOpen: true
  }
}`,...g.parameters?.docs?.source}}},_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'departement',
    label: 'Département',
    options,
    required: false,
    shouldResetOnOpen: false,
    value: '05'
  }
}`,..._.parameters?.docs?.source}}},v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
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
}`,...v.parameters?.docs?.source}}},y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
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
}`,...y.parameters?.docs?.source}}};var b=[`Default`,`NoResetOnOpen`,`WithOnsearchTrigger`,`WithinFormValidation`];export{g as Default,_ as NoResetOnOpen,v as WithOnsearchTrigger,y as WithinFormValidation,b as __namedExportsOrder,m as default};