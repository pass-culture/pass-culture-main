import{j as e}from"./jsx-runtime-DF2Pcvd1.js";import{u as se,a as ie,F as oe}from"./index.esm-BGRy545K.js";import{c as W}from"./index-DeARc5FM.js";import{r as i}from"./index-B2-qRKKC.js";import{B as le}from"./Button-C8CVdQWZ.js";import{F as de}from"./FieldError-B3RhE53I.js";import{F as ue}from"./FieldLayoutCharacterCount-DKTgIOgC.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./stroke-pass-CALgybTM.js";import"./SvgIcon-DfLnDDE5.js";import"./Tooltip-wih_D3VG.js";import"./Button.module-CpX5ULHU.js";import"./types-yVZEaApa.js";import"./stroke-error-DSZD431a.js";import"./index.module-D7-Ko2QV.js";const ce="_wrapper_1yry5_1",pe="_label_1yry5_61",me="_description_1yry5_72",he="_footer_1yry5_81",fe="_error_1yry5_88",n={wrapper:ce,"text-area":"_text-area_1yry5_5","has-error":"_has-error_1yry5_56",label:pe,"has-description":"_has-description_1yry5_61","template-button":"_template-button_1yry5_66",description:me,footer:he,error:fe},d=i.forwardRef(({name:r,className:l,disabled:g,description:o,label:Q,maxLength:x=1e3,required:_=!1,asterisk:U=!0,initialRows:X=7,hasTemplateButton:v=!1,wordingTemplate:T,hasDefaultPlaceholder:Y,onPressTemplateButton:q,error:u,onChange:V,onBlur:w,value:Z,count:ee=!0},re)=>{const a=i.useRef(null),[s,b]=i.useState(Z),F=i.useId(),j=i.useId(),D=i.useId(),te=(s==null?void 0:s.length)??0;i.useImperativeHandle(re,()=>a.current);function ae(){if(a.current){a.current.style.height="unset";const t=a.current.scrollHeight;a.current.style.height=`${v?t+92:t}px`}}i.useEffect(()=>{ae()},[s]);const C=[`field-characters-count-description-${r}`,D];o&&C.unshift(j);const ne=()=>{T&&b(T),a.current&&(a.current.focus(),a.current.setSelectionRange(128,128)),q&&q()};return e.jsxs("div",{className:l,children:[e.jsxs("div",{children:[e.jsxs("label",{className:W(n.label,{[n["has-description"]]:!!o}),htmlFor:F,children:[Q," ",_&&U&&"*"]}),o&&e.jsx("span",{id:j,"data-testid":`description-${r}`,className:n.description,children:o})]}),e.jsxs("div",{className:n.wrapper,children:[e.jsx("textarea",{ref:a,"aria-invalid":!!u,"aria-describedby":C.join(" "),className:W(n["text-area"],{[n["has-error"]]:!!u}),disabled:g,id:F,rows:X,value:s,maxLength:x,"aria-required":!_,placeholder:Y?"Écrivez ici...":void 0,onChange:t=>{b(t.target.value),V&&V({...t,target:{...t.target,value:t.target.value,name:r}})},onBlur:t=>{b(t.target.value),w&&w({...t,target:{...t.target,value:t.target.value,name:r}})}}),v&&e.jsx(le,{className:n["template-button"],onClick:ne,disabled:!!(s!=null&&s.length),children:"Générer un modèle"})]}),e.jsxs("div",{className:n.footer,children:[e.jsx("div",{role:"alert",className:n.error,id:D,children:u&&e.jsx(de,{name:r,children:u})}),ee&&e.jsx(ue,{count:te,maxLength:x,name:r})]})]})});d.displayName="TextArea";try{d.displayName="TextArea",d.__docgenInfo={description:"",displayName:"TextArea",props:{name:{defaultValue:null,description:"The name of the textarea field.",name:"name",required:!0,type:{name:"string"}},initialRows:{defaultValue:{value:"7"},description:"The initial number of visible text lines for the control. The field will still expand indefinitely if the input is higher than this value.",name:"initialRows",required:!1,type:{name:"number"}},maxLength:{defaultValue:{value:"1000"},description:"The maximum number of characters allowed in the textarea.",name:"maxLength",required:!1,type:{name:"number"}},required:{defaultValue:{value:"false"},description:"Whether the field is optional.",name:"required",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"The label text for the textarea.",name:"label",required:!0,type:{name:"ReactNode"}},description:{defaultValue:null,description:"A description providing additional information about the textarea.",name:"description",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"Custom CSS class for the textarea component.",name:"className",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"Whether the textarea is disabled.",name:"disabled",required:!1,type:{name:"boolean"}},hasDefaultPlaceholder:{defaultValue:null,description:"",name:"hasDefaultPlaceholder",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"If the asterisk should be displayed when the field is required.",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"Error text displayed under the field. If the error is trythy, the field has the error styles.",name:"error",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"((e: { target: { value: string; name?: string; }; }) => void)"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"((e: FocusEvent<HTMLTextAreaElement, Element>) => void)"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},count:{defaultValue:{value:"true"},description:"Count of characters typed in the field. If `undefined`, the counter is not displayed.",name:"count",required:!1,type:{name:"boolean"}},hasTemplateButton:{defaultValue:{value:"false"},description:"Whether the template button should be displayed.",name:"hasTemplateButton",required:!1,type:{name:"boolean"}},wordingTemplate:{defaultValue:null,description:"Content of the templated added to the field when the template button is clicked",name:"wordingTemplate",required:!1,type:{name:"string"}},onPressTemplateButton:{defaultValue:null,description:"Callback after the template button is clicked.",name:"onPressTemplateButton",required:!1,type:{name:"(() => void)"}}}}}catch{}const ye=({children:r})=>{const l=ie({defaultValues:{myField:"default value"}});return e.jsx(oe,{...l,children:e.jsx("form",{children:r})})},Ie={title:"ui-kit/formsV2/TextArea",component:d},c={args:{name:"description",label:"Description",required:!0}},p={args:{name:"description",label:"Description",error:"This is an error"}},m={args:{name:"description",label:"Description",initialRows:20}},h={args:{name:"description",label:"Description",disabled:!0}},f={args:{name:"description",label:"Description",hasTemplateButton:!0,wordingTemplate:"Template content...",onPressTemplateButton:()=>{}}},y={args:{name:"description",label:"Description"},decorators:[r=>e.jsx(ye,{children:e.jsx(r,{})})],render:r=>{const{setValue:l,watch:g}=se();return e.jsx(d,{...r,value:g("myField"),onChange:o=>{l("myField",o.target.value)}})}};var B,I,N;c.parameters={...c.parameters,docs:{...(B=c.parameters)==null?void 0:B.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    required: true
  }
}`,...(N=(I=c.parameters)==null?void 0:I.docs)==null?void 0:N.source}}};var S,k,A;p.parameters={...p.parameters,docs:{...(S=p.parameters)==null?void 0:S.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    error: 'This is an error'
  }
}`,...(A=(k=p.parameters)==null?void 0:k.docs)==null?void 0:A.source}}};var E,R,H;m.parameters={...m.parameters,docs:{...(E=m.parameters)==null?void 0:E.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    initialRows: 20
  }
}`,...(H=(R=m.parameters)==null?void 0:R.docs)==null?void 0:H.source}}};var P,G,L;h.parameters={...h.parameters,docs:{...(P=h.parameters)==null?void 0:P.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    disabled: true
  }
}`,...(L=(G=h.parameters)==null?void 0:G.docs)==null?void 0:L.source}}};var $,z,M;f.parameters={...f.parameters,docs:{...($=f.parameters)==null?void 0:$.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    hasTemplateButton: true,
    wordingTemplate: 'Template content...',
    onPressTemplateButton: () => {}
  }
}`,...(M=(z=f.parameters)==null?void 0:z.docs)==null?void 0:M.source}}};var O,J,K;y.parameters={...y.parameters,docs:{...(O=y.parameters)==null?void 0:O.docs,source:{originalSource:`{
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
}`,...(K=(J=y.parameters)==null?void 0:J.docs)==null?void 0:K.source}}};const Ne=["Default","WithError","WithInitialHeight","Disabled","WithGeneratedTemplate","WithinForm"];export{c as Default,h as Disabled,p as WithError,f as WithGeneratedTemplate,m as WithInitialHeight,y as WithinForm,Ne as __namedExportsOrder,Ie as default};
