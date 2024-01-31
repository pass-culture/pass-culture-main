import{j as o}from"./jsx-runtime-iXOPPpZ7.js";import{b as x}from"./formik.esm-y2tUiI7x.js";import"./Divider-Bz64tZ7o.js";import"./SubmitButton-O9BTAZP-.js";import{B as m,a as L}from"./Button-8IihqDqY.js";import{T as e}from"./Thumb-q4ZX0JjJ.js";import"./stroke-offer-vqhbfYxZ.js";import"./Banner-t8EdiXMJ.js";import"./InfoBox-pbhRsQAz.js";import{F as t}from"./index-0w8z2L7Z.js";import"./index-7OBYoplD.js";import"./_commonjsHelpers-4gQjN7DL.js";import"./index-XNbs-YUW.js";import"./index-Odt4icYv.js";import"./index-NZh7eYUr.js";import"./SvgIcon-UUSKXfrA.js";import"./Button.module-yhzTO7gk.js";import"./stroke-pass-84wyy11D.js";import"./Tooltip-ryJtHgPl.js";import"./useTooltipProps-Xf9SOXrU.js";import"./full-next-6FYpialQ.js";import"./BaseCheckbox-Q_oD9jls.js";import"./BaseFileInput-L1z9lXK8.js";import"./BaseRadio-NI7qJIMy.js";import"./FieldError-_oiQB8Lp.js";import"./stroke-error-U5wg3Vd5.js";import"./FieldSuccess-KBPQwpG2.js";import"./stroke-valid-qcZpl8lN.js";import"./full-clear-0L2gsxg_.js";import"./index-VFMbf6KQ.js";import"./SelectInput-aEEqLxEg.js";import"./stroke-down-4xbrRvHV.js";import"./typeof-Q9eVcF_1.js";import"./BaseInput-GGUmafiT.js";import"./stroke-close-KQNU-49n.js";import"./shadow-tips-help-vs0tLBP5.js";import"./shadow-tips-warning-og_aO0Ug.js";import"./LinkNodes-rxhr_AqJ.js";import"./full-link-GGegv9yK.js";const no={title:"components/FormLayout",component:t},y=r=>o.jsx("div",{style:{width:780},children:o.jsxs(t,{...r,children:[o.jsx(t.Section,{description:"Lorem ipsum dolor sit amet",title:"Lorem ipsum dolor sit amet",children:o.jsx(t.Row,{children:o.jsxs("label",{children:["Hello",o.jsx("input",{type:"text"})]})})}),o.jsxs(t.Section,{description:"Lorem ipsum dolor sit amet",title:"Lorem ipsum dolor sit amet",children:[o.jsx(t.Row,{children:o.jsxs("label",{children:["Hello",o.jsx("input",{type:"text"})]})}),o.jsx(t.SubSection,{title:"Sub section title",children:o.jsxs(t.Row,{inline:!0,children:[o.jsxs("label",{children:["Hello",o.jsx("input",{type:"text"})]}),o.jsxs("label",{children:["Hello",o.jsx("input",{type:"text"})]})]})})]}),o.jsxs(t.Actions,{children:[o.jsx("button",{type:"button",children:"Annuler"}),o.jsx("button",{type:"button",children:"Envoyer"})]})]})}),n=y.bind({});n.args={small:!1};const s=()=>o.jsxs("div",{children:[o.jsx("h4",{children:"Information sur champs"}),o.jsx("p",{children:"Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet sit amet"})]}),b=r=>o.jsx("div",{style:{width:850},children:o.jsx(x,{initialValues:{},onSubmit:()=>alert("Form submit !"),children:o.jsxs(t,{...r,children:[o.jsxs(t.Section,{description:"Lorem ipsum dolor sit amet",title:"Lorem ipsum dolor sit amet",children:[o.jsx(t.Row,{sideComponent:o.jsx(s,{}),children:o.jsx(e,{label:"Nom",name:"lastname"})}),o.jsx(t.Row,{children:o.jsx(e,{label:"Tel",name:"Tel"})}),o.jsx(t.Row,{children:o.jsx(e,{label:"Mail",name:"mail"})}),o.jsx(t.Row,{children:o.jsx(e,{label:"Jambon",name:"ham"})})]}),o.jsxs(t.Section,{description:"Lorem ipsum dolor sit amet",title:"Lorem ipsum dolor sit amet",children:[o.jsx(t.Row,{sideComponent:null,children:o.jsx(e,{label:"Prénom",name:"firstname"})}),o.jsx(t.SubSection,{title:"Sub section title",children:o.jsx(t.Row,{inline:!0,sideComponent:o.jsx(s,{}),children:o.jsxs(o.Fragment,{children:[o.jsx(e,{label:"Prénom",name:"firstname"}),o.jsx(e,{label:"Nom",name:"lastname"})]})})})]}),o.jsxs(t.Actions,{children:[o.jsx(m,{variant:L.SECONDARY,children:"Annuler"}),o.jsx(m,{children:"Envoyer"})]})]})})}),i=b.bind({});i.args={small:!0};var l,a,u;n.parameters={...n.parameters,docs:{...(l=n.parameters)==null?void 0:l.docs,source:{originalSource:`args => <div style={{
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
  </div>`,...(u=(a=n.parameters)==null?void 0:a.docs)==null?void 0:u.source}}};var p,d,c;i.parameters={...i.parameters,docs:{...(p=i.parameters)==null?void 0:p.docs,source:{originalSource:`args => <div style={{
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
  </div>`,...(c=(d=i.parameters)==null?void 0:d.docs)==null?void 0:c.source}}};const io=["Default","Designed"];export{n as Default,i as Designed,io as __namedExportsOrder,no as default};
