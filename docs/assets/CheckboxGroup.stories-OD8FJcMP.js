import{a as e,n as t}from"./rolldown-runtime-DkW27tQK.js";import{f as n}from"./iframe-9m7LIQG_.js";import{t as r}from"./jsx-runtime-DeHZSEgm.js";import{t as i}from"./classnames-D09xBJOL.js";import{n as a,t as o}from"./SvgIcon-DRPrlrFF.js";import{n as s,r as c}from"./FormLayoutSideComponentContext-C_YIrsGe.js";import{n as l,t as u}from"./full-error-BAxfKzLK.js";import{n as d,t as f}from"./dog-CXGBgOem.js";import{n as p,t as m}from"./Checkbox-_hRNUR5Q.js";import{n as h,t as g}from"./light.web-3-jOaeS_.js";var _;function v(){return(v=t((()=>{_={"checkbox-group-description":`_checkbox-group-description_b0ou4_1`,"checkbox-group":`_checkbox-group_b0ou4_1`,"label-as-text":`_label-as-text_b0ou4_8`,"checkbox-group-error":`_checkbox-group-error_b0ou4_13`,"checkbox-group-error-icon":`_checkbox-group-error-icon_b0ou4_20`,"checkbox-group-options":`_checkbox-group-options_b0ou4_25`,"display-vertical":`_display-vertical_b0ou4_32`,"display-horizontal":`_display-horizontal_b0ou4_35`,"variant-default":`_variant-default_b0ou4_38`,"variant-detailed":`_variant-detailed_b0ou4_44`}})))()}var y,b,x,S;function C(){return(C=t((()=>{y=e(i(),1),l(),b=n(),a(),s(),p(),v(),x=r(),S=({label:e,description:t,error:n,options:r,display:i=`vertical`,variant:a=`default`,disabled:s=!1,describedBy:l})=>{let d=c(),f=(0,b.useId)(),p=(0,b.useId)(),h=[n?f:``,t?p:``,l??``,d??``].filter(Boolean).join(` `),g=typeof e==`string`;return(0,x.jsxs)(`fieldset`,{"aria-describedby":h||void 0,className:(0,y.default)(_[`checkbox-group`],_[`display-${i}`],_[`variant-${a}`],{[_[`label-as-text`]]:g}),children:[(0,x.jsx)(`legend`,{className:_[`checkbox-group-legend`],children:e}),t&&(0,x.jsx)(`p`,{id:p,className:_[`checkbox-group-description`],children:t}),(0,x.jsx)(`div`,{role:`alert`,children:n&&(0,x.jsxs)(`div`,{id:f,children:[(0,x.jsx)(o,{src:u,alt:``,width:`16`,className:_[`checkbox-group-error-icon`]}),(0,x.jsx)(`span`,{className:_[`checkbox-group-error`],children:n})]})}),(0,x.jsx)(`div`,{className:_[`checkbox-group-options`],children:r.map(e=>(0,x.jsx)(`div`,{className:_[`checkbox-group-item`],children:a==="default"?(0,x.jsx)(m,{...e,description:void 0,asset:void 0,collapsed:void 0,hasError:!!n,disabled:s||e.disabled,variant:`default`}):(0,x.jsx)(m,{...e,hasError:!!n,disabled:s||e.disabled,variant:`detailed`})},e.label))})]})};try{S.displayName=`CheckboxGroup`,S.__docgenInfo={description:``,displayName:`CheckboxGroup`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,methods:[],props:{label:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`Label for the checkbox group`,name:`label`,required:!0,tags:{},type:{name:`ReactNode`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:``,name:`description`,required:!1,tags:{},type:{name:`string`}},error:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`Error message for the checkbox group`,name:`error`,required:!1,tags:{},type:{name:`string`}},options:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`List of options as checkboxes`,name:`options`,required:!0,tags:{},type:{name:`CheckboxGroupOption[]`}},display:{defaultValue:{value:`vertical`},declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`Display style of the checkbox group, defaults to 'vertical'`,name:`display`,required:!1,tags:{},type:{name:`enum`,raw:`"horizontal" | "vertical"`,value:[{value:`"horizontal"`},{value:`"vertical"`}]}},variant:{defaultValue:{value:`default`},declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`Variant of the checkboxes (applied to all), defaults to 'default'`,name:`variant`,required:!1,tags:{},type:{name:`enum`,raw:`"default" | "detailed"`,value:[{value:`"default"`},{value:`"detailed"`}]}},disabled:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`If the checkbox group is disabled, making all options unselectable`,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},describedBy:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:``,name:`describedBy`,required:!1,tags:{},type:{name:`string`}}},tags:{}}}catch{}})))()}var w,T,E,D,O,k,A,j,M,N,P,F,I,L,R,z,B,V;function H(){return(H=t((()=>{d(),C(),g(),w=r(),T=[{label:`Option 1`,checked:!1},{label:`Option 2`,checked:!1},{label:`Option 3`,checked:!1}],E=[{label:`Detailed 1`,description:`Detailed description 1`,asset:{variant:`image`,src:f},checked:!1},{label:`Detailed 2`,checked:!1,description:`Detailed description 2`,asset:{variant:`image`,src:f}},{label:`Detailed 3`,checked:!1,description:`Detailed description 3`,asset:{variant:`image`,src:f}}],D={title:`Design System/CheckboxGroup`,component:S,tags:[`autodocs`]},O={args:{label:`Choose your options`,options:T,variant:`default`,display:`vertical`}},k={args:{label:`Choose your options`,options:T,variant:`default`,display:`horizontal`}},A={args:{label:`Choose your options`,description:`You can select several options.`,options:T,variant:`default`,display:`vertical`}},j={args:{label:`Choose your options`,error:`You must select at least one option.`,options:T,variant:`default`,display:`vertical`}},M={args:{label:`Choose your options`,options:T,variant:`default`,display:`vertical`,disabled:!0}},N={args:{label:`Choose your options`,options:T,variant:`default`,display:`vertical`}},P={args:{label:`Choose your detailed options`,options:E,variant:`detailed`,display:`vertical`}},F={args:{label:`Choose your detailed options`,options:E,variant:`detailed`,display:`horizontal`}},I={args:{label:`Choose your detailed options`,description:`You can select several options.`,options:E,variant:`detailed`,display:`vertical`}},L={args:{label:(0,w.jsx)(`h2`,{style:{fontFamily:h.typography.title2.fontFamily,lineHeight:h.typography.title2.lineHeight,fontSize:h.typography.title2.fontSize},children:`Radio Button Group with Heading Tag as Title`}),options:E,variant:`detailed`,description:`Description with heading`}},R={args:{label:`Choose your detailed options`,error:`You must select at least one option.`,options:E,variant:`detailed`,display:`vertical`}},z={args:{label:`Choose your detailed options`,options:E,variant:`detailed`,display:`vertical`,disabled:!0}},B={args:{label:`Choose your detailed options`,options:E,variant:`detailed`,display:`vertical`}},V=[`DefaultVertical`,`DefaultHorizontal`,`DefaultWithDescription`,`DefaultWithError`,`DefaultDisabled`,`DefaultWithDefaultValue`,`DetailedVertical`,`DetailedHorizontal`,`DetailedWithDescription`,`DetailedWithHeadingTag`,`DetailedWithError`,`DetailedDisabled`,`DetailedWithDefaultValue`],O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...O.parameters?.docs?.source}}},k.parameters={...k.parameters,docs:{...k.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'horizontal'
  }
}`,...k.parameters?.docs?.source}}},A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    description: 'You can select several options.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...A.parameters?.docs?.source}}},j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    error: 'You must select at least one option.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...j.parameters?.docs?.source}}},M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    disabled: true
  }
}`,...M.parameters?.docs?.source}}},N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...N.parameters?.docs?.source}}},P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...P.parameters?.docs?.source}}},F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'horizontal'
  }
}`,...F.parameters?.docs?.source}}},I.parameters={...I.parameters,docs:{...I.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    description: 'You can select several options.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...I.parameters?.docs?.source}}},L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
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
}`,...L.parameters?.docs?.source}}},R.parameters={...R.parameters,docs:{...R.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    error: 'You must select at least one option.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...R.parameters?.docs?.source}}},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
    disabled: true
  }
}`,...z.parameters?.docs?.source}}},B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...B.parameters?.docs?.source}}}})))()}H();export{M as DefaultDisabled,k as DefaultHorizontal,O as DefaultVertical,N as DefaultWithDefaultValue,A as DefaultWithDescription,j as DefaultWithError,z as DetailedDisabled,F as DetailedHorizontal,P as DetailedVertical,B as DetailedWithDefaultValue,I as DetailedWithDescription,R as DetailedWithError,L as DetailedWithHeadingTag,V as __namedExportsOrder,D as default};