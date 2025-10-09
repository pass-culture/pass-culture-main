import{i as k}from"./dog-C0QzEjl8.js";import{j as a}from"./jsx-runtime-DeZVbDx8.js";import{c as C}from"./index-BjQbGDRl.js";import{f as w}from"./full-error-BFAmjN4t.js";import{r as j}from"./iframe-BtENIfoR.js";import{S as G}from"./SvgIcon-D5zkCJFh.js";import{C as T}from"./Checkbox-gTOyCHZ3.js";import"./preload-helper-PPVm8Dsz.js";import"./Tag-XpNqxPd7.js";import"./full-thumb-up-Bb4kpRpM.js";const H="_disabled_1naqm_29",e={"checkbox-group-label-h1":"_checkbox-group-label-h1_1naqm_1","checkbox-group-label-h2":"_checkbox-group-label-h2_1naqm_6","checkbox-group-label-h3":"_checkbox-group-label-h3_1naqm_11","checkbox-group-label-h4":"_checkbox-group-label-h4_1naqm_16","checkbox-group-label-span":"_checkbox-group-label-span_1naqm_21","checkbox-group-label":"_checkbox-group-label_1naqm_1",disabled:H,"checkbox-group-description":"_checkbox-group-description_1naqm_32","has-label-span":"_has-label-span_1naqm_36","has-label-h1":"_has-label-h1_1naqm_41","has-label-h2":"_has-label-h2_1naqm_41","has-label-h3":"_has-label-h3_1naqm_41","has-label-h4":"_has-label-h4_1naqm_41","checkbox-group-error":"_checkbox-group-error_1naqm_49","checkbox-group-error-icon":"_checkbox-group-error-icon_1naqm_56","checkbox-group-options":"_checkbox-group-options_1naqm_61","checkbox-group":"_checkbox-group_1naqm_1","display-vertical":"_display-vertical_1naqm_68","display-horizontal":"_display-horizontal_1naqm_71","variant-default":"_variant-default_1naqm_74","variant-detailed":"_variant-detailed_1naqm_80"},q=({label:O,labelTag:l="span",description:D,error:r,options:E,display:z="vertical",variant:S="default",disabled:s=!1})=>{const V=j.useId(),W=j.useId(),N=`${r?V:""} ${D?W:""}`;return a.jsxs("fieldset",{"aria-describedby":N,className:C(e["checkbox-group"],e[`display-${z}`],e[`variant-${S}`],{[e.disabled]:s}),children:[a.jsx("legend",{className:e["checkbox-group-legend"],children:a.jsx(l,{className:C(e[`checkbox-group-label-${l}`],{[e.disabled]:s}),children:O})}),D&&a.jsx("p",{id:W,className:C(e["checkbox-group-description"],{[e.disabled]:s,[e[`has-label-${l}`]]:l}),children:D}),a.jsx("div",{role:"alert",children:r&&a.jsxs("div",{id:V,children:[a.jsx(G,{src:w,alt:"",width:"16",className:e["checkbox-group-error-icon"]}),a.jsx("span",{className:e["checkbox-group-error"],children:r})]})}),a.jsx("div",{className:e["checkbox-group-options"],children:E.map(i=>a.jsx("div",{className:e["checkbox-group-item"],children:S==="default"?a.jsx(T,{...i,description:void 0,asset:void 0,collapsed:void 0,hasError:!!r,disabled:s||i.disabled,variant:"default"}):a.jsx(T,{...i,hasError:!!r,disabled:s||i.disabled,variant:"detailed"})},i.label))})]})};try{q.displayName="CheckboxGroup",q.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{label:{defaultValue:null,description:"Label for the checkbox group",name:"label",required:!0,type:{name:"string"}},labelTag:{defaultValue:null,description:"Tag for the label, defaults to 'span', can be 'h1', 'h2', etc.",name:"labelTag",required:!1,type:{name:"ElementType"}},description:{defaultValue:null,description:"Description for the checkbox group",name:"description",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error message for the checkbox group",name:"error",required:!1,type:{name:"string"}},options:{defaultValue:null,description:"List of options as checkboxes",name:"options",required:!0,type:{name:"CheckboxGroupOption[]"}},display:{defaultValue:{value:"vertical"},description:"Display style of the checkbox group, defaults to 'vertical'",name:"display",required:!1,type:{name:"enum",value:[{value:'"horizontal"'},{value:'"vertical"'}]}},variant:{defaultValue:{value:"default"},description:"Variant of the checkboxes (applied to all), defaults to 'default'",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},disabled:{defaultValue:{value:"false"},description:"If the checkbox group is disabled, making all options unselectable",name:"disabled",required:!1,type:{name:"boolean"}}}}}catch{}const t=[{label:"Option 1",checked:!1},{label:"Option 2",checked:!1},{label:"Option 3",checked:!1}],o=[{label:"Detailed 1",description:"Detailed description 1",asset:{variant:"image",src:k},checked:!1},{label:"Detailed 2",checked:!1,description:"Detailed description 2",asset:{variant:"image",src:k}},{label:"Detailed 3",checked:!1,description:"Detailed description 3",asset:{variant:"image",src:k}}],P={title:"Design System/CheckboxGroup",component:q,tags:["autodocs"]},n={args:{label:"Choose your options",options:t,variant:"default",display:"vertical"}},d={args:{label:"Choose your options",options:t,variant:"default",display:"horizontal"}},c={args:{label:"Choose your options",description:"You can select several options.",options:t,variant:"default",display:"vertical"}},p={args:{label:"Choose your options",error:"You must select at least one option.",options:t,variant:"default",display:"vertical"}},u={args:{label:"Choose your options",options:t,variant:"default",display:"vertical",disabled:!0}},h={args:{label:"Choose your options",options:t,variant:"default",display:"vertical"}},m={args:{label:"Choose your detailed options",options:o,variant:"detailed",display:"vertical"}},b={args:{label:"Choose your detailed options",options:o,variant:"detailed",display:"horizontal"}},g={args:{label:"Choose your detailed options",description:"You can select several options.",options:o,variant:"detailed",display:"vertical"}},f={args:{label:"Radio Button Group with Heading Tag",labelTag:"h2",options:o,variant:"detailed",description:"Description with heading"}},v={args:{label:"Radio Button Group with Span Tag",labelTag:"span",options:o,variant:"detailed",description:"Description with span"}},y={args:{label:"Choose your detailed options",error:"You must select at least one option.",options:o,variant:"detailed",display:"vertical"}},_={args:{label:"Choose your detailed options",options:o,variant:"detailed",display:"vertical",disabled:!0}},x={args:{label:"Choose your detailed options",options:o,variant:"detailed",display:"vertical"}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...n.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'horizontal'
  }
}`,...d.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    description: 'You can select several options.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...c.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    error: 'You must select at least one option.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...p.parameters?.docs?.source}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    disabled: true
  }
}`,...u.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...h.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...m.parameters?.docs?.source}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'horizontal'
  }
}`,...b.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    description: 'You can select several options.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...g.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Radio Button Group with Heading Tag',
    labelTag: 'h2',
    options: detailedOptions,
    variant: 'detailed',
    description: 'Description with heading'
  }
}`,...f.parameters?.docs?.source}}};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Radio Button Group with Span Tag',
    labelTag: 'span',
    options: detailedOptions,
    variant: 'detailed',
    description: 'Description with span'
  }
}`,...v.parameters?.docs?.source}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    error: 'You must select at least one option.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...y.parameters?.docs?.source}}};_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
    disabled: true
  }
}`,..._.parameters?.docs?.source}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...x.parameters?.docs?.source}}};const Q=["DefaultVertical","DefaultHorizontal","DefaultWithDescription","DefaultWithError","DefaultDisabled","DefaultWithDefaultValue","DetailedVertical","DetailedHorizontal","DetailedWithDescription","DetailedWithHeadingTag","DetailedWithSpanTag","DetailedWithError","DetailedDisabled","DetailedWithDefaultValue"];export{u as DefaultDisabled,d as DefaultHorizontal,n as DefaultVertical,h as DefaultWithDefaultValue,c as DefaultWithDescription,p as DefaultWithError,_ as DetailedDisabled,b as DetailedHorizontal,m as DetailedVertical,x as DetailedWithDefaultValue,g as DetailedWithDescription,y as DetailedWithError,f as DetailedWithHeadingTag,v as DetailedWithSpanTag,Q as __namedExportsOrder,P as default};
