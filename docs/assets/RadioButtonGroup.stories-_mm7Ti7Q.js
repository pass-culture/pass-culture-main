import{j as a}from"./jsx-runtime-DF2Pcvd1.js";import{r as R}from"./index-B2-qRKKC.js";import{R as C}from"./RadioButton-C6m5LUKX.js";import{T as Ve}from"./Tag-BDZYioa0.js";import{s as We}from"./stroke-date-CWTXq8J4.js";import{i as ke}from"./dog-C0QzEjl8.js";import{c as W}from"./index-DeARc5FM.js";import{f as je}from"./full-error-BFAmjN4t.js";import{S as Ne}from"./SvgIcon-DfLnDDE5.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./full-thumb-up-Bb4kpRpM.js";const o={"radio-button-group":"_radio-button-group_15fp2_1","radio-button-group-header":"_radio-button-group-header_15fp2_6","radio-button-group-label-h1":"_radio-button-group-label-h1_15fp2_11","radio-button-group-label-h2":"_radio-button-group-label-h2_15fp2_16","radio-button-group-label-h3":"_radio-button-group-label-h3_15fp2_21","radio-button-group-label-h4":"_radio-button-group-label-h4_15fp2_26","radio-button-group-label-span":"_radio-button-group-label-span_15fp2_31","radio-button-group-description":"_radio-button-group-description_15fp2_37","radio-button-group-error":"_radio-button-group-error_15fp2_42","radio-button-group-error-icon":"_radio-button-group-error-icon_15fp2_52","radio-button-group-options":"_radio-button-group-options_15fp2_59","display-horizontal":"_display-horizontal_15fp2_66","sizing-fill":"_sizing-fill_15fp2_66","radio-button-group-option":"_radio-button-group-option_15fp2_59","display-vertical":"_display-vertical_15fp2_70","variant-detailed":"_variant-detailed_15fp2_76"},T=({name:t,label:G,options:i,labelTag:D="span",description:S,error:r,variant:x="default",sizing:z="fill",display:we="vertical",disabled:w=!1,checkedOption:Ee,asset:qe,onChange:E,onBlur:Ie,required:q,asterisk:He=!0})=>{const I=R.useId(),H=R.useId(),O=R.useId(),Oe=`${r?H:""}${S?` ${O}`:""}`,V=i.map(n=>n.value);if(new Set(V).size!==V.length)throw new Error("RadioButtonGroup options must have unique values.");return a.jsxs("div",{role:"radiogroup","aria-labelledby":I,"aria-describedby":Oe,"aria-disabled":w,"aria-required":q,"aria-invalid":!!r,className:o["radio-button-group"],"data-testid":`wrapper-${t}`,children:[a.jsxs("div",{className:o["radio-button-group-header"],children:[a.jsxs(D,{id:I,className:W(o[`radio-button-group-label-${D}`]),children:[G,q&&He?" *":""]}),S&&a.jsx("span",{id:O,className:o["radio-button-group-description"],"aria-live":"polite",children:S}),a.jsx("div",{role:"alert",id:H,children:r&&a.jsxs("span",{className:o["radio-button-group-error"],children:[a.jsx(Ne,{className:o["radio-button-group-error-icon"],src:je,alt:"Erreur"}),r]})})]}),a.jsx("div",{className:W(o["radio-button-group-options"],o[`display-${we}`],o[`sizing-${z}`],o[`variant-${x}`]),children:i.map(n=>a.jsx("div",{className:o["radio-button-group-option"],children:a.jsx(C,{...n,name:t,variant:x,sizing:z,disabled:w,hasError:!!r,onChange:E,onBlur:Ie,asset:qe,...E&&{checked:Ee===n.value}})},n.value))})]})};try{T.displayName="RadioButtonGroup",T.__docgenInfo={description:"",displayName:"RadioButtonGroup",props:{name:{defaultValue:null,description:"Name of the radio button group, binding all radio buttons together",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"Label for the radio button group",name:"label",required:!0,type:{name:"string"}},options:{defaultValue:null,description:"List of options as radio buttons",name:"options",required:!0,type:{name:'(Omit<RadioButtonProps, "name"> & { name?: string | undefined; sizing?: RadioButtonSizing | undefined; disabled?: boolean | undefined; onChange?: ((event: ChangeEvent<...>) => void) | undefined; onBlur?: ((event: FocusEvent<...>) => void) | undefined; } & RadioButtonVariantProps)[]'}},labelTag:{defaultValue:null,description:"Tag for the label, defaults to 'span', can be 'h1', 'h2', etc.",name:"labelTag",required:!1,type:{name:"ElementType"}},description:{defaultValue:null,description:"Description for the radio button group",name:"description",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error message for the radio button group",name:"error",required:!1,type:{name:"string"}},variant:{defaultValue:{value:"default"},description:"Variant of the radio buttons (applied to all), defaults to 'default'",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},sizing:{defaultValue:{value:"fill"},description:"Sizing of the radio buttons (applied to all), defaults to 'fill'",name:"sizing",required:!1,type:{name:"enum",value:[{value:'"hug"'},{value:'"fill"'}]}},asset:{defaultValue:null,description:"Asset of the radio buttons (applied to all), displayed when variant is 'detailed'",name:"asset",required:!1,type:{name:"RadioButtonAssetProps"}},display:{defaultValue:{value:"vertical"},description:"Display style of the radio button group, defaults to 'vertical'",name:"display",required:!1,type:{name:"enum",value:[{value:'"horizontal"'},{value:'"vertical"'}]}},checkedOption:{defaultValue:null,description:"Selected option, required if the group is non-controlled",name:"checkedOption",required:!1,type:{name:"string"}},disabled:{defaultValue:{value:"false"},description:"If the radio button group is disabled, making all options unselectable",name:"disabled",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"Event handler for change",name:"onChange",required:!1,type:{name:"((event: ChangeEvent<HTMLInputElement>) => void)"}},onBlur:{defaultValue:null,description:"Event handler for blur",name:"onBlur",required:!1,type:{name:"((event: FocusEvent<HTMLInputElement, Element>) => void)"}},required:{defaultValue:null,description:"Whether the checkbox is required or not",name:"required",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"Whether the required asterisk is displayed or not",name:"asterisk",required:!1,type:{name:"boolean"}}}}}catch{}const Ye={title:"@/design-system/RadioButtonGroup",component:T},e=[{label:"Option 1",name:"group1",description:"Description 1",value:"1"},{label:"Option 2",name:"group1",description:"Description 2 that is a little longer...",value:"2"},{label:"Option 3",name:"group1",description:"Description 3",value:"3"}],k={label:"Option 4",name:"group1",description:"Description 4",value:"4",collapsed:a.jsxs("div",{style:{display:"flex",flexDirection:"row",gap:16},children:[a.jsx(C,{name:"subchoice",label:"Sous-label 1",value:"1"}),a.jsx(C,{name:"subchoice",label:"Sous-label 2",value:"2"})]})},s={args:{name:"radio-button-group",label:"Radio Button Group",options:e}},l={args:{name:"radio-button-group",label:"Detailed Radio Button Group",variant:"detailed",options:e}},u={args:{name:"radio-button-group",label:"Detailed Radio Button Group",variant:"detailed",sizing:"hug",options:e}},d={args:{name:"radio-button-group",label:"Horizontal Radio Button Group",variant:"detailed",display:"horizontal",sizing:"fill",options:e}},p={args:{name:"radio-button-group",label:"Hugged Horizontal Radio Button Group",variant:"detailed",display:"horizontal",sizing:"hug",options:e}},c={args:{name:"radio-button-group",label:"Disabled Radio Button Group",disabled:!0,variant:"detailed",options:e}},m={args:{name:"radio-button-group",label:"Radio Button Group with Description",description:"This is a description for the radio button group.",options:e}},g={args:{name:"radio-button-group",label:"Radio Button Group with Heading Tag as Title",labelTag:"h2",options:e}},b={args:{name:"radio-button-group",label:"Radio Button Group with Span Tag as Title",labelTag:"span",options:e}},h={args:{name:"radio-button-group",label:"Radio Button Group with Error",error:"This is an error message.",options:e}},f={args:{name:"radio-button-group",label:"Radio Button Group with Common Tag",variant:"detailed",asset:{variant:"tag",tag:{label:"Tag",variant:Ve.SUCCESS}},options:e}},v={args:{name:"radio-button-group",label:"Radio Button Group with Common Text",variant:"detailed",asset:{variant:"text",text:"19€"},options:e}},_={args:{name:"radio-button-group",label:"Radio Button Group with Common Icon",variant:"detailed",asset:{variant:"icon",src:We},options:e}},y={args:{name:"radio-button-group",label:"Radio Button Group with Common Image",variant:"detailed",asset:{variant:"image",src:ke,size:"s"},options:e}},B={render:()=>{const[t,G]=R.useState(k.value);return a.jsx(T,{name:"radio-button-group",label:"Radio Button Group with Collapsed Option",variant:"detailed",checkedOption:t,onChange:i=>G(i.target.value),options:[...e,k]})}};var j,N,$;s.parameters={...s.parameters,docs:{...(j=s.parameters)==null?void 0:j.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group',
    options
  }
}`,...($=(N=s.parameters)==null?void 0:N.docs)==null?void 0:$.source}}};var A,F,L;l.parameters={...l.parameters,docs:{...(A=l.parameters)==null?void 0:A.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    options
  }
}`,...(L=(F=l.parameters)==null?void 0:F.docs)==null?void 0:L.source}}};var M,U,P;u.parameters={...u.parameters,docs:{...(M=u.parameters)==null?void 0:M.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    sizing: 'hug',
    options
  }
}`,...(P=(U=u.parameters)==null?void 0:U.docs)==null?void 0:P.source}}};var J,K,Q;d.parameters={...d.parameters,docs:{...(J=d.parameters)==null?void 0:J.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'fill',
    options
  }
}`,...(Q=(K=d.parameters)==null?void 0:K.docs)==null?void 0:Q.source}}};var X,Y,Z;p.parameters={...p.parameters,docs:{...(X=p.parameters)==null?void 0:X.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Hugged Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'hug',
    options
  }
}`,...(Z=(Y=p.parameters)==null?void 0:Y.docs)==null?void 0:Z.source}}};var ee,ae,oe;c.parameters={...c.parameters,docs:{...(ee=c.parameters)==null?void 0:ee.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Disabled Radio Button Group',
    disabled: true,
    variant: 'detailed',
    options
  }
}`,...(oe=(ae=c.parameters)==null?void 0:ae.docs)==null?void 0:oe.source}}};var te,re,ne;m.parameters={...m.parameters,docs:{...(te=m.parameters)==null?void 0:te.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Description',
    description: 'This is a description for the radio button group.',
    options
  }
}`,...(ne=(re=m.parameters)==null?void 0:re.docs)==null?void 0:ne.source}}};var ie,se,le;g.parameters={...g.parameters,docs:{...(ie=g.parameters)==null?void 0:ie.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Heading Tag as Title',
    labelTag: 'h2',
    options
  }
}`,...(le=(se=g.parameters)==null?void 0:se.docs)==null?void 0:le.source}}};var ue,de,pe;b.parameters={...b.parameters,docs:{...(ue=b.parameters)==null?void 0:ue.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Span Tag as Title',
    labelTag: 'span',
    options
  }
}`,...(pe=(de=b.parameters)==null?void 0:de.docs)==null?void 0:pe.source}}};var ce,me,ge;h.parameters={...h.parameters,docs:{...(ce=h.parameters)==null?void 0:ce.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Error',
    error: 'This is an error message.',
    options
  }
}`,...(ge=(me=h.parameters)==null?void 0:me.docs)==null?void 0:ge.source}}};var be,he,fe;f.parameters={...f.parameters,docs:{...(be=f.parameters)==null?void 0:be.docs,source:{originalSource:`{
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
}`,...(fe=(he=f.parameters)==null?void 0:he.docs)==null?void 0:fe.source}}};var ve,_e,ye;v.parameters={...v.parameters,docs:{...(ve=v.parameters)==null?void 0:ve.docs,source:{originalSource:`{
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
}`,...(ye=(_e=v.parameters)==null?void 0:_e.docs)==null?void 0:ye.source}}};var Be,Re,Te;_.parameters={..._.parameters,docs:{...(Be=_.parameters)==null?void 0:Be.docs,source:{originalSource:`{
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
}`,...(Te=(Re=_.parameters)==null?void 0:Re.docs)==null?void 0:Te.source}}};var Ge,Se,Ce;y.parameters={...y.parameters,docs:{...(Ge=y.parameters)==null?void 0:Ge.docs,source:{originalSource:`{
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
}`,...(Ce=(Se=y.parameters)==null?void 0:Se.docs)==null?void 0:Ce.source}}};var De,xe,ze;B.parameters={...B.parameters,docs:{...(De=B.parameters)==null?void 0:De.docs,source:{originalSource:`{
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [checkedOption, setCheckedOption] = useState<string>(collapsedOption.value);
    return <RadioButtonGroup name="radio-button-group" label="Radio Button Group with Collapsed Option" variant="detailed" checkedOption={checkedOption} onChange={e => setCheckedOption(e.target.value)} options={[...options, collapsedOption]} />;
  }
}`,...(ze=(xe=B.parameters)==null?void 0:xe.docs)==null?void 0:ze.source}}};const Ze=["Default","Detailed","DetailedHugged","FilledHorizontalDisplay","HuggedHorizontalDisplay","Disabled","WithDescription","WithHeadingTagAsTitle","WithSpanTagAsTitle","WithError","WithCommonTag","WithCommonText","WithCommonIcon","WithCommonImage","WithCollapsed"];export{s as Default,l as Detailed,u as DetailedHugged,c as Disabled,d as FilledHorizontalDisplay,p as HuggedHorizontalDisplay,B as WithCollapsed,_ as WithCommonIcon,y as WithCommonImage,f as WithCommonTag,v as WithCommonText,m as WithDescription,h as WithError,g as WithHeadingTagAsTitle,b as WithSpanTagAsTitle,Ze as __namedExportsOrder,Ye as default};
