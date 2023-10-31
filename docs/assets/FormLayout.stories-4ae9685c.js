import{j as o}from"./jsx-runtime-ffb262ed.js";import{c as x}from"./formik.esm-104d8394.js";import"./Divider-7c035ea9.js";import"./SubmitButton-66b6b99e.js";import{B as m,a as L}from"./Button-64288dd7.js";import{T as e}from"./Thumb-1dde1204.js";import"./stroke-show-579dd273.js";import"./Banner-650e7c30.js";import"./InfoBox-295abe36.js";import{F as t}from"./FormLayout-a2f35473.js";import"./index-76fb7be0.js";import"./_commonjsHelpers-de833af9.js";import"./hoist-non-react-statics.cjs-3f8ebaa8.js";import"./index-a587463d.js";import"./index-9d82e518.js";import"./full-right-83efe067.js";import"./SvgIcon-c0bf369c.js";import"./Button.module-a8fe741a.js";import"./stroke-pass-cf331655.js";import"./Tooltip-7f0a196a.js";import"./useTooltipProps-b20503ef.js";import"./full-next-ebff3494.js";import"./BaseCheckbox-10462bad.js";import"./BaseFileInput-aa929aed.js";import"./BaseRadio-06d1d75a.js";import"./FieldError-10cbd29d.js";import"./stroke-error-ed5fe82d.js";import"./FieldSuccess-31bdacb0.js";import"./stroke-valid-9c345a33.js";import"./full-clear-9268779e.js";import"./index-9d475cdf.js";import"./typeof-7fd5df1e.js";import"./BaseInput-433b1c48.js";import"./stroke-close-3a7bfe9e.js";import"./shadow-tips-help-841f916a.js";import"./shadow-tips-warning-66fb0429.js";import"./LinkNodes-2a267152.js";import"./full-link-9eb5e1cb.js";const eo={title:"components/FormLayout",component:t},y=n=>o.jsx("div",{style:{width:780},children:o.jsxs(t,{...n,children:[o.jsx(t.Section,{description:"Lorem ipsum dolor sit amet",title:"Lorem ipsum dolor sit amet",children:o.jsx(t.Row,{children:o.jsxs("label",{children:["Hello",o.jsx("input",{type:"text"})]})})}),o.jsxs(t.Section,{description:"Lorem ipsum dolor sit amet",title:"Lorem ipsum dolor sit amet",children:[o.jsx(t.Row,{children:o.jsxs("label",{children:["Hello",o.jsx("input",{type:"text"})]})}),o.jsx(t.SubSection,{title:"Sub section title",children:o.jsxs(t.Row,{inline:!0,children:[o.jsxs("label",{children:["Hello",o.jsx("input",{type:"text"})]}),o.jsxs("label",{children:["Hello",o.jsx("input",{type:"text"})]})]})})]}),o.jsxs(t.Actions,{children:[o.jsx("button",{type:"button",children:"Annuler"}),o.jsx("button",{type:"button",children:"Envoyer"})]})]})}),i=y.bind({});i.args={small:!1};const s=()=>o.jsxs("div",{children:[o.jsx("h4",{children:"Information sur champs"}),o.jsx("p",{children:"Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet sit amet"})]}),b=n=>o.jsx("div",{style:{width:850},children:o.jsx(x,{initialValues:{},onSubmit:()=>alert("Form submit !"),children:o.jsxs(t,{...n,children:[o.jsxs(t.Section,{description:"Lorem ipsum dolor sit amet",title:"Lorem ipsum dolor sit amet",children:[o.jsx(t.Row,{sideComponent:o.jsx(s,{}),children:o.jsx(e,{label:"Nom",name:"lastname"})}),o.jsx(t.Row,{children:o.jsx(e,{label:"Tel",name:"Tel"})}),o.jsx(t.Row,{children:o.jsx(e,{label:"Mail",name:"mail"})}),o.jsx(t.Row,{children:o.jsx(e,{label:"Jambon",name:"ham"})})]}),o.jsxs(t.Section,{description:"Lorem ipsum dolor sit amet",title:"Lorem ipsum dolor sit amet",children:[o.jsx(t.Row,{sideComponent:null,children:o.jsx(e,{label:"Prénom",name:"firstname"})}),o.jsx(t.SubSection,{title:"Sub section title",children:o.jsx(t.Row,{inline:!0,sideComponent:o.jsx(s,{}),children:o.jsxs(o.Fragment,{children:[o.jsx(e,{label:"Prénom",name:"firstname"}),o.jsx(e,{label:"Nom",name:"lastname"})]})})})]}),o.jsxs(t.Actions,{children:[o.jsx(m,{variant:L.SECONDARY,children:"Annuler"}),o.jsx(m,{children:"Envoyer"})]})]})})}),r=b.bind({});r.args={small:!0};var l,a,u;i.parameters={...i.parameters,docs:{...(l=i.parameters)==null?void 0:l.docs,source:{originalSource:`args => <div style={{
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
  </div>`,...(u=(a=i.parameters)==null?void 0:a.docs)==null?void 0:u.source}}};var p,d,c;r.parameters={...r.parameters,docs:{...(p=r.parameters)==null?void 0:p.docs,source:{originalSource:`args => <div style={{
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
  </div>`,...(c=(d=r.parameters)==null?void 0:d.docs)==null?void 0:c.source}}};const io=["Default","Designed"];export{i as Default,r as Designed,io as __namedExportsOrder,eo as default};
//# sourceMappingURL=FormLayout.stories-4ae9685c.js.map
