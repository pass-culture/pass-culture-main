import{a as e,n as t}from"./chunk-DnJy8xQt.js";import{S as n}from"./iframe-C8wwTksf.js";import{t as r}from"./jsx-runtime-DC6t-S6Q.js";import{t as i}from"./classnames-6GGtIhaA.js";import{n as a,t as o}from"./SvgIcon-DseL4pN0.js";import{n as s,r as c}from"./Tag-CcRsdfWX.js";import{n as l}from"./full-error-CIp815Mb.js";import{n as u,t as d}from"./assertOrFrontendError-B1lIOtWI.js";import{n as f,t as p}from"./stroke-date-BhA_9fCr.js";import{n as m,t as h}from"./dog-DwuGTXK2.js";import{n as g,t as _}from"./light.web-F_31CU8o.js";import{n as v,t as y}from"./RadioButton-Ci_5w_na.js";var b,x=t((()=>{b={"radio-button-group":`_radio-button-group_33h3t_1`,"radio-button-group-legend":`_radio-button-group-legend_33h3t_6`,"radio-button-group-description":`_radio-button-group-description_33h3t_12`,"label-as-text":`_label-as-text_33h3t_20`,"radio-button-group-error":`_radio-button-group-error_33h3t_26`,"radio-button-group-error-icon":`_radio-button-group-error-icon_33h3t_36`,"radio-button-group-options":`_radio-button-group-options_33h3t_43`,"display-horizontal":`_display-horizontal_33h3t_50`,"sizing-fill":`_sizing-fill_33h3t_50`,"radio-button-group-option":`_radio-button-group-option_33h3t_43`,"display-vertical":`_display-vertical_33h3t_54`,"variant-detailed":`_variant-detailed_33h3t_60`}})),S,C,w,T,E=t((()=>{S=e(i(),1),C=e(n(),1),u(),v(),l(),a(),x(),w=r(),T=({name:e,label:t,options:n,description:r,error:i,variant:a=`default`,sizing:s=`fill`,display:c=`vertical`,disabled:l=!1,checkedOption:u,asset:f,onChange:p,onBlur:m})=>{let h=(0,C.useId)(),g=(0,C.useId)(),_=`${i?h:``}${r?` ${g}`:``}`,v=typeof t==`string`,x=n.map(e=>e.value);return d(new Set(x).size===x.length,`RadioButtonGroup options must have unique values.`),(0,w.jsxs)(`fieldset`,{"aria-describedby":_,className:(0,S.default)(b[`radio-button-group`],{[b[`label-as-text`]]:v}),children:[(0,w.jsx)(`legend`,{className:b[`radio-button-group-legend`],children:t}),(0,w.jsxs)(`div`,{className:b[`radio-button-group-header`],children:[r&&(0,w.jsx)(`span`,{id:g,className:b[`radio-button-group-description`],"aria-live":`polite`,children:r}),(0,w.jsx)(`div`,{role:`alert`,id:h,children:i&&(0,w.jsxs)(`span`,{className:b[`radio-button-group-error`],children:[(0,w.jsx)(o,{className:b[`radio-button-group-error-icon`],src:``+new URL(`full-error-BxG7-hWY.svg`,import.meta.url).href,alt:`Erreur`}),i]})})]}),(0,w.jsx)(`div`,{className:(0,S.default)(b[`radio-button-group-options`],b[`display-${c}`],b[`sizing-${s}`],b[`variant-${a}`]),children:n.map(t=>(0,w.jsx)(`div`,{className:b[`radio-button-group-option`],children:(0,w.jsx)(y,{name:e,variant:a,sizing:s,disabled:l,hasError:!!i,onChange:p,onBlur:m,asset:f,...t,...p&&{checked:u===t.value}})},t.value))})]})};try{T.displayName=`RadioButtonGroup`,T.__docgenInfo={description:``,displayName:`RadioButtonGroup`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,methods:[],props:{name:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Name of the radio button group, binding all radio buttons together`,name:`name`,required:!0,tags:{},type:{name:`string`}},label:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Label for the radio button group`,name:`label`,required:!0,tags:{},type:{name:`ReactNode`}},options:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`List of options as radio buttons`,name:`options`,required:!0,tags:{},type:{name:`Omit<RadioButtonProps, "name">[]`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:``,name:`description`,required:!1,tags:{},type:{name:`string`}},error:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Error message for the radio button group`,name:`error`,required:!1,tags:{},type:{name:`string`}},variant:{defaultValue:{value:`default`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Variant of the radio buttons (applied to all), defaults to 'default'`,name:`variant`,required:!1,tags:{},type:{name:`enum`,raw:`"default" | "detailed"`,value:[{value:`"default"`},{value:`"detailed"`}]}},sizing:{defaultValue:{value:`fill`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Sizing of the radio buttons (applied to all), defaults to 'fill'`,name:`sizing`,required:!1,tags:{},type:{name:`enum`,raw:`RadioButtonSizing`,value:[{value:`"fill"`},{value:`"hug"`}]}},asset:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Asset of the radio buttons (applied to all), displayed when variant is 'detailed'`,name:`asset`,required:!1,tags:{},type:{name:`AssetProps`}},display:{defaultValue:{value:`vertical`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Display style of the radio button group, defaults to 'vertical'`,name:`display`,required:!1,tags:{},type:{name:`enum`,raw:`"horizontal" | "vertical"`,value:[{value:`"horizontal"`},{value:`"vertical"`}]}},checkedOption:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Selected option, required if the group is non-controlled`,name:`checkedOption`,required:!1,tags:{},type:{name:`string`}},disabled:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`If the radio button group is disabled, making all options unselectable`,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Event handler for change`,name:`onChange`,required:!1,tags:{},type:{name:`((event: ChangeEvent<HTMLInputElement, Element>) => void)`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Event handler for blur`,name:`onBlur`,required:!1,tags:{},type:{name:`((event: FocusEvent<HTMLInputElement, Element>) => void)`}}},tags:{}}}catch{}})),D,O,k,A,j,M,N,P,F,I,L,R,z,B,V,H,U,W,G,K;t((()=>{D=e(n(),1),v(),c(),p(),m(),E(),_(),O=r(),k={title:`@/design-system/RadioButtonGroup`,component:T},A=[{label:`Option 1`,name:`group1`,description:`Description 1`,value:`1`},{label:`Option 2`,name:`group1`,description:`Description 2 that is a little longer...`,value:`2`},{label:`Option 3`,name:`group1`,description:`Description 3`,value:`3`}],j={label:`Option 4`,name:`group1`,description:`Description 4`,value:`4`,collapsed:(0,O.jsxs)(`div`,{style:{display:`flex`,flexDirection:`row`,gap:16},children:[(0,O.jsx)(y,{name:`subchoice`,label:`Sous-label 1`,value:`1`}),(0,O.jsx)(y,{name:`subchoice`,label:`Sous-label 2`,value:`2`})]})},M={args:{name:`radio-button-group`,label:`Radio Button Group`,options:A}},N={args:{name:`radio-button-group`,label:`Detailed Radio Button Group`,variant:`detailed`,options:A}},P={args:{name:`radio-button-group`,label:`Detailed Radio Button Group`,variant:`detailed`,sizing:`hug`,options:A}},F={args:{name:`radio-button-group`,label:`Horizontal Radio Button Group`,variant:`detailed`,display:`horizontal`,sizing:`fill`,options:A}},I={args:{name:`radio-button-group`,label:`Hugged Horizontal Radio Button Group`,variant:`detailed`,display:`horizontal`,sizing:`hug`,options:A}},L={args:{name:`radio-button-group`,label:`Disabled Radio Button Group`,disabled:!0,variant:`detailed`,options:A}},R={args:{name:`radio-button-group`,label:`Radio Button Group with Description`,description:`This is a description for the radio button group.`,options:A}},z={args:{name:`radio-button-group`,label:(0,O.jsx)(`h2`,{style:{fontFamily:g.typography.title2.fontFamily,lineHeight:g.typography.title2.lineHeight,fontSize:g.typography.title2.fontSize},children:`Radio Button Group with Heading Tag as Title`}),options:A,description:`This is a description for the radio button group.`}},B={args:{name:`radio-button-group`,label:`Radio Button Group with Error`,error:`This is an error message.`,options:A}},V={args:{name:`radio-button-group`,label:`Radio Button Group with Common Tag`,variant:`detailed`,asset:{variant:`tag`,tag:{label:`Tag`,variant:s.SUCCESS}},options:A}},H={args:{name:`radio-button-group`,label:`Radio Button Group with Common Text`,variant:`detailed`,asset:{variant:`text`,text:`19€`},options:A}},U={args:{name:`radio-button-group`,label:`Radio Button Group with Common Icon`,variant:`detailed`,asset:{variant:`icon`,src:f},options:A}},W={args:{name:`radio-button-group`,label:`Radio Button Group with Common Image`,variant:`detailed`,asset:{variant:`image`,src:h,size:`s`},options:A}},G={render:()=>{let[e,t]=(0,D.useState)(j.value);return(0,O.jsx)(T,{name:`radio-button-group`,label:`Radio Button Group with Collapsed Option`,variant:`detailed`,checkedOption:e,onChange:e=>t(e.target.value),options:[...A,j]})}},M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group',
    options
  }
}`,...M.parameters?.docs?.source}}},N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    options
  }
}`,...N.parameters?.docs?.source}}},P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    sizing: 'hug',
    options
  }
}`,...P.parameters?.docs?.source}}},F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'fill',
    options
  }
}`,...F.parameters?.docs?.source}}},I.parameters={...I.parameters,docs:{...I.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Hugged Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'hug',
    options
  }
}`,...I.parameters?.docs?.source}}},L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Disabled Radio Button Group',
    disabled: true,
    variant: 'detailed',
    options
  }
}`,...L.parameters?.docs?.source}}},R.parameters={...R.parameters,docs:{...R.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Description',
    description: 'This is a description for the radio button group.',
    options
  }
}`,...R.parameters?.docs?.source}}},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
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
}`,...z.parameters?.docs?.source}}},B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Error',
    error: 'This is an error message.',
    options
  }
}`,...B.parameters?.docs?.source}}},V.parameters={...V.parameters,docs:{...V.parameters?.docs,source:{originalSource:`{
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
}`,...V.parameters?.docs?.source}}},H.parameters={...H.parameters,docs:{...H.parameters?.docs,source:{originalSource:`{
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
}`,...H.parameters?.docs?.source}}},U.parameters={...U.parameters,docs:{...U.parameters?.docs,source:{originalSource:`{
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
}`,...U.parameters?.docs?.source}}},W.parameters={...W.parameters,docs:{...W.parameters?.docs,source:{originalSource:`{
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
}`,...W.parameters?.docs?.source}}},G.parameters={...G.parameters,docs:{...G.parameters?.docs,source:{originalSource:`{
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [checkedOption, setCheckedOption] = useState<string>(collapsedOption.value);
    return <RadioButtonGroup name="radio-button-group" label="Radio Button Group with Collapsed Option" variant="detailed" checkedOption={checkedOption} onChange={e => setCheckedOption(e.target.value)} options={[...options, collapsedOption]} />;
  }
}`,...G.parameters?.docs?.source}}},K=[`Default`,`Detailed`,`DetailedHugged`,`FilledHorizontalDisplay`,`HuggedHorizontalDisplay`,`Disabled`,`WithDescription`,`WithHeadingTagAsTitle`,`WithError`,`WithCommonTag`,`WithCommonText`,`WithCommonIcon`,`WithCommonImage`,`WithCollapsed`]}))();export{M as Default,N as Detailed,P as DetailedHugged,L as Disabled,F as FilledHorizontalDisplay,I as HuggedHorizontalDisplay,G as WithCollapsed,U as WithCommonIcon,W as WithCommonImage,V as WithCommonTag,H as WithCommonText,R as WithDescription,B as WithError,z as WithHeadingTagAsTitle,K as __namedExportsOrder,k as default};