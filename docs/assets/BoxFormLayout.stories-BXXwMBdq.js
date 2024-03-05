import{j as e}from"./jsx-runtime-vNq4Oc-g.js";import{u as c,F as y,a as x}from"./formik.esm-ymFmkpzG.js";import{r as f}from"./index-4g5l5LRQ.js";import{F as n}from"./index-z1pkEVGR.js";import"./Divider-RocaqWVQ.js";import{S as F}from"./SubmitButton-Bl3Kc9XW.js";import{B as _}from"./ButtonLink-iC8iNd8u.js";import{B}from"./Button-Wmu66FbF.js";import{T as l}from"./Thumb-0eo5GemF.js";import"./stroke-offer-kjKFmafA.js";import"./Banner-usFi2Sq1.js";import"./InfoBox-PhRJYNPY.js";import{B as h}from"./BoxRounded-sgD7gEa1.js";import{c as i}from"./index-XNbs-YUW.js";import"./_commonjsHelpers-4gQjN7DL.js";import"./Callout-k7xmnO-J.js";import"./full-info-y_GgizFl.js";import"./full-validate-UsEvEnOv.js";import"./full-warning-sCBth3ad.js";import"./stroke-close-KQNU-49n.js";import"./SvgIcon-QVOPtTle.js";import"./LinkNodes-LX9WZqgT.js";import"./full-link-GGegv9yK.js";import"./full-next-6FYpialQ.js";import"./index-VkxvJQxW.js";import"./index-CQtvWCGL.js";import"./Button.module-fn58QZwY.js";import"./stroke-pass-84wyy11D.js";import"./Tooltip-kKBX527K.js";import"./useTooltipProps-5VZ0BXiJ.js";import"./BaseRadio-FPTZu85Z.js";import"./FieldError-Tc_LJzie.js";import"./stroke-error-U5wg3Vd5.js";import"./FieldSuccess-GGwnsLIr.js";import"./stroke-valid-qcZpl8lN.js";import"./full-clear-0L2gsxg_.js";import"./index-VFMbf6KQ.js";import"./SelectInput-6KaGHNHr.js";import"./stroke-down-4xbrRvHV.js";import"./BaseCheckbox-ktuHWrzJ.js";import"./typeof-Q9eVcF_1.js";import"./BaseInput-AweWbigz.js";import"./shadow-tips-help-vs0tLBP5.js";import"./shadow-tips-warning-og_aO0Ug.js";import"./full-edit--NrgCQQr.js";const t={"box-form-layout":"_box-form-layout_o65z6_1","box-form-layout-header-title":"_box-form-layout-header-title_o65z6_5","box-form-layout-fields":"_box-form-layout-fields_o65z6_10","box-form-layout-form-header":"_box-form-layout-form-header_o65z6_14","box-form-layout-form-header-secondary":"_box-form-layout-form-header-secondary_o65z6_18","box-form-layout-required-message":"_box-form-layout-required-message_o65z6_22"},g=({className:o,banner:r})=>e.jsx("div",{className:i(t["box-form-layout-banner"],o),children:r});try{BoxFormLayoutBanner.displayName="BoxFormLayoutBanner",BoxFormLayoutBanner.__docgenInfo={description:"",displayName:"BoxFormLayoutBanner",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},banner:{defaultValue:null,description:"",name:"banner",required:!0,type:{name:"ReactNode"}}}}}catch{}const b=({className:o,children:r})=>e.jsx("div",{className:i(t["box-form-layout-fields"],o),children:r});try{BoxFormLayoutFields.displayName="BoxFormLayoutFields",BoxFormLayoutFields.__docgenInfo={description:"",displayName:"BoxFormLayoutFields",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const L=({className:o,textPrimary:r,textSecondary:s})=>e.jsxs("div",{className:i(t["box-form-layout-form-header"],o),children:[e.jsx("span",{className:t["box-form-layout-form-header-secondary"],children:s})," : ",e.jsx("span",{children:r})]});try{BoxFormLayoutFormHeader.displayName="BoxFormLayoutFormHeader",BoxFormLayoutFormHeader.__docgenInfo={description:"",displayName:"BoxFormLayoutFormHeader",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},textPrimary:{defaultValue:null,description:"",name:"textPrimary",required:!0,type:{name:"string"}},textSecondary:{defaultValue:null,description:"",name:"textSecondary",required:!0,type:{name:"string"}}}}}catch{}const N=({className:o,subtitle:r,title:s})=>e.jsxs("div",{className:i(t["box-form-layout-header"],o),children:[e.jsx("div",{className:t["box-form-layout-header-title"],children:s}),e.jsx("div",{className:t["box-form-layout-header-subtitle"],children:r})]});try{BoxFormLayoutHeader.displayName="BoxFormLayoutHeader",BoxFormLayoutHeader.__docgenInfo={description:"",displayName:"BoxFormLayoutHeader",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},subtitle:{defaultValue:null,description:"",name:"subtitle",required:!0,type:{name:"string"}},title:{defaultValue:null,description:"",name:"title",required:!0,type:{name:"string"}}}}}catch{}const j=({className:o})=>e.jsx(n.MandatoryInfo,{className:i(t["box-form-layout-required-message"],o)});try{BoxFormLayoutRequiredMessage.displayName="BoxFormLayoutRequiredMessage",BoxFormLayoutRequiredMessage.__docgenInfo={description:"",displayName:"BoxFormLayoutRequiredMessage",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const a=({children:o,className:r})=>e.jsx("div",{className:i(t["box-form-layout"],r),children:o});a.Header=N;a.Banner=g;a.Fields=b;a.FormHeader=L;a.RequiredMessage=j;try{a.displayName="BoxFormLayout",a.__docgenInfo={description:"",displayName:"BoxFormLayout",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const S=()=>{const[o,r]=f.useState(!1),s=c({initialValues:{email:"",password:""},onSubmit:()=>{s.setSubmitting(!1),r(!1)},validateOnChange:!1});return e.jsx(a,{children:e.jsx(h,{onClickModify:()=>r(!0),showButtonModify:!o,children:o?e.jsxs(e.Fragment,{children:[e.jsx(a.RequiredMessage,{}),e.jsx(a.Fields,{children:e.jsx(y,{value:s,children:e.jsxs(x,{onSubmit:s.handleSubmit,children:[e.jsxs(n,{children:[e.jsx(n.Row,{children:e.jsx(l,{label:"Nouvelle adresse email",name:"email",placeholder:"email@exemple.com"})}),e.jsx(n.Row,{children:e.jsx(l,{label:"Mot de passe (requis pour modifier votre email)",name:"password",type:"password"})})]}),e.jsxs("div",{children:[e.jsx(B,{style:{marginTop:24,marginRight:24},onClick:()=>r(!1),variant:_.SECONDARY,children:"Annuler"}),e.jsx(F,{isLoading:s.isSubmitting,children:"Enregistrer"})]})]})})})]}):e.jsx(e.Fragment,{children:e.jsx(a.Header,{subtitle:"Je suis le sous-titre",title:"Adresse email"})})})})},m=S.bind({});m.storyName="Box Form Layout";const _e={title:"components/BoxFormLayout"};var d,u,p;m.parameters={...m.parameters,docs:{...(d=m.parameters)==null?void 0:d.docs,source:{originalSource:`() => {
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
                    <SubmitButton isLoading={formik.isSubmitting}>
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
}`,...(p=(u=m.parameters)==null?void 0:u.docs)==null?void 0:p.source}}};const Be=["BasicBoxFormLayout"];export{m as BasicBoxFormLayout,Be as __namedExportsOrder,_e as default};
