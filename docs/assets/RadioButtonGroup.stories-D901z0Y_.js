import{j as a}from"./jsx-runtime-DF2Pcvd1.js";import{r as B}from"./index-B2-qRKKC.js";import{R as C}from"./RadioButton-CRHTcNNM.js";import{T as Ie}from"./Tag-ClYlfzfP.js";import{s as We}from"./stroke-date-CWTXq8J4.js";import{i as ke}from"./dog-C0QzEjl8.js";import{c as S}from"./index-DeARc5FM.js";import{f as He}from"./full-error-BFAmjN4t.js";import{S as Ne}from"./SvgIcon-DfLnDDE5.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./full-thumb-up-Bb4kpRpM.js";const o={"radio-button-group":"_radio-button-group_ml532_1","radio-button-group-header":"_radio-button-group-header_ml532_6","radio-button-group-label-h1":"_radio-button-group-label-h1_ml532_12","radio-button-group-label-h2":"_radio-button-group-label-h2_ml532_17","radio-button-group-label-h3":"_radio-button-group-label-h3_ml532_22","radio-button-group-label-h4":"_radio-button-group-label-h4_ml532_27","radio-button-group-label-span":"_radio-button-group-label-span_ml532_32","radio-button-group-description":"_radio-button-group-description_ml532_38","radio-button-group-error":"_radio-button-group-error_ml532_42","radio-button-group-error-icon":"_radio-button-group-error-icon_ml532_51","radio-button-group-options":"_radio-button-group-options_ml532_58","display-vertical":"_display-vertical_ml532_63","variant-detailed":"_variant-detailed_ml532_67","display-horizontal":"_display-horizontal_ml532_71","sizing-hug":"_sizing-hug_ml532_79"},R=({name:t,label:T,options:r,labelTag:G="span",description:w,error:n,variant:x="default",sizing:D="fill",display:Ce="vertical",disabled:Ge=!1,checkedOption:we,className:xe,labelClassName:De,asset:ze,onChange:z,onBlur:qe,required:q,asterisk:Ee=!0,allowSingleOrNoneOption:Oe})=>{const E=B.useId(),O=B.useId(),V=B.useId(),Ve=`${n?O:""}${w?` ${V}`:""}`;if(!Oe&&r.length<2)throw new Error("RadioButtonGroup requires at least two options.");const I=r.map(i=>i.value);if(new Set(I).size!==I.length)throw new Error("RadioButtonGroup options must have unique values.");return a.jsxs("div",{role:"radiogroup","aria-labelledby":E,"aria-describedby":Ve,"aria-required":q,"aria-invalid":!!n,className:S(o["radio-button-group"],xe),"data-testid":`wrapper-${t}`,children:[a.jsxs("div",{className:o["radio-button-group-header"],children:[a.jsxs(G,{id:E,className:S(o[`radio-button-group-label-${G}`],De),children:[T,q&&Ee?" *":""]}),a.jsx("span",{id:V,className:o["radio-button-group-description"],"aria-live":"polite",children:w}),a.jsx("div",{role:"alert",id:O,children:n&&a.jsxs("span",{className:o["radio-button-group-error"],children:[a.jsx(Ne,{className:o["radio-button-group-error-icon"],src:He,alt:"Erreur"}),n]})})]}),a.jsx("div",{className:S(o["radio-button-group-options"],o[`display-${Ce}`],o[`sizing-${D}`],o[`variant-${x}`]),children:r.map(i=>a.jsx(C,{...i,name:t,variant:x,sizing:D,disabled:Ge,hasError:!!n,onChange:z,onBlur:qe,asset:ze,...z&&{checked:we===i.value}},i.value))})]})};try{R.displayName="RadioButtonGroup",R.__docgenInfo={description:"",displayName:"RadioButtonGroup",props:{name:{defaultValue:null,description:"Name of the radio button group, binding all radio buttons together",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"Label for the radio button group",name:"label",required:!0,type:{name:"string"}},options:{defaultValue:null,description:"List of options as radio buttons",name:"options",required:!0,type:{name:'(Omit<RadioButtonProps, "name"> & { name?: string | undefined; sizing?: RadioButtonSizing | undefined; disabled?: boolean | undefined; onChange?: ((event: ChangeEvent<...>) => void) | undefined; onBlur?: ((event: FocusEvent<...>) => void) | undefined; } & RadioButtonVariantProps)[]'}},labelTag:{defaultValue:null,description:"Tag for the label, defaults to 'span', can be 'h1', 'h2', etc.",name:"labelTag",required:!1,type:{name:"ElementType"}},description:{defaultValue:null,description:"Description for the radio button group",name:"description",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error message for the radio button group",name:"error",required:!1,type:{name:"string"}},variant:{defaultValue:{value:"default"},description:"Variant of the radio buttons (applied to all), defaults to 'default'",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},sizing:{defaultValue:{value:"fill"},description:"Sizing of the radio buttons (applied to all), defaults to 'fill'",name:"sizing",required:!1,type:{name:"enum",value:[{value:'"hug"'},{value:'"fill"'}]}},asset:{defaultValue:null,description:"Asset of the radio buttons (applied to all), displayed when variant is 'detailed'",name:"asset",required:!1,type:{name:"RadioButtonAssetProps"}},display:{defaultValue:{value:"vertical"},description:"Display style of the radio button group, defaults to 'vertical'",name:"display",required:!1,type:{name:"enum",value:[{value:'"horizontal"'},{value:'"vertical"'}]}},checkedOption:{defaultValue:null,description:"Selected option, required if the group is non-controlled",name:"checkedOption",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"Custom CSS class for the radio button group",name:"className",required:!1,type:{name:"string"}},labelClassName:{defaultValue:null,description:"Custom CSS class for the label",name:"labelClassName",required:!1,type:{name:"string"}},disabled:{defaultValue:{value:"false"},description:"If the radio button group is disabled, making all options unselectable",name:"disabled",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"Event handler for change",name:"onChange",required:!1,type:{name:"((event: ChangeEvent<HTMLInputElement>) => void)"}},onBlur:{defaultValue:null,description:"Event handler for blur",name:"onBlur",required:!1,type:{name:"((event: FocusEvent<HTMLInputElement, Element>) => void)"}},required:{defaultValue:null,description:"Whether the checkbox is required or not",name:"required",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"Whether the required asterisk is displayed or not",name:"asterisk",required:!1,type:{name:"boolean"}},allowSingleOrNoneOption:{defaultValue:null,description:"Allow options to be an array with none, or a single element - exception case: CollectiveOfferSelectionDuplication",name:"allowSingleOrNoneOption",required:!1,type:{name:"boolean"}}}}}catch{}const Xe={title:"design-system/RadioButtonGroup",component:R},e=[{label:"Option 1",name:"group1",description:"Description 1",value:"1"},{label:"Option 2",name:"group1",description:"Description 2",value:"2"},{label:"Option 3",name:"group1",description:"Description 3",value:"3"}],W={label:"Option 4",name:"group1",description:"Description 4",value:"4",collapsed:a.jsxs("div",{style:{display:"flex",flexDirection:"row",gap:16},children:[a.jsx(C,{name:"subchoice",label:"Sous-label 1",value:"1"}),a.jsx(C,{name:"subchoice",label:"Sous-label 2",value:"2"})]})},s={args:{name:"radio-button-group",label:"Radio Button Group",options:e}},l={args:{name:"radio-button-group",label:"Detailed Radio Button Group",variant:"detailed",options:e}},u={args:{name:"radio-button-group",label:"Horizontal Radio Button Group",variant:"detailed",display:"horizontal",sizing:"fill",options:e}},d={args:{name:"radio-button-group",label:"Hugged Horizontal Radio Button Group",variant:"detailed",display:"horizontal",sizing:"hug",options:e}},p={args:{name:"radio-button-group",label:"Disabled Radio Button Group",disabled:!0,variant:"detailed",options:e}},c={args:{name:"radio-button-group",label:"Radio Button Group with Description",description:"This is a description for the radio button group.",options:e}},m={args:{name:"radio-button-group",label:"Radio Button Group with Heading Tag as Title",labelTag:"h2",options:e}},g={args:{name:"radio-button-group",label:"Radio Button Group with Span Tag as Title",labelTag:"span",options:e}},b={args:{name:"radio-button-group",label:"Radio Button Group with Error",error:"This is an error message.",options:e}},h={args:{name:"radio-button-group",label:"Radio Button Group with Common Tag",variant:"detailed",asset:{variant:"tag",tag:{label:"Tag",variant:Ie.SUCCESS}},options:e}},f={args:{name:"radio-button-group",label:"Radio Button Group with Common Text",variant:"detailed",asset:{variant:"text",text:"19€"},options:e}},v={args:{name:"radio-button-group",label:"Radio Button Group with Common Icon",variant:"detailed",asset:{variant:"icon",src:We},options:e}},_={args:{name:"radio-button-group",label:"Radio Button Group with Common Image",variant:"detailed",asset:{variant:"image",src:ke,size:"s"},options:e}},y={render:()=>{const[t,T]=B.useState(W.value);return a.jsx(R,{name:"radio-button-group",label:"Radio Button Group with Collapsed Option",variant:"detailed",checkedOption:t,onChange:r=>T(r.target.value),options:[...e,W]})}};var k,H,N;s.parameters={...s.parameters,docs:{...(k=s.parameters)==null?void 0:k.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group',
    options
  }
}`,...(N=(H=s.parameters)==null?void 0:H.docs)==null?void 0:N.source}}};var j,$,A;l.parameters={...l.parameters,docs:{...(j=l.parameters)==null?void 0:j.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    options
  }
}`,...(A=($=l.parameters)==null?void 0:$.docs)==null?void 0:A.source}}};var F,L,M;u.parameters={...u.parameters,docs:{...(F=u.parameters)==null?void 0:F.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'fill',
    options
  }
}`,...(M=(L=u.parameters)==null?void 0:L.docs)==null?void 0:M.source}}};var U,P,J;d.parameters={...d.parameters,docs:{...(U=d.parameters)==null?void 0:U.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Hugged Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'hug',
    options
  }
}`,...(J=(P=d.parameters)==null?void 0:P.docs)==null?void 0:J.source}}};var K,Q,X;p.parameters={...p.parameters,docs:{...(K=p.parameters)==null?void 0:K.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Disabled Radio Button Group',
    disabled: true,
    variant: 'detailed',
    options
  }
}`,...(X=(Q=p.parameters)==null?void 0:Q.docs)==null?void 0:X.source}}};var Y,Z,ee;c.parameters={...c.parameters,docs:{...(Y=c.parameters)==null?void 0:Y.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Description',
    description: 'This is a description for the radio button group.',
    options
  }
}`,...(ee=(Z=c.parameters)==null?void 0:Z.docs)==null?void 0:ee.source}}};var ae,oe,te;m.parameters={...m.parameters,docs:{...(ae=m.parameters)==null?void 0:ae.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Heading Tag as Title',
    labelTag: 'h2',
    options
  }
}`,...(te=(oe=m.parameters)==null?void 0:oe.docs)==null?void 0:te.source}}};var re,ne,ie;g.parameters={...g.parameters,docs:{...(re=g.parameters)==null?void 0:re.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Span Tag as Title',
    labelTag: 'span',
    options
  }
}`,...(ie=(ne=g.parameters)==null?void 0:ne.docs)==null?void 0:ie.source}}};var se,le,ue;b.parameters={...b.parameters,docs:{...(se=b.parameters)==null?void 0:se.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Error',
    error: 'This is an error message.',
    options
  }
}`,...(ue=(le=b.parameters)==null?void 0:le.docs)==null?void 0:ue.source}}};var de,pe,ce;h.parameters={...h.parameters,docs:{...(de=h.parameters)==null?void 0:de.docs,source:{originalSource:`{
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
}`,...(ce=(pe=h.parameters)==null?void 0:pe.docs)==null?void 0:ce.source}}};var me,ge,be;f.parameters={...f.parameters,docs:{...(me=f.parameters)==null?void 0:me.docs,source:{originalSource:`{
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
}`,...(be=(ge=f.parameters)==null?void 0:ge.docs)==null?void 0:be.source}}};var he,fe,ve;v.parameters={...v.parameters,docs:{...(he=v.parameters)==null?void 0:he.docs,source:{originalSource:`{
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
}`,...(ve=(fe=v.parameters)==null?void 0:fe.docs)==null?void 0:ve.source}}};var _e,ye,Be;_.parameters={..._.parameters,docs:{...(_e=_.parameters)==null?void 0:_e.docs,source:{originalSource:`{
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
}`,...(Be=(ye=_.parameters)==null?void 0:ye.docs)==null?void 0:Be.source}}};var Re,Te,Se;y.parameters={...y.parameters,docs:{...(Re=y.parameters)==null?void 0:Re.docs,source:{originalSource:`{
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [checkedOption, setCheckedOption] = useState<string>(collapsedOption.value);
    return <RadioButtonGroup name="radio-button-group" label="Radio Button Group with Collapsed Option" variant="detailed" checkedOption={checkedOption} onChange={e => setCheckedOption(e.target.value)} options={[...options, collapsedOption]} />;
  }
}`,...(Se=(Te=y.parameters)==null?void 0:Te.docs)==null?void 0:Se.source}}};const Ye=["Default","Detailed","FilledHorizontalDisplay","HuggedHorizontalDisplay","Disabled","WithDescription","WithHeadingTagAsTitle","WithSpanTagAsTitle","WithError","WithCommonTag","WithCommonText","WithCommonIcon","WithCommonImage","WithCollapsed"];export{s as Default,l as Detailed,p as Disabled,u as FilledHorizontalDisplay,d as HuggedHorizontalDisplay,y as WithCollapsed,v as WithCommonIcon,_ as WithCommonImage,h as WithCommonTag,f as WithCommonText,c as WithDescription,b as WithError,m as WithHeadingTagAsTitle,g as WithSpanTagAsTitle,Ye as __namedExportsOrder,Xe as default};
