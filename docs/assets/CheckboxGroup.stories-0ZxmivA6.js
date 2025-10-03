import{i as O}from"./dog-C0QzEjl8.js";import{j as o}from"./jsx-runtime-Uoxi5foy.js";import{c as S}from"./index-CORXSc3e.js";import{f as R}from"./full-error-BFAmjN4t.js";import{r as V}from"./iframe-CUb4CGq4.js";import{S as $}from"./SvgIcon-ooyuOU-r.js";import{C as F}from"./Checkbox-67It0vyI.js";import"./preload-helper-PPVm8Dsz.js";import"./Tag-CKdaIW1Z.js";import"./full-thumb-up-Bb4kpRpM.js";const P="_disabled_6o1zp_35",a={"checkbox-group-header":"_checkbox-group-header_6o1zp_1","checkbox-group-label-h1":"_checkbox-group-label-h1_6o1zp_7","checkbox-group-label-h2":"_checkbox-group-label-h2_6o1zp_12","checkbox-group-label-h3":"_checkbox-group-label-h3_6o1zp_17","checkbox-group-label-h4":"_checkbox-group-label-h4_6o1zp_22","checkbox-group-label-span":"_checkbox-group-label-span_6o1zp_27","checkbox-group-label":"_checkbox-group-label_6o1zp_7",disabled:P,"checkbox-group-description":"_checkbox-group-description_6o1zp_38","has-label-span":"_has-label-span_6o1zp_38","has-label-h1":"_has-label-h1_6o1zp_43","has-label-h2":"_has-label-h2_6o1zp_43","has-label-h3":"_has-label-h3_6o1zp_43","has-label-h4":"_has-label-h4_6o1zp_43","checkbox-group-error":"_checkbox-group-error_6o1zp_54","checkbox-group-error-icon":"_checkbox-group-error-icon_6o1zp_60","checkbox-group-options":"_checkbox-group-options_6o1zp_65","checkbox-group":"_checkbox-group_6o1zp_1","display-vertical":"_display-vertical_6o1zp_72","display-horizontal":"_display-horizontal_6o1zp_75","variant-default":"_variant-default_6o1zp_78","variant-detailed":"_variant-detailed_6o1zp_84"},W=({label:w,labelTag:l="span",description:C,error:i,options:T,value:G,onChange:I,display:N="vertical",variant:B="default",disabled:n=!1})=>{if(T.length<2)throw new Error("CheckboxGroup requires at least two options.");const j=V.useId(),q=V.useId(),E=V.useId(),H=[i?q:null,C?E:null].filter(Boolean).join(" "),d=G??[],Y=e=>{let s;d.includes(e.value)?s=d.filter(z=>z!==e.value):s=[...d,e.value],I?.(s)};return o.jsxs("div",{role:"group","aria-labelledby":j,"aria-describedby":H,className:S(a["checkbox-group"],a[`display-${N}`],a[`variant-${B}`],{[a.disabled]:n}),children:[o.jsxs("div",{className:a["checkbox-group-header"],children:[o.jsx(l,{id:j,className:S(a[`checkbox-group-label-${l}`],{[a.disabled]:n}),children:w}),C&&o.jsx("span",{id:E,className:S(a["checkbox-group-description"],{[a.disabled]:n,[a[`has-label-${l}`]]:l}),children:C}),o.jsx("div",{role:"alert",id:q,children:i&&o.jsxs(o.Fragment,{children:[o.jsx($,{src:R,alt:"",width:"16",className:a["checkbox-group-error-icon"]}),o.jsx("span",{className:a["checkbox-group-error"],children:i})]})})]}),o.jsx("div",{className:a["checkbox-group-options"],children:T.map(e=>{const s=d.includes(e.value),z=e.variant==="detailed"?{description:e.description,asset:e.asset,collapsed:e.collapsed}:{};return o.jsx(F,{label:e.label,checked:s,onChange:()=>Y(e),hasError:!!i,disabled:n,sizing:e.sizing,indeterminate:e.indeterminate,name:e.name,required:e.required,asterisk:e.asterisk,onBlur:e.onBlur,variant:e.variant,...z},e.value)})})]})};try{W.displayName="CheckboxGroup",W.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{label:{defaultValue:null,description:"Label for the checkbox group",name:"label",required:!0,type:{name:"string"}},labelTag:{defaultValue:null,description:"Tag for the label, defaults to 'span', can be 'h1', 'h2', etc.",name:"labelTag",required:!1,type:{name:"ElementType"}},description:{defaultValue:null,description:"Description for the checkbox group",name:"description",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error message for the checkbox group",name:"error",required:!1,type:{name:"string"}},options:{defaultValue:null,description:"List of options as checkboxes",name:"options",required:!0,type:{name:"CheckboxGroupOption[]"}},value:{defaultValue:null,description:"Controlled selected values",name:"value",required:!0,type:{name:"string[]"}},onChange:{defaultValue:null,description:"Event handler called with the new array of selected values",name:"onChange",required:!0,type:{name:"(value: string[]) => void"}},display:{defaultValue:{value:"vertical"},description:"Display style of the checkbox group, defaults to 'vertical'",name:"display",required:!1,type:{name:"enum",value:[{value:'"horizontal"'},{value:'"vertical"'}]}},variant:{defaultValue:{value:"default"},description:"Variant of the checkboxes (applied to all), defaults to 'default'",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},disabled:{defaultValue:{value:"false"},description:"If the checkbox group is disabled, making all options unselectable",name:"disabled",required:!1,type:{name:"boolean"}}}}}catch{}const t=[{label:"Option 1",value:"1"},{label:"Option 2",value:"2"},{label:"Option 3",value:"3"}],r=[{label:"Detailed 1",value:"a",variant:"detailed",description:"Detailed description 1",asset:{variant:"image",src:O}},{label:"Detailed 2",value:"b",variant:"detailed",description:"Detailed description 2",asset:{variant:"image",src:O}},{label:"Detailed 3",value:"c",variant:"detailed",description:"Detailed description 3",asset:{variant:"image",src:O}}],ae={title:"Design System/CheckboxGroup",component:W,tags:["autodocs"]},c={args:{label:"Choose your options",options:t,variant:"default",display:"vertical"}},p={args:{label:"Choose your options",options:t,variant:"default",display:"horizontal"}},u={args:{label:"Choose your options",description:"You can select several options.",options:t,variant:"default",display:"vertical"}},h={args:{label:"Choose your options",error:"You must select at least one option.",options:t,variant:"default",display:"vertical"}},b={args:{label:"Choose your options",options:t,variant:"default",display:"vertical",disabled:!0}},m={args:{label:"Choose your options",options:t,variant:"default",display:"vertical",value:["2"]}},g={args:{label:"Choose your detailed options",options:r,variant:"detailed",display:"vertical"}},v={args:{label:"Choose your detailed options",options:r,variant:"detailed",display:"horizontal"}},f={args:{label:"Choose your detailed options",description:"You can select several options.",options:r,variant:"detailed",display:"vertical"}},y={args:{label:"Radio Button Group with Heading Tag",labelTag:"h2",options:r,variant:"detailed",description:"Description with heading"}},_={args:{label:"Radio Button Group with Span Tag",labelTag:"span",options:r,variant:"detailed",description:"Description with span"}},x={args:{label:"Choose your detailed options",error:"You must select at least one option.",options:r,variant:"detailed",display:"vertical"}},D={args:{label:"Choose your detailed options",options:r,variant:"detailed",display:"vertical",disabled:!0}},k={args:{label:"Choose your detailed options",options:r,variant:"detailed",display:"vertical",value:["b"]}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...c.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'horizontal'
  }
}`,...p.parameters?.docs?.source}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    description: 'You can select several options.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...u.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    error: 'You must select at least one option.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...h.parameters?.docs?.source}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    disabled: true
  }
}`,...b.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    value: ['2']
  }
}`,...m.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...g.parameters?.docs?.source}}};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'horizontal'
  }
}`,...v.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    description: 'You can select several options.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...f.parameters?.docs?.source}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Radio Button Group with Heading Tag',
    labelTag: 'h2',
    options: detailedOptions,
    variant: 'detailed',
    description: 'Description with heading'
  }
}`,...y.parameters?.docs?.source}}};_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Radio Button Group with Span Tag',
    labelTag: 'span',
    options: detailedOptions,
    variant: 'detailed',
    description: 'Description with span'
  }
}`,..._.parameters?.docs?.source}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    error: 'You must select at least one option.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...x.parameters?.docs?.source}}};D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
    disabled: true
  }
}`,...D.parameters?.docs?.source}}};k.parameters={...k.parameters,docs:{...k.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
    value: ['b']
  }
}`,...k.parameters?.docs?.source}}};const oe=["DefaultVertical","DefaultHorizontal","DefaultWithDescription","DefaultWithError","DefaultDisabled","DefaultWithDefaultValue","DetailedVertical","DetailedHorizontal","DetailedWithDescription","DetailedWithHeadingTag","DetailedWithSpanTag","DetailedWithError","DetailedDisabled","DetailedWithDefaultValue"];export{b as DefaultDisabled,p as DefaultHorizontal,c as DefaultVertical,m as DefaultWithDefaultValue,u as DefaultWithDescription,h as DefaultWithError,D as DetailedDisabled,v as DetailedHorizontal,g as DetailedVertical,k as DetailedWithDefaultValue,f as DetailedWithDescription,x as DetailedWithError,y as DetailedWithHeadingTag,_ as DetailedWithSpanTag,oe as __namedExportsOrder,ae as default};
