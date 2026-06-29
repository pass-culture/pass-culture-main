import{i as e,s as t}from"./preload-helper-xPQekRTU.js";import{C as n}from"./iframe-BSjMbmwf.js";import{t as r}from"./jsx-runtime-CaZkqeYb.js";import{t as i}from"./classnames-Dm_LJ4P4.js";import{n as a,t as o}from"./Button-CUSpUoO-.js";import{n as s,t as c}from"./FieldFooter-BvC7uffD.js";import{i as l,o as u,s as d,t as f}from"./index.esm-C5X_SmZ2.js";var p,m,h,g,_=e((()=>{p=`_wrapper_16amp_2`,m=`_label_16amp_58`,h=`_description_16amp_69`,g={wrapper:p,"text-area":`_text-area_16amp_6`,"has-error":`_has-error_16amp_53`,label:m,"has-description":`_has-description_16amp_58`,"template-button":`_template-button_16amp_63`,description:h,"field-header-right":`_field-header-right_16amp_78`}})),v,y,b,x,S=e((()=>{v=t(i(),1),y=t(n(),1),a(),s(),_(),b=r(),x=(0,y.forwardRef)(({name:e,className:t,disabled:n,description:r,label:i,maxLength:a=1e3,required:s=!1,requiredIndicator:l=`symbol`,initialRows:u=7,hasTemplateButton:d=!1,wordingTemplate:f,hasDefaultPlaceholder:p,onPressTemplateButton:m,error:h,onChange:_,onBlur:x,value:S},C)=>{let w=(0,y.useRef)(null),[T,E]=(0,y.useState)(S),D=(0,y.useId)(),O=(0,y.useId)(),k=(0,y.useId)(),A=(0,y.useId)(),j=T?.length??0;(0,y.useImperativeHandle)(C,()=>w.current);let M=(0,y.useCallback)(()=>{if(w.current){w.current.style.height=`unset`;let e=w.current.scrollHeight;w.current.style.height=`${d?e+92:e}px`}},[d]);(0,y.useEffect)(()=>{M()},[M]);let N=[k,A];r&&N.unshift(O);let P=()=>{f&&E(f),w.current&&(w.current.focus(),w.current.setSelectionRange(128,128)),m?.()};return(0,b.jsxs)(`div`,{className:t,children:[(0,b.jsxs)(`div`,{children:[(0,b.jsxs)(`label`,{className:(0,v.default)(g.label,{[g[`has-description`]]:!!r}),htmlFor:D,children:[i,s&&l===`symbol`&&(0,b.jsx)(b.Fragment,{children:`\xA0*`}),s&&l===`explicit`&&(0,b.jsx)(`span`,{className:g[`field-header-right`],children:`Obligatoire`})]}),r&&(0,b.jsx)(`span`,{id:O,"data-testid":`description-${e}`,className:g.description,children:r})]}),(0,b.jsxs)(`div`,{className:g.wrapper,children:[(0,b.jsx)(`textarea`,{ref:w,"aria-invalid":!!h,"aria-describedby":N.join(` `),className:(0,v.default)(g[`text-area`],{[g[`has-error`]]:!!h}),disabled:n,id:D,rows:u,value:T,maxLength:a,"aria-required":!s,placeholder:p?`Écrivez ici...`:void 0,onChange:t=>{E(t.target.value),_&&_({...t,target:{...t.target,value:t.target.value,name:e}})},onBlur:t=>{E(t.target.value),x&&x({...t,target:{...t.target,value:t.target.value,name:e}})}}),d&&(0,b.jsx)(`div`,{className:g[`template-button`],children:(0,b.jsx)(o,{onClick:P,disabled:!!T?.length,label:`Générer un modèle`})})]}),(0,b.jsx)(c,{error:h,errorId:A,charactersCount:{current:j,max:a},charactersCountId:k})]})}),x.displayName=`TextArea`;try{x.displayName=`TextArea`,x.__docgenInfo={description:``,displayName:`TextArea`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/form/TextArea/TextArea.tsx`,methods:[],props:{name:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`The name of the textarea field.`,name:`name`,required:!0,tags:{},type:{name:`string`}},initialRows:{defaultValue:{value:`7`},declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`The initial number of visible text lines for the control. The field will still expand indefinitely if the input is higher than this value.`,name:`initialRows`,required:!1,tags:{default:`7`},type:{name:`number`}},maxLength:{defaultValue:{value:`1000`},declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`The maximum number of characters allowed in the textarea.`,name:`maxLength`,required:!1,tags:{default:`1000`},type:{name:`number`}},required:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Whether the field is optional.`,name:`required`,required:!1,tags:{},type:{name:`boolean`}},label:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`The label text for the textarea.`,name:`label`,required:!0,tags:{},type:{name:`ReactNode`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`A description providing additional information about the textarea.`,name:`description`,required:!1,tags:{},type:{name:`string`}},className:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Custom CSS class for the textarea component.`,name:`className`,required:!1,tags:{},type:{name:`string`}},disabled:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Whether the textarea is disabled.`,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},hasDefaultPlaceholder:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:``,name:`hasDefaultPlaceholder`,required:!1,tags:{},type:{name:`boolean`}},requiredIndicator:{defaultValue:{value:`symbol`},declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`What type of required indicator is displayed`,name:`requiredIndicator`,required:!1,tags:{},type:{name:`enum`,raw:`RequiredIndicator`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}},error:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Error text displayed under the field. If the error is trythy, the field has the error styles.`,name:`error`,required:!1,tags:{},type:{name:`string`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:``,name:`onChange`,required:!1,tags:{},type:{name:`((e: { target: { value: string; name?: string; }; }) => void)`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:``,name:`onBlur`,required:!1,tags:{},type:{name:`((e: FocusEvent<HTMLTextAreaElement, Element>) => void)`}},value:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:``,name:`value`,required:!1,tags:{},type:{name:`string`}},hasTemplateButton:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`},{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Whether the template button should be displayed.`,name:`hasTemplateButton`,required:!1,tags:{},type:{name:`boolean`}},wordingTemplate:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`},{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Content of the templated added to the field when the template button is clicked`,name:`wordingTemplate`,required:!1,tags:{},type:{name:`string`}},onPressTemplateButton:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`},{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Callback after the template button is clicked.`,name:`onPressTemplateButton`,required:!1,tags:{},type:{name:`(() => void)`}}},tags:{param:`props - The props for the TextArea component.`,returns:`The rendered TextArea component.`,example:`<TextArea
  name="message"
  label="Your Message"
  description="Please enter your message."
  maxLength={500}
/>`}}}catch{}})),C,w,T,E,D,O,k,A,j,M;e((()=>{l(),S(),C=r(),w=({children:e})=>(0,C.jsx)(f,{...u({defaultValues:{myField:`default value`}}),children:(0,C.jsx)(`form`,{children:e})}),T={title:`@/ui-kit/forms/TextArea`,component:x},E={args:{name:`description`,label:`Description`,required:!0}},D={args:{name:`description`,label:`Description`,error:`This is an error`}},O={args:{name:`description`,label:`Description`,initialRows:20}},k={args:{name:`description`,label:`Description`,disabled:!0}},A={args:{name:`description`,label:`Description`,hasTemplateButton:!0,wordingTemplate:`Template content...`,onPressTemplateButton:()=>{}}},j={args:{name:`description`,label:`Description`},decorators:[e=>(0,C.jsx)(w,{children:(0,C.jsx)(e,{})})],render:e=>{let{setValue:t,watch:n}=d();return(0,C.jsx)(x,{...e,value:n(`myField`),onChange:e=>{t(`myField`,e.target.value)}})}},E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    required: true
  }
}`,...E.parameters?.docs?.source}}},D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    error: 'This is an error'
  }
}`,...D.parameters?.docs?.source}}},O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    initialRows: 20
  }
}`,...O.parameters?.docs?.source}}},k.parameters={...k.parameters,docs:{...k.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    disabled: true
  }
}`,...k.parameters?.docs?.source}}},A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    hasTemplateButton: true,
    wordingTemplate: 'Template content...',
    onPressTemplateButton: () => {}
  }
}`,...A.parameters?.docs?.source}}},j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description'
  },
  decorators: [(Story: any) => <Wrapper>
        <Story />
      </Wrapper>],
  render: (args: any) => {
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
}`,...j.parameters?.docs?.source}}},M=[`Default`,`WithError`,`WithInitialHeight`,`Disabled`,`WithGeneratedTemplate`,`WithinForm`]}))();export{E as Default,k as Disabled,D as WithError,A as WithGeneratedTemplate,O as WithInitialHeight,j as WithinForm,M as __namedExportsOrder,T as default};