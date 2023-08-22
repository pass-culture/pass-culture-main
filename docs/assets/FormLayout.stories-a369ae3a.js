import{j as o}from"./jsx-runtime-ffb262ed.js";import{b as x}from"./formik.esm-d2c4e539.js";import"./Divider-7c035ea9.js";import"./SubmitButton-5bfc815d.js";import"./Tag-2c2f8155.js";import{B as n,a as L}from"./Button-3c00c379.js";import{T as e}from"./TextInput-77016454.js";import"./TextArea-9c4b842d.js";import"./Select-b2484593.js";import"./RadioButton-3679d57d.js";import"./EmailSpellCheckInput-43beaa11.js";import"./DatePicker-23ec506e.js";import"./TimePicker-63ef8aa4.js";import"./MultiSelectAutocomplete-e63951c3.js";import"./stroke-offer-3e15095b.js";import"./Banner-aca798cf.js";import"./InfoBox-caa25892.js";import"./Thumb-df00323d.js";import{F as t}from"./FormLayout-ceb11561.js";import"./index-76fb7be0.js";import"./_commonjsHelpers-de833af9.js";import"./hoist-non-react-statics.cjs-3f8ebaa8.js";import"./index-a587463d.js";import"./stroke-close-3a7bfe9e.js";import"./SvgIcon-c0bf369c.js";import"./index-76bbc159.js";import"./full-right-83efe067.js";import"./Tooltip-383b3df2.js";import"./stroke-pass-cf331655.js";import"./BaseCheckbox-58c59efd.js";import"./BaseFileInput-5547a44b.js";import"./stroke-down-10f026f9.js";import"./BaseInput-be025c1d.js";import"./AutocompleteList-7ebf0db4.js";import"./BaseRadio-dfa7f1ae.js";import"./full-clear-9268779e.js";import"./FieldError-0089fdbc.js";import"./stroke-error-ed5fe82d.js";import"./FieldSuccess-31bdacb0.js";import"./stroke-valid-9c345a33.js";import"./index-9d475cdf.js";import"./full-next-ebff3494.js";import"./Checkbox-c363f83f.js";import"./CheckboxGroup-109fa7f4.js";import"./stroke-show-1133cf8e.js";import"./utils-70f14cd5.js";import"./typeof-7fd5df1e.js";import"./index-564ee5c9.js";import"./getLabelString-a0462018.js";import"./shadow-tips-help-841f916a.js";import"./shadow-tips-warning-66fb0429.js";import"./LinkNodes-25866b44.js";import"./full-link-9eb5e1cb.js";const jo={title:"components/FormLayout",component:t},y=m=>o.jsx("div",{style:{width:780},children:o.jsxs(t,{...m,children:[o.jsx(t.Section,{description:"Lorem ipsum dolor sit amet",title:"Lorem ipsum dolor sit amet",children:o.jsx(t.Row,{children:o.jsxs("label",{children:["Hello",o.jsx("input",{type:"text"})]})})}),o.jsxs(t.Section,{description:"Lorem ipsum dolor sit amet",title:"Lorem ipsum dolor sit amet",children:[o.jsx(t.Row,{children:o.jsxs("label",{children:["Hello",o.jsx("input",{type:"text"})]})}),o.jsx(t.SubSection,{title:"Sub section title",children:o.jsxs(t.Row,{inline:!0,children:[o.jsxs("label",{children:["Hello",o.jsx("input",{type:"text"})]}),o.jsxs("label",{children:["Hello",o.jsx("input",{type:"text"})]})]})})]}),o.jsxs(t.Actions,{children:[o.jsx("button",{type:"button",children:"Annuler"}),o.jsx("button",{type:"button",children:"Envoyer"})]})]})}),i=y.bind({});i.args={small:!1};const s=()=>o.jsxs("div",{children:[o.jsx("h4",{children:"Information sur champs"}),o.jsx("p",{children:"Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet sit amet"})]}),b=m=>o.jsx("div",{style:{width:850},children:o.jsx(x,{initialValues:{},onSubmit:()=>alert("Form submit !"),children:o.jsxs(t,{...m,children:[o.jsxs(t.Section,{description:"Lorem ipsum dolor sit amet",title:"Lorem ipsum dolor sit amet",children:[o.jsx(t.Row,{sideComponent:o.jsx(s,{}),children:o.jsx(e,{label:"Nom",name:"lastname"})}),o.jsx(t.Row,{children:o.jsx(e,{label:"Tel",name:"Tel"})}),o.jsx(t.Row,{children:o.jsx(e,{label:"Mail",name:"mail"})}),o.jsx(t.Row,{children:o.jsx(e,{label:"Jambon",name:"ham"})})]}),o.jsxs(t.Section,{description:"Lorem ipsum dolor sit amet",title:"Lorem ipsum dolor sit amet",children:[o.jsx(t.Row,{sideComponent:null,children:o.jsx(e,{label:"Prénom",name:"firstname"})}),o.jsx(t.SubSection,{title:"Sub section title",children:o.jsx(t.Row,{inline:!0,sideComponent:o.jsx(s,{}),children:o.jsxs(o.Fragment,{children:[o.jsx(e,{label:"Prénom",name:"firstname"}),o.jsx(e,{label:"Nom",name:"lastname"})]})})})]}),o.jsxs(t.Actions,{children:[o.jsx(n,{variant:L.SECONDARY,children:"Annuler"}),o.jsx(n,{children:"Envoyer"})]})]})})}),r=b.bind({});r.args={small:!0};var l,a,p;i.parameters={...i.parameters,docs:{...(l=i.parameters)==null?void 0:l.docs,source:{originalSource:`args => <div style={{
  width: 780
}}>
    <FormLayout {...args}>
      <FormLayout.Section description="Lorem ipsum dolor sit amet" title="Lorem ipsum dolor sit amet">
        <FormLayout.Row>
          <label>
            Hello
            <input type="text" />
          </label>
        </FormLayout.Row>
      </FormLayout.Section>
      <FormLayout.Section description="Lorem ipsum dolor sit amet" title="Lorem ipsum dolor sit amet">
        <FormLayout.Row>
          <label>
            Hello
            <input type="text" />
          </label>
        </FormLayout.Row>
        <FormLayout.SubSection title="Sub section title">
          <FormLayout.Row inline>
            <label>
              Hello
              <input type="text" />
            </label>
            <label>
              Hello
              <input type="text" />
            </label>
          </FormLayout.Row>
        </FormLayout.SubSection>
      </FormLayout.Section>
      <FormLayout.Actions>
        <button type="button">Annuler</button>
        <button type="button">Envoyer</button>
      </FormLayout.Actions>
    </FormLayout>
  </div>`,...(p=(a=i.parameters)==null?void 0:a.docs)==null?void 0:p.source}}};var u,d,c;r.parameters={...r.parameters,docs:{...(u=r.parameters)==null?void 0:u.docs,source:{originalSource:`args => <div style={{
  width: 850
}}>
    <Formik initialValues={{}} onSubmit={() => alert('Form submit !')}>
      <FormLayout {...args}>
        <FormLayout.Section description="Lorem ipsum dolor sit amet" title="Lorem ipsum dolor sit amet">
          <FormLayout.Row sideComponent={<DemoInformationBox />}>
            <TextInput label="Nom" name="lastname" />
          </FormLayout.Row>
          <FormLayout.Row>
            <TextInput label="Tel" name="Tel" />
          </FormLayout.Row>
          <FormLayout.Row>
            <TextInput label="Mail" name="mail" />
          </FormLayout.Row>
          <FormLayout.Row>
            <TextInput label="Jambon" name="ham" />
          </FormLayout.Row>
        </FormLayout.Section>
        <FormLayout.Section description="Lorem ipsum dolor sit amet" title="Lorem ipsum dolor sit amet">
          <FormLayout.Row sideComponent={null}>
            <TextInput label="Prénom" name="firstname" />
          </FormLayout.Row>
          <FormLayout.SubSection title="Sub section title">
            <FormLayout.Row inline sideComponent={<DemoInformationBox />}>
              <>
                <TextInput label="Prénom" name="firstname" />
                <TextInput label="Nom" name="lastname" />
              </>
            </FormLayout.Row>
          </FormLayout.SubSection>
        </FormLayout.Section>
        <FormLayout.Actions>
          <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
          <Button>Envoyer</Button>
        </FormLayout.Actions>
      </FormLayout>
    </Formik>
  </div>`,...(c=(d=r.parameters)==null?void 0:d.docs)==null?void 0:c.source}}};const Fo=["Default","Designed"];export{i as Default,r as Designed,Fo as __namedExportsOrder,jo as default};
//# sourceMappingURL=FormLayout.stories-a369ae3a.js.map
