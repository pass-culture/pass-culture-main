import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-CJKEVxxk.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./classnames-MYlGWOUq.js";import{t as i}from"./SvgIcon-DK-x56iF.js";import{n as a}from"./Tag-BV-j8xUv.js";import"./full-error-DfJ4Bv1q.js";import{t as o}from"./assertOrFrontendError-BgKHGT-s.js";import{t as s}from"./stroke-date-B1Pf4eWF.js";import{t as c}from"./dog--Ms-T-99.js";import{t as l}from"./light.web-B5OSk-45.js";import{t as u}from"./RadioButton-eHydnkYt.js";var d=e(t(),1),f=e(r(),1),p={"radio-button-group":`_radio-button-group_33h3t_1`,"radio-button-group-legend":`_radio-button-group-legend_33h3t_6`,"radio-button-group-description":`_radio-button-group-description_33h3t_12`,"label-as-text":`_label-as-text_33h3t_20`,"radio-button-group-error":`_radio-button-group-error_33h3t_26`,"radio-button-group-error-icon":`_radio-button-group-error-icon_33h3t_36`,"radio-button-group-options":`_radio-button-group-options_33h3t_43`,"display-horizontal":`_display-horizontal_33h3t_50`,"sizing-fill":`_sizing-fill_33h3t_50`,"radio-button-group-option":`_radio-button-group-option_33h3t_43`,"display-vertical":`_display-vertical_33h3t_54`,"variant-detailed":`_variant-detailed_33h3t_60`},m=n(),h=({name:e,label:t,options:n,description:r,error:a,variant:s=`default`,sizing:c=`fill`,display:l=`vertical`,disabled:h=!1,checkedOption:g,asset:_,onChange:v,onBlur:y})=>{let b=(0,d.useId)(),x=(0,d.useId)(),S=`${a?b:``}${r?` ${x}`:``}`,C=typeof t==`string`,w=n.map(e=>e.value);return o(new Set(w).size===w.length,`RadioButtonGroup options must have unique values.`),(0,m.jsxs)(`fieldset`,{"aria-describedby":S,className:(0,f.default)(p[`radio-button-group`],{[p[`label-as-text`]]:C}),children:[(0,m.jsx)(`legend`,{className:p[`radio-button-group-legend`],children:t}),(0,m.jsxs)(`div`,{className:p[`radio-button-group-header`],children:[r&&(0,m.jsx)(`span`,{id:x,className:p[`radio-button-group-description`],"aria-live":`polite`,children:r}),(0,m.jsx)(`div`,{role:`alert`,id:b,children:a&&(0,m.jsxs)(`span`,{className:p[`radio-button-group-error`],children:[(0,m.jsx)(i,{className:p[`radio-button-group-error-icon`],src:``+new URL(`full-error-BxG7-hWY.svg`,import.meta.url).href,alt:`Erreur`}),a]})})]}),(0,m.jsx)(`div`,{className:(0,f.default)(p[`radio-button-group-options`],p[`display-${l}`],p[`sizing-${c}`],p[`variant-${s}`]),children:n.map(t=>(0,m.jsx)(`div`,{className:p[`radio-button-group-option`],children:(0,m.jsx)(u,{name:e,variant:s,sizing:c,disabled:h,hasError:!!a,onChange:v,onBlur:y,asset:_,...t,...v&&{checked:g===t.value}})},t.value))})]})};try{h.displayName=`RadioButtonGroup`,h.__docgenInfo={description:``,displayName:`RadioButtonGroup`,props:{name:{defaultValue:null,description:`Name of the radio button group, binding all radio buttons together`,name:`name`,required:!0,type:{name:`string`}},label:{defaultValue:null,description:`Label for the radio button group`,name:`label`,required:!0,type:{name:`ReactNode`}},options:{defaultValue:null,description:`List of options as radio buttons`,name:`options`,required:!0,type:{name:`Omit<RadioButtonProps, "name">[]`}},description:{defaultValue:null,description:``,name:`description`,required:!1,type:{name:`string`}},error:{defaultValue:null,description:`Error message for the radio button group`,name:`error`,required:!1,type:{name:`string`}},variant:{defaultValue:{value:`default`},description:`Variant of the radio buttons (applied to all), defaults to 'default'`,name:`variant`,required:!1,type:{name:`enum`,value:[{value:`"default"`},{value:`"detailed"`}]}},sizing:{defaultValue:{value:`fill`},description:`Sizing of the radio buttons (applied to all), defaults to 'fill'`,name:`sizing`,required:!1,type:{name:`enum`,value:[{value:`"hug"`},{value:`"fill"`}]}},asset:{defaultValue:null,description:`Asset of the radio buttons (applied to all), displayed when variant is 'detailed'`,name:`asset`,required:!1,type:{name:`AssetProps`}},display:{defaultValue:{value:`vertical`},description:`Display style of the radio button group, defaults to 'vertical'`,name:`display`,required:!1,type:{name:`enum`,value:[{value:`"horizontal"`},{value:`"vertical"`}]}},checkedOption:{defaultValue:null,description:`Selected option, required if the group is non-controlled`,name:`checkedOption`,required:!1,type:{name:`string`}},disabled:{defaultValue:{value:`false`},description:`If the radio button group is disabled, making all options unselectable`,name:`disabled`,required:!1,type:{name:`boolean`}},onChange:{defaultValue:null,description:`Event handler for change`,name:`onChange`,required:!1,type:{name:`((event: ChangeEvent<HTMLInputElement, Element>) => void)`}},onBlur:{defaultValue:null,description:`Event handler for blur`,name:`onBlur`,required:!1,type:{name:`((event: FocusEvent<HTMLInputElement, Element>) => void)`}}}}}catch{}var g={title:`@/design-system/RadioButtonGroup`,component:h},_=[{label:`Option 1`,name:`group1`,description:`Description 1`,value:`1`},{label:`Option 2`,name:`group1`,description:`Description 2 that is a little longer...`,value:`2`},{label:`Option 3`,name:`group1`,description:`Description 3`,value:`3`}],v={label:`Option 4`,name:`group1`,description:`Description 4`,value:`4`,collapsed:(0,m.jsxs)(`div`,{style:{display:`flex`,flexDirection:`row`,gap:16},children:[(0,m.jsx)(u,{name:`subchoice`,label:`Sous-label 1`,value:`1`}),(0,m.jsx)(u,{name:`subchoice`,label:`Sous-label 2`,value:`2`})]})},y={args:{name:`radio-button-group`,label:`Radio Button Group`,options:_}},b={args:{name:`radio-button-group`,label:`Detailed Radio Button Group`,variant:`detailed`,options:_}},x={args:{name:`radio-button-group`,label:`Detailed Radio Button Group`,variant:`detailed`,sizing:`hug`,options:_}},S={args:{name:`radio-button-group`,label:`Horizontal Radio Button Group`,variant:`detailed`,display:`horizontal`,sizing:`fill`,options:_}},C={args:{name:`radio-button-group`,label:`Hugged Horizontal Radio Button Group`,variant:`detailed`,display:`horizontal`,sizing:`hug`,options:_}},w={args:{name:`radio-button-group`,label:`Disabled Radio Button Group`,disabled:!0,variant:`detailed`,options:_}},T={args:{name:`radio-button-group`,label:`Radio Button Group with Description`,description:`This is a description for the radio button group.`,options:_}},E={args:{name:`radio-button-group`,label:(0,m.jsx)(`h2`,{style:{fontFamily:l.typography.title2.fontFamily,lineHeight:l.typography.title2.lineHeight,fontSize:l.typography.title2.fontSize},children:`Radio Button Group with Heading Tag as Title`}),options:_,description:`This is a description for the radio button group.`}},D={args:{name:`radio-button-group`,label:`Radio Button Group with Error`,error:`This is an error message.`,options:_}},O={args:{name:`radio-button-group`,label:`Radio Button Group with Common Tag`,variant:`detailed`,asset:{variant:`tag`,tag:{label:`Tag`,variant:a.SUCCESS}},options:_}},k={args:{name:`radio-button-group`,label:`Radio Button Group with Common Text`,variant:`detailed`,asset:{variant:`text`,text:`19€`},options:_}},A={args:{name:`radio-button-group`,label:`Radio Button Group with Common Icon`,variant:`detailed`,asset:{variant:`icon`,src:s},options:_}},j={args:{name:`radio-button-group`,label:`Radio Button Group with Common Image`,variant:`detailed`,asset:{variant:`image`,src:c,size:`s`},options:_}},M={render:()=>{let[e,t]=(0,d.useState)(v.value);return(0,m.jsx)(h,{name:`radio-button-group`,label:`Radio Button Group with Collapsed Option`,variant:`detailed`,checkedOption:e,onChange:e=>t(e.target.value),options:[..._,v]})}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group',
    options
  }
}`,...y.parameters?.docs?.source}}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    options
  }
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    sizing: 'hug',
    options
  }
}`,...x.parameters?.docs?.source}}},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'fill',
    options
  }
}`,...S.parameters?.docs?.source}}},C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Hugged Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'hug',
    options
  }
}`,...C.parameters?.docs?.source}}},w.parameters={...w.parameters,docs:{...w.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Disabled Radio Button Group',
    disabled: true,
    variant: 'detailed',
    options
  }
}`,...w.parameters?.docs?.source}}},T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Description',
    description: 'This is a description for the radio button group.',
    options
  }
}`,...T.parameters?.docs?.source}}},E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
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
}`,...E.parameters?.docs?.source}}},D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Error',
    error: 'This is an error message.',
    options
  }
}`,...D.parameters?.docs?.source}}},O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
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
}`,...O.parameters?.docs?.source}}},k.parameters={...k.parameters,docs:{...k.parameters?.docs,source:{originalSource:`{
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
}`,...k.parameters?.docs?.source}}},A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
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
}`,...A.parameters?.docs?.source}}},j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
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
}`,...j.parameters?.docs?.source}}},M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [checkedOption, setCheckedOption] = useState<string>(collapsedOption.value);
    return <RadioButtonGroup name="radio-button-group" label="Radio Button Group with Collapsed Option" variant="detailed" checkedOption={checkedOption} onChange={e => setCheckedOption(e.target.value)} options={[...options, collapsedOption]} />;
  }
}`,...M.parameters?.docs?.source}}};var N=[`Default`,`Detailed`,`DetailedHugged`,`FilledHorizontalDisplay`,`HuggedHorizontalDisplay`,`Disabled`,`WithDescription`,`WithHeadingTagAsTitle`,`WithError`,`WithCommonTag`,`WithCommonText`,`WithCommonIcon`,`WithCommonImage`,`WithCollapsed`];export{y as Default,b as Detailed,x as DetailedHugged,w as Disabled,S as FilledHorizontalDisplay,C as HuggedHorizontalDisplay,M as WithCollapsed,A as WithCommonIcon,j as WithCommonImage,O as WithCommonTag,k as WithCommonText,T as WithDescription,D as WithError,E as WithHeadingTagAsTitle,N as __namedExportsOrder,g as default};