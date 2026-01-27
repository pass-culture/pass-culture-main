import{j as e}from"./jsx-runtime-C_uOM0Gm.js";import{r as D}from"./iframe-CTnXOULQ.js";import{R as C}from"./RadioButton-B-UIjsZf.js";import{a as L}from"./Tag-CZrfY-rG.js";import{s as $}from"./stroke-date-CWTXq8J4.js";import{i as A}from"./dog-C0QzEjl8.js";import{c as w}from"./index-TscbDd2H.js";import{r as U,a as M}from"./store-DbzJj_LB.js";import{S as P}from"./SnackBar-DSFSWWuB.js";import{w as J,c as K}from"./exports-XRHBct3C.js";import{f as Q}from"./full-error-BFAmjN4t.js";import{S as X}from"./SvgIcon-CJiY4LCz.js";import{t as z}from"./light.web-BxcFpQrB.js";import"./preload-helper-PPVm8Dsz.js";import"./Asset-DEO5YOFe.js";import"./full-thumb-up-Bb4kpRpM.js";import"./date-CrU56jqV.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-validate-CbMNulkZ.js";import"./useMediaQuery-DeNVqfPX.js";class Y extends Error{constructor(){super(...arguments),this.name="FrontendError"}}const Z={isSilent:!1,userMessage:"Une erreur est survenue de notre côté. Veuillez réessayer plus tard."};function ee(a,i={}){const{context:r,extras:n,isSilent:s,userMessage:l}={...Z,...i};!s&&typeof l=="string"&&U.dispatch(M({description:l,variant:P.ERROR})),J(d=>{r&&d.setContext("context",r),n&&d.setExtras(n),K(a)}),console.error(a)}function te(a,i,r){if(a)return;const n=new Y(i);throw ee(n,r),n}const o={"radio-button-group":"_radio-button-group_33h3t_1","radio-button-group-legend":"_radio-button-group-legend_33h3t_6","radio-button-group-description":"_radio-button-group-description_33h3t_12","label-as-text":"_label-as-text_33h3t_20","radio-button-group-error":"_radio-button-group-error_33h3t_26","radio-button-group-error-icon":"_radio-button-group-error-icon_33h3t_36","radio-button-group-options":"_radio-button-group-options_33h3t_43","display-horizontal":"_display-horizontal_33h3t_50","sizing-fill":"_sizing-fill_33h3t_50","radio-button-group-option":"_radio-button-group-option_33h3t_43","display-vertical":"_display-vertical_33h3t_54","variant-detailed":"_variant-detailed_33h3t_60"},G=({name:a,label:i,options:r,description:n,error:s,variant:l="default",sizing:d="fill",display:V="vertical",disabled:j=!1,checkedOption:k,asset:W,onChange:T,onBlur:q})=>{const E=D.useId(),H=D.useId(),N=`${s?E:""}${n?` ${H}`:""}`,F=typeof i=="string",O=r.map(u=>u.value);return te(new Set(O).size===O.length,"RadioButtonGroup options must have unique values."),e.jsxs("fieldset",{"aria-describedby":N,className:w(o["radio-button-group"],{[o["label-as-text"]]:F}),children:[e.jsx("legend",{className:o["radio-button-group-legend"],children:i}),e.jsxs("div",{className:o["radio-button-group-header"],children:[n&&e.jsx("span",{id:H,className:o["radio-button-group-description"],"aria-live":"polite",children:n}),e.jsx("div",{role:"alert",id:E,children:s&&e.jsxs("span",{className:o["radio-button-group-error"],children:[e.jsx(X,{className:o["radio-button-group-error-icon"],src:Q,alt:"Erreur"}),s]})})]}),e.jsx("div",{className:w(o["radio-button-group-options"],o[`display-${V}`],o[`sizing-${d}`],o[`variant-${l}`]),children:r.map(u=>e.jsx("div",{className:o["radio-button-group-option"],children:e.jsx(C,{...u,name:a,variant:l,sizing:d,disabled:j,hasError:!!s,onChange:T,onBlur:q,asset:W,...T&&{checked:k===u.value}})},u.value))})]})};try{G.displayName="RadioButtonGroup",G.__docgenInfo={description:"",displayName:"RadioButtonGroup",props:{name:{defaultValue:null,description:"Name of the radio button group, binding all radio buttons together",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"Label for the radio button group",name:"label",required:!0,type:{name:"ReactNode"}},options:{defaultValue:null,description:"List of options as radio buttons",name:"options",required:!0,type:{name:'Omit<RadioButtonProps, "name">[]'}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error message for the radio button group",name:"error",required:!1,type:{name:"string"}},variant:{defaultValue:{value:"default"},description:"Variant of the radio buttons (applied to all), defaults to 'default'",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},sizing:{defaultValue:{value:"fill"},description:"Sizing of the radio buttons (applied to all), defaults to 'fill'",name:"sizing",required:!1,type:{name:"enum",value:[{value:'"hug"'},{value:'"fill"'}]}},asset:{defaultValue:null,description:"Asset of the radio buttons (applied to all), displayed when variant is 'detailed'",name:"asset",required:!1,type:{name:"AssetProps"}},display:{defaultValue:{value:"vertical"},description:"Display style of the radio button group, defaults to 'vertical'",name:"display",required:!1,type:{name:"enum",value:[{value:'"horizontal"'},{value:'"vertical"'}]}},checkedOption:{defaultValue:null,description:"Selected option, required if the group is non-controlled",name:"checkedOption",required:!1,type:{name:"string"}},disabled:{defaultValue:{value:"false"},description:"If the radio button group is disabled, making all options unselectable",name:"disabled",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"Event handler for change",name:"onChange",required:!1,type:{name:"((event: ChangeEvent<HTMLInputElement>) => void)"}},onBlur:{defaultValue:null,description:"Event handler for blur",name:"onBlur",required:!1,type:{name:"((event: FocusEvent<HTMLInputElement, Element>) => void)"}}}}}catch{}const Be={title:"@/design-system/RadioButtonGroup",component:G},t=[{label:"Option 1",name:"group1",description:"Description 1",value:"1"},{label:"Option 2",name:"group1",description:"Description 2 that is a little longer...",value:"2"},{label:"Option 3",name:"group1",description:"Description 3",value:"3"}],I={label:"Option 4",name:"group1",description:"Description 4",value:"4",collapsed:e.jsxs("div",{style:{display:"flex",flexDirection:"row",gap:16},children:[e.jsx(C,{name:"subchoice",label:"Sous-label 1",value:"1"}),e.jsx(C,{name:"subchoice",label:"Sous-label 2",value:"2"})]})},p={args:{name:"radio-button-group",label:"Radio Button Group",options:t}},c={args:{name:"radio-button-group",label:"Detailed Radio Button Group",variant:"detailed",options:t}},m={args:{name:"radio-button-group",label:"Detailed Radio Button Group",variant:"detailed",sizing:"hug",options:t}},g={args:{name:"radio-button-group",label:"Horizontal Radio Button Group",variant:"detailed",display:"horizontal",sizing:"fill",options:t}},h={args:{name:"radio-button-group",label:"Hugged Horizontal Radio Button Group",variant:"detailed",display:"horizontal",sizing:"hug",options:t}},b={args:{name:"radio-button-group",label:"Disabled Radio Button Group",disabled:!0,variant:"detailed",options:t}},f={args:{name:"radio-button-group",label:"Radio Button Group with Description",description:"This is a description for the radio button group.",options:t}},v={args:{name:"radio-button-group",label:e.jsx("h2",{style:{fontFamily:z.typography.title2.fontFamily,lineHeight:z.typography.title2.lineHeight,fontSize:z.typography.title2.fontSize},children:"Radio Button Group with Heading Tag as Title"}),options:t,description:"This is a description for the radio button group."}},y={args:{name:"radio-button-group",label:"Radio Button Group with Error",error:"This is an error message.",options:t}},_={args:{name:"radio-button-group",label:"Radio Button Group with Common Tag",variant:"detailed",asset:{variant:"tag",tag:{label:"Tag",variant:L.SUCCESS}},options:t}},R={args:{name:"radio-button-group",label:"Radio Button Group with Common Text",variant:"detailed",asset:{variant:"text",text:"19€"},options:t}},x={args:{name:"radio-button-group",label:"Radio Button Group with Common Icon",variant:"detailed",asset:{variant:"icon",src:$},options:t}},B={args:{name:"radio-button-group",label:"Radio Button Group with Common Image",variant:"detailed",asset:{variant:"image",src:A,size:"s"},options:t}},S={render:()=>{const[a,i]=D.useState(I.value);return e.jsx(G,{name:"radio-button-group",label:"Radio Button Group with Collapsed Option",variant:"detailed",checkedOption:a,onChange:r=>i(r.target.value),options:[...t,I]})}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group',
    options
  }
}`,...p.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    options
  }
}`,...c.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    sizing: 'hug',
    options
  }
}`,...m.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'fill',
    options
  }
}`,...g.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Hugged Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'hug',
    options
  }
}`,...h.parameters?.docs?.source}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Disabled Radio Button Group',
    disabled: true,
    variant: 'detailed',
    options
  }
}`,...b.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Description',
    description: 'This is a description for the radio button group.',
    options
  }
}`,...f.parameters?.docs?.source}}};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
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
}`,...v.parameters?.docs?.source}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Error',
    error: 'This is an error message.',
    options
  }
}`,...y.parameters?.docs?.source}}};_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
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
}`,..._.parameters?.docs?.source}}};R.parameters={...R.parameters,docs:{...R.parameters?.docs,source:{originalSource:`{
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
}`,...R.parameters?.docs?.source}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
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
}`,...x.parameters?.docs?.source}}};B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
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
}`,...B.parameters?.docs?.source}}};S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [checkedOption, setCheckedOption] = useState<string>(collapsedOption.value);
    return <RadioButtonGroup name="radio-button-group" label="Radio Button Group with Collapsed Option" variant="detailed" checkedOption={checkedOption} onChange={e => setCheckedOption(e.target.value)} options={[...options, collapsedOption]} />;
  }
}`,...S.parameters?.docs?.source}}};const Se=["Default","Detailed","DetailedHugged","FilledHorizontalDisplay","HuggedHorizontalDisplay","Disabled","WithDescription","WithHeadingTagAsTitle","WithError","WithCommonTag","WithCommonText","WithCommonIcon","WithCommonImage","WithCollapsed"];export{p as Default,c as Detailed,m as DetailedHugged,b as Disabled,g as FilledHorizontalDisplay,h as HuggedHorizontalDisplay,S as WithCollapsed,x as WithCommonIcon,B as WithCommonImage,_ as WithCommonTag,R as WithCommonText,f as WithDescription,y as WithError,v as WithHeadingTagAsTitle,Se as __namedExportsOrder,Be as default};
