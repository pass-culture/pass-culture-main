import{j as e}from"./jsx-runtime-DF2Pcvd1.js";import{u as se,a as ie,F as le}from"./index.esm-BBvhERNj.js";import{c as W}from"./index-DeARc5FM.js";import{r as i}from"./index-B2-qRKKC.js";import{B as oe}from"./Button-CJb_rOOr.js";import{F as de}from"./FieldError-B3RhE53I.js";import{F as ce}from"./FieldLayoutCharacterCount-Cg7wcWeq.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./stroke-pass-CALgybTM.js";import"./SvgIcon-DfLnDDE5.js";import"./Tooltip-C-mHJC8R.js";import"./Button.module-Md2doL54.js";import"./types-yVZEaApa.js";import"./stroke-error-DSZD431a.js";import"./index.module-BDmDBTbR.js";const ue="_wrapper_lf3ng_1",pe="_label_lf3ng_57",me="_description_lf3ng_68",fe="_footer_lf3ng_77",he="_error_lf3ng_84",n={wrapper:ue,"text-area":"_text-area_lf3ng_5","has-error":"_has-error_lf3ng_52",label:pe,"has-description":"_has-description_lf3ng_57","template-button":"_template-button_lf3ng_62",description:me,footer:fe,error:he},d=i.forwardRef(({name:r,className:o,disabled:b,description:l,label:Q,maxLength:_=1e3,required:v=!1,asterisk:U=!0,initialRows:X=7,hasTemplateButton:T=!1,wordingTemplate:q,hasDefaultPlaceholder:Y,onPressTemplateButton:x,error:c,onChange:V,onBlur:w,value:Z,count:ee=!0},re)=>{const a=i.useRef(null),[s,y]=i.useState(Z),F=i.useId(),j=i.useId(),D=i.useId(),te=(s==null?void 0:s.length)??0;i.useImperativeHandle(re,()=>a.current);function ae(){if(a.current){a.current.style.height="unset";const t=a.current.scrollHeight;a.current.style.height=`${T?t+92:t}px`}}i.useEffect(()=>{ae()},[s]);const C=[`field-characters-count-description-${r}`,D];l&&C.unshift(j);const ne=()=>{q&&y(q),a.current&&(a.current.focus(),a.current.setSelectionRange(128,128)),x==null||x()};return e.jsxs("div",{className:o,children:[e.jsxs("div",{children:[e.jsxs("label",{className:W(n.label,{[n["has-description"]]:!!l}),htmlFor:F,children:[Q," ",v&&U&&"*"]}),l&&e.jsx("span",{id:j,"data-testid":`description-${r}`,className:n.description,children:l})]}),e.jsxs("div",{className:n.wrapper,children:[e.jsx("textarea",{ref:a,"aria-invalid":!!c,"aria-describedby":C.join(" "),className:W(n["text-area"],{[n["has-error"]]:!!c}),disabled:b,id:F,rows:X,value:s,maxLength:_,"aria-required":!v,placeholder:Y?"Écrivez ici...":void 0,onChange:t=>{y(t.target.value),V&&V({...t,target:{...t.target,value:t.target.value,name:r}})},onBlur:t=>{y(t.target.value),w&&w({...t,target:{...t.target,value:t.target.value,name:r}})}}),T&&e.jsx(oe,{className:n["template-button"],onClick:ne,disabled:!!(s!=null&&s.length),children:"Générer un modèle"})]}),e.jsxs("div",{className:n.footer,children:[e.jsx("div",{role:"alert",className:n.error,id:D,children:c&&e.jsx(de,{name:r,children:c})}),ee&&e.jsx(ce,{count:te,maxLength:_,name:r})]})]})});d.displayName="TextArea";try{d.displayName="TextArea",d.__docgenInfo={description:"",displayName:"TextArea",props:{name:{defaultValue:null,description:"The name of the textarea field.",name:"name",required:!0,type:{name:"string"}},initialRows:{defaultValue:{value:"7"},description:"The initial number of visible text lines for the control. The field will still expand indefinitely if the input is higher than this value.",name:"initialRows",required:!1,type:{name:"number"}},maxLength:{defaultValue:{value:"1000"},description:"The maximum number of characters allowed in the textarea.",name:"maxLength",required:!1,type:{name:"number"}},required:{defaultValue:{value:"false"},description:"Whether the field is optional.",name:"required",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"The label text for the textarea.",name:"label",required:!0,type:{name:"ReactNode"}},description:{defaultValue:null,description:"A description providing additional information about the textarea.",name:"description",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"Custom CSS class for the textarea component.",name:"className",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"Whether the textarea is disabled.",name:"disabled",required:!1,type:{name:"boolean"}},hasDefaultPlaceholder:{defaultValue:null,description:"",name:"hasDefaultPlaceholder",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"If the asterisk should be displayed when the field is required.",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"Error text displayed under the field. If the error is trythy, the field has the error styles.",name:"error",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"((e: { target: { value: string; name?: string; }; }) => void)"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"((e: FocusEvent<HTMLTextAreaElement, Element>) => void)"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},count:{defaultValue:{value:"true"},description:"Count of characters typed in the field. If `undefined`, the counter is not displayed.",name:"count",required:!1,type:{name:"boolean"}},hasTemplateButton:{defaultValue:{value:"false"},description:"Whether the template button should be displayed.",name:"hasTemplateButton",required:!1,type:{name:"boolean"}},wordingTemplate:{defaultValue:null,description:"Content of the templated added to the field when the template button is clicked",name:"wordingTemplate",required:!1,type:{name:"string"}},onPressTemplateButton:{defaultValue:null,description:"Callback after the template button is clicked.",name:"onPressTemplateButton",required:!1,type:{name:"(() => void)"}}}}}catch{}const ge=({children:r})=>{const o=ie({defaultValues:{myField:"default value"}});return e.jsx(le,{...o,children:e.jsx("form",{children:r})})},Ne={title:"@/ui-kit/forms/TextArea",component:d},u={args:{name:"description",label:"Description",required:!0}},p={args:{name:"description",label:"Description",error:"This is an error"}},m={args:{name:"description",label:"Description",initialRows:20}},f={args:{name:"description",label:"Description",disabled:!0}},h={args:{name:"description",label:"Description",hasTemplateButton:!0,wordingTemplate:"Template content...",onPressTemplateButton:()=>{}}},g={args:{name:"description",label:"Description"},decorators:[r=>e.jsx(ge,{children:e.jsx(r,{})})],render:r=>{const{setValue:o,watch:b}=se();return e.jsx(d,{...r,value:b("myField"),onChange:l=>{o("myField",l.target.value)}})}};var I,N,S;u.parameters={...u.parameters,docs:{...(I=u.parameters)==null?void 0:I.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    required: true
  }
}`,...(S=(N=u.parameters)==null?void 0:N.docs)==null?void 0:S.source}}};var k,A,E;p.parameters={...p.parameters,docs:{...(k=p.parameters)==null?void 0:k.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    error: 'This is an error'
  }
}`,...(E=(A=p.parameters)==null?void 0:A.docs)==null?void 0:E.source}}};var B,R,H;m.parameters={...m.parameters,docs:{...(B=m.parameters)==null?void 0:B.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    initialRows: 20
  }
}`,...(H=(R=m.parameters)==null?void 0:R.docs)==null?void 0:H.source}}};var G,L,P;f.parameters={...f.parameters,docs:{...(G=f.parameters)==null?void 0:G.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    disabled: true
  }
}`,...(P=(L=f.parameters)==null?void 0:L.docs)==null?void 0:P.source}}};var $,z,M;h.parameters={...h.parameters,docs:{...($=h.parameters)==null?void 0:$.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    hasTemplateButton: true,
    wordingTemplate: 'Template content...',
    onPressTemplateButton: () => {}
  }
}`,...(M=(z=h.parameters)==null?void 0:z.docs)==null?void 0:M.source}}};var O,J,K;g.parameters={...g.parameters,docs:{...(O=g.parameters)==null?void 0:O.docs,source:{originalSource:`{
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
}`,...(K=(J=g.parameters)==null?void 0:J.docs)==null?void 0:K.source}}};const Se=["Default","WithError","WithInitialHeight","Disabled","WithGeneratedTemplate","WithinForm"];export{u as Default,f as Disabled,p as WithError,h as WithGeneratedTemplate,m as WithInitialHeight,g as WithinForm,Se as __namedExportsOrder,Ne as default};
