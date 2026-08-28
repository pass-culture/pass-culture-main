import{a as e,n as t}from"./rolldown-runtime-DkW27tQK.js";import{d as n}from"./iframe-Dcc9vyTo.js";import{t as r}from"./jsx-runtime-DeHZSEgm.js";import{t as i}from"./classnames-D09xBJOL.js";import{n as a,t as o}from"./Button-BDZFzen8.js";import{n as s,r as c}from"./FormLayoutSideComponentContext-CZ0JR0Ne.js";import{n as l,t as u}from"./FieldFooter-B_D2Lv0D.js";import{i as d,o as f,s as p,t as m}from"./index.esm-DIXGw63T.js";var h,g,_,v;function y(){return(y=t((()=>{h=`_wrapper_1p6gr_2`,g=`_label_1p6gr_58`,_=`_description_1p6gr_71`,v={wrapper:h,"text-area":`_text-area_1p6gr_6`,"has-error":`_has-error_1p6gr_53`,label:g,"has-description":`_has-description_1p6gr_58`,"template-button":`_template-button_1p6gr_65`,description:_,"field-header-right":`_field-header-right_1p6gr_80`}})))()}var b,x,S,C;function w(){return(w=t((()=>{b=e(i(),1),x=n(),s(),a(),l(),y(),S=r(),C=(0,x.forwardRef)(({name:e,className:t,disabled:n,description:r,label:i,maxLength:a=1e3,required:s=!1,requiredIndicator:l=`symbol`,initialRows:d=7,hasTemplateButton:f=!1,wordingTemplate:p,hasDefaultPlaceholder:m,onPressTemplateButton:h,error:g,onChange:_,onBlur:y,value:C,describedBy:w},T)=>{let E=c(),D=(0,x.useRef)(null),[O,k]=(0,x.useState)(C),A=(0,x.useId)(),j=(0,x.useId)(),M=(0,x.useId)(),N=(0,x.useId)(),P=D.current?.value?.length??O?.length??0;(0,x.useImperativeHandle)(T,()=>D.current);let F=(0,x.useCallback)(()=>{if(D.current){D.current.style.height=`unset`;let e=D.current.scrollHeight;e>0&&(D.current.style.height=`${f?e+92:e}px`)}},[f]);(0,x.useEffect)(()=>{F()},[F]);let I=[r?j:``,g?N:``,M,w??``,E??``].filter(Boolean).join(` `),L=()=>{p&&k(p),D.current&&(D.current.focus(),D.current.setSelectionRange(128,128)),h?.()};return(0,S.jsxs)(`div`,{className:t,children:[(0,S.jsxs)(`div`,{children:[(0,S.jsxs)(`label`,{className:(0,b.default)(v.label,{[v[`has-description`]]:!!r}),htmlFor:A,children:[i,s&&l===`symbol`&&(0,S.jsx)(S.Fragment,{children:`\xA0*`}),s&&l===`explicit`&&(0,S.jsx)(`span`,{className:v[`field-header-right`],children:`Obligatoire`})]}),r&&(0,S.jsx)(`p`,{id:j,"data-testid":`description-${e}`,className:v.description,children:r})]}),(0,S.jsxs)(`div`,{className:v.wrapper,children:[(0,S.jsx)(`textarea`,{ref:D,"aria-invalid":!!g,"aria-describedby":I||void 0,className:(0,b.default)(v[`text-area`],{[v[`has-error`]]:!!g}),disabled:n,id:A,rows:d,value:O,maxLength:a,"aria-required":!s,placeholder:m?`Écrivez ici...`:void 0,onChange:t=>{k(t.target.value),_&&_({...t,target:{...t.target,value:t.target.value,name:e}})},onBlur:t=>{k(t.target.value),y&&y({...t,target:{...t.target,value:t.target.value,name:e}})}}),f&&(0,S.jsx)(`div`,{className:v[`template-button`],children:(0,S.jsx)(o,{onClick:L,disabled:!!O?.length,label:`Générer un modèle`})})]}),(0,S.jsx)(u,{error:g,errorId:N,charactersCount:{current:P,max:a},charactersCountId:M})]})}),C.displayName=`TextArea`;try{C.displayName=`TextArea`,C.__docgenInfo={description:``,displayName:`TextArea`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/form/TextArea/TextArea.tsx`,methods:[],props:{name:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`The name of the textarea field.`,name:`name`,required:!0,tags:{},type:{name:`string`}},initialRows:{defaultValue:{value:`7`},declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`The initial number of visible text lines for the control. The field will still expand indefinitely if the input is higher than this value.`,name:`initialRows`,required:!1,tags:{default:`7`},type:{name:`number`}},maxLength:{defaultValue:{value:`1000`},declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`The maximum number of characters allowed in the textarea.`,name:`maxLength`,required:!1,tags:{default:`1000`},type:{name:`number`}},required:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Whether the field is optional.`,name:`required`,required:!1,tags:{},type:{name:`boolean`}},label:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`The label text for the textarea.`,name:`label`,required:!0,tags:{},type:{name:`ReactNode`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`A description providing additional information about the textarea.`,name:`description`,required:!1,tags:{},type:{name:`string`}},className:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Custom CSS class for the textarea component.`,name:`className`,required:!1,tags:{},type:{name:`string`}},disabled:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Whether the textarea is disabled.`,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},hasDefaultPlaceholder:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:``,name:`hasDefaultPlaceholder`,required:!1,tags:{},type:{name:`boolean`}},requiredIndicator:{defaultValue:{value:`symbol`},declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`What type of required indicator is displayed`,name:`requiredIndicator`,required:!1,tags:{},type:{name:`enum`,raw:`RequiredIndicator`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}},error:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Error text displayed under the field. If the error is trythy, the field has the error styles.`,name:`error`,required:!1,tags:{},type:{name:`string`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:``,name:`onChange`,required:!1,tags:{},type:{name:`((e: { target: { value: string; name?: string; }; }) => void)`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:``,name:`onBlur`,required:!1,tags:{},type:{name:`((e: FocusEvent<HTMLTextAreaElement, Element>) => void)`}},value:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:``,name:`value`,required:!1,tags:{},type:{name:`string`}},describedBy:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:``,name:`describedBy`,required:!1,tags:{},type:{name:`string`}},hasTemplateButton:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`},{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Whether the template button should be displayed.`,name:`hasTemplateButton`,required:!1,tags:{},type:{name:`boolean`}},wordingTemplate:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`},{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Content of the templated added to the field when the template button is clicked`,name:`wordingTemplate`,required:!1,tags:{},type:{name:`string`}},onPressTemplateButton:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`},{fileName:`pro/src/ui-kit/form/TextArea/TextArea.tsx`,name:`TypeLiteral`}],description:`Callback after the template button is clicked.`,name:`onPressTemplateButton`,required:!1,tags:{},type:{name:`(() => void)`}}},tags:{param:`props - The props for the TextArea component.`,returns:`The rendered TextArea component.`,example:`<TextArea
  name="message"
  label="Your Message"
  description="Please enter your message."
  maxLength={500}
/>`}}}catch{}})))()}var T,E,D,O,k,A,j,M,N,P;function F(){return(F=t((()=>{d(),w(),T=r(),E=({children:e})=>{let t=f({defaultValues:{myField:`default value`}});return(0,T.jsx)(m,{...t,children:(0,T.jsx)(`form`,{children:e})})},D={title:`@/ui-kit/forms/TextArea`,component:C},O={args:{name:`description`,label:`Description`,required:!0}},k={args:{name:`description`,label:`Description`,error:`This is an error`}},A={args:{name:`description`,label:`Description`,initialRows:20}},j={args:{name:`description`,label:`Description`,disabled:!0}},M={args:{name:`description`,label:`Description`,hasTemplateButton:!0,wordingTemplate:`Template content...`,onPressTemplateButton:()=>{}}},N={args:{name:`description`,label:`Description`},decorators:[e=>(0,T.jsx)(E,{children:(0,T.jsx)(e,{})})],render:e=>{let{setValue:t,watch:n}=p();return(0,T.jsx)(C,{...e,value:n(`myField`),onChange:e=>{t(`myField`,e.target.value)}})}},O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    required: true
  }
}`,...O.parameters?.docs?.source}}},k.parameters={...k.parameters,docs:{...k.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    error: 'This is an error'
  }
}`,...k.parameters?.docs?.source}}},A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    initialRows: 20
  }
}`,...A.parameters?.docs?.source}}},j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    disabled: true
  }
}`,...j.parameters?.docs?.source}}},M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'description',
    label: 'Description',
    hasTemplateButton: true,
    wordingTemplate: 'Template content...',
    onPressTemplateButton: () => {}
  }
}`,...M.parameters?.docs?.source}}},N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
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
}`,...N.parameters?.docs?.source}}},P=[`Default`,`WithError`,`WithInitialHeight`,`Disabled`,`WithGeneratedTemplate`,`WithinForm`]})))()}F();export{O as Default,j as Disabled,k as WithError,M as WithGeneratedTemplate,A as WithInitialHeight,N as WithinForm,P as __namedExportsOrder,D as default};