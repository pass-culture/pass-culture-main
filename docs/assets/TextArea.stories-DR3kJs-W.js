import{i as e}from"./chunk-DseTPa7n.js";import{t}from"./react-DCnNfEIY.js";import{t as n}from"./jsx-runtime-BUC2lftT.js";import{t as r}from"./classnames-BHgbbynn.js";import{t as i}from"./Button-CBfbphSU.js";import{t as a}from"./FieldFooter-D0lVTCoT.js";import{a as o,o as s,t as c}from"./index.esm-DCH0oH1a.js";var l=e(t(),1),u=e(r(),1),d={wrapper:`_wrapper_16amp_2`,"text-area":`_text-area_16amp_6`,"has-error":`_has-error_16amp_53`,label:`_label_16amp_58`,"has-description":`_has-description_16amp_58`,"template-button":`_template-button_16amp_63`,description:`_description_16amp_69`,"field-header-right":`_field-header-right_16amp_78`},f=n(),p=(0,l.forwardRef)(({name:e,className:t,disabled:n,description:r,label:o,maxLength:s=1e3,required:c=!1,requiredIndicator:p=`symbol`,initialRows:m=7,hasTemplateButton:h=!1,wordingTemplate:g,hasDefaultPlaceholder:_,onPressTemplateButton:v,error:y,onChange:b,onBlur:x,value:S},C)=>{let w=(0,l.useRef)(null),[T,E]=(0,l.useState)(S),D=(0,l.useId)(),O=(0,l.useId)(),k=(0,l.useId)(),A=(0,l.useId)(),j=T?.length??0;(0,l.useImperativeHandle)(C,()=>w.current);let M=(0,l.useCallback)(()=>{if(w.current){w.current.style.height=`unset`;let e=w.current.scrollHeight;w.current.style.height=`${h?e+92:e}px`}},[h]);(0,l.useEffect)(()=>{M()},[M]);let N=[k,A];r&&N.unshift(O);let P=()=>{g&&E(g),w.current&&(w.current.focus(),w.current.setSelectionRange(128,128)),v?.()};return(0,f.jsxs)(`div`,{className:t,children:[(0,f.jsxs)(`div`,{children:[(0,f.jsxs)(`label`,{className:(0,u.default)(d.label,{[d[`has-description`]]:!!r}),htmlFor:D,children:[o,c&&p===`symbol`&&(0,f.jsx)(f.Fragment,{children:`\xA0*`}),c&&p===`explicit`&&(0,f.jsx)(`span`,{className:d[`field-header-right`],children:`Obligatoire`})]}),r&&(0,f.jsx)(`span`,{id:O,"data-testid":`description-${e}`,className:d.description,children:r})]}),(0,f.jsxs)(`div`,{className:d.wrapper,children:[(0,f.jsx)(`textarea`,{ref:w,"aria-invalid":!!y,"aria-describedby":N.join(` `),className:(0,u.default)(d[`text-area`],{[d[`has-error`]]:!!y}),disabled:n,id:D,rows:m,value:T,maxLength:s,"aria-required":!c,placeholder:_?`Écrivez ici...`:void 0,onChange:t=>{E(t.target.value),b&&b({...t,target:{...t.target,value:t.target.value,name:e}})},onBlur:t=>{E(t.target.value),x&&x({...t,target:{...t.target,value:t.target.value,name:e}})}}),h&&(0,f.jsx)(`div`,{className:d[`template-button`],children:(0,f.jsx)(i,{onClick:P,disabled:!!T?.length,label:`Générer un modèle`})})]}),(0,f.jsx)(a,{error:y,errorId:A,charactersCount:{current:j,max:s},charactersCountId:k})]})});p.displayName=`TextArea`;try{p.displayName=`TextArea`,p.__docgenInfo={description:``,displayName:`TextArea`,props:{name:{defaultValue:null,description:`The name of the textarea field.`,name:`name`,required:!0,type:{name:`string`}},initialRows:{defaultValue:{value:`7`},description:`The initial number of visible text lines for the control. The field will still expand indefinitely if the input is higher than this value.`,name:`initialRows`,required:!1,type:{name:`number`}},maxLength:{defaultValue:{value:`1000`},description:`The maximum number of characters allowed in the textarea.`,name:`maxLength`,required:!1,type:{name:`number`}},required:{defaultValue:{value:`false`},description:`Whether the field is optional.`,name:`required`,required:!1,type:{name:`boolean`}},label:{defaultValue:null,description:`The label text for the textarea.`,name:`label`,required:!0,type:{name:`ReactNode`}},description:{defaultValue:null,description:`A description providing additional information about the textarea.`,name:`description`,required:!1,type:{name:`string`}},className:{defaultValue:null,description:`Custom CSS class for the textarea component.`,name:`className`,required:!1,type:{name:`string`}},disabled:{defaultValue:null,description:`Whether the textarea is disabled.`,name:`disabled`,required:!1,type:{name:`boolean`}},hasDefaultPlaceholder:{defaultValue:null,description:``,name:`hasDefaultPlaceholder`,required:!1,type:{name:`boolean`}},requiredIndicator:{defaultValue:{value:`symbol`},description:`What type of required indicator is displayed`,name:`requiredIndicator`,required:!1,type:{name:`enum`,value:[{value:`"symbol"`},{value:`"explicit"`},{value:`"hidden"`}]}},error:{defaultValue:null,description:`Error text displayed under the field. If the error is trythy, the field has the error styles.`,name:`error`,required:!1,type:{name:`string`}},onChange:{defaultValue:null,description:``,name:`onChange`,required:!1,type:{name:`((e: { target: { value: string; name?: string; }; }) => void)`}},onBlur:{defaultValue:null,description:``,name:`onBlur`,required:!1,type:{name:`((e: FocusEvent<HTMLTextAreaElement, Element>) => void)`}},value:{defaultValue:null,description:``,name:`value`,required:!1,type:{name:`string`}},hasTemplateButton:{defaultValue:{value:`false`},description:`Whether the template button should be displayed.`,name:`hasTemplateButton`,required:!1,type:{name:`boolean`}},wordingTemplate:{defaultValue:null,description:`Content of the templated added to the field when the template button is clicked`,name:`wordingTemplate`,required:!1,type:{name:`string`}},onPressTemplateButton:{defaultValue:null,description:`Callback after the template button is clicked.`,name:`onPressTemplateButton`,required:!1,type:{name:`(() => void)`}}}}}catch{}var m=({children:e})=>(0,f.jsx)(c,{...o({defaultValues:{myField:`default value`}}),children:(0,f.jsx)(`form`,{children:e})}),h={title:`@/ui-kit/forms/TextArea`,component:p},g={args:{name:`description`,label:`Description`,required:!0}},_={args:{name:`description`,label:`Description`,error:`This is an error`}},v={args:{name:`description`,label:`Description`,initialRows:20}},y={args:{name:`description`,label:`Description`,disabled:!0}},b={args:{name:`description`,label:`Description`,hasTemplateButton:!0,wordingTemplate:`Template content...`,onPressTemplateButton:()=>{}}},x={args:{name:`description`,label:`Description`},decorators:[e=>(0,f.jsx)(m,{children:(0,f.jsx)(e,{})})],render:e=>{let{setValue:t,watch:n}=s();return(0,f.jsx)(p,{...e,value:n(`myField`),onChange:e=>{t(`myField`,e.target.value)}})}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    required: true
  }
}`,...g.parameters?.docs?.source}}},_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    error: 'This is an error'
  }
}`,..._.parameters?.docs?.source}}},v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    initialRows: 20
  }
}`,...v.parameters?.docs?.source}}},y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    disabled: true
  }
}`,...y.parameters?.docs?.source}}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    hasTemplateButton: true,
    wordingTemplate: 'Template content...',
    onPressTemplateButton: () => {}
  }
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
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
}`,...x.parameters?.docs?.source}}};var S=[`Default`,`WithError`,`WithInitialHeight`,`Disabled`,`WithGeneratedTemplate`,`WithinForm`];export{g as Default,y as Disabled,_ as WithError,b as WithGeneratedTemplate,v as WithInitialHeight,x as WithinForm,S as __namedExportsOrder,h as default};