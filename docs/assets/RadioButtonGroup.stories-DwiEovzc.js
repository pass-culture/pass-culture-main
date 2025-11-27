import{j as e}from"./jsx-runtime-ClLXs_K9.js";import{r as S}from"./iframe-DJYZD3Zy.js";import{R as z}from"./RadioButton-D0qTVRa8.js";import{a as $}from"./Tag-CfF66_0B.js";import{s as L}from"./stroke-date-CWTXq8J4.js";import{i as A}from"./dog-C0QzEjl8.js";import{c as I}from"./index-CvgiTef4.js";import{f as M}from"./full-error-BFAmjN4t.js";import{S as U}from"./SvgIcon-CZCOIJ-y.js";import{t as x}from"./light.web-BxcFpQrB.js";import"./preload-helper-PPVm8Dsz.js";import"./Asset-D8QBoant.js";import"./full-thumb-up-Bb4kpRpM.js";const o={"radio-button-group":"_radio-button-group_33h3t_1","radio-button-group-legend":"_radio-button-group-legend_33h3t_6","radio-button-group-description":"_radio-button-group-description_33h3t_12","label-as-text":"_label-as-text_33h3t_20","radio-button-group-error":"_radio-button-group-error_33h3t_26","radio-button-group-error-icon":"_radio-button-group-error-icon_33h3t_36","radio-button-group-options":"_radio-button-group-options_33h3t_43","display-horizontal":"_display-horizontal_33h3t_50","sizing-fill":"_sizing-fill_33h3t_50","radio-button-group-option":"_radio-button-group-option_33h3t_43","display-vertical":"_display-vertical_33h3t_54","variant-detailed":"_variant-detailed_33h3t_60"},R=({name:r,label:n,options:i,description:G,error:s,variant:D="default",sizing:C="fill",display:j="vertical",disabled:V=!1,checkedOption:W,asset:k,onChange:T,onBlur:q})=>{const H=S.useId(),w=S.useId(),N=`${s?H:""}${G?` ${w}`:""}`,F=typeof n=="string",E=i.map(t=>t.value);if(new Set(E).size!==E.length)throw new Error("RadioButtonGroup options must have unique values.");return e.jsxs("fieldset",{"aria-describedby":N,className:I(o["radio-button-group"],{[o["label-as-text"]]:F}),children:[e.jsx("legend",{className:o["radio-button-group-legend"],children:n}),e.jsxs("div",{className:o["radio-button-group-header"],children:[G&&e.jsx("span",{id:w,className:o["radio-button-group-description"],"aria-live":"polite",children:G}),e.jsx("div",{role:"alert",id:H,children:s&&e.jsxs("span",{className:o["radio-button-group-error"],children:[e.jsx(U,{className:o["radio-button-group-error-icon"],src:M,alt:"Erreur"}),s]})})]}),e.jsx("div",{className:I(o["radio-button-group-options"],o[`display-${j}`],o[`sizing-${C}`],o[`variant-${D}`]),children:i.map(t=>e.jsx("div",{className:o["radio-button-group-option"],children:e.jsx(z,{...t,name:r,variant:D,sizing:C,disabled:V,hasError:!!s,onChange:T,onBlur:q,asset:k,...T&&{checked:W===t.value}})},t.value))})]})};try{R.displayName="RadioButtonGroup",R.__docgenInfo={description:"",displayName:"RadioButtonGroup",props:{name:{defaultValue:null,description:"Name of the radio button group, binding all radio buttons together",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"Label for the radio button group",name:"label",required:!0,type:{name:"ReactNode"}},options:{defaultValue:null,description:"List of options as radio buttons",name:"options",required:!0,type:{name:'Omit<RadioButtonProps, "name">[]'}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error message for the radio button group",name:"error",required:!1,type:{name:"string"}},variant:{defaultValue:{value:"default"},description:"Variant of the radio buttons (applied to all), defaults to 'default'",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},sizing:{defaultValue:{value:"fill"},description:"Sizing of the radio buttons (applied to all), defaults to 'fill'",name:"sizing",required:!1,type:{name:"enum",value:[{value:'"hug"'},{value:'"fill"'}]}},asset:{defaultValue:null,description:"Asset of the radio buttons (applied to all), displayed when variant is 'detailed'",name:"asset",required:!1,type:{name:"AssetProps"}},display:{defaultValue:{value:"vertical"},description:"Display style of the radio button group, defaults to 'vertical'",name:"display",required:!1,type:{name:"enum",value:[{value:'"horizontal"'},{value:'"vertical"'}]}},checkedOption:{defaultValue:null,description:"Selected option, required if the group is non-controlled",name:"checkedOption",required:!1,type:{name:"string"}},disabled:{defaultValue:{value:"false"},description:"If the radio button group is disabled, making all options unselectable",name:"disabled",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"Event handler for change",name:"onChange",required:!1,type:{name:"((event: ChangeEvent<HTMLInputElement>) => void)"}},onBlur:{defaultValue:null,description:"Event handler for blur",name:"onBlur",required:!1,type:{name:"((event: FocusEvent<HTMLInputElement, Element>) => void)"}}}}}catch{}const ie={title:"@/design-system/RadioButtonGroup",component:R},a=[{label:"Option 1",name:"group1",description:"Description 1",value:"1"},{label:"Option 2",name:"group1",description:"Description 2 that is a little longer...",value:"2"},{label:"Option 3",name:"group1",description:"Description 3",value:"3"}],O={label:"Option 4",name:"group1",description:"Description 4",value:"4",collapsed:e.jsxs("div",{style:{display:"flex",flexDirection:"row",gap:16},children:[e.jsx(z,{name:"subchoice",label:"Sous-label 1",value:"1"}),e.jsx(z,{name:"subchoice",label:"Sous-label 2",value:"2"})]})},l={args:{name:"radio-button-group",label:"Radio Button Group",options:a}},d={args:{name:"radio-button-group",label:"Detailed Radio Button Group",variant:"detailed",options:a}},u={args:{name:"radio-button-group",label:"Detailed Radio Button Group",variant:"detailed",sizing:"hug",options:a}},p={args:{name:"radio-button-group",label:"Horizontal Radio Button Group",variant:"detailed",display:"horizontal",sizing:"fill",options:a}},c={args:{name:"radio-button-group",label:"Hugged Horizontal Radio Button Group",variant:"detailed",display:"horizontal",sizing:"hug",options:a}},m={args:{name:"radio-button-group",label:"Disabled Radio Button Group",disabled:!0,variant:"detailed",options:a}},g={args:{name:"radio-button-group",label:"Radio Button Group with Description",description:"This is a description for the radio button group.",options:a}},h={args:{name:"radio-button-group",label:e.jsx("h2",{style:{fontFamily:x.typography.title2.fontFamily,lineHeight:x.typography.title2.lineHeight,fontSize:x.typography.title2.fontSize},children:"Radio Button Group with Heading Tag as Title"}),options:a,description:"This is a description for the radio button group."}},b={args:{name:"radio-button-group",label:"Radio Button Group with Error",error:"This is an error message.",options:a}},f={args:{name:"radio-button-group",label:"Radio Button Group with Common Tag",variant:"detailed",asset:{variant:"tag",tag:{label:"Tag",variant:$.SUCCESS}},options:a}},v={args:{name:"radio-button-group",label:"Radio Button Group with Common Text",variant:"detailed",asset:{variant:"text",text:"19€"},options:a}},y={args:{name:"radio-button-group",label:"Radio Button Group with Common Icon",variant:"detailed",asset:{variant:"icon",src:L},options:a}},_={args:{name:"radio-button-group",label:"Radio Button Group with Common Image",variant:"detailed",asset:{variant:"image",src:A,size:"s"},options:a}},B={render:()=>{const[r,n]=S.useState(O.value);return e.jsx(R,{name:"radio-button-group",label:"Radio Button Group with Collapsed Option",variant:"detailed",checkedOption:r,onChange:i=>n(i.target.value),options:[...a,O]})}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group',
    options
  }
}`,...l.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    options
  }
}`,...d.parameters?.docs?.source}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    sizing: 'hug',
    options
  }
}`,...u.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'fill',
    options
  }
}`,...p.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Hugged Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'hug',
    options
  }
}`,...c.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Disabled Radio Button Group',
    disabled: true,
    variant: 'detailed',
    options
  }
}`,...m.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Description',
    description: 'This is a description for the radio button group.',
    options
  }
}`,...g.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
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
}`,...h.parameters?.docs?.source}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Error',
    error: 'This is an error message.',
    options
  }
}`,...b.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
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
}`,...f.parameters?.docs?.source}}};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
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
}`,...v.parameters?.docs?.source}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
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
}`,...y.parameters?.docs?.source}}};_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
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
}`,..._.parameters?.docs?.source}}};B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [checkedOption, setCheckedOption] = useState<string>(collapsedOption.value);
    return <RadioButtonGroup name="radio-button-group" label="Radio Button Group with Collapsed Option" variant="detailed" checkedOption={checkedOption} onChange={e => setCheckedOption(e.target.value)} options={[...options, collapsedOption]} />;
  }
}`,...B.parameters?.docs?.source}}};const se=["Default","Detailed","DetailedHugged","FilledHorizontalDisplay","HuggedHorizontalDisplay","Disabled","WithDescription","WithHeadingTagAsTitle","WithError","WithCommonTag","WithCommonText","WithCommonIcon","WithCommonImage","WithCollapsed"];export{l as Default,d as Detailed,u as DetailedHugged,m as Disabled,p as FilledHorizontalDisplay,c as HuggedHorizontalDisplay,B as WithCollapsed,y as WithCommonIcon,_ as WithCommonImage,f as WithCommonTag,v as WithCommonText,g as WithDescription,b as WithError,h as WithHeadingTagAsTitle,se as __namedExportsOrder,ie as default};
