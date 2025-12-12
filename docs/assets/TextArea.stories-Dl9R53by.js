import{j as e}from"./jsx-runtime-Bt4IpClZ.js";import{a as P,u as G,F as L}from"./index.esm-CIAcMOKc.js";import{c as W}from"./index-C8LSr36h.js";import{r as n}from"./iframe-04rcAfZw.js";import{F as $}from"./FieldFooter-CqihlP3V.js";import{B as M}from"./Button-YNlFRGtz.js";import"./preload-helper-PPVm8Dsz.js";import"./full-error-BFAmjN4t.js";import"./index.module-DybMtIfr.js";import"./SvgIcon-BV9bQICR.js";import"./stroke-pass-CALgybTM.js";import"./Tooltip-Va54JagT.js";import"./Button.module-CY1ZDZvt.js";import"./types-yVZEaApa.js";const O="_wrapper_15izt_1",J="_label_15izt_57",K="_description_15izt_68",s={wrapper:O,"text-area":"_text-area_15izt_5","has-error":"_has-error_15izt_52",label:J,"has-description":"_has-description_15izt_57","template-button":"_template-button_15izt_62",description:K},o=n.forwardRef(({name:r,className:l,disabled:g,description:i,label:B,maxLength:y=1e3,required:v=!1,requiredIndicator:C="symbol",initialRows:S=7,hasTemplateButton:T=!1,wordingTemplate:_,hasDefaultPlaceholder:A,onPressTemplateButton:N,error:b,onChange:q,onBlur:V,value:E},R)=>{const a=n.useRef(null),[d,x]=n.useState(E),F=n.useId(),w=n.useId(),D=n.useId(),j=n.useId(),k=d?.length??0;n.useImperativeHandle(R,()=>a.current);function z(){if(a.current){a.current.style.height="unset";const t=a.current.scrollHeight;a.current.style.height=`${T?t+92:t}px`}}n.useEffect(()=>{z()},[d]);const I=[D,j];i&&I.unshift(w);const H=()=>{_&&x(_),a.current&&(a.current.focus(),a.current.setSelectionRange(128,128)),N?.()};return e.jsxs("div",{className:l,children:[e.jsxs("div",{children:[e.jsxs("label",{className:W(s.label,{[s["has-description"]]:!!i}),htmlFor:F,children:[B,v&&C==="symbol"&&e.jsx(e.Fragment,{children:" *"})]}),i&&e.jsx("span",{id:w,"data-testid":`description-${r}`,className:s.description,children:i})]}),e.jsxs("div",{className:s.wrapper,children:[e.jsx("textarea",{ref:a,"aria-invalid":!!b,"aria-describedby":I.join(" "),className:W(s["text-area"],{[s["has-error"]]:!!b}),disabled:g,id:F,rows:S,value:d,maxLength:y,"aria-required":!v,placeholder:A?"Écrivez ici...":void 0,onChange:t=>{x(t.target.value),q&&q({...t,target:{...t.target,value:t.target.value,name:r}})},onBlur:t=>{x(t.target.value),V&&V({...t,target:{...t.target,value:t.target.value,name:r}})}}),T&&e.jsx(M,{className:s["template-button"],onClick:H,disabled:!!d?.length,children:"Générer un modèle"})]}),e.jsx($,{error:b,errorId:j,charactersCount:{current:k,max:y},charactersCountId:D})]})});o.displayName="TextArea";try{o.displayName="TextArea",o.__docgenInfo={description:"",displayName:"TextArea",props:{name:{defaultValue:null,description:"The name of the textarea field.",name:"name",required:!0,type:{name:"string"}},initialRows:{defaultValue:{value:"7"},description:"The initial number of visible text lines for the control. The field will still expand indefinitely if the input is higher than this value.",name:"initialRows",required:!1,type:{name:"number"}},maxLength:{defaultValue:{value:"1000"},description:"The maximum number of characters allowed in the textarea.",name:"maxLength",required:!1,type:{name:"number"}},required:{defaultValue:{value:"false"},description:"Whether the field is optional.",name:"required",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"The label text for the textarea.",name:"label",required:!0,type:{name:"ReactNode"}},description:{defaultValue:null,description:"A description providing additional information about the textarea.",name:"description",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"Custom CSS class for the textarea component.",name:"className",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"Whether the textarea is disabled.",name:"disabled",required:!1,type:{name:"boolean"}},hasDefaultPlaceholder:{defaultValue:null,description:"",name:"hasDefaultPlaceholder",required:!1,type:{name:"boolean"}},requiredIndicator:{defaultValue:{value:"symbol"},description:"What type of required indicator is displayed",name:"requiredIndicator",required:!1,type:{name:"enum",value:[{value:'"symbol"'},{value:'"hidden"'},{value:'"explicit"'}]}},error:{defaultValue:null,description:"Error text displayed under the field. If the error is trythy, the field has the error styles.",name:"error",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"((e: { target: { value: string; name?: string; }; }) => void)"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"((e: FocusEvent<HTMLTextAreaElement, Element>) => void)"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},hasTemplateButton:{defaultValue:{value:"false"},description:"Whether the template button should be displayed.",name:"hasTemplateButton",required:!1,type:{name:"boolean"}},wordingTemplate:{defaultValue:null,description:"Content of the templated added to the field when the template button is clicked",name:"wordingTemplate",required:!1,type:{name:"string"}},onPressTemplateButton:{defaultValue:null,description:"Callback after the template button is clicked.",name:"onPressTemplateButton",required:!1,type:{name:"(() => void)"}}}}}catch{}const Q=({children:r})=>{const l=G({defaultValues:{myField:"default value"}});return e.jsx(L,{...l,children:e.jsx("form",{children:r})})},ue={title:"@/ui-kit/forms/TextArea",component:o},u={args:{name:"description",label:"Description",required:!0}},c={args:{name:"description",label:"Description",error:"This is an error"}},p={args:{name:"description",label:"Description",initialRows:20}},m={args:{name:"description",label:"Description",disabled:!0}},h={args:{name:"description",label:"Description",hasTemplateButton:!0,wordingTemplate:"Template content...",onPressTemplateButton:()=>{}}},f={args:{name:"description",label:"Description"},decorators:[r=>e.jsx(Q,{children:e.jsx(r,{})})],render:r=>{const{setValue:l,watch:g}=P();return e.jsx(o,{...r,value:g("myField"),onChange:i=>{l("myField",i.target.value)}})}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    required: true
  }
}`,...u.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    error: 'This is an error'
  }
}`,...c.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    initialRows: 20
  }
}`,...p.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    disabled: true
  }
}`,...m.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    hasTemplateButton: true,
    wordingTemplate: 'Template content...',
    onPressTemplateButton: () => {}
  }
}`,...h.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
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
}`,...f.parameters?.docs?.source}}};const ce=["Default","WithError","WithInitialHeight","Disabled","WithGeneratedTemplate","WithinForm"];export{u as Default,m as Disabled,c as WithError,h as WithGeneratedTemplate,p as WithInitialHeight,f as WithinForm,ce as __namedExportsOrder,ue as default};
