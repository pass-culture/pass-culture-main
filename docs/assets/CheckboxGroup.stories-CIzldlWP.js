import{i as V}from"./dog-C0QzEjl8.js";import{j as o}from"./jsx-runtime-DF2Pcvd1.js";import{c as W}from"./index-DeARc5FM.js";import{f as we}from"./full-error-BFAmjN4t.js";import{r as w}from"./index-B2-qRKKC.js";import{S as Te}from"./SvgIcon-DfLnDDE5.js";import{C as je}from"./Checkbox-DkZJSOtP.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./Tag-BDZYioa0.js";import"./full-thumb-up-Bb4kpRpM.js";const qe="_disabled_16lxv_35",a={"checkbox-group-header":"_checkbox-group-header_16lxv_1","checkbox-group-label-h1":"_checkbox-group-label-h1_16lxv_7","checkbox-group-label-h2":"_checkbox-group-label-h2_16lxv_12","checkbox-group-label-h3":"_checkbox-group-label-h3_16lxv_17","checkbox-group-label-h4":"_checkbox-group-label-h4_16lxv_22","checkbox-group-label-span":"_checkbox-group-label-span_16lxv_27","checkbox-group-label":"_checkbox-group-label_16lxv_7",disabled:qe,"checkbox-group-description":"_checkbox-group-description_16lxv_38","has-label-span":"_has-label-span_16lxv_38","has-label-h1":"_has-label-h1_16lxv_43","has-label-h2":"_has-label-h2_16lxv_43","has-label-h3":"_has-label-h3_16lxv_43","has-label-h4":"_has-label-h4_16lxv_43","checkbox-group-error":"_checkbox-group-error_16lxv_54","checkbox-group-error-icon":"_checkbox-group-error-icon_16lxv_60","checkbox-group-options":"_checkbox-group-options_16lxv_65","checkbox-group":"_checkbox-group_16lxv_1","display-vertical":"_display-vertical_16lxv_72","display-horizontal":"_display-horizontal_16lxv_75","variant-default":"_variant-default_16lxv_78","variant-detailed":"_variant-detailed_16lxv_84"},T=({label:j,labelTag:s="span",description:C,error:i,options:q,value:Ce,onChange:O,display:Oe="vertical",variant:Se="default",disabled:n=!1})=>{if(q.length<2)throw new Error("CheckboxGroup requires at least two options.");const z=w.useId(),E=w.useId(),G=w.useId(),Ve=[i?E:null,C?G:null].filter(Boolean).join(" "),d=Ce??[],We=e=>{let l;d.includes(e.value)?l=d.filter(S=>S!==e.value):l=[...d,e.value],O==null||O(l)};return o.jsxs("div",{role:"group","aria-labelledby":z,"aria-describedby":Ve,className:W(a["checkbox-group"],a[`display-${Oe}`],a[`variant-${Se}`],{[a.disabled]:n}),children:[o.jsxs("div",{className:a["checkbox-group-header"],children:[o.jsx(s,{id:z,className:W(a[`checkbox-group-label-${s}`],{[a.disabled]:n}),children:j}),C&&o.jsx("span",{id:G,className:W(a["checkbox-group-description"],{[a.disabled]:n,[a[`has-label-${s}`]]:s}),children:C}),o.jsx("div",{role:"alert",id:E,children:i&&o.jsxs(o.Fragment,{children:[o.jsx(Te,{src:we,alt:"",width:"16",className:a["checkbox-group-error-icon"]}),o.jsx("span",{className:a["checkbox-group-error"],children:i})]})})]}),o.jsx("div",{className:a["checkbox-group-options"],children:q.map(e=>{const l=d.includes(e.value),S=e.variant==="detailed"?{description:e.description,asset:e.asset,collapsed:e.collapsed}:{};return o.jsx(je,{label:e.label,checked:l,onChange:()=>We(e),hasError:!!i,disabled:n,sizing:e.sizing,indeterminate:e.indeterminate,name:e.name,required:e.required,asterisk:e.asterisk,onBlur:e.onBlur,variant:e.variant,...S},e.value)})})]})};try{T.displayName="CheckboxGroup",T.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{label:{defaultValue:null,description:"Label for the checkbox group",name:"label",required:!0,type:{name:"string"}},labelTag:{defaultValue:null,description:"Tag for the label, defaults to 'span', can be 'h1', 'h2', etc.",name:"labelTag",required:!1,type:{name:"ElementType"}},description:{defaultValue:null,description:"Description for the checkbox group",name:"description",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error message for the checkbox group",name:"error",required:!1,type:{name:"string"}},options:{defaultValue:null,description:"List of options as checkboxes",name:"options",required:!0,type:{name:"CheckboxGroupOption[]"}},value:{defaultValue:null,description:"Controlled selected values",name:"value",required:!0,type:{name:"string[]"}},onChange:{defaultValue:null,description:"Event handler called with the new array of selected values",name:"onChange",required:!0,type:{name:"(value: string[]) => void"}},display:{defaultValue:{value:"vertical"},description:"Display style of the checkbox group, defaults to 'vertical'",name:"display",required:!1,type:{name:"enum",value:[{value:'"horizontal"'},{value:'"vertical"'}]}},variant:{defaultValue:{value:"default"},description:"Variant of the checkboxes (applied to all), defaults to 'default'",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},disabled:{defaultValue:{value:"false"},description:"If the checkbox group is disabled, making all options unselectable",name:"disabled",required:!1,type:{name:"boolean"}}}}}catch{}const t=[{label:"Option 1",value:"1"},{label:"Option 2",value:"2"},{label:"Option 3",value:"3"}],r=[{label:"Detailed 1",value:"a",variant:"detailed",description:"Detailed description 1",asset:{variant:"image",src:V}},{label:"Detailed 2",value:"b",variant:"detailed",description:"Detailed description 2",asset:{variant:"image",src:V}},{label:"Detailed 3",value:"c",variant:"detailed",description:"Detailed description 3",asset:{variant:"image",src:V}}],Fe={title:"Design System/CheckboxGroup",component:T,tags:["autodocs"]},c={args:{label:"Choose your options",options:t,variant:"default",display:"vertical"}},p={args:{label:"Choose your options",options:t,variant:"default",display:"horizontal"}},u={args:{label:"Choose your options",description:"You can select several options.",options:t,variant:"default",display:"vertical"}},h={args:{label:"Choose your options",error:"You must select at least one option.",options:t,variant:"default",display:"vertical"}},b={args:{label:"Choose your options",options:t,variant:"default",display:"vertical",disabled:!0}},v={args:{label:"Choose your options",options:t,variant:"default",display:"vertical",value:["2"]}},m={args:{label:"Choose your detailed options",options:r,variant:"detailed",display:"vertical"}},g={args:{label:"Choose your detailed options",options:r,variant:"detailed",display:"horizontal"}},f={args:{label:"Choose your detailed options",description:"You can select several options.",options:r,variant:"detailed",display:"vertical"}},x={args:{label:"Radio Button Group with Heading Tag",labelTag:"h2",options:r,variant:"detailed",description:"Description with heading"}},y={args:{label:"Radio Button Group with Span Tag",labelTag:"span",options:r,variant:"detailed",description:"Description with span"}},_={args:{label:"Choose your detailed options",error:"You must select at least one option.",options:r,variant:"detailed",display:"vertical"}},D={args:{label:"Choose your detailed options",options:r,variant:"detailed",display:"vertical",disabled:!0}},k={args:{label:"Choose your detailed options",options:r,variant:"detailed",display:"vertical",value:["b"]}};var I,N,B;c.parameters={...c.parameters,docs:{...(I=c.parameters)==null?void 0:I.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...(B=(N=c.parameters)==null?void 0:N.docs)==null?void 0:B.source}}};var H,Y,R;p.parameters={...p.parameters,docs:{...(H=p.parameters)==null?void 0:H.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'horizontal'
  }
}`,...(R=(Y=p.parameters)==null?void 0:Y.docs)==null?void 0:R.source}}};var $,F,P;u.parameters={...u.parameters,docs:{...($=u.parameters)==null?void 0:$.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    description: 'You can select several options.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...(P=(F=u.parameters)==null?void 0:F.docs)==null?void 0:P.source}}};var A,J,K;h.parameters={...h.parameters,docs:{...(A=h.parameters)==null?void 0:A.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    error: 'You must select at least one option.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical'
  }
}`,...(K=(J=h.parameters)==null?void 0:J.docs)==null?void 0:K.source}}};var M,Q,U;b.parameters={...b.parameters,docs:{...(M=b.parameters)==null?void 0:M.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    disabled: true
  }
}`,...(U=(Q=b.parameters)==null?void 0:Q.docs)==null?void 0:U.source}}};var X,Z,L;v.parameters={...v.parameters,docs:{...(X=v.parameters)==null?void 0:X.docs,source:{originalSource:`{
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    value: ['2']
  }
}`,...(L=(Z=v.parameters)==null?void 0:Z.docs)==null?void 0:L.source}}};var ee,ae,oe;m.parameters={...m.parameters,docs:{...(ee=m.parameters)==null?void 0:ee.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...(oe=(ae=m.parameters)==null?void 0:ae.docs)==null?void 0:oe.source}}};var re,te,le;g.parameters={...g.parameters,docs:{...(re=g.parameters)==null?void 0:re.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'horizontal'
  }
}`,...(le=(te=g.parameters)==null?void 0:te.docs)==null?void 0:le.source}}};var se,ie,ne;f.parameters={...f.parameters,docs:{...(se=f.parameters)==null?void 0:se.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    description: 'You can select several options.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...(ne=(ie=f.parameters)==null?void 0:ie.docs)==null?void 0:ne.source}}};var de,ce,pe;x.parameters={...x.parameters,docs:{...(de=x.parameters)==null?void 0:de.docs,source:{originalSource:`{
  args: {
    label: 'Radio Button Group with Heading Tag',
    labelTag: 'h2',
    options: detailedOptions,
    variant: 'detailed',
    description: 'Description with heading'
  }
}`,...(pe=(ce=x.parameters)==null?void 0:ce.docs)==null?void 0:pe.source}}};var ue,he,be;y.parameters={...y.parameters,docs:{...(ue=y.parameters)==null?void 0:ue.docs,source:{originalSource:`{
  args: {
    label: 'Radio Button Group with Span Tag',
    labelTag: 'span',
    options: detailedOptions,
    variant: 'detailed',
    description: 'Description with span'
  }
}`,...(be=(he=y.parameters)==null?void 0:he.docs)==null?void 0:be.source}}};var ve,me,ge;_.parameters={..._.parameters,docs:{...(ve=_.parameters)==null?void 0:ve.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    error: 'You must select at least one option.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical'
  }
}`,...(ge=(me=_.parameters)==null?void 0:me.docs)==null?void 0:ge.source}}};var fe,xe,ye;D.parameters={...D.parameters,docs:{...(fe=D.parameters)==null?void 0:fe.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
    disabled: true
  }
}`,...(ye=(xe=D.parameters)==null?void 0:xe.docs)==null?void 0:ye.source}}};var _e,De,ke;k.parameters={...k.parameters,docs:{...(_e=k.parameters)==null?void 0:_e.docs,source:{originalSource:`{
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
    value: ['b']
  }
}`,...(ke=(De=k.parameters)==null?void 0:De.docs)==null?void 0:ke.source}}};const Pe=["DefaultVertical","DefaultHorizontal","DefaultWithDescription","DefaultWithError","DefaultDisabled","DefaultWithDefaultValue","DetailedVertical","DetailedHorizontal","DetailedWithDescription","DetailedWithHeadingTag","DetailedWithSpanTag","DetailedWithError","DetailedDisabled","DetailedWithDefaultValue"];export{b as DefaultDisabled,p as DefaultHorizontal,c as DefaultVertical,v as DefaultWithDefaultValue,u as DefaultWithDescription,h as DefaultWithError,D as DetailedDisabled,g as DetailedHorizontal,m as DetailedVertical,k as DetailedWithDefaultValue,f as DetailedWithDescription,_ as DetailedWithError,x as DetailedWithHeadingTag,y as DetailedWithSpanTag,Pe as __namedExportsOrder,Fe as default};
