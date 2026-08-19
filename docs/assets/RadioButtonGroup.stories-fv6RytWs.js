import{a as e,n as t}from"./rolldown-runtime-DkW27tQK.js";import{d as n}from"./iframe-Comgj_ZN.js";import{t as r}from"./jsx-runtime-DeHZSEgm.js";import{t as i}from"./classnames-D09xBJOL.js";import{n as a,t as o}from"./SvgIcon-DRPrlrFF.js";import{n as s,r as c}from"./FormLayoutSideComponentContext-CEf_tDlA.js";import{n as l,r as u}from"./Tag-Bs8URsvh.js";import{n as d}from"./full-error-23kXpe9X.js";import{n as f,t as p}from"./assertOrFrontendError-DO345Qa4.js";import{n as m,t as h}from"./stroke-date-CgooKoSV.js";import{n as g,t as _}from"./dog-BpyAKmCU.js";import{n as v,t as y}from"./light.web-3-jOaeS_.js";import{n as b,t as x}from"./RadioButton-BVbxTviE.js";var S;function C(){return(C=t((()=>{S={"radio-button-group":`_radio-button-group_33h3t_1`,"radio-button-group-legend":`_radio-button-group-legend_33h3t_6`,"radio-button-group-description":`_radio-button-group-description_33h3t_12`,"label-as-text":`_label-as-text_33h3t_20`,"radio-button-group-error":`_radio-button-group-error_33h3t_26`,"radio-button-group-error-icon":`_radio-button-group-error-icon_33h3t_36`,"radio-button-group-options":`_radio-button-group-options_33h3t_43`,"display-horizontal":`_display-horizontal_33h3t_50`,"sizing-fill":`_sizing-fill_33h3t_50`,"radio-button-group-option":`_radio-button-group-option_33h3t_43`,"display-vertical":`_display-vertical_33h3t_54`,"variant-detailed":`_variant-detailed_33h3t_60`}})))()}var w,T,E,D;function O(){return(O=t((()=>{w=e(i(),1),T=n(),s(),f(),b(),d(),a(),C(),E=r(),D=({name:e,label:t,options:n,description:r,error:i,variant:a=`default`,sizing:s=`fill`,display:l=`vertical`,disabled:u=!1,checkedOption:d,asset:f,onChange:m,onBlur:h,describedBy:g})=>{let _=c(),v=(0,T.useId)(),y=(0,T.useId)(),b=[i?v:``,r?y:``,g??``,_??``].filter(Boolean).join(` `),C=typeof t==`string`,D=n.map(e=>e.value);return p(new Set(D).size===D.length,`RadioButtonGroup options must have unique values.`),(0,E.jsxs)(`fieldset`,{"aria-describedby":b||void 0,className:(0,w.default)(S[`radio-button-group`],{[S[`label-as-text`]]:C}),children:[(0,E.jsx)(`legend`,{className:S[`radio-button-group-legend`],children:t}),(0,E.jsxs)(`div`,{className:S[`radio-button-group-header`],children:[r&&(0,E.jsx)(`span`,{id:y,className:S[`radio-button-group-description`],"aria-live":`polite`,children:r}),(0,E.jsx)(`div`,{role:`alert`,id:v,children:i&&(0,E.jsxs)(`span`,{className:S[`radio-button-group-error`],children:[(0,E.jsx)(o,{className:S[`radio-button-group-error-icon`],src:``+new URL(`full-error-BxG7-hWY.svg`,import.meta.url).href,alt:`Erreur`}),i]})})]}),(0,E.jsx)(`div`,{className:(0,w.default)(S[`radio-button-group-options`],S[`display-${l}`],S[`sizing-${s}`],S[`variant-${a}`]),children:n.map(t=>(0,E.jsx)(`div`,{className:S[`radio-button-group-option`],children:(0,E.jsx)(x,{name:e,variant:a,sizing:s,disabled:u,hasError:!!i,onChange:m,onBlur:h,asset:f,...t,...m&&{checked:d===t.value}})},t.value))})]})};try{D.displayName=`RadioButtonGroup`,D.__docgenInfo={description:``,displayName:`RadioButtonGroup`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,methods:[],props:{name:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Name of the radio button group, binding all radio buttons together`,name:`name`,required:!0,tags:{},type:{name:`string`}},label:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Label for the radio button group`,name:`label`,required:!0,tags:{},type:{name:`ReactNode`}},options:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`List of options as radio buttons`,name:`options`,required:!0,tags:{},type:{name:`Omit<RadioButtonProps, "name">[]`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:``,name:`description`,required:!1,tags:{},type:{name:`string`}},error:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Error message for the radio button group`,name:`error`,required:!1,tags:{},type:{name:`string`}},variant:{defaultValue:{value:`default`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Variant of the radio buttons (applied to all), defaults to 'default'`,name:`variant`,required:!1,tags:{},type:{name:`enum`,raw:`RadioButtonVariant`,value:[{value:`"default"`},{value:`"detailed"`}]}},sizing:{defaultValue:{value:`fill`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Sizing of the radio buttons (applied to all), defaults to 'fill'`,name:`sizing`,required:!1,tags:{},type:{name:`enum`,raw:`RadioButtonSizing`,value:[{value:`"fill"`},{value:`"hug"`}]}},asset:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Asset of the radio buttons (applied to all), displayed when variant is 'detailed'`,name:`asset`,required:!1,tags:{},type:{name:`AssetProps`}},display:{defaultValue:{value:`vertical`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Display style of the radio button group, defaults to 'vertical'`,name:`display`,required:!1,tags:{},type:{name:`enum`,raw:`"horizontal" | "vertical"`,value:[{value:`"horizontal"`},{value:`"vertical"`}]}},checkedOption:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Selected option, required if the group is non-controlled`,name:`checkedOption`,required:!1,tags:{},type:{name:`string`}},disabled:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`If the radio button group is disabled, making all options unselectable`,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Event handler for change`,name:`onChange`,required:!1,tags:{},type:{name:`((event: ChangeEvent<HTMLInputElement, Element>) => void)`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Event handler for blur`,name:`onBlur`,required:!1,tags:{},type:{name:`((event: FocusEvent<HTMLInputElement, Element>) => void)`}},describedBy:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:``,name:`describedBy`,required:!1,tags:{},type:{name:`string`}}},tags:{}}}catch{}})))()}var k,A,j,M,N,P,F,I,L,R,z,B,V,H,U,W,G,K,q,J;function Y(){return(Y=t((()=>{k=n(),b(),u(),h(),g(),O(),y(),A=r(),j={title:`@/design-system/RadioButtonGroup`,component:D},M=[{label:`Option 1`,name:`group1`,description:`Description 1`,value:`1`},{label:`Option 2`,name:`group1`,description:`Description 2 that is a little longer...`,value:`2`},{label:`Option 3`,name:`group1`,description:`Description 3`,value:`3`}],N={label:`Option 4`,name:`group1`,description:`Description 4`,value:`4`,collapsed:(0,A.jsxs)(`div`,{style:{display:`flex`,flexDirection:`row`,gap:16},children:[(0,A.jsx)(x,{name:`subchoice`,label:`Sous-label 1`,value:`1`}),(0,A.jsx)(x,{name:`subchoice`,label:`Sous-label 2`,value:`2`})]})},P={args:{name:`radio-button-group`,label:`Radio Button Group`,options:M}},F={args:{name:`radio-button-group`,label:`Detailed Radio Button Group`,variant:`detailed`,options:M}},I={args:{name:`radio-button-group`,label:`Detailed Radio Button Group`,variant:`detailed`,sizing:`hug`,options:M}},L={args:{name:`radio-button-group`,label:`Horizontal Radio Button Group`,variant:`detailed`,display:`horizontal`,sizing:`fill`,options:M}},R={args:{name:`radio-button-group`,label:`Hugged Horizontal Radio Button Group`,variant:`detailed`,display:`horizontal`,sizing:`hug`,options:M}},z={args:{name:`radio-button-group`,label:`Disabled Radio Button Group`,disabled:!0,variant:`detailed`,options:M}},B={args:{name:`radio-button-group`,label:`Radio Button Group with Description`,description:`This is a description for the radio button group.`,options:M}},V={args:{name:`radio-button-group`,label:(0,A.jsx)(`h2`,{style:{fontFamily:v.typography.title2.fontFamily,lineHeight:v.typography.title2.lineHeight,fontSize:v.typography.title2.fontSize},children:`Radio Button Group with Heading Tag as Title`}),options:M,description:`This is a description for the radio button group.`}},H={args:{name:`radio-button-group`,label:`Radio Button Group with Error`,error:`This is an error message.`,options:M}},U={args:{name:`radio-button-group`,label:`Radio Button Group with Common Tag`,variant:`detailed`,asset:{variant:`tag`,tag:{label:`Tag`,variant:l.SUCCESS}},options:M}},W={args:{name:`radio-button-group`,label:`Radio Button Group with Common Text`,variant:`detailed`,asset:{variant:`text`,text:`19€`},options:M}},G={args:{name:`radio-button-group`,label:`Radio Button Group with Common Icon`,variant:`detailed`,asset:{variant:`icon`,src:m},options:M}},K={args:{name:`radio-button-group`,label:`Radio Button Group with Common Image`,variant:`detailed`,asset:{variant:`image`,src:_,size:`s`},options:M}},q={render:()=>{let[e,t]=(0,k.useState)(N.value);return(0,A.jsx)(D,{name:`radio-button-group`,label:`Radio Button Group with Collapsed Option`,variant:`detailed`,checkedOption:e,onChange:e=>t(e.target.value),options:[...M,N]})}},P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group',
    options
  }
}`,...P.parameters?.docs?.source}}},F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    options
  }
}`,...F.parameters?.docs?.source}}},I.parameters={...I.parameters,docs:{...I.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    sizing: 'hug',
    options
  }
}`,...I.parameters?.docs?.source}}},L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'fill',
    options
  }
}`,...L.parameters?.docs?.source}}},R.parameters={...R.parameters,docs:{...R.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Hugged Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'hug',
    options
  }
}`,...R.parameters?.docs?.source}}},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Disabled Radio Button Group',
    disabled: true,
    variant: 'detailed',
    options
  }
}`,...z.parameters?.docs?.source}}},B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Description',
    description: 'This is a description for the radio button group.',
    options
  }
}`,...B.parameters?.docs?.source}}},V.parameters={...V.parameters,docs:{...V.parameters?.docs,source:{originalSource:`{
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
}`,...V.parameters?.docs?.source}}},H.parameters={...H.parameters,docs:{...H.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Error',
    error: 'This is an error message.',
    options
  }
}`,...H.parameters?.docs?.source}}},U.parameters={...U.parameters,docs:{...U.parameters?.docs,source:{originalSource:`{
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
}`,...U.parameters?.docs?.source}}},W.parameters={...W.parameters,docs:{...W.parameters?.docs,source:{originalSource:`{
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
}`,...W.parameters?.docs?.source}}},G.parameters={...G.parameters,docs:{...G.parameters?.docs,source:{originalSource:`{
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
}`,...G.parameters?.docs?.source}}},K.parameters={...K.parameters,docs:{...K.parameters?.docs,source:{originalSource:`{
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
}`,...K.parameters?.docs?.source}}},q.parameters={...q.parameters,docs:{...q.parameters?.docs,source:{originalSource:`{
  render: () => {
    const [checkedOption, setCheckedOption] = useState<string>(collapsedOption.value);
    return <RadioButtonGroup name="radio-button-group" label="Radio Button Group with Collapsed Option" variant="detailed" checkedOption={checkedOption} onChange={e => setCheckedOption(e.target.value)} options={[...options, collapsedOption]} />;
  }
}`,...q.parameters?.docs?.source}}},J=[`Default`,`Detailed`,`DetailedHugged`,`FilledHorizontalDisplay`,`HuggedHorizontalDisplay`,`Disabled`,`WithDescription`,`WithHeadingTagAsTitle`,`WithError`,`WithCommonTag`,`WithCommonText`,`WithCommonIcon`,`WithCommonImage`,`WithCollapsed`]})))()}Y();export{P as Default,F as Detailed,I as DetailedHugged,z as Disabled,L as FilledHorizontalDisplay,R as HuggedHorizontalDisplay,q as WithCollapsed,G as WithCommonIcon,K as WithCommonImage,U as WithCommonTag,W as WithCommonText,B as WithDescription,H as WithError,V as WithHeadingTagAsTitle,J as __namedExportsOrder,j as default};