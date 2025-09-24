import{j as e}from"./jsx-runtime-Cf8x2fCZ.js";import{u as G,a as L,F as $}from"./index.esm-D1X9ZzX-.js";import{c as B}from"./index-B0pXE9zJ.js";import{r as s}from"./index-QQMyt9Ur.js";import{B as z}from"./Button-ouo4aZ-_.js";import{F as M}from"./FieldError-2mFOl_uD.js";import{F as O}from"./FieldLayoutCharacterCount-CCjrqBrG.js";import"./index-yBjzXJbu.js";import"./_commonjsHelpers-CqkleIqs.js";import"./stroke-pass-CALgybTM.js";import"./SvgIcon-B5V96DYN.js";import"./Tooltip-Du1ylKtn.js";import"./Button.module-Md2doL54.js";import"./types-yVZEaApa.js";import"./stroke-error-DSZD431a.js";import"./index.module-DTkZ18fI.js";const J="_wrapper_lf3ng_1",K="_label_lf3ng_57",Q="_description_lf3ng_68",U="_footer_lf3ng_77",X="_error_lf3ng_84",n={wrapper:J,"text-area":"_text-area_lf3ng_5","has-error":"_has-error_lf3ng_52",label:K,"has-description":"_has-description_lf3ng_57","template-button":"_template-button_lf3ng_62",description:Q,footer:U,error:X},o=s.forwardRef(({name:r,className:l,disabled:b,description:i,label:C,maxLength:y=1e3,required:_=!1,asterisk:W=!0,initialRows:I=7,hasTemplateButton:T=!1,wordingTemplate:v,hasDefaultPlaceholder:N,onPressTemplateButton:S,error:d,onChange:V,onBlur:q,value:k,count:A=!0},E)=>{const a=s.useRef(null),[u,x]=s.useState(k),w=s.useId(),F=s.useId(),j=s.useId(),R=u?.length??0;s.useImperativeHandle(E,()=>a.current);function H(){if(a.current){a.current.style.height="unset";const t=a.current.scrollHeight;a.current.style.height=`${T?t+92:t}px`}}s.useEffect(()=>{H()},[u]);const D=[`field-characters-count-description-${r}`,j];i&&D.unshift(F);const P=()=>{v&&x(v),a.current&&(a.current.focus(),a.current.setSelectionRange(128,128)),S?.()};return e.jsxs("div",{className:l,children:[e.jsxs("div",{children:[e.jsxs("label",{className:B(n.label,{[n["has-description"]]:!!i}),htmlFor:w,children:[C," ",_&&W&&"*"]}),i&&e.jsx("span",{id:F,"data-testid":`description-${r}`,className:n.description,children:i})]}),e.jsxs("div",{className:n.wrapper,children:[e.jsx("textarea",{ref:a,"aria-invalid":!!d,"aria-describedby":D.join(" "),className:B(n["text-area"],{[n["has-error"]]:!!d}),disabled:b,id:w,rows:I,value:u,maxLength:y,"aria-required":!_,placeholder:N?"Écrivez ici...":void 0,onChange:t=>{x(t.target.value),V&&V({...t,target:{...t.target,value:t.target.value,name:r}})},onBlur:t=>{x(t.target.value),q&&q({...t,target:{...t.target,value:t.target.value,name:r}})}}),T&&e.jsx(z,{className:n["template-button"],onClick:P,disabled:!!u?.length,children:"Générer un modèle"})]}),e.jsxs("div",{className:n.footer,children:[e.jsx("div",{role:"alert",className:n.error,id:j,children:d&&e.jsx(M,{name:r,children:d})}),A&&e.jsx(O,{count:R,maxLength:y,name:r})]})]})});o.displayName="TextArea";try{o.displayName="TextArea",o.__docgenInfo={description:"",displayName:"TextArea",props:{name:{defaultValue:null,description:"The name of the textarea field.",name:"name",required:!0,type:{name:"string"}},initialRows:{defaultValue:{value:"7"},description:"The initial number of visible text lines for the control. The field will still expand indefinitely if the input is higher than this value.",name:"initialRows",required:!1,type:{name:"number"}},maxLength:{defaultValue:{value:"1000"},description:"The maximum number of characters allowed in the textarea.",name:"maxLength",required:!1,type:{name:"number"}},required:{defaultValue:{value:"false"},description:"Whether the field is optional.",name:"required",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"The label text for the textarea.",name:"label",required:!0,type:{name:"ReactNode"}},description:{defaultValue:null,description:"A description providing additional information about the textarea.",name:"description",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"Custom CSS class for the textarea component.",name:"className",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"Whether the textarea is disabled.",name:"disabled",required:!1,type:{name:"boolean"}},hasDefaultPlaceholder:{defaultValue:null,description:"",name:"hasDefaultPlaceholder",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"If the asterisk should be displayed when the field is required.",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"Error text displayed under the field. If the error is trythy, the field has the error styles.",name:"error",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"((e: { target: { value: string; name?: string; }; }) => void)"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"((e: FocusEvent<HTMLTextAreaElement, Element>) => void)"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},count:{defaultValue:{value:"true"},description:"Count of characters typed in the field. If `undefined`, the counter is not displayed.",name:"count",required:!1,type:{name:"boolean"}},hasTemplateButton:{defaultValue:{value:"false"},description:"Whether the template button should be displayed.",name:"hasTemplateButton",required:!1,type:{name:"boolean"}},wordingTemplate:{defaultValue:null,description:"Content of the templated added to the field when the template button is clicked",name:"wordingTemplate",required:!1,type:{name:"string"}},onPressTemplateButton:{defaultValue:null,description:"Callback after the template button is clicked.",name:"onPressTemplateButton",required:!1,type:{name:"(() => void)"}}}}}catch{}const Y=({children:r})=>{const l=L({defaultValues:{myField:"default value"}});return e.jsx($,{...l,children:e.jsx("form",{children:r})})},he={title:"@/ui-kit/forms/TextArea",component:o},c={args:{name:"description",label:"Description",required:!0}},p={args:{name:"description",label:"Description",error:"This is an error"}},m={args:{name:"description",label:"Description",initialRows:20}},f={args:{name:"description",label:"Description",disabled:!0}},h={args:{name:"description",label:"Description",hasTemplateButton:!0,wordingTemplate:"Template content...",onPressTemplateButton:()=>{}}},g={args:{name:"description",label:"Description"},decorators:[r=>e.jsx(Y,{children:e.jsx(r,{})})],render:r=>{const{setValue:l,watch:b}=G();return e.jsx(o,{...r,value:b("myField"),onChange:i=>{l("myField",i.target.value)}})}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    required: true
  }
}`,...c.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    error: 'This is an error'
  }
}`,...p.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    initialRows: 20
  }
}`,...m.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    disabled: true
  }
}`,...f.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    hasTemplateButton: true,
    wordingTemplate: 'Template content...',
    onPressTemplateButton: () => {}
  }
}`,...h.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
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
}`,...g.parameters?.docs?.source}}};const ge=["Default","WithError","WithInitialHeight","Disabled","WithGeneratedTemplate","WithinForm"];export{c as Default,f as Disabled,p as WithError,h as WithGeneratedTemplate,m as WithInitialHeight,g as WithinForm,ge as __namedExportsOrder,he as default};
