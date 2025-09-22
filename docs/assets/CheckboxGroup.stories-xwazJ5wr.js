import{i as S}from"./dog-C0QzEjl8.js";import{j as o}from"./jsx-runtime-Cf8x2fCZ.js";import{c as V}from"./index-B0pXE9zJ.js";import{f as R}from"./full-error-BFAmjN4t.js";import{r as W}from"./index-QQMyt9Ur.js";import{S as $}from"./SvgIcon-B5V96DYN.js";import{C as F}from"./Checkbox-C7BN2dD1.js";import"./index-yBjzXJbu.js";import"./_commonjsHelpers-CqkleIqs.js";import"./Tag-DpLUbPXr.js";import"./full-thumb-up-Bb4kpRpM.js";const P="_disabled_16lxv_35",a={"checkbox-group-header":"_checkbox-group-header_16lxv_1","checkbox-group-label-h1":"_checkbox-group-label-h1_16lxv_7","checkbox-group-label-h2":"_checkbox-group-label-h2_16lxv_12","checkbox-group-label-h3":"_checkbox-group-label-h3_16lxv_17","checkbox-group-label-h4":"_checkbox-group-label-h4_16lxv_22","checkbox-group-label-span":"_checkbox-group-label-span_16lxv_27","checkbox-group-label":"_checkbox-group-label_16lxv_7",disabled:P,"checkbox-group-description":"_checkbox-group-description_16lxv_38","has-label-span":"_has-label-span_16lxv_38","has-label-h1":"_has-label-h1_16lxv_43","has-label-h2":"_has-label-h2_16lxv_43","has-label-h3":"_has-label-h3_16lxv_43","has-label-h4":"_has-label-h4_16lxv_43","checkbox-group-error":"_checkbox-group-error_16lxv_54","checkbox-group-error-icon":"_checkbox-group-error-icon_16lxv_60","checkbox-group-options":"_checkbox-group-options_16lxv_65","checkbox-group":"_checkbox-group_16lxv_1","display-vertical":"_display-vertical_16lxv_72","display-horizontal":"_display-horizontal_16lxv_75","variant-default":"_variant-default_16lxv_78","variant-detailed":"_variant-detailed_16lxv_84"},w=({label:T,labelTag:s="span",description:C,error:i,options:j,value:G,onChange:I,display:N="vertical",variant:B="default",disabled:n=!1})=>{if(j.length<2)throw new Error("CheckboxGroup requires at least two options.");const q=W.useId(),z=W.useId(),E=W.useId(),H=[i?z:null,C?E:null].filter(Boolean).join(" "),d=G??[],Y=e=>{let l;d.includes(e.value)?l=d.filter(O=>O!==e.value):l=[...d,e.value],I?.(l)};return o.jsxs("div",{role:"group","aria-labelledby":q,"aria-describedby":H,className:V(a["checkbox-group"],a[`display-${N}`],a[`variant-${B}`],{[a.disabled]:n}),children:[o.jsxs("div",{className:a["checkbox-group-header"],children:[o.jsx(s,{id:q,className:V(a[`checkbox-group-label-${s}`],{[a.disabled]:n}),children:T}),C&&o.jsx("span",{id:E,className:V(a["checkbox-group-description"],{[a.disabled]:n,[a[`has-label-${s}`]]:s}),children:C}),o.jsx("div",{role:"alert",id:z,children:i&&o.jsxs(o.Fragment,{children:[o.jsx($,{src:R,alt:"",width:"16",className:a["checkbox-group-error-icon"]}),o.jsx("span",{className:a["checkbox-group-error"],children:i})]})})]}),o.jsx("div",{className:a["checkbox-group-options"],children:j.map(e=>{const l=d.includes(e.value),O=e.variant==="detailed"?{description:e.description,asset:e.asset,collapsed:e.collapsed}:{};return o.jsx(F,{label:e.label,checked:l,onChange:()=>Y(e),hasError:!!i,disabled:n,sizing:e.sizing,indeterminate:e.indeterminate,name:e.name,required:e.required,asterisk:e.asterisk,onBlur:e.onBlur,variant:e.variant,...O},e.value)})})]})};try{w.displayName="CheckboxGroup",w.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{label:{defaultValue:null,description:"Label for the checkbox group",name:"label",required:!0,type:{name:"string"}},labelTag:{defaultValue:null,description:"Tag for the label, defaults to 'span', can be 'h1', 'h2', etc.",name:"labelTag",required:!1,type:{name:"ElementType"}},description:{defaultValue:null,description:"Description for the checkbox group",name:"description",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error message for the checkbox group",name:"error",required:!1,type:{name:"string"}},options:{defaultValue:null,description:"List of options as checkboxes",name:"options",required:!0,type:{name:"CheckboxGroupOption[]"}},value:{defaultValue:null,description:"Controlled selected values",name:"value",required:!0,type:{name:"string[]"}},onChange:{defaultValue:null,description:"Event handler called with the new array of selected values",name:"onChange",required:!0,type:{name:"(value: string[]) => void"}},display:{defaultValue:{value:"vertical"},description:"Display style of the checkbox group, defaults to 'vertical'",name:"display",required:!1,type:{name:"enum",value:[{value:'"horizontal"'},{value:'"vertical"'}]}},variant:{defaultValue:{value:"default"},description:"Variant of the checkboxes (applied to all), defaults to 'default'",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},disabled:{defaultValue:{value:"false"},description:"If the checkbox group is disabled, making all options unselectable",name:"disabled",required:!1,type:{name:"boolean"}}}}}catch{}const t=[{label:"Option 1",value:"1"},{label:"Option 2",value:"2"},{label:"Option 3",value:"3"}],r=[{label:"Detailed 1",value:"a",variant:"detailed",description:"Detailed description 1",asset:{variant:"image",src:S}},{label:"Detailed 2",value:"b",variant:"detailed",description:"Detailed description 2",asset:{variant:"image",src:S}},{label:"Detailed 3",value:"c",variant:"detailed",description:"Detailed description 3",asset:{variant:"image",src:S}}],oe={title:"Design System/CheckboxGroup",component:w,tags:["autodocs"]},c={args:{label:"Choose your options",options:t,variant:"default",display:"vertical"}},p={args:{label:"Choose your options",options:t,variant:"default",display:"horizontal"}},u={args:{label:"Choose your options",description:"You can select several options.",options:t,variant:"default",display:"vertical"}},h={args:{label:"Choose your options",error:"You must select at least one option.",options:t,variant:"default",display:"vertical"}},b={args:{label:"Choose your options",options:t,variant:"default",display:"vertical",disabled:!0}},v={args:{label:"Choose your options",options:t,variant:"default",display:"vertical",value:["2"]}},m={args:{label:"Choose your detailed options",options:r,variant:"detailed",display:"vertical"}},g={args:{label:"Choose your detailed options",options:r,variant:"detailed",display:"horizontal"}},f={args:{label:"Choose your detailed options",description:"You can select several options.",options:r,variant:"detailed",display:"vertical"}},x={args:{label:"Radio Button Group with Heading Tag",labelTag:"h2",options:r,variant:"detailed",description:"Description with heading"}},y={args:{label:"Radio Button Group with Span Tag",labelTag:"span",options:r,variant:"detailed",description:"Description with span"}},_={args:{label:"Choose your detailed options",error:"You must select at least one option.",options:r,variant:"detailed",display:"vertical"}},D={args:{label:"Choose your detailed options",options:r,variant:"detailed",display:"vertical",disabled:!0}},k={args:{label:"Choose your detailed options",options:r,variant:"detailed",display:"vertical",value:["b"]}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
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
}`,...b.parameters?.docs?.source}}};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    value: ['2']
  }
}`,...v.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...m.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'horizontal'
  }
}`,...g.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    description: 'You can select several options.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...f.parameters?.docs?.source}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Radio Button Group with Heading Tag',
    labelTag: 'h2',
    options: detailedOptions,
    variant: 'detailed',
    description: 'Description with heading'
  }
}`,...x.parameters?.docs?.source}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Radio Button Group with Span Tag',
    labelTag: 'span',
    options: detailedOptions,
    variant: 'detailed',
    description: 'Description with span'
  }
}`,...y.parameters?.docs?.source}}};_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    error: 'You must select at least one option.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,..._.parameters?.docs?.source}}};D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
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
}`,...k.parameters?.docs?.source}}};const re=["DefaultVertical","DefaultHorizontal","DefaultWithDescription","DefaultWithError","DefaultDisabled","DefaultWithDefaultValue","DetailedVertical","DetailedHorizontal","DetailedWithDescription","DetailedWithHeadingTag","DetailedWithSpanTag","DetailedWithError","DetailedDisabled","DetailedWithDefaultValue"];export{b as DefaultDisabled,p as DefaultHorizontal,c as DefaultVertical,v as DefaultWithDefaultValue,u as DefaultWithDescription,h as DefaultWithError,D as DetailedDisabled,g as DetailedHorizontal,m as DetailedVertical,k as DetailedWithDefaultValue,f as DetailedWithDescription,_ as DetailedWithError,x as DetailedWithHeadingTag,y as DetailedWithSpanTag,re as __namedExportsOrder,oe as default};
