import{a as e,n as t}from"./rolldown-runtime-DkW27tQK.js";import{f as n}from"./iframe-DUJeN7Co.js";import{t as r}from"./jsx-runtime-DeHZSEgm.js";import{t as i}from"./classnames-D09xBJOL.js";import{n as a,t as o}from"./SvgIcon-DRPrlrFF.js";import{n as s,r as c}from"./FormLayoutSideComponentContext-C6J0Vyw1.js";import{n as l,r as u}from"./Tag-BZ3ZrpxM.js";import{n as d,t as f}from"./full-error-BAxfKzLK.js";import{n as p,t as m}from"./assertOrFrontendError-1BmE5jKA.js";import{n as h,t as g}from"./stroke-date-DpapDUHs.js";import{n as _,t as v}from"./dog-CXGBgOem.js";import{n as y,t as b}from"./light.web-3-jOaeS_.js";import{n as x,t as S}from"./RadioButton-CgyklSpC.js";var C;function w(){return(w=t((()=>{C={"radio-button-group":`_radio-button-group_33h3t_1`,"radio-button-group-legend":`_radio-button-group-legend_33h3t_6`,"radio-button-group-description":`_radio-button-group-description_33h3t_12`,"label-as-text":`_label-as-text_33h3t_20`,"radio-button-group-error":`_radio-button-group-error_33h3t_26`,"radio-button-group-error-icon":`_radio-button-group-error-icon_33h3t_36`,"radio-button-group-options":`_radio-button-group-options_33h3t_43`,"display-horizontal":`_display-horizontal_33h3t_50`,"sizing-fill":`_sizing-fill_33h3t_50`,"radio-button-group-option":`_radio-button-group-option_33h3t_43`,"display-vertical":`_display-vertical_33h3t_54`,"variant-detailed":`_variant-detailed_33h3t_60`}})))()}var T,E,D,O;function k(){return(k=t((()=>{T=e(i(),1),E=n(),s(),p(),x(),d(),a(),w(),D=r(),O=({name:e,label:t,options:n,description:r,error:i,variant:a=`default`,sizing:s=`fill`,display:l=`vertical`,disabled:u=!1,checkedOption:d,asset:p,onChange:h,onBlur:g,describedBy:_})=>{let v=c(),y=(0,E.useId)(),b=(0,E.useId)(),x=[i?y:``,r?b:``,_??``,v??``].filter(Boolean).join(` `),w=typeof t==`string`,O=n.map(e=>e.value);return m(new Set(O).size===O.length,`RadioButtonGroup options must have unique values.`),(0,D.jsxs)(`fieldset`,{"aria-describedby":x||void 0,"aria-invalid":!!i||void 0,className:(0,T.default)(C[`radio-button-group`],{[C[`label-as-text`]]:w}),children:[(0,D.jsx)(`legend`,{className:C[`radio-button-group-legend`],children:t}),(0,D.jsxs)(`div`,{className:C[`radio-button-group-header`],children:[r&&(0,D.jsx)(`span`,{id:b,className:C[`radio-button-group-description`],"aria-live":`polite`,children:r}),(0,D.jsx)(`div`,{role:`alert`,id:y,children:i&&(0,D.jsxs)(`span`,{className:C[`radio-button-group-error`],children:[(0,D.jsx)(o,{className:C[`radio-button-group-error-icon`],src:f,alt:`Erreur`}),i]})})]}),(0,D.jsx)(`div`,{className:(0,T.default)(C[`radio-button-group-options`],C[`display-${l}`],C[`sizing-${s}`],C[`variant-${a}`]),children:n.map(t=>(0,D.jsx)(`div`,{className:C[`radio-button-group-option`],children:(0,D.jsx)(S,{name:e,variant:a,sizing:s,disabled:u,hasError:!!i,onChange:h,onBlur:g,asset:p,...t,...h&&{checked:d===t.value}})},t.value))})]})};try{O.displayName=`RadioButtonGroup`,O.__docgenInfo={description:``,displayName:`RadioButtonGroup`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,methods:[],props:{name:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Name of the radio button group, binding all radio buttons together`,name:`name`,required:!0,tags:{},type:{name:`string`}},label:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Label for the radio button group`,name:`label`,required:!0,tags:{},type:{name:`ReactNode`}},options:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`List of options as radio buttons`,name:`options`,required:!0,tags:{},type:{name:`Omit<RadioButtonProps, "name">[]`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:``,name:`description`,required:!1,tags:{},type:{name:`string`}},error:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Error message for the radio button group`,name:`error`,required:!1,tags:{},type:{name:`string`}},variant:{defaultValue:{value:`default`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Variant of the radio buttons (applied to all), defaults to 'default'`,name:`variant`,required:!1,tags:{},type:{name:`enum`,raw:`RadioButtonVariant`,value:[{value:`"default"`},{value:`"detailed"`}]}},sizing:{defaultValue:{value:`fill`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Sizing of the radio buttons (applied to all), defaults to 'fill'`,name:`sizing`,required:!1,tags:{},type:{name:`enum`,raw:`RadioButtonSizing`,value:[{value:`"hug"`},{value:`"fill"`}]}},asset:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Asset of the radio buttons (applied to all), displayed when variant is 'detailed'`,name:`asset`,required:!1,tags:{},type:{name:`AssetProps`}},display:{defaultValue:{value:`vertical`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Display style of the radio button group, defaults to 'vertical'`,name:`display`,required:!1,tags:{},type:{name:`enum`,raw:`"horizontal" | "vertical"`,value:[{value:`"horizontal"`},{value:`"vertical"`}]}},checkedOption:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Selected option, required if the group is non-controlled`,name:`checkedOption`,required:!1,tags:{},type:{name:`string`}},disabled:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`If the radio button group is disabled, making all options unselectable`,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Event handler for change`,name:`onChange`,required:!1,tags:{},type:{name:`((event: ChangeEvent<HTMLInputElement, Element>) => void)`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Event handler for blur`,name:`onBlur`,required:!1,tags:{},type:{name:`((event: FocusEvent<HTMLInputElement, Element>) => void)`}},describedBy:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:``,name:`describedBy`,required:!1,tags:{},type:{name:`string`}}},tags:{}}}catch{}})))()}var A,j,M,N,P,F,I,L,R,z,B,V,H,U,W,G,K,q,J,Y;function X(){return(X=t((()=>{A=n(),x(),u(),g(),_(),k(),b(),j=r(),M={title:`@/design-system/RadioButtonGroup`,component:O},N=[{label:`Option 1`,name:`group1`,description:`Description 1`,value:`1`},{label:`Option 2`,name:`group1`,description:`Description 2 that is a little longer...`,value:`2`},{label:`Option 3`,name:`group1`,description:`Description 3`,value:`3`}],P={label:`Option 4`,name:`group1`,description:`Description 4`,value:`4`,collapsed:(0,j.jsxs)(`div`,{style:{display:`flex`,flexDirection:`row`,gap:16},children:[(0,j.jsx)(S,{name:`subchoice`,label:`Sous-label 1`,value:`1`}),(0,j.jsx)(S,{name:`subchoice`,label:`Sous-label 2`,value:`2`})]})},F={args:{name:`radio-button-group`,label:`Radio Button Group`,options:N}},I={args:{name:`radio-button-group`,label:`Detailed Radio Button Group`,variant:`detailed`,options:N}},L={args:{name:`radio-button-group`,label:`Detailed Radio Button Group`,variant:`detailed`,sizing:`hug`,options:N}},R={args:{name:`radio-button-group`,label:`Horizontal Radio Button Group`,variant:`detailed`,display:`horizontal`,sizing:`fill`,options:N}},z={args:{name:`radio-button-group`,label:`Hugged Horizontal Radio Button Group`,variant:`detailed`,display:`horizontal`,sizing:`hug`,options:N}},B={args:{name:`radio-button-group`,label:`Disabled Radio Button Group`,disabled:!0,variant:`detailed`,options:N}},V={args:{name:`radio-button-group`,label:`Radio Button Group with Description`,description:`This is a description for the radio button group.`,options:N}},H={args:{name:`radio-button-group`,label:(0,j.jsx)(`h2`,{style:{fontFamily:y.typography.title2.fontFamily,lineHeight:y.typography.title2.lineHeight,fontSize:y.typography.title2.fontSize},children:`Radio Button Group with Heading Tag as Title`}),options:N,description:`This is a description for the radio button group.`}},U={args:{name:`radio-button-group`,label:`Radio Button Group with Error`,error:`This is an error message.`,options:N}},W={args:{name:`radio-button-group`,label:`Radio Button Group with Common Tag`,variant:`detailed`,asset:{variant:`tag`,tag:{label:`Tag`,variant:l.SUCCESS}},options:N}},G={args:{name:`radio-button-group`,label:`Radio Button Group with Common Text`,variant:`detailed`,asset:{variant:`text`,text:`19€`},options:N}},K={args:{name:`radio-button-group`,label:`Radio Button Group with Common Icon`,variant:`detailed`,asset:{variant:`icon`,src:h},options:N}},q={args:{name:`radio-button-group`,label:`Radio Button Group with Common Image`,variant:`detailed`,asset:{variant:`image`,src:v,size:`s`},options:N}},J={render:()=>{let[e,t]=(0,A.useState)(P.value);return(0,j.jsx)(O,{name:`radio-button-group`,label:`Radio Button Group with Collapsed Option`,variant:`detailed`,checkedOption:e,onChange:e=>t(e.target.value),options:[...N,P]})}},Y=[`Default`,`Detailed`,`DetailedHugged`,`FilledHorizontalDisplay`,`HuggedHorizontalDisplay`,`Disabled`,`WithDescription`,`WithHeadingTagAsTitle`,`WithError`,`WithCommonTag`,`WithCommonText`,`WithCommonIcon`,`WithCommonImage`,`WithCollapsed`],F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group',
    options
  }
}`,...F.parameters?.docs?.source}}},I.parameters={...I.parameters,docs:{...I.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    options
  }
}`,...I.parameters?.docs?.source}}},L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    sizing: 'hug',
    options
  }
}`,...L.parameters?.docs?.source}}},R.parameters={...R.parameters,docs:{...R.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'fill',
    options
  }
}`,...R.parameters?.docs?.source}}},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Hugged Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'hug',
    options
  }
}`,...z.parameters?.docs?.source}}},B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Disabled Radio Button Group',
    disabled: true,
    variant: 'detailed',
    options
  }
}`,...B.parameters?.docs?.source}}},V.parameters={...V.parameters,docs:{...V.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Description',
    description: 'This is a description for the radio button group.',
    options
  }
}`,...V.parameters?.docs?.source}}},H.parameters={...H.parameters,docs:{...H.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: <h2 style={{
      fontFamily: theme.typography.title2.fontFamily,
      lineHeight: theme.typography.title2.lineHeight,
      fontSize: theme.typography.title2.fontSize
    }}>Radio Button Group with Heading Tag as Title</h2>,
    options,
    description: 'This is a description for the radio button group.'
  }
}`,...H.parameters?.docs?.source}}},U.parameters={...U.parameters,docs:{...U.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Error',
    error: 'This is an error message.',
    options
  }
}`,...U.parameters?.docs?.source}}},W.parameters={...W.parameters,docs:{...W.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Common Tag',
    variant: 'detailed',
    asset: {
      variant: 'tag',
      tag: {
        label: 'Tag',
        variant: TagVariant.SUCCESS
      }
    },
    options
  }
}`,...W.parameters?.docs?.source}}},G.parameters={...G.parameters,docs:{...G.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Common Text',
    variant: 'detailed',
    asset: {
      variant: 'text',
      text: '19€'
    },
    options
  }
}`,...G.parameters?.docs?.source}}},K.parameters={...K.parameters,docs:{...K.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Common Icon',
    variant: 'detailed',
    asset: {
      variant: 'icon',
      src: strokeDateIcon
    },
    options
  }
}`,...K.parameters?.docs?.source}}},q.parameters={...q.parameters,docs:{...q.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Common Image',
    variant: 'detailed',
    asset: {
      variant: 'image',
      src: imageDemo,
      size: 's'
    },
    options
  }
}`,...q.parameters?.docs?.source}}},J.parameters={...J.parameters,docs:{...J.parameters?.docs,source:{originalSource:`{
  render: () => {
    const [checkedOption, setCheckedOption] = useState<string>(collapsedOption.value);
    return <RadioButtonGroup name="radio-button-group" label="Radio Button Group with Collapsed Option" variant="detailed" checkedOption={checkedOption} onChange={e => setCheckedOption(e.target.value)} options={[...options, collapsedOption]} />;
  }
}`,...J.parameters?.docs?.source}}}})))()}X();export{F as Default,I as Detailed,L as DetailedHugged,B as Disabled,R as FilledHorizontalDisplay,z as HuggedHorizontalDisplay,J as WithCollapsed,K as WithCommonIcon,q as WithCommonImage,W as WithCommonTag,G as WithCommonText,V as WithDescription,U as WithError,H as WithHeadingTagAsTitle,Y as __namedExportsOrder,M as default};