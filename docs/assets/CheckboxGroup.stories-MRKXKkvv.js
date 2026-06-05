import{i as e,s as t}from"./preload-helper-xPQekRTU.js";import{C as n}from"./iframe-ChvDpgef.js";import{t as r}from"./jsx-runtime-CaZkqeYb.js";import{t as i}from"./classnames-Dm_LJ4P4.js";import{n as a,t as o}from"./SvgIcon-DVxB_oBw.js";import{n as s}from"./full-error-CpwG8hPh.js";import{n as c,t as l}from"./dog-DmcOYdTr.js";import{n as u,t as d}from"./Checkbox-DrQixOz2.js";import{n as f,t as p}from"./light.web-CQqX2vFd.js";var m,h=e((()=>{m={"checkbox-group-description":`_checkbox-group-description_b0ou4_1`,"checkbox-group":`_checkbox-group_b0ou4_1`,"label-as-text":`_label-as-text_b0ou4_8`,"checkbox-group-error":`_checkbox-group-error_b0ou4_13`,"checkbox-group-error-icon":`_checkbox-group-error-icon_b0ou4_20`,"checkbox-group-options":`_checkbox-group-options_b0ou4_25`,"display-vertical":`_display-vertical_b0ou4_32`,"display-horizontal":`_display-horizontal_b0ou4_35`,"variant-default":`_variant-default_b0ou4_38`,"variant-detailed":`_variant-detailed_b0ou4_44`}})),g,_,v,y,b=e((()=>{g=t(i(),1),s(),_=t(n(),1),a(),u(),h(),v=r(),y=({label:e,description:t,error:n,options:r,display:i=`vertical`,variant:a=`default`,disabled:s=!1})=>{let c=(0,_.useId)(),l=(0,_.useId)(),u=`${n?c:``} ${t?l:``}`,f=typeof e==`string`;return(0,v.jsxs)(`fieldset`,{"aria-describedby":u,className:(0,g.default)(m[`checkbox-group`],m[`display-${i}`],m[`variant-${a}`],{[m[`label-as-text`]]:f}),children:[(0,v.jsx)(`legend`,{className:m[`checkbox-group-legend`],children:e}),t&&(0,v.jsx)(`p`,{id:l,className:m[`checkbox-group-description`],children:t}),(0,v.jsx)(`div`,{role:`alert`,children:n&&(0,v.jsxs)(`div`,{id:c,children:[(0,v.jsx)(o,{src:``+new URL(`full-error-BxG7-hWY.svg`,import.meta.url).href,alt:``,width:`16`,className:m[`checkbox-group-error-icon`]}),(0,v.jsx)(`span`,{className:m[`checkbox-group-error`],children:n})]})}),(0,v.jsx)(`div`,{className:m[`checkbox-group-options`],children:r.map(e=>(0,v.jsx)(`div`,{className:m[`checkbox-group-item`],children:a===`default`?(0,v.jsx)(d,{...e,description:void 0,asset:void 0,collapsed:void 0,hasError:!!n,disabled:s||e.disabled,variant:`default`}):(0,v.jsx)(d,{...e,hasError:!!n,disabled:s||e.disabled,variant:`detailed`})},e.label))})]})};try{y.displayName=`CheckboxGroup`,y.__docgenInfo={description:``,displayName:`CheckboxGroup`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,methods:[],props:{label:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`Label for the checkbox group`,name:`label`,required:!0,tags:{},type:{name:`ReactNode`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:``,name:`description`,required:!1,tags:{},type:{name:`string`}},error:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`Error message for the checkbox group`,name:`error`,required:!1,tags:{},type:{name:`string`}},options:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`List of options as checkboxes`,name:`options`,required:!0,tags:{},type:{name:`CheckboxGroupOption[]`}},display:{defaultValue:{value:`vertical`},declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`Display style of the checkbox group, defaults to 'vertical'`,name:`display`,required:!1,tags:{},type:{name:`enum`,raw:`"horizontal" | "vertical"`,value:[{value:`"horizontal"`},{value:`"vertical"`}]}},variant:{defaultValue:{value:`default`},declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`Variant of the checkboxes (applied to all), defaults to 'default'`,name:`variant`,required:!1,tags:{},type:{name:`enum`,raw:`"default" | "detailed"`,value:[{value:`"default"`},{value:`"detailed"`}]}},disabled:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/design-system/CheckboxGroup/CheckboxGroup.tsx`,name:`TypeLiteral`}],description:`If the checkbox group is disabled, making all options unselectable`,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}}},tags:{}}}catch{}})),x,S,C,w,T,E,D,O,k,A,j,M,N,P,F,I,L,R;e((()=>{c(),b(),p(),x=r(),S=[{label:`Option 1`,checked:!1},{label:`Option 2`,checked:!1},{label:`Option 3`,checked:!1}],C=[{label:`Detailed 1`,description:`Detailed description 1`,asset:{variant:`image`,src:l},checked:!1},{label:`Detailed 2`,checked:!1,description:`Detailed description 2`,asset:{variant:`image`,src:l}},{label:`Detailed 3`,checked:!1,description:`Detailed description 3`,asset:{variant:`image`,src:l}}],w={title:`Design System/CheckboxGroup`,component:y,tags:[`autodocs`]},T={args:{label:`Choose your options`,options:S,variant:`default`,display:`vertical`}},E={args:{label:`Choose your options`,options:S,variant:`default`,display:`horizontal`}},D={args:{label:`Choose your options`,description:`You can select several options.`,options:S,variant:`default`,display:`vertical`}},O={args:{label:`Choose your options`,error:`You must select at least one option.`,options:S,variant:`default`,display:`vertical`}},k={args:{label:`Choose your options`,options:S,variant:`default`,display:`vertical`,disabled:!0}},A={args:{label:`Choose your options`,options:S,variant:`default`,display:`vertical`}},j={args:{label:`Choose your detailed options`,options:C,variant:`detailed`,display:`vertical`}},M={args:{label:`Choose your detailed options`,options:C,variant:`detailed`,display:`horizontal`}},N={args:{label:`Choose your detailed options`,description:`You can select several options.`,options:C,variant:`detailed`,display:`vertical`}},P={args:{label:(0,x.jsx)(`h2`,{style:{fontFamily:f.typography.title2.fontFamily,lineHeight:f.typography.title2.lineHeight,fontSize:f.typography.title2.fontSize},children:`Radio Button Group with Heading Tag as Title`}),options:C,variant:`detailed`,description:`Description with heading`}},F={args:{label:`Choose your detailed options`,error:`You must select at least one option.`,options:C,variant:`detailed`,display:`vertical`}},I={args:{label:`Choose your detailed options`,options:C,variant:`detailed`,display:`vertical`,disabled:!0}},L={args:{label:`Choose your detailed options`,options:C,variant:`detailed`,display:`vertical`}},T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...T.parameters?.docs?.source}}},E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'horizontal'
  }
}`,...E.parameters?.docs?.source}}},D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    description: 'You can select several options.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...D.parameters?.docs?.source}}},O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    error: 'You must select at least one option.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...O.parameters?.docs?.source}}},k.parameters={...k.parameters,docs:{...k.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    disabled: true
  }
}`,...k.parameters?.docs?.source}}},A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...A.parameters?.docs?.source}}},j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...j.parameters?.docs?.source}}},M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'horizontal'
  }
}`,...M.parameters?.docs?.source}}},N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    description: 'You can select several options.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...N.parameters?.docs?.source}}},P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
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
}`,...P.parameters?.docs?.source}}},F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    error: 'You must select at least one option.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...F.parameters?.docs?.source}}},I.parameters={...I.parameters,docs:{...I.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
    disabled: true
  }
}`,...I.parameters?.docs?.source}}},L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...L.parameters?.docs?.source}}},R=[`DefaultVertical`,`DefaultHorizontal`,`DefaultWithDescription`,`DefaultWithError`,`DefaultDisabled`,`DefaultWithDefaultValue`,`DetailedVertical`,`DetailedHorizontal`,`DetailedWithDescription`,`DetailedWithHeadingTag`,`DetailedWithError`,`DetailedDisabled`,`DetailedWithDefaultValue`]}))();export{k as DefaultDisabled,E as DefaultHorizontal,T as DefaultVertical,A as DefaultWithDefaultValue,D as DefaultWithDescription,O as DefaultWithError,I as DetailedDisabled,M as DetailedHorizontal,j as DetailedVertical,L as DetailedWithDefaultValue,N as DetailedWithDescription,F as DetailedWithError,P as DetailedWithHeadingTag,R as __namedExportsOrder,w as default};