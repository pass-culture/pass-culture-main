import{a as e,n as t}from"./rolldown-runtime-DkW27tQK.js";import{d as n}from"./iframe-2dgRlPYV.js";import{t as r}from"./jsx-runtime-DeHZSEgm.js";import{t as i}from"./classnames-D09xBJOL.js";import{n as a,t as o}from"./SvgIcon-DRPrlrFF.js";import{n as s,r as c}from"./FormLayoutSideComponentContext-D4sgWi2P.js";import{n as l}from"./full-error-23kXpe9X.js";import{n as u,t as d}from"./dog-BpyAKmCU.js";import{n as f,t as p}from"./Checkbox-B21SxO4b.js";import{n as m,t as h}from"./light.web-3-jOaeS_.js";var g;function _(){return(_=t((()=>{g={"checkbox-group-description":`_checkbox-group-description_b0ou4_1`,"checkbox-group":`_checkbox-group_b0ou4_1`,"label-as-text":`_label-as-text_b0ou4_8`,"checkbox-group-error":`_checkbox-group-error_b0ou4_13`,"checkbox-group-error-icon":`_checkbox-group-error-icon_b0ou4_20`,"checkbox-group-options":`_checkbox-group-options_b0ou4_25`,"display-vertical":`_display-vertical_b0ou4_32`,"display-horizontal":`_display-horizontal_b0ou4_35`,"variant-default":`_variant-default_b0ou4_38`,"variant-detailed":`_variant-detailed_b0ou4_44`}})))()}var v,y,b,x;function S(){return(S=t((()=>{v=e(i(),1),l(),y=n(),a(),s(),f(),_(),b=r(),x=({label:e,description:t,error:n,options:r,display:i=`vertical`,variant:a=`default`,disabled:s=!1,describedBy:l})=>{let u=c(),d=(0,y.useId)(),f=(0,y.useId)(),m=[n?d:``,t?f:``,l??``,u??``].filter(Boolean).join(` `),h=typeof e==`string`;return(0,b.jsxs)(`fieldset`,{"aria-describedby":m||void 0,className:(0,v.default)(g[`checkbox-group`],g[`display-${i}`],g[`variant-${a}`],{[g[`label-as-text`]]:h}),children:[(0,b.jsx)(`legend`,{className:g[`checkbox-group-legend`],children:e}),t&&(0,b.jsx)(`p`,{id:f,className:g[`checkbox-group-description`],children:t}),(0,b.jsx)(`div`,{role:`alert`,children:n&&(0,b.jsxs)(`div`,{id:d,children:[(0,b.jsx)(o,{src:``+new URL(`full-error-BxG7-hWY.svg`,import.meta.url).href,alt:``,width:`16`,className:g[`checkbox-group-error-icon`]}),(0,b.jsx)(`span`,{className:g[`checkbox-group-error`],children:n})]})}),(0,b.jsx)(`div`,{className:g[`checkbox-group-options`],children:r.map(e=>(0,b.jsx)(`div`,{className:g[`checkbox-group-item`],children:a==="default"?(0,b.jsx)(p,{...e,description:void 0,asset:void 0,collapsed:void 0,hasError:!!n,disabled:s||e.disabled,variant:`default`}):(0,b.jsx)(p,{...e,hasError:!!n,disabled:s||e.disabled,variant:`detailed`})},e.label))})]})};try{x.displayName=`CheckboxGroup`,x.__docgenInfo={description:``,displayName:`CheckboxGroup`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,methods:[],props:{label:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`Label for the checkbox group`,name:`label`,required:!0,tags:{},type:{name:`ReactNode`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:``,name:`description`,required:!1,tags:{},type:{name:`string`}},error:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`Error message for the checkbox group`,name:`error`,required:!1,tags:{},type:{name:`string`}},options:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`List of options as checkboxes`,name:`options`,required:!0,tags:{},type:{name:`CheckboxGroupOption[]`}},display:{defaultValue:{value:`vertical`},declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`Display style of the checkbox group, defaults to 'vertical'`,name:`display`,required:!1,tags:{},type:{name:`enum`,raw:`"horizontal" | "vertical"`,value:[{value:`"horizontal"`},{value:`"vertical"`}]}},variant:{defaultValue:{value:`default`},declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`Variant of the checkboxes (applied to all), defaults to 'default'`,name:`variant`,required:!1,tags:{},type:{name:`enum`,raw:`"default" | "detailed"`,value:[{value:`"default"`},{value:`"detailed"`}]}},disabled:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`If the checkbox group is disabled, making all options unselectable`,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},describedBy:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:``,name:`describedBy`,required:!1,tags:{},type:{name:`string`}}},tags:{}}}catch{}})))()}var C,w,T,E,D,O,k,A,j,M,N,P,F,I,L,R,z,B;function V(){return(V=t((()=>{u(),S(),h(),C=r(),w=[{label:`Option 1`,checked:!1},{label:`Option 2`,checked:!1},{label:`Option 3`,checked:!1}],T=[{label:`Detailed 1`,description:`Detailed description 1`,asset:{variant:`image`,src:d},checked:!1},{label:`Detailed 2`,checked:!1,description:`Detailed description 2`,asset:{variant:`image`,src:d}},{label:`Detailed 3`,checked:!1,description:`Detailed description 3`,asset:{variant:`image`,src:d}}],E={title:`Design System/CheckboxGroup`,component:x,tags:[`autodocs`]},D={args:{label:`Choose your options`,options:w,variant:`default`,display:`vertical`}},O={args:{label:`Choose your options`,options:w,variant:`default`,display:`horizontal`}},k={args:{label:`Choose your options`,description:`You can select several options.`,options:w,variant:`default`,display:`vertical`}},A={args:{label:`Choose your options`,error:`You must select at least one option.`,options:w,variant:`default`,display:`vertical`}},j={args:{label:`Choose your options`,options:w,variant:`default`,display:`vertical`,disabled:!0}},M={args:{label:`Choose your options`,options:w,variant:`default`,display:`vertical`}},N={args:{label:`Choose your detailed options`,options:T,variant:`detailed`,display:`vertical`}},P={args:{label:`Choose your detailed options`,options:T,variant:`detailed`,display:`horizontal`}},F={args:{label:`Choose your detailed options`,description:`You can select several options.`,options:T,variant:`detailed`,display:`vertical`}},I={args:{label:(0,C.jsx)(`h2`,{style:{fontFamily:m.typography.title2.fontFamily,lineHeight:m.typography.title2.lineHeight,fontSize:m.typography.title2.fontSize},children:`Radio Button Group with Heading Tag as Title`}),options:T,variant:`detailed`,description:`Description with heading`}},L={args:{label:`Choose your detailed options`,error:`You must select at least one option.`,options:T,variant:`detailed`,display:`vertical`}},R={args:{label:`Choose your detailed options`,options:T,variant:`detailed`,display:`vertical`,disabled:!0}},z={args:{label:`Choose your detailed options`,options:T,variant:`detailed`,display:`vertical`}},D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...D.parameters?.docs?.source}}},O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'horizontal'
  }
}`,...O.parameters?.docs?.source}}},k.parameters={...k.parameters,docs:{...k.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    description: 'You can select several options.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...k.parameters?.docs?.source}}},A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    error: 'You must select at least one option.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...A.parameters?.docs?.source}}},j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    disabled: true
  }
}`,...j.parameters?.docs?.source}}},M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...M.parameters?.docs?.source}}},N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...N.parameters?.docs?.source}}},P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'horizontal'
  }
}`,...P.parameters?.docs?.source}}},F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    description: 'You can select several options.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...F.parameters?.docs?.source}}},I.parameters={...I.parameters,docs:{...I.parameters?.docs,source:{originalSource:`{
  args: {
    label: <h2 style={{
      fontFamily: theme.typography.title2.fontFamily,
      lineHeight: theme.typography.title2.lineHeight,
      fontSize: theme.typography.title2.fontSize
    }}>Radio Button Group with Heading Tag as Title</h2>,
    options: detailedOptions,
    variant: 'detailed',
    description: 'Description with heading'
  }
}`,...I.parameters?.docs?.source}}},L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    error: 'You must select at least one option.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...L.parameters?.docs?.source}}},R.parameters={...R.parameters,docs:{...R.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
    disabled: true
  }
}`,...R.parameters?.docs?.source}}},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...z.parameters?.docs?.source}}},B=[`DefaultVertical`,`DefaultHorizontal`,`DefaultWithDescription`,`DefaultWithError`,`DefaultDisabled`,`DefaultWithDefaultValue`,`DetailedVertical`,`DetailedHorizontal`,`DetailedWithDescription`,`DetailedWithHeadingTag`,`DetailedWithError`,`DetailedDisabled`,`DetailedWithDefaultValue`]})))()}V();export{j as DefaultDisabled,O as DefaultHorizontal,D as DefaultVertical,M as DefaultWithDefaultValue,k as DefaultWithDescription,A as DefaultWithError,R as DetailedDisabled,P as DetailedHorizontal,N as DetailedVertical,z as DetailedWithDefaultValue,F as DetailedWithDescription,L as DetailedWithError,I as DetailedWithHeadingTag,B as __namedExportsOrder,E as default};