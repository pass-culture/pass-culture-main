import{j as e}from"./jsx-runtime-BYYWji4R.js";import{u as ne,a as se,F as ie}from"./index.esm-Z2NZos4s.js";import{c as le}from"./index-DeARc5FM.js";import{r as i}from"./index-ClcD9ViR.js";import{B as oe}from"./Button-DXGZYGNf.js";import{F as de}from"./FieldError-azuIsM2E.js";import{F as ue}from"./FieldLayoutCharacterCount-WDa3y29M.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./stroke-pass-CALgybTM.js";import"./SvgIcon-CyWUmZpn.js";import"./Tooltip-BU5AxWXW.js";import"./Button.module-RJ8zZwJi.js";import"./types-DjX_gQD6.js";import"./stroke-error-DSZD431a.js";const ce="_wrapper_1wwn3_1",pe="_error_1wwn3_67",n={wrapper:ce,"text-area":"_text-area_1wwn3_5","has-error":"_has-error_1wwn3_56","template-button":"_template-button_1wwn3_61",error:pe},d=i.forwardRef(({name:r,className:l,disabled:y,description:o,label:K,maxLength:x=1e3,required:v=!1,asterisk:Q=!0,initialRows:U=7,hasTemplateButton:T=!1,wordingTemplate:w,hasDefaultPlaceholder:X,onPressTemplateButton:_,error:u,onChange:q,onBlur:V,value:Y,count:Z=!0},ee)=>{const a=i.useRef(null),[s,b]=i.useState(Y),F=i.useId(),j=i.useId(),D=i.useId(),re=(s==null?void 0:s.length)??0;i.useImperativeHandle(ee,()=>a.current);function te(){if(a.current){a.current.style.height="unset";const t=a.current.scrollHeight;a.current.style.height=`${T?t+92:t}px`}}i.useEffect(()=>{te()},[s]);const C=[`field-characters-count-description-${r}`,D];o&&C.unshift(j);const ae=()=>{w&&b(w),a.current&&(a.current.focus(),a.current.setSelectionRange(128,128)),_&&_()};return e.jsxs("div",{className:l,children:[e.jsxs("div",{className:n["input-layout-label-container"],children:[e.jsxs("label",{className:n["input-layout-label"],htmlFor:F,children:[K," ",v&&Q&&"*"]}),o&&e.jsx("span",{id:j,"data-testid":`description-${r}`,className:n["input-layout-input-description"],children:o})]}),e.jsxs("div",{className:n.wrapper,children:[e.jsx("textarea",{ref:a,"aria-invalid":!!u,"aria-describedby":C.join(" "),className:le(n["text-area"],{[n["has-error"]]:!!u}),disabled:y,id:F,rows:U,value:s,maxLength:x,"aria-required":!v,placeholder:X?"Écrivez ici...":void 0,onChange:t=>{b(t.target.value),q&&q({...t,target:{...t.target,value:t.target.value,name:r}})},onBlur:t=>{b(t.target.value),V&&V({...t,target:{...t.target,value:t.target.value,name:r}})}}),T&&e.jsx(oe,{className:n["template-button"],onClick:ae,disabled:!!(s!=null&&s.length),children:"Générer un modèle"})]}),e.jsxs("div",{className:n["input-layout-footer"],children:[e.jsx("div",{role:"alert",className:n.error,id:D,children:u&&e.jsx(de,{name:r,children:u})}),Z&&e.jsx(ue,{count:re,maxLength:x,name:r})]})]})});d.displayName="TextArea";try{d.displayName="TextArea",d.__docgenInfo={description:"",displayName:"TextArea",props:{name:{defaultValue:null,description:"The name of the textarea field.",name:"name",required:!0,type:{name:"string"}},initialRows:{defaultValue:{value:"7"},description:"The initial number of visible text lines for the control. The field will still expand indefinitely if the input is higher than this value.",name:"initialRows",required:!1,type:{name:"number"}},maxLength:{defaultValue:{value:"1000"},description:"The maximum number of characters allowed in the textarea.",name:"maxLength",required:!1,type:{name:"number"}},required:{defaultValue:{value:"false"},description:"Whether the field is optional.",name:"required",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"The label text for the textarea.",name:"label",required:!0,type:{name:"ReactNode"}},description:{defaultValue:null,description:"A description providing additional information about the textarea.",name:"description",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"Custom CSS class for the textarea component.",name:"className",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"Whether the textarea is disabled.",name:"disabled",required:!1,type:{name:"boolean"}},hasDefaultPlaceholder:{defaultValue:null,description:"",name:"hasDefaultPlaceholder",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"If the asterisk should be displayed when the field is required.",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"Error text displayed under the field. If the error is trythy, the field has the error styles.",name:"error",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"((e: { target: { value: string; name?: string; }; }) => void)"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"((e: FocusEvent<HTMLTextAreaElement, Element>) => void)"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},count:{defaultValue:{value:"true"},description:"Count of characters typed in the field. If `undefined`, the counter is not displayed.",name:"count",required:!1,type:{name:"boolean"}},hasTemplateButton:{defaultValue:{value:"false"},description:"Whether the template button should be displayed.",name:"hasTemplateButton",required:!1,type:{name:"boolean"}},wordingTemplate:{defaultValue:null,description:"Content of the templated added to the field when the template button is clicked",name:"wordingTemplate",required:!1,type:{name:"string"}},onPressTemplateButton:{defaultValue:null,description:"Callback after the template button is clicked.",name:"onPressTemplateButton",required:!1,type:{name:"(() => void)"}}}}}catch{}const me=({children:r})=>{const l=se({defaultValues:{myField:"default value"}});return e.jsx(ie,{...l,children:e.jsx("form",{children:r})})},De={title:"ui-kit/formsV2/TextArea",component:d},c={args:{name:"description",label:"Description",required:!0}},p={args:{name:"description",label:"Description",error:"This is an error"}},m={args:{name:"description",label:"Description",initialRows:20}},h={args:{name:"description",label:"Description",disabled:!0}},f={args:{name:"description",label:"Description",hasTemplateButton:!0,wordingTemplate:"Template content...",onPressTemplateButton:()=>{}}},g={args:{name:"description",label:"Description"},decorators:[r=>e.jsx(me,{children:e.jsx(r,{})})],render:r=>{const{setValue:l,watch:y}=ne();return e.jsx(d,{...r,value:y("myField"),onChange:o=>{l("myField",o.target.value)}})}};var N,W,I;c.parameters={...c.parameters,docs:{...(N=c.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    required: true
  }
}`,...(I=(W=c.parameters)==null?void 0:W.docs)==null?void 0:I.source}}};var B,S,k;p.parameters={...p.parameters,docs:{...(B=p.parameters)==null?void 0:B.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    error: 'This is an error'
  }
}`,...(k=(S=p.parameters)==null?void 0:S.docs)==null?void 0:k.source}}};var A,E,R;m.parameters={...m.parameters,docs:{...(A=m.parameters)==null?void 0:A.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    initialRows: 20
  }
}`,...(R=(E=m.parameters)==null?void 0:E.docs)==null?void 0:R.source}}};var H,P,G;h.parameters={...h.parameters,docs:{...(H=h.parameters)==null?void 0:H.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    disabled: true
  }
}`,...(G=(P=h.parameters)==null?void 0:P.docs)==null?void 0:G.source}}};var L,$,z;f.parameters={...f.parameters,docs:{...(L=f.parameters)==null?void 0:L.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    hasTemplateButton: true,
    wordingTemplate: 'Template content...',
    onPressTemplateButton: () => {}
  }
}`,...(z=($=f.parameters)==null?void 0:$.docs)==null?void 0:z.source}}};var M,O,J;g.parameters={...g.parameters,docs:{...(M=g.parameters)==null?void 0:M.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description'
  },
  decorators: [(Story: any) => <Wrapper>
        <Story />
      </Wrapper>],
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const {
      setValue,
      watch
    } = useFormContext<{
      myField: string;
    }>();
    return <TextArea {...args} value={watch('myField')} onChange={e => {
      setValue('myField', e.target.value);
    }}></TextArea>;
  }
}`,...(J=(O=g.parameters)==null?void 0:O.docs)==null?void 0:J.source}}};const Ce=["Default","WithError","WithInitialHeight","Disabled","WithGeneratedTemplate","WithinForm"];export{c as Default,h as Disabled,p as WithError,f as WithGeneratedTemplate,m as WithInitialHeight,g as WithinForm,Ce as __namedExportsOrder,De as default};
