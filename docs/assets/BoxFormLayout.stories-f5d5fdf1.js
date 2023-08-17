import{j as e}from"./jsx-runtime-ffb262ed.js";import{u as c,F as y,d as x}from"./formik.esm-d2c4e539.js";import{r as f}from"./index-76fb7be0.js";import{F as l}from"./FormLayout-2c82bba0.js";import"./Divider-7c035ea9.js";import{S as F}from"./SubmitButton-5bfc815d.js";import"./Tag-2c2f8155.js";import{B as _,a as B}from"./Button-3c00c379.js";import{T as n}from"./TextInput-032a83b6.js";import"./TextArea-845d5a84.js";import"./Select-56684ba7.js";import"./RadioButton-024b03f5.js";import"./EmailSpellCheckInput-9aeb6872.js";import"./DatePicker-d2e9df6e.js";import"./TimePicker-4c8db26e.js";import"./MultiSelectAutocomplete-0d740c35.js";import"./stroke-offer-3e15095b.js";import"./Banner-aca798cf.js";import"./InfoBox-caa25892.js";import"./Thumb-df00323d.js";import{B as h}from"./BoxRounded-0f9c18b7.js";import{c as i}from"./index-a587463d.js";import"./_commonjsHelpers-de833af9.js";import"./hoist-non-react-statics.cjs-3f8ebaa8.js";import"./stroke-close-3a7bfe9e.js";import"./SvgIcon-c0bf369c.js";import"./index-76bbc159.js";import"./full-right-83efe067.js";import"./Tooltip-383b3df2.js";import"./stroke-pass-cf331655.js";import"./BaseCheckbox-2cbf2f9d.js";import"./BaseFileInput-5547a44b.js";import"./stroke-down-fe50db78.js";import"./BaseInput-fad17e7a.js";import"./AutocompleteList-8264ed5d.js";import"./BaseRadio-dfa7f1ae.js";import"./full-clear-9268779e.js";import"./FieldError-0089fdbc.js";import"./stroke-error-ed5fe82d.js";import"./FieldSuccess-31bdacb0.js";import"./stroke-valid-9c345a33.js";import"./index-9d475cdf.js";import"./full-next-ebff3494.js";import"./Checkbox-a77ebae6.js";import"./CheckboxGroup-7378cf78.js";import"./stroke-show-1133cf8e.js";import"./utils-70f14cd5.js";import"./typeof-7fd5df1e.js";import"./index-564ee5c9.js";import"./getLabelString-a0462018.js";import"./shadow-tips-help-841f916a.js";import"./shadow-tips-warning-66fb0429.js";import"./LinkNodes-25866b44.js";import"./full-link-9eb5e1cb.js";import"./full-edit-fa9e4e17.js";const t={"box-form-layout":"_box-form-layout_o65z6_1","box-form-layout-header-title":"_box-form-layout-header-title_o65z6_5","box-form-layout-fields":"_box-form-layout-fields_o65z6_10","box-form-layout-form-header":"_box-form-layout-form-header_o65z6_14","box-form-layout-form-header-secondary":"_box-form-layout-form-header-secondary_o65z6_18","box-form-layout-required-message":"_box-form-layout-required-message_o65z6_22"},g=({className:o,banner:r})=>e.jsx("div",{className:i(t["box-form-layout-banner"],o),children:r});try{BoxFormLayoutBanner.displayName="BoxFormLayoutBanner",BoxFormLayoutBanner.__docgenInfo={description:"",displayName:"BoxFormLayoutBanner",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},banner:{defaultValue:null,description:"",name:"banner",required:!0,type:{name:"ReactNode"}}}}}catch{}const b=({className:o,children:r})=>e.jsx("div",{className:i(t["box-form-layout-fields"],o),children:r});try{BoxFormLayoutFields.displayName="BoxFormLayoutFields",BoxFormLayoutFields.__docgenInfo={description:"",displayName:"BoxFormLayoutFields",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const L=({className:o,textPrimary:r,textSecondary:s})=>e.jsxs("div",{className:i(t["box-form-layout-form-header"],o),children:[e.jsx("span",{className:t["box-form-layout-form-header-secondary"],children:s})," : ",e.jsx("span",{children:r})]});try{BoxFormLayoutFormHeader.displayName="BoxFormLayoutFormHeader",BoxFormLayoutFormHeader.__docgenInfo={description:"",displayName:"BoxFormLayoutFormHeader",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},textPrimary:{defaultValue:null,description:"",name:"textPrimary",required:!0,type:{name:"string"}},textSecondary:{defaultValue:null,description:"",name:"textSecondary",required:!0,type:{name:"string"}}}}}catch{}const N=({className:o,subtitle:r,title:s})=>e.jsxs("div",{className:i(t["box-form-layout-header"],o),children:[e.jsx("div",{className:t["box-form-layout-header-title"],children:s}),e.jsx("div",{className:t["box-form-layout-header-subtitle"],children:r})]});try{BoxFormLayoutHeader.displayName="BoxFormLayoutHeader",BoxFormLayoutHeader.__docgenInfo={description:"",displayName:"BoxFormLayoutHeader",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},subtitle:{defaultValue:null,description:"",name:"subtitle",required:!0,type:{name:"string"}},title:{defaultValue:null,description:"",name:"title",required:!0,type:{name:"string"}}}}}catch{}const j=({className:o})=>e.jsx(l.MandatoryInfo,{className:i(t["box-form-layout-required-message"],o)});try{BoxFormLayoutRequiredMessage.displayName="BoxFormLayoutRequiredMessage",BoxFormLayoutRequiredMessage.__docgenInfo={description:"",displayName:"BoxFormLayoutRequiredMessage",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const a=({children:o,className:r})=>e.jsx("div",{className:i(t["box-form-layout"],r),children:o});a.Header=N;a.Banner=g;a.Fields=b;a.FormHeader=L;a.RequiredMessage=j;try{a.displayName="BoxFormLayout",a.__docgenInfo={description:"",displayName:"BoxFormLayout",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const S=()=>{const[o,r]=f.useState(!1),s=c({initialValues:{email:"",password:""},onSubmit:()=>{s.setSubmitting(!1),r(!1)},validateOnChange:!1});return e.jsx(a,{children:e.jsx(h,{onClickModify:()=>r(!0),showButtonModify:!o,children:o?e.jsxs(e.Fragment,{children:[e.jsx(a.RequiredMessage,{}),e.jsx(a.Fields,{children:e.jsx(y,{value:s,children:e.jsxs(x,{onSubmit:s.handleSubmit,children:[e.jsxs(l,{children:[e.jsx(l.Row,{children:e.jsx(n,{label:"Nouvelle adresse email",name:"email",placeholder:"email@exemple.com"})}),e.jsx(l.Row,{children:e.jsx(n,{label:"Mot de passe (requis pour modifier votre email)",name:"password",type:"password"})})]}),e.jsxs("div",{children:[e.jsx(_,{style:{marginTop:24,marginRight:24},onClick:()=>r(!1),variant:B.SECONDARY,children:"Annuler"}),e.jsx(F,{className:"primary-button",isLoading:s.isSubmitting,children:"Enregistrer"})]})]})})})]}):e.jsx(e.Fragment,{children:e.jsx(a.Header,{subtitle:"Je suis le sous-titre",title:"Adresse email"})})})})},m=S.bind({});m.storyName="Box Form Layout";const ve={title:"components/BoxFormLayout"};var d,u,p;m.parameters={...m.parameters,docs:{...(d=m.parameters)==null?void 0:d.docs,source:{originalSource:`() => {
  const [showForm, setShowForm] = useState(false);
  const formik = useFormik({
    initialValues: {
      email: '',
      password: ''
    },
    onSubmit: () => {
      formik.setSubmitting(false);
      setShowForm(false);
    },
    validateOnChange: false
  });
  return <BoxFormLayout>
      <BoxRounded onClickModify={() => setShowForm(true)} showButtonModify={!showForm}>
        {showForm ? <>
            <BoxFormLayout.RequiredMessage />
            <BoxFormLayout.Fields>
              <FormikProvider value={formik}>
                <Form onSubmit={formik.handleSubmit}>
                  <FormLayout>
                    <FormLayout.Row>
                      <TextInput label="Nouvelle adresse email" name="email" placeholder="email@exemple.com" />
                    </FormLayout.Row>
                    <FormLayout.Row>
                      <TextInput label="Mot de passe (requis pour modifier votre email)" name="password" type="password" />
                    </FormLayout.Row>
                  </FormLayout>
                  <div>
                    <Button style={{
                  marginTop: 24,
                  marginRight: 24
                }} onClick={() => setShowForm(false)} variant={ButtonVariant.SECONDARY}>
                      Annuler
                    </Button>
                    <SubmitButton className="primary-button" isLoading={formik.isSubmitting}>
                      Enregistrer
                    </SubmitButton>
                  </div>
                </Form>
              </FormikProvider>
            </BoxFormLayout.Fields>
          </> : <>
            <BoxFormLayout.Header subtitle={'Je suis le sous-titre'} title="Adresse email" />
          </>}
      </BoxRounded>
    </BoxFormLayout>;
}`,...(p=(u=m.parameters)==null?void 0:u.docs)==null?void 0:p.source}}};const we=["BasicBoxFormLayout"];export{m as BasicBoxFormLayout,we as __namedExportsOrder,ve as default};
//# sourceMappingURL=BoxFormLayout.stories-f5d5fdf1.js.map
