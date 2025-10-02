import{j as a}from"./jsx-runtime-B3Z_H2YK.js";import{r as R}from"./iframe-Bnhr5QWa.js";import{R as C}from"./RadioButton-COeZi4LT.js";import{a as M}from"./Tag-Dplc8Dk0.js";import{s as U}from"./stroke-date-CWTXq8J4.js";import{i as P}from"./dog-C0QzEjl8.js";import{c as W}from"./index-4a8x82_B.js";import{f as J}from"./full-error-BFAmjN4t.js";import{S as K}from"./SvgIcon-BYOQvJ8S.js";import"./preload-helper-PPVm8Dsz.js";import"./full-thumb-up-Bb4kpRpM.js";const o={"radio-button-group":"_radio-button-group_lcu78_1","radio-button-group-header":"_radio-button-group-header_lcu78_6","radio-button-group-label-h1":"_radio-button-group-label-h1_lcu78_11","radio-button-group-label-h2":"_radio-button-group-label-h2_lcu78_16","radio-button-group-label-h3":"_radio-button-group-label-h3_lcu78_21","radio-button-group-label-h4":"_radio-button-group-label-h4_lcu78_26","radio-button-group-label-span":"_radio-button-group-label-span_lcu78_31","radio-button-group-description":"_radio-button-group-description_lcu78_37","radio-button-group-error":"_radio-button-group-error_lcu78_42","radio-button-group-error-icon":"_radio-button-group-error-icon_lcu78_52","radio-button-group-options":"_radio-button-group-options_lcu78_59","display-horizontal":"_display-horizontal_lcu78_66","sizing-fill":"_sizing-fill_lcu78_66","radio-button-group-option":"_radio-button-group-option_lcu78_59","display-vertical":"_display-vertical_lcu78_70","variant-detailed":"_variant-detailed_lcu78_76"},T=({name:t,label:G,options:i,labelTag:D="span",description:S,error:r,variant:x="default",sizing:z="fill",display:j="vertical",disabled:w=!1,checkedOption:N,asset:$,onChange:E,onBlur:A,required:q,asterisk:F=!0})=>{const I=R.useId(),H=R.useId(),O=R.useId(),L=`${r?H:""}${S?` ${O}`:""}`,V=i.map(n=>n.value);if(new Set(V).size!==V.length)throw new Error("RadioButtonGroup options must have unique values.");return a.jsxs("div",{role:"radiogroup","aria-labelledby":I,"aria-describedby":L,"aria-disabled":w,"aria-required":q,"aria-invalid":!!r,className:o["radio-button-group"],"data-testid":`wrapper-${t}`,children:[a.jsxs("div",{className:o["radio-button-group-header"],children:[a.jsxs(D,{id:I,className:W(o[`radio-button-group-label-${D}`]),children:[G,q&&F?" *":""]}),S&&a.jsx("span",{id:O,className:o["radio-button-group-description"],"aria-live":"polite",children:S}),a.jsx("div",{role:"alert",id:H,children:r&&a.jsxs("span",{className:o["radio-button-group-error"],children:[a.jsx(K,{className:o["radio-button-group-error-icon"],src:J,alt:"Erreur"}),r]})})]}),a.jsx("div",{className:W(o["radio-button-group-options"],o[`display-${j}`],o[`sizing-${z}`],o[`variant-${x}`]),children:i.map(n=>a.jsx("div",{className:o["radio-button-group-option"],children:a.jsx(C,{...n,name:t,variant:x,sizing:z,disabled:w,hasError:!!r,onChange:E,onBlur:A,asset:$,...E&&{checked:N===n.value}})},n.value))})]})};try{T.displayName="RadioButtonGroup",T.__docgenInfo={description:"",displayName:"RadioButtonGroup",props:{name:{defaultValue:null,description:"Name of the radio button group, binding all radio buttons together",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"Label for the radio button group",name:"label",required:!0,type:{name:"string"}},options:{defaultValue:null,description:"List of options as radio buttons",name:"options",required:!0,type:{name:'(Omit<RadioButtonProps, "name"> & { name?: string | undefined; sizing?: RadioButtonSizing | undefined; disabled?: boolean | undefined; onChange?: ((event: ChangeEvent<...>) => void) | undefined; onBlur?: ((event: FocusEvent<...>) => void) | undefined; } & RadioButtonVariantProps)[]'}},labelTag:{defaultValue:null,description:"Tag for the label, defaults to 'span', can be 'h1', 'h2', etc.",name:"labelTag",required:!1,type:{name:"ElementType"}},description:{defaultValue:null,description:"Description for the radio button group",name:"description",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error message for the radio button group",name:"error",required:!1,type:{name:"string"}},variant:{defaultValue:{value:"default"},description:"Variant of the radio buttons (applied to all), defaults to 'default'",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},sizing:{defaultValue:{value:"fill"},description:"Sizing of the radio buttons (applied to all), defaults to 'fill'",name:"sizing",required:!1,type:{name:"enum",value:[{value:'"hug"'},{value:'"fill"'}]}},asset:{defaultValue:null,description:"Asset of the radio buttons (applied to all), displayed when variant is 'detailed'",name:"asset",required:!1,type:{name:"RadioButtonAssetProps"}},display:{defaultValue:{value:"vertical"},description:"Display style of the radio button group, defaults to 'vertical'",name:"display",required:!1,type:{name:"enum",value:[{value:'"horizontal"'},{value:'"vertical"'}]}},checkedOption:{defaultValue:null,description:"Selected option, required if the group is non-controlled",name:"checkedOption",required:!1,type:{name:"string"}},disabled:{defaultValue:{value:"false"},description:"If the radio button group is disabled, making all options unselectable",name:"disabled",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"Event handler for change",name:"onChange",required:!1,type:{name:"((event: ChangeEvent<HTMLInputElement>) => void)"}},onBlur:{defaultValue:null,description:"Event handler for blur",name:"onBlur",required:!1,type:{name:"((event: FocusEvent<HTMLInputElement, Element>) => void)"}},required:{defaultValue:null,description:"Whether the checkbox is required or not",name:"required",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"Whether the required asterisk is displayed or not",name:"asterisk",required:!1,type:{name:"boolean"}}}}}catch{}const se={title:"@/design-system/RadioButtonGroup",component:T},e=[{label:"Option 1",name:"group1",description:"Description 1",value:"1"},{label:"Option 2",name:"group1",description:"Description 2 that is a little longer...",value:"2"},{label:"Option 3",name:"group1",description:"Description 3",value:"3"}],k={label:"Option 4",name:"group1",description:"Description 4",value:"4",collapsed:a.jsxs("div",{style:{display:"flex",flexDirection:"row",gap:16},children:[a.jsx(C,{name:"subchoice",label:"Sous-label 1",value:"1"}),a.jsx(C,{name:"subchoice",label:"Sous-label 2",value:"2"})]})},s={args:{name:"radio-button-group",label:"Radio Button Group",options:e}},l={args:{name:"radio-button-group",label:"Detailed Radio Button Group",variant:"detailed",options:e}},u={args:{name:"radio-button-group",label:"Detailed Radio Button Group",variant:"detailed",sizing:"hug",options:e}},d={args:{name:"radio-button-group",label:"Horizontal Radio Button Group",variant:"detailed",display:"horizontal",sizing:"fill",options:e}},p={args:{name:"radio-button-group",label:"Hugged Horizontal Radio Button Group",variant:"detailed",display:"horizontal",sizing:"hug",options:e}},c={args:{name:"radio-button-group",label:"Disabled Radio Button Group",disabled:!0,variant:"detailed",options:e}},m={args:{name:"radio-button-group",label:"Radio Button Group with Description",description:"This is a description for the radio button group.",options:e}},g={args:{name:"radio-button-group",label:"Radio Button Group with Heading Tag as Title",labelTag:"h2",options:e}},b={args:{name:"radio-button-group",label:"Radio Button Group with Span Tag as Title",labelTag:"span",options:e}},h={args:{name:"radio-button-group",label:"Radio Button Group with Error",error:"This is an error message.",options:e}},v={args:{name:"radio-button-group",label:"Radio Button Group with Common Tag",variant:"detailed",asset:{variant:"tag",tag:{label:"Tag",variant:M.SUCCESS}},options:e}},f={args:{name:"radio-button-group",label:"Radio Button Group with Common Text",variant:"detailed",asset:{variant:"text",text:"19€"},options:e}},_={args:{name:"radio-button-group",label:"Radio Button Group with Common Icon",variant:"detailed",asset:{variant:"icon",src:U},options:e}},y={args:{name:"radio-button-group",label:"Radio Button Group with Common Image",variant:"detailed",asset:{variant:"image",src:P,size:"s"},options:e}},B={render:()=>{const[t,G]=R.useState(k.value);return a.jsx(T,{name:"radio-button-group",label:"Radio Button Group with Collapsed Option",variant:"detailed",checkedOption:t,onChange:i=>G(i.target.value),options:[...e,k]})}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group',
    options
  }
}`,...s.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    options
  }
}`,...l.parameters?.docs?.source}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    sizing: 'hug',
    options
  }
}`,...u.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'fill',
    options
  }
}`,...d.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Hugged Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'hug',
    options
  }
}`,...p.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Disabled Radio Button Group',
    disabled: true,
    variant: 'detailed',
    options
  }
}`,...c.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Description',
    description: 'This is a description for the radio button group.',
    options
  }
}`,...m.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Heading Tag as Title',
    labelTag: 'h2',
    options
  }
}`,...g.parameters?.docs?.source}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Span Tag as Title',
    labelTag: 'span',
    options
  }
}`,...b.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Error',
    error: 'This is an error message.',
    options
  }
}`,...h.parameters?.docs?.source}}};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
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
}`,...v.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
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
}`,...f.parameters?.docs?.source}}};_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
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
}`,..._.parameters?.docs?.source}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
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
}`,...y.parameters?.docs?.source}}};B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [checkedOption, setCheckedOption] = useState<string>(collapsedOption.value);
    return <RadioButtonGroup name="radio-button-group" label="Radio Button Group with Collapsed Option" variant="detailed" checkedOption={checkedOption} onChange={e => setCheckedOption(e.target.value)} options={[...options, collapsedOption]} />;
  }
}`,...B.parameters?.docs?.source}}};const le=["Default","Detailed","DetailedHugged","FilledHorizontalDisplay","HuggedHorizontalDisplay","Disabled","WithDescription","WithHeadingTagAsTitle","WithSpanTagAsTitle","WithError","WithCommonTag","WithCommonText","WithCommonIcon","WithCommonImage","WithCollapsed"];export{s as Default,l as Detailed,u as DetailedHugged,c as Disabled,d as FilledHorizontalDisplay,p as HuggedHorizontalDisplay,B as WithCollapsed,_ as WithCommonIcon,y as WithCommonImage,v as WithCommonTag,f as WithCommonText,m as WithDescription,h as WithError,g as WithHeadingTagAsTitle,b as WithSpanTagAsTitle,le as __namedExportsOrder,se as default};
