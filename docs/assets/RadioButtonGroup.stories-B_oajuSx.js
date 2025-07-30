import{i as da}from"./dog-C0QzEjl8.js";import{j as o}from"./jsx-runtime-DF2Pcvd1.js";import{c as pa}from"./index-DeARc5FM.js";import{r as f}from"./index-B2-qRKKC.js";import{R as ga}from"./RadioButton-cKQWA5sp.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./Tag-T67fX36U.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-DfLnDDE5.js";const e={"radio-button-group":"_radio-button-group_1whpr_1","radio-button-group-header":"_radio-button-group-header_1whpr_6","radio-button-group-label-h1":"_radio-button-group-label-h1_1whpr_12","radio-button-group-label-h2":"_radio-button-group-label-h2_1whpr_17","radio-button-group-label-h3":"_radio-button-group-label-h3_1whpr_22","radio-button-group-label-h4":"_radio-button-group-label-h4_1whpr_27","radio-button-group-label-span":"_radio-button-group-label-span_1whpr_32","radio-button-group-description":"_radio-button-group-description_1whpr_38","radio-button-group-error":"_radio-button-group-error_1whpr_42","radio-button-group-options":"_radio-button-group-options_1whpr_49","display-vertical":"_display-vertical_1whpr_54","variant-detailed":"_variant-detailed_1whpr_58","display-horizontal":"_display-horizontal_1whpr_62","sizing-hug":"_sizing-hug_1whpr_70"},v=({name:_,label:ra,options:b,labelTag:y="span",description:h,error:r,variant:B="default",sizing:R="fill",display:ta="vertical",disabled:na=!1,asset:ia,onChange:sa,onBlur:ua})=>{const w=f.useId(),z=f.useId(),G=f.useId(),la=`${r?z:""}${h?` ${G}`:""}`;if(b.length<2)throw new Error("RadioButtonGroup requires at least two options.");const D=b.map(t=>t.value);if(new Set(D).size!==D.length)throw new Error("RadioButtonGroup options must have unique values.");return o.jsxs("div",{role:"radiogroup","aria-labelledby":w,"aria-describedby":la,className:e["radio-button-group"],children:[o.jsxs("div",{className:e["radio-button-group-header"],children:[o.jsx(y,{id:w,className:e[`radio-button-group-label-${y}`],children:ra}),h&&o.jsx("span",{id:G,className:e["radio-button-group-description"],children:h}),o.jsx("div",{role:"alert",id:z,children:r&&o.jsx("span",{className:e["radio-button-group-error"],children:r})})]}),o.jsx("div",{className:pa(e["radio-button-group-options"],e[`display-${ta}`],e[`sizing-${R}`],e[`variant-${B}`]),children:b.map(t=>o.jsx(ga,{...t,name:_,variant:B,sizing:R,disabled:na,hasError:!!r,onChange:sa,onBlur:ua,asset:ia},t.value))})]})};try{v.displayName="RadioButtonGroup",v.__docgenInfo={description:"",displayName:"RadioButtonGroup",props:{name:{defaultValue:null,description:"Name of the radio button group, binding all radio buttons together",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"Label for the radio button group",name:"label",required:!0,type:{name:"string"}},options:{defaultValue:null,description:"List of options as radio buttons",name:"options",required:!0,type:{name:'(Omit<RadioButtonProps, "name"> & { name?: string | undefined; sizing?: RadioButtonSizing | undefined; disabled?: boolean | undefined; onChange?: ((event: ChangeEvent<...>) => void) | undefined; onBlur?: ((event: FocusEvent<...>) => void) | undefined; } & RadioButtonVariantProps)[]'}},labelTag:{defaultValue:null,description:"Tag for the label, defaults to 'span', can be 'h1', 'h2', etc.",name:"labelTag",required:!1,type:{name:"ElementType"}},description:{defaultValue:null,description:"Description for the radio button group",name:"description",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error message for the radio button group",name:"error",required:!1,type:{name:"string"}},variant:{defaultValue:{value:"default"},description:"Variant of the radio buttons (applied to all), defaults to 'default'",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},sizing:{defaultValue:{value:"fill"},description:"Sizing of the radio buttons (applied to all), defaults to 'fill'",name:"sizing",required:!1,type:{name:"enum",value:[{value:'"hug"'},{value:'"fill"'}]}},asset:{defaultValue:null,description:"Asset of the radio buttons (applied to all), displayed when variant is 'detailed'",name:"asset",required:!1,type:{name:"RadioButtonAssetProps"}},display:{defaultValue:{value:"vertical"},description:"Display style of the radio button group, defaults to 'vertical'",name:"display",required:!1,type:{name:"enum",value:[{value:'"horizontal"'},{value:'"vertical"'}]}},disabled:{defaultValue:{value:"false"},description:"If the radio button group is disabled, making all options unselectable",name:"disabled",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"Event handler for change",name:"onChange",required:!1,type:{name:"((event: ChangeEvent<HTMLInputElement>) => void)"}},onBlur:{defaultValue:null,description:"Event handler for blur",name:"onBlur",required:!1,type:{name:"((event: FocusEvent<HTMLInputElement, Element>) => void)"}}}}}catch{}const Ra={title:"design-system/RadioButtonGroup",component:v},a=[{label:"Option 1",name:"group1",description:"Description 1",value:"1"},{label:"Option 2",name:"group1",description:"Description 2",value:"2"},{label:"Option 3",name:"group1",description:"Description 3",value:"3"}],n={args:{name:"radio-button-group",label:"Radio Button Group",options:a}},i={args:{name:"radio-button-group",label:"Detailed Radio Button Group",variant:"detailed",options:a}},s={args:{name:"radio-button-group",label:"Horizontal Radio Button Group",variant:"detailed",display:"horizontal",sizing:"fill",options:a}},u={args:{name:"radio-button-group",label:"Hugged Horizontal Radio Button Group",variant:"detailed",display:"horizontal",sizing:"hug",options:a}},l={args:{name:"radio-button-group",label:"Disabled Radio Button Group",disabled:!0,variant:"detailed",options:a}},d={args:{name:"radio-button-group",label:"Radio Button Group with Description",description:"This is a description for the radio button group.",options:a}},p={args:{name:"radio-button-group",label:"Radio Button Group with Heading Tag",labelTag:"h2",options:a}},g={args:{name:"radio-button-group",label:"Radio Button Group with Span Tag",labelTag:"span",options:a}},c={args:{name:"radio-button-group",label:"Radio Button Group with Error",error:"This is an error message.",options:a}},m={args:{name:"radio-button-group",label:"Radio Button Group with Common Asset",variant:"detailed",asset:{variant:"image",src:da,size:"s"},options:a}};var T,E,H;n.parameters={...n.parameters,docs:{...(T=n.parameters)==null?void 0:T.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group',
    options
  }
}`,...(H=(E=n.parameters)==null?void 0:E.docs)==null?void 0:H.source}}};var S,q,V;i.parameters={...i.parameters,docs:{...(S=i.parameters)==null?void 0:S.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    options
  }
}`,...(V=(q=i.parameters)==null?void 0:q.docs)==null?void 0:V.source}}};var x,j,I;s.parameters={...s.parameters,docs:{...(x=s.parameters)==null?void 0:x.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'fill',
    options
  }
}`,...(I=(j=s.parameters)==null?void 0:j.docs)==null?void 0:I.source}}};var W,C,N;u.parameters={...u.parameters,docs:{...(W=u.parameters)==null?void 0:W.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Hugged Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'hug',
    options
  }
}`,...(N=(C=u.parameters)==null?void 0:C.docs)==null?void 0:N.source}}};var $,A,O;l.parameters={...l.parameters,docs:{...($=l.parameters)==null?void 0:$.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Disabled Radio Button Group',
    disabled: true,
    variant: 'detailed',
    options
  }
}`,...(O=(A=l.parameters)==null?void 0:A.docs)==null?void 0:O.source}}};var F,L,M;d.parameters={...d.parameters,docs:{...(F=d.parameters)==null?void 0:F.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Description',
    description: 'This is a description for the radio button group.',
    options
  }
}`,...(M=(L=d.parameters)==null?void 0:L.docs)==null?void 0:M.source}}};var P,k,J;p.parameters={...p.parameters,docs:{...(P=p.parameters)==null?void 0:P.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Heading Tag',
    labelTag: 'h2',
    options
  }
}`,...(J=(k=p.parameters)==null?void 0:k.docs)==null?void 0:J.source}}};var K,Q,U;g.parameters={...g.parameters,docs:{...(K=g.parameters)==null?void 0:K.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Span Tag',
    labelTag: 'span',
    options
  }
}`,...(U=(Q=g.parameters)==null?void 0:Q.docs)==null?void 0:U.source}}};var X,Y,Z;c.parameters={...c.parameters,docs:{...(X=c.parameters)==null?void 0:X.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Error',
    error: 'This is an error message.',
    options
  }
}`,...(Z=(Y=c.parameters)==null?void 0:Y.docs)==null?void 0:Z.source}}};var aa,ea,oa;m.parameters={...m.parameters,docs:{...(aa=m.parameters)==null?void 0:aa.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Common Asset',
    variant: 'detailed',
    asset: {
      variant: 'image',
      src: imageDemo,
      size: 's'
    },
    options
  }
}`,...(oa=(ea=m.parameters)==null?void 0:ea.docs)==null?void 0:oa.source}}};const wa=["Default","Detailed","FilledHorizontalDisplay","HuggedHorizontalDisplay","Disabled","WithDescription","WithHeadingTag","WithSpanTag","WithError","WithCommonAsset"];export{n as Default,i as Detailed,l as Disabled,s as FilledHorizontalDisplay,u as HuggedHorizontalDisplay,m as WithCommonAsset,d as WithDescription,c as WithError,p as WithHeadingTag,g as WithSpanTag,wa as __namedExportsOrder,Ra as default};
