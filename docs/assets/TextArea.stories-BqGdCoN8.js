import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-Dzcs3kz1.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./classnames-MYlGWOUq.js";import{t as i}from"./Button-A5Vimemh.js";import{t as a}from"./FieldFooter-BVy5QrGF.js";import{a as o,o as s,t as c}from"./index.esm-BjndPqes.js";var l=e(r(),1),u=e(t(),1),d=`_wrapper_16amp_2`,f=`_label_16amp_58`,p=`_description_16amp_69`,m={wrapper:d,"text-area":`_text-area_16amp_6`,"has-error":`_has-error_16amp_53`,label:f,"has-description":`_has-description_16amp_58`,"template-button":`_template-button_16amp_63`,description:p,"field-header-right":`_field-header-right_16amp_78`},h=n(),g=(0,u.forwardRef)(({name:e,className:t,disabled:n,description:r,label:o,maxLength:s=1e3,required:c=!1,requiredIndicator:d=`symbol`,initialRows:f=7,hasTemplateButton:p=!1,wordingTemplate:g,hasDefaultPlaceholder:_,onPressTemplateButton:v,error:y,onChange:b,onBlur:x,value:S},C)=>{let w=(0,u.useRef)(null),[T,E]=(0,u.useState)(S),D=(0,u.useId)(),O=(0,u.useId)(),k=(0,u.useId)(),A=(0,u.useId)(),j=T?.length??0;(0,u.useImperativeHandle)(C,()=>w.current);let M=(0,u.useCallback)(()=>{if(w.current){w.current.style.height=`unset`;let e=w.current.scrollHeight;w.current.style.height=`${p?e+92:e}px`}},[]);(0,u.useEffect)(()=>{M()},[T,M]);let N=[k,A];r&&N.unshift(O);let P=()=>{g&&E(g),w.current&&(w.current.focus(),w.current.setSelectionRange(128,128)),v?.()};return(0,h.jsxs)(`div`,{className:t,children:[(0,h.jsxs)(`div`,{children:[(0,h.jsxs)(`label`,{className:(0,l.default)(m.label,{[m[`has-description`]]:!!r}),htmlFor:D,children:[o,c&&d===`symbol`&&(0,h.jsx)(h.Fragment,{children:`\xA0*`}),c&&d===`explicit`&&(0,h.jsx)(`span`,{className:m[`field-header-right`],children:`Obligatoire`})]}),r&&(0,h.jsx)(`span`,{id:O,"data-testid":`description-${e}`,className:m.description,children:r})]}),(0,h.jsxs)(`div`,{className:m.wrapper,children:[(0,h.jsx)(`textarea`,{ref:w,"aria-invalid":!!y,"aria-describedby":N.join(` `),className:(0,l.default)(m[`text-area`],{[m[`has-error`]]:!!y}),disabled:n,id:D,rows:f,value:T,maxLength:s,"aria-required":!c,placeholder:_?`Écrivez ici...`:void 0,onChange:t=>{E(t.target.value),b&&b({...t,target:{...t.target,value:t.target.value,name:e}})},onBlur:t=>{E(t.target.value),x&&x({...t,target:{...t.target,value:t.target.value,name:e}})}}),p&&(0,h.jsx)(`div`,{className:m[`template-button`],children:(0,h.jsx)(i,{onClick:P,disabled:!!T?.length,label:`Générer un modèle`})})]}),(0,h.jsx)(a,{error:y,errorId:A,charactersCount:{current:j,max:s},charactersCountId:k})]})});g.displayName=`TextArea`;try{g.displayName=`TextArea`,g.__docgenInfo={description:``,displayName:`TextArea`,props:{name:{defaultValue:null,description:`The name of the textarea field.`,name:`name`,required:!0,type:{name:`string`}},initialRows:{defaultValue:{value:`7`},description:`The initial number of visible text lines for the control. The field will still expand indefinitely if the input is higher than this value.`,name:`initialRows`,required:!1,type:{name:`number`}},maxLength:{defaultValue:{value:`1000`},description:`The maximum number of characters allowed in the textarea.`,name:`maxLength`,required:!1,type:{name:`number`}},required:{defaultValue:{value:`false`},description:`Whether the field is optional.`,name:`required`,required:!1,type:{name:`boolean`}},label:{defaultValue:null,description:`The label text for the textarea.`,name:`label`,required:!0,type:{name:`ReactNode`}},description:{defaultValue:null,description:`A description providing additional information about the textarea.`,name:`description`,required:!1,type:{name:`string`}},className:{defaultValue:null,description:`Custom CSS class for the textarea component.`,name:`className`,required:!1,type:{name:`string`}},disabled:{defaultValue:null,description:`Whether the textarea is disabled.`,name:`disabled`,required:!1,type:{name:`boolean`}},hasDefaultPlaceholder:{defaultValue:null,description:``,name:`hasDefaultPlaceholder`,required:!1,type:{name:`boolean`}},requiredIndicator:{defaultValue:{value:`symbol`},description:`What type of required indicator is displayed`,name:`requiredIndicator`,required:!1,type:{name:`enum`,value:[{value:`"symbol"`},{value:`"explicit"`},{value:`"hidden"`}]}},error:{defaultValue:null,description:`Error text displayed under the field. If the error is trythy, the field has the error styles.`,name:`error`,required:!1,type:{name:`string`}},onChange:{defaultValue:null,description:``,name:`onChange`,required:!1,type:{name:`((e: { target: { value: string; name?: string; }; }) => void)`}},onBlur:{defaultValue:null,description:``,name:`onBlur`,required:!1,type:{name:`((e: FocusEvent<HTMLTextAreaElement, Element>) => void)`}},value:{defaultValue:null,description:``,name:`value`,required:!1,type:{name:`string`}},hasTemplateButton:{defaultValue:{value:`false`},description:`Whether the template button should be displayed.`,name:`hasTemplateButton`,required:!1,type:{name:`boolean`}},wordingTemplate:{defaultValue:null,description:`Content of the templated added to the field when the template button is clicked`,name:`wordingTemplate`,required:!1,type:{name:`string`}},onPressTemplateButton:{defaultValue:null,description:`Callback after the template button is clicked.`,name:`onPressTemplateButton`,required:!1,type:{name:`(() => void)`}}}}}catch{}var _=({children:e})=>(0,h.jsx)(c,{...o({defaultValues:{myField:`default value`}}),children:(0,h.jsx)(`form`,{children:e})}),v={title:`@/ui-kit/forms/TextArea`,component:g},y={args:{name:`description`,label:`Description`,required:!0}},b={args:{name:`description`,label:`Description`,error:`This is an error`}},x={args:{name:`description`,label:`Description`,initialRows:20}},S={args:{name:`description`,label:`Description`,disabled:!0}},C={args:{name:`description`,label:`Description`,hasTemplateButton:!0,wordingTemplate:`Template content...`,onPressTemplateButton:()=>{}}},w={args:{name:`description`,label:`Description`},decorators:[e=>(0,h.jsx)(_,{children:(0,h.jsx)(e,{})})],render:e=>{let{setValue:t,watch:n}=s();return(0,h.jsx)(g,{...e,value:n(`myField`),onChange:e=>{t(`myField`,e.target.value)}})}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    required: true
  }
}`,...y.parameters?.docs?.source}}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    error: 'This is an error'
  }
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    initialRows: 20
  }
}`,...x.parameters?.docs?.source}}},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    disabled: true
  }
}`,...S.parameters?.docs?.source}}},C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    hasTemplateButton: true,
    wordingTemplate: 'Template content...',
    onPressTemplateButton: () => {}
  }
}`,...C.parameters?.docs?.source}}},w.parameters={...w.parameters,docs:{...w.parameters?.docs,source:{originalSource:`{
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
}`,...w.parameters?.docs?.source}}};var T=[`Default`,`WithError`,`WithInitialHeight`,`Disabled`,`WithGeneratedTemplate`,`WithinForm`];export{y as Default,S as Disabled,b as WithError,C as WithGeneratedTemplate,x as WithInitialHeight,w as WithinForm,T as __namedExportsOrder,v as default};