import{j as e}from"./jsx-runtime-DKKDLQjB.js";import{a as G,u as L,F as O}from"./index.esm-CuEGUcun.js";import{c as I}from"./index-DMt7lw30.js";import{r}from"./iframe-CnfVxGgg.js";import{B as $}from"./Button-CRTTfNRA.js";import{F as z}from"./FieldFooter-CBnn5hci.js";import"./preload-helper-PPVm8Dsz.js";import"./Tooltip-0Q1hzrna.js";import"./SvgIcon-BgRkYrhG.js";import"./stroke-pass-CALgybTM.js";import"./chunk-EPOLDU6W-WowPydQ5.js";import"./full-error-BFAmjN4t.js";import"./index.module-E4YOit4J.js";const M="_wrapper_19aq9_1",J="_label_19aq9_57",K="_description_19aq9_68",s={wrapper:M,"text-area":"_text-area_19aq9_5","has-error":"_has-error_19aq9_52",label:J,"has-description":"_has-description_19aq9_57","template-button":"_template-button_19aq9_62",description:K,"field-header-right":"_field-header-right_19aq9_77"},o=r.forwardRef(({name:t,className:l,disabled:g,description:i,label:N,maxLength:v=1e3,required:b=!1,requiredIndicator:_="symbol",initialRows:S=7,hasTemplateButton:T=!1,wordingTemplate:q,hasDefaultPlaceholder:A,onPressTemplateButton:E,error:x,onChange:V,onBlur:F,value:R},k)=>{const n=r.useRef(null),[d,y]=r.useState(R),j=r.useId(),w=r.useId(),D=r.useId(),W=r.useId(),H=d?.length??0;r.useImperativeHandle(k,()=>n.current);const B=r.useCallback(()=>{if(n.current){n.current.style.height="unset";const a=n.current.scrollHeight;n.current.style.height=`${T?a+92:a}px`}},[]);r.useEffect(()=>{B()},[d,B]);const C=[D,W];i&&C.unshift(w);const P=()=>{q&&y(q),n.current&&(n.current.focus(),n.current.setSelectionRange(128,128)),E?.()};return e.jsxs("div",{className:l,children:[e.jsxs("div",{children:[e.jsxs("label",{className:I(s.label,{[s["has-description"]]:!!i}),htmlFor:j,children:[N,b&&_==="symbol"&&e.jsx(e.Fragment,{children:" *"}),b&&_==="explicit"&&e.jsx("span",{className:s["field-header-right"],children:"Obligatoire"})]}),i&&e.jsx("span",{id:w,"data-testid":`description-${t}`,className:s.description,children:i})]}),e.jsxs("div",{className:s.wrapper,children:[e.jsx("textarea",{ref:n,"aria-invalid":!!x,"aria-describedby":C.join(" "),className:I(s["text-area"],{[s["has-error"]]:!!x}),disabled:g,id:j,rows:S,value:d,maxLength:v,"aria-required":!b,placeholder:A?"Écrivez ici...":void 0,onChange:a=>{y(a.target.value),V&&V({...a,target:{...a.target,value:a.target.value,name:t}})},onBlur:a=>{y(a.target.value),F&&F({...a,target:{...a.target,value:a.target.value,name:t}})}}),T&&e.jsx("div",{className:s["template-button"],children:e.jsx($,{onClick:P,disabled:!!d?.length,label:"Générer un modèle"})})]}),e.jsx(z,{error:x,errorId:W,charactersCount:{current:H,max:v},charactersCountId:D})]})});o.displayName="TextArea";try{o.displayName="TextArea",o.__docgenInfo={description:"",displayName:"TextArea",props:{name:{defaultValue:null,description:"The name of the textarea field.",name:"name",required:!0,type:{name:"string"}},initialRows:{defaultValue:{value:"7"},description:"The initial number of visible text lines for the control. The field will still expand indefinitely if the input is higher than this value.",name:"initialRows",required:!1,type:{name:"number"}},maxLength:{defaultValue:{value:"1000"},description:"The maximum number of characters allowed in the textarea.",name:"maxLength",required:!1,type:{name:"number"}},required:{defaultValue:{value:"false"},description:"Whether the field is optional.",name:"required",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"The label text for the textarea.",name:"label",required:!0,type:{name:"ReactNode"}},description:{defaultValue:null,description:"A description providing additional information about the textarea.",name:"description",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"Custom CSS class for the textarea component.",name:"className",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"Whether the textarea is disabled.",name:"disabled",required:!1,type:{name:"boolean"}},hasDefaultPlaceholder:{defaultValue:null,description:"",name:"hasDefaultPlaceholder",required:!1,type:{name:"boolean"}},requiredIndicator:{defaultValue:{value:"symbol"},description:"What type of required indicator is displayed",name:"requiredIndicator",required:!1,type:{name:"enum",value:[{value:'"symbol"'},{value:'"hidden"'},{value:'"explicit"'}]}},error:{defaultValue:null,description:"Error text displayed under the field. If the error is trythy, the field has the error styles.",name:"error",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"((e: { target: { value: string; name?: string; }; }) => void)"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"((e: FocusEvent<HTMLTextAreaElement, Element>) => void)"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},hasTemplateButton:{defaultValue:{value:"false"},description:"Whether the template button should be displayed.",name:"hasTemplateButton",required:!1,type:{name:"boolean"}},wordingTemplate:{defaultValue:null,description:"Content of the templated added to the field when the template button is clicked",name:"wordingTemplate",required:!1,type:{name:"string"}},onPressTemplateButton:{defaultValue:null,description:"Callback after the template button is clicked.",name:"onPressTemplateButton",required:!1,type:{name:"(() => void)"}}}}}catch{}const Q=({children:t})=>{const l=L({defaultValues:{myField:"default value"}});return e.jsx(O,{...l,children:e.jsx("form",{children:t})})},de={title:"@/ui-kit/forms/TextArea",component:o},u={args:{name:"description",label:"Description",required:!0}},c={args:{name:"description",label:"Description",error:"This is an error"}},p={args:{name:"description",label:"Description",initialRows:20}},m={args:{name:"description",label:"Description",disabled:!0}},h={args:{name:"description",label:"Description",hasTemplateButton:!0,wordingTemplate:"Template content...",onPressTemplateButton:()=>{}}},f={args:{name:"description",label:"Description"},decorators:[t=>e.jsx(Q,{children:e.jsx(t,{})})],render:t=>{const{setValue:l,watch:g}=G();return e.jsx(o,{...t,value:g("myField"),onChange:i=>{l("myField",i.target.value)}})}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
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
}`,...f.parameters?.docs?.source}}};const ue=["Default","WithError","WithInitialHeight","Disabled","WithGeneratedTemplate","WithinForm"];export{u as Default,m as Disabled,c as WithError,h as WithGeneratedTemplate,p as WithInitialHeight,f as WithinForm,ue as __namedExportsOrder,de as default};
