import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-lL4_MI5A.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./classnames-MYlGWOUq.js";import{t as i}from"./SvgIcon-DK-x56iF.js";import"./full-error-DfJ4Bv1q.js";import{t as a}from"./dog--Ms-T-99.js";import{t as o}from"./Checkbox-TVzYKVvH.js";import{t as s}from"./light.web-B5OSk-45.js";var c=e(r(),1),l=e(t(),1),u={"checkbox-group-description":`_checkbox-group-description_b0ou4_1`,"checkbox-group":`_checkbox-group_b0ou4_1`,"label-as-text":`_label-as-text_b0ou4_8`,"checkbox-group-error":`_checkbox-group-error_b0ou4_13`,"checkbox-group-error-icon":`_checkbox-group-error-icon_b0ou4_20`,"checkbox-group-options":`_checkbox-group-options_b0ou4_25`,"display-vertical":`_display-vertical_b0ou4_32`,"display-horizontal":`_display-horizontal_b0ou4_35`,"variant-default":`_variant-default_b0ou4_38`,"variant-detailed":`_variant-detailed_b0ou4_44`},d=n(),f=({label:e,description:t,error:n,options:r,display:a=`vertical`,variant:s=`default`,disabled:f=!1})=>{let p=(0,l.useId)(),m=(0,l.useId)(),h=`${n?p:``} ${t?m:``}`,g=typeof e==`string`;return(0,d.jsxs)(`fieldset`,{"aria-describedby":h,className:(0,c.default)(u[`checkbox-group`],u[`display-${a}`],u[`variant-${s}`],{[u[`label-as-text`]]:g}),children:[(0,d.jsx)(`legend`,{className:u[`checkbox-group-legend`],children:e}),t&&(0,d.jsx)(`p`,{id:m,className:u[`checkbox-group-description`],children:t}),(0,d.jsx)(`div`,{role:`alert`,children:n&&(0,d.jsxs)(`div`,{id:p,children:[(0,d.jsx)(i,{src:``+new URL(`full-error-BxG7-hWY.svg`,import.meta.url).href,alt:``,width:`16`,className:u[`checkbox-group-error-icon`]}),(0,d.jsx)(`span`,{className:u[`checkbox-group-error`],children:n})]})}),(0,d.jsx)(`div`,{className:u[`checkbox-group-options`],children:r.map(e=>(0,d.jsx)(`div`,{className:u[`checkbox-group-item`],children:s===`default`?(0,d.jsx)(o,{...e,description:void 0,asset:void 0,collapsed:void 0,hasError:!!n,disabled:f||e.disabled,variant:`default`}):(0,d.jsx)(o,{...e,hasError:!!n,disabled:f||e.disabled,variant:`detailed`})},e.label))})]})};try{f.displayName=`CheckboxGroup`,f.__docgenInfo={description:``,displayName:`CheckboxGroup`,props:{label:{defaultValue:null,description:`Label for the checkbox group`,name:`label`,required:!0,type:{name:`ReactNode`}},description:{defaultValue:null,description:``,name:`description`,required:!1,type:{name:`string`}},error:{defaultValue:null,description:`Error message for the checkbox group`,name:`error`,required:!1,type:{name:`string`}},options:{defaultValue:null,description:`List of options as checkboxes`,name:`options`,required:!0,type:{name:`CheckboxGroupOption[]`}},display:{defaultValue:{value:`vertical`},description:`Display style of the checkbox group, defaults to 'vertical'`,name:`display`,required:!1,type:{name:`enum`,value:[{value:`"horizontal"`},{value:`"vertical"`}]}},variant:{defaultValue:{value:`default`},description:`Variant of the checkboxes (applied to all), defaults to 'default'`,name:`variant`,required:!1,type:{name:`enum`,value:[{value:`"default"`},{value:`"detailed"`}]}},disabled:{defaultValue:{value:`false`},description:`If the checkbox group is disabled, making all options unselectable`,name:`disabled`,required:!1,type:{name:`boolean`}}}}}catch{}var p=[{label:`Option 1`,checked:!1},{label:`Option 2`,checked:!1},{label:`Option 3`,checked:!1}],m=[{label:`Detailed 1`,description:`Detailed description 1`,asset:{variant:`image`,src:a},checked:!1},{label:`Detailed 2`,checked:!1,description:`Detailed description 2`,asset:{variant:`image`,src:a}},{label:`Detailed 3`,checked:!1,description:`Detailed description 3`,asset:{variant:`image`,src:a}}],h={title:`Design System/CheckboxGroup`,component:f,tags:[`autodocs`]},g={args:{label:`Choose your options`,options:p,variant:`default`,display:`vertical`}},_={args:{label:`Choose your options`,options:p,variant:`default`,display:`horizontal`}},v={args:{label:`Choose your options`,description:`You can select several options.`,options:p,variant:`default`,display:`vertical`}},y={args:{label:`Choose your options`,error:`You must select at least one option.`,options:p,variant:`default`,display:`vertical`}},b={args:{label:`Choose your options`,options:p,variant:`default`,display:`vertical`,disabled:!0}},x={args:{label:`Choose your options`,options:p,variant:`default`,display:`vertical`}},S={args:{label:`Choose your detailed options`,options:m,variant:`detailed`,display:`vertical`}},C={args:{label:`Choose your detailed options`,options:m,variant:`detailed`,display:`horizontal`}},w={args:{label:`Choose your detailed options`,description:`You can select several options.`,options:m,variant:`detailed`,display:`vertical`}},T={args:{label:(0,d.jsx)(`h2`,{style:{fontFamily:s.typography.title2.fontFamily,lineHeight:s.typography.title2.lineHeight,fontSize:s.typography.title2.fontSize},children:`Radio Button Group with Heading Tag as Title`}),options:m,variant:`detailed`,description:`Description with heading`}},E={args:{label:`Choose your detailed options`,error:`You must select at least one option.`,options:m,variant:`detailed`,display:`vertical`}},D={args:{label:`Choose your detailed options`,options:m,variant:`detailed`,display:`vertical`,disabled:!0}},O={args:{label:`Choose your detailed options`,options:m,variant:`detailed`,display:`vertical`}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...g.parameters?.docs?.source}}},_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'horizontal'
  }
}`,..._.parameters?.docs?.source}}},v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    description: 'You can select several options.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...v.parameters?.docs?.source}}},y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    error: 'You must select at least one option.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...y.parameters?.docs?.source}}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    disabled: true
  }
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...x.parameters?.docs?.source}}},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...S.parameters?.docs?.source}}},C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'horizontal'
  }
}`,...C.parameters?.docs?.source}}},w.parameters={...w.parameters,docs:{...w.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    description: 'You can select several options.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...w.parameters?.docs?.source}}},T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
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
}`,...T.parameters?.docs?.source}}},E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    error: 'You must select at least one option.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...E.parameters?.docs?.source}}},D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
    disabled: true
  }
}`,...D.parameters?.docs?.source}}},O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...O.parameters?.docs?.source}}};var k=[`DefaultVertical`,`DefaultHorizontal`,`DefaultWithDescription`,`DefaultWithError`,`DefaultDisabled`,`DefaultWithDefaultValue`,`DetailedVertical`,`DetailedHorizontal`,`DetailedWithDescription`,`DetailedWithHeadingTag`,`DetailedWithError`,`DetailedDisabled`,`DetailedWithDefaultValue`];export{b as DefaultDisabled,_ as DefaultHorizontal,g as DefaultVertical,x as DefaultWithDefaultValue,v as DefaultWithDescription,y as DefaultWithError,D as DetailedDisabled,C as DetailedHorizontal,S as DetailedVertical,O as DetailedWithDefaultValue,w as DetailedWithDescription,E as DetailedWithError,T as DetailedWithHeadingTag,k as __namedExportsOrder,h as default};