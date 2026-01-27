import{j as e}from"./jsx-runtime-C_uOM0Gm.js";import{i as D}from"./dog-C0QzEjl8.js";import{c as I}from"./index-TscbDd2H.js";import{f as Y}from"./full-error-BFAmjN4t.js";import{r as z}from"./iframe-CTnXOULQ.js";import{S as q}from"./SvgIcon-CJiY4LCz.js";import{C as j}from"./Checkbox-BYovAbr0.js";import{t as _}from"./light.web-BxcFpQrB.js";import"./preload-helper-PPVm8Dsz.js";import"./Asset-DEO5YOFe.js";import"./Tag-CZrfY-rG.js";import"./full-thumb-up-Bb4kpRpM.js";const a={"checkbox-group-description":"_checkbox-group-description_b0ou4_1","checkbox-group":"_checkbox-group_b0ou4_1","label-as-text":"_label-as-text_b0ou4_8","checkbox-group-error":"_checkbox-group-error_b0ou4_13","checkbox-group-error-icon":"_checkbox-group-error-icon_b0ou4_20","checkbox-group-options":"_checkbox-group-options_b0ou4_25","display-vertical":"_display-vertical_b0ou4_32","display-horizontal":"_display-horizontal_b0ou4_35","variant-default":"_variant-default_b0ou4_38","variant-detailed":"_variant-detailed_b0ou4_44"},k=({label:v,description:x,error:r,options:W,display:H="vertical",variant:C="default",disabled:S=!1})=>{const O=z.useId(),V=z.useId(),E=`${r?O:""} ${x?V:""}`,N=typeof v=="string";return e.jsxs("fieldset",{"aria-describedby":E,className:I(a["checkbox-group"],a[`display-${H}`],a[`variant-${C}`],{[a["label-as-text"]]:N}),children:[e.jsx("legend",{className:a["checkbox-group-legend"],children:v}),x&&e.jsx("p",{id:V,className:a["checkbox-group-description"],children:x}),e.jsx("div",{role:"alert",children:r&&e.jsxs("div",{id:O,children:[e.jsx(q,{src:Y,alt:"",width:"16",className:a["checkbox-group-error-icon"]}),e.jsx("span",{className:a["checkbox-group-error"],children:r})]})}),e.jsx("div",{className:a["checkbox-group-options"],children:W.map(s=>e.jsx("div",{className:a["checkbox-group-item"],children:C==="default"?e.jsx(j,{...s,description:void 0,asset:void 0,collapsed:void 0,hasError:!!r,disabled:S||s.disabled,variant:"default"}):e.jsx(j,{...s,hasError:!!r,disabled:S||s.disabled,variant:"detailed"})},s.label))})]})};try{k.displayName="CheckboxGroup",k.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{label:{defaultValue:null,description:"Label for the checkbox group",name:"label",required:!0,type:{name:"ReactNode"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error message for the checkbox group",name:"error",required:!1,type:{name:"string"}},options:{defaultValue:null,description:"List of options as checkboxes",name:"options",required:!0,type:{name:"CheckboxGroupOption[]"}},display:{defaultValue:{value:"vertical"},description:"Display style of the checkbox group, defaults to 'vertical'",name:"display",required:!1,type:{name:"enum",value:[{value:'"horizontal"'},{value:'"vertical"'}]}},variant:{defaultValue:{value:"default"},description:"Variant of the checkboxes (applied to all), defaults to 'default'",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},disabled:{defaultValue:{value:"false"},description:"If the checkbox group is disabled, making all options unselectable",name:"disabled",required:!1,type:{name:"boolean"}}}}}catch{}const t=[{label:"Option 1",checked:!1},{label:"Option 2",checked:!1},{label:"Option 3",checked:!1}],o=[{label:"Detailed 1",description:"Detailed description 1",asset:{variant:"image",src:D},checked:!1},{label:"Detailed 2",checked:!1,description:"Detailed description 2",asset:{variant:"image",src:D}},{label:"Detailed 3",checked:!1,description:"Detailed description 3",asset:{variant:"image",src:D}}],P={title:"Design System/CheckboxGroup",component:k,tags:["autodocs"]},i={args:{label:"Choose your options",options:t,variant:"default",display:"vertical"}},l={args:{label:"Choose your options",options:t,variant:"default",display:"horizontal"}},n={args:{label:"Choose your options",description:"You can select several options.",options:t,variant:"default",display:"vertical"}},d={args:{label:"Choose your options",error:"You must select at least one option.",options:t,variant:"default",display:"vertical"}},c={args:{label:"Choose your options",options:t,variant:"default",display:"vertical",disabled:!0}},p={args:{label:"Choose your options",options:t,variant:"default",display:"vertical"}},u={args:{label:"Choose your detailed options",options:o,variant:"detailed",display:"vertical"}},m={args:{label:"Choose your detailed options",options:o,variant:"detailed",display:"horizontal"}},h={args:{label:"Choose your detailed options",description:"You can select several options.",options:o,variant:"detailed",display:"vertical"}},b={args:{label:e.jsx("h2",{style:{fontFamily:_.typography.title2.fontFamily,lineHeight:_.typography.title2.lineHeight,fontSize:_.typography.title2.fontSize},children:"Radio Button Group with Heading Tag as Title"}),options:o,variant:"detailed",description:"Description with heading"}},g={args:{label:"Choose your detailed options",error:"You must select at least one option.",options:o,variant:"detailed",display:"vertical"}},f={args:{label:"Choose your detailed options",options:o,variant:"detailed",display:"vertical",disabled:!0}},y={args:{label:"Choose your detailed options",options:o,variant:"detailed",display:"vertical"}};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...i.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'horizontal'
  }
}`,...l.parameters?.docs?.source}}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    description: 'You can select several options.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...n.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    error: 'You must select at least one option.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...d.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    disabled: true
  }
}`,...c.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...p.parameters?.docs?.source}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...u.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'horizontal'
  }
}`,...m.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    description: 'You can select several options.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...h.parameters?.docs?.source}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
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
}`,...b.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    error: 'You must select at least one option.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...g.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
    disabled: true
  }
}`,...f.parameters?.docs?.source}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...y.parameters?.docs?.source}}};const Q=["DefaultVertical","DefaultHorizontal","DefaultWithDescription","DefaultWithError","DefaultDisabled","DefaultWithDefaultValue","DetailedVertical","DetailedHorizontal","DetailedWithDescription","DetailedWithHeadingTag","DetailedWithError","DetailedDisabled","DetailedWithDefaultValue"];export{c as DefaultDisabled,l as DefaultHorizontal,i as DefaultVertical,p as DefaultWithDefaultValue,n as DefaultWithDescription,d as DefaultWithError,f as DetailedDisabled,m as DetailedHorizontal,u as DetailedVertical,y as DetailedWithDefaultValue,h as DetailedWithDescription,g as DetailedWithError,b as DetailedWithHeadingTag,Q as __namedExportsOrder,P as default};
