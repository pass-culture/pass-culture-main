import{a as e,n as t}from"./chunk-DnJy8xQt.js";import{a as n}from"./iframe-D5WGLVdA.js";import{t as r}from"./jsx-runtime-DxP0NviS.js";import{a as i,i as a,n as o,r as s}from"./store-x-Nmz-Pp.js";import{t as c}from"./classnames-DQU-W_eL.js";import{n as l,t as u}from"./SvgIcon-BUaaBCiJ.js";import{n as d,r as f}from"./Tag-C_n82SUN.js";import{n as p}from"./full-error-CNR9tP4R.js";import{n as m,r as h}from"./SnackBar-BQnocbU2.js";import{n as g,r as _,t as v}from"./prod-COOWQFb4.js";import{n as ee,t as y}from"./stroke-date-CNqLdRay.js";import{n as b,t as x}from"./dog-Cq2Neyyf.js";import{n as S,t as C}from"./light.web-l5Xvl1rq.js";import{n as w,t as T}from"./RadioButton-CnlGWCwh.js";var E,te=t((()=>{E=class extends Error{constructor(...e){super(...e),this.name=`FrontendError`}}}));function ne(e,t={}){let{context:n,isSilent:r,userMessage:i}={...D,...t},o=s.getState().user.currentUser?.isImpersonated??null;!r&&i&&s.dispatch(a({description:i,variant:m.ERROR})),_(t=>{t.setContext(`default`,{isUserImpersonated:o}),n&&t.setContext(`custom`,n),g(e)}),console.error(e)}var D,re=t((()=>{v(),i(),o(),h(),D={isSilent:!1,userMessage:`Une erreur est survenue de notre côté. Veuillez réessayer plus tard.`}}));function ie(e,t,n){if(e)return;let r=new E(t);throw ne(r,n),r}var ae=t((()=>{te(),re()})),O,oe=t((()=>{O={"radio-button-group":`_radio-button-group_33h3t_1`,"radio-button-group-legend":`_radio-button-group-legend_33h3t_6`,"radio-button-group-description":`_radio-button-group-description_33h3t_12`,"label-as-text":`_label-as-text_33h3t_20`,"radio-button-group-error":`_radio-button-group-error_33h3t_26`,"radio-button-group-error-icon":`_radio-button-group-error-icon_33h3t_36`,"radio-button-group-options":`_radio-button-group-options_33h3t_43`,"display-horizontal":`_display-horizontal_33h3t_50`,"sizing-fill":`_sizing-fill_33h3t_50`,"radio-button-group-option":`_radio-button-group-option_33h3t_43`,"display-vertical":`_display-vertical_33h3t_54`,"variant-detailed":`_variant-detailed_33h3t_60`}})),k,A,j,M,N=t((()=>{k=e(c(),1),A=e(n(),1),ae(),w(),p(),l(),oe(),j=r(),M=({name:e,label:t,options:n,description:r,error:i,variant:a=`default`,sizing:o=`fill`,display:s=`vertical`,disabled:c=!1,checkedOption:l,asset:d,onChange:f,onBlur:p})=>{let m=(0,A.useId)(),h=(0,A.useId)(),g=`${i?m:``}${r?` ${h}`:``}`,_=typeof t==`string`,v=n.map(e=>e.value);return ie(new Set(v).size===v.length,`RadioButtonGroup options must have unique values.`),(0,j.jsxs)(`fieldset`,{"aria-describedby":g,className:(0,k.default)(O[`radio-button-group`],{[O[`label-as-text`]]:_}),children:[(0,j.jsx)(`legend`,{className:O[`radio-button-group-legend`],children:t}),(0,j.jsxs)(`div`,{className:O[`radio-button-group-header`],children:[r&&(0,j.jsx)(`span`,{id:h,className:O[`radio-button-group-description`],"aria-live":`polite`,children:r}),(0,j.jsx)(`div`,{role:`alert`,id:m,children:i&&(0,j.jsxs)(`span`,{className:O[`radio-button-group-error`],children:[(0,j.jsx)(u,{className:O[`radio-button-group-error-icon`],src:``+new URL(`full-error-BxG7-hWY.svg`,import.meta.url).href,alt:`Erreur`}),i]})})]}),(0,j.jsx)(`div`,{className:(0,k.default)(O[`radio-button-group-options`],O[`display-${s}`],O[`sizing-${o}`],O[`variant-${a}`]),children:n.map(t=>(0,j.jsx)(`div`,{className:O[`radio-button-group-option`],children:(0,j.jsx)(T,{name:e,variant:a,sizing:o,disabled:c,hasError:!!i,onChange:f,onBlur:p,asset:d,...t,...f&&{checked:l===t.value}})},t.value))})]})};try{M.displayName=`RadioButtonGroup`,M.__docgenInfo={description:``,displayName:`RadioButtonGroup`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,methods:[],props:{name:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Name of the radio button group, binding all radio buttons together`,name:`name`,required:!0,tags:{},type:{name:`string`}},label:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Label for the radio button group`,name:`label`,required:!0,tags:{},type:{name:`ReactNode`}},options:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`List of options as radio buttons`,name:`options`,required:!0,tags:{},type:{name:`Omit<RadioButtonProps, "name">[]`}},description:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:``,name:`description`,required:!1,tags:{},type:{name:`string`}},error:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Error message for the radio button group`,name:`error`,required:!1,tags:{},type:{name:`string`}},variant:{defaultValue:{value:`default`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Variant of the radio buttons (applied to all), defaults to 'default'`,name:`variant`,required:!1,tags:{},type:{name:`enum`,raw:`"default" | "detailed"`,value:[{value:`"default"`},{value:`"detailed"`}]}},sizing:{defaultValue:{value:`fill`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Sizing of the radio buttons (applied to all), defaults to 'fill'`,name:`sizing`,required:!1,tags:{},type:{name:`enum`,raw:`RadioButtonSizing`,value:[{value:`"hug"`},{value:`"fill"`}]}},asset:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Asset of the radio buttons (applied to all), displayed when variant is 'detailed'`,name:`asset`,required:!1,tags:{},type:{name:`AssetProps`}},display:{defaultValue:{value:`vertical`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Display style of the radio button group, defaults to 'vertical'`,name:`display`,required:!1,tags:{},type:{name:`enum`,raw:`"horizontal" | "vertical"`,value:[{value:`"horizontal"`},{value:`"vertical"`}]}},checkedOption:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Selected option, required if the group is non-controlled`,name:`checkedOption`,required:!1,tags:{},type:{name:`string`}},disabled:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`If the radio button group is disabled, making all options unselectable`,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Event handler for change`,name:`onChange`,required:!1,tags:{},type:{name:`((event: ChangeEvent<HTMLInputElement, Element>) => void)`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/RadioButtonGroup/RadioButtonGroup.tsx`,name:`TypeLiteral`}],description:`Event handler for blur`,name:`onBlur`,required:!1,tags:{},type:{name:`((event: FocusEvent<HTMLInputElement, Element>) => void)`}}},tags:{}}}catch{}})),P,F,I,L,R,z,B,V,H,U,W,G,K,q,J,Y,X,Z,Q,$;t((()=>{P=e(n(),1),w(),f(),y(),b(),N(),C(),F=r(),I={title:`@/design-system/RadioButtonGroup`,component:M},L=[{label:`Option 1`,name:`group1`,description:`Description 1`,value:`1`},{label:`Option 2`,name:`group1`,description:`Description 2 that is a little longer...`,value:`2`},{label:`Option 3`,name:`group1`,description:`Description 3`,value:`3`}],R={label:`Option 4`,name:`group1`,description:`Description 4`,value:`4`,collapsed:(0,F.jsxs)(`div`,{style:{display:`flex`,flexDirection:`row`,gap:16},children:[(0,F.jsx)(T,{name:`subchoice`,label:`Sous-label 1`,value:`1`}),(0,F.jsx)(T,{name:`subchoice`,label:`Sous-label 2`,value:`2`})]})},z={args:{name:`radio-button-group`,label:`Radio Button Group`,options:L}},B={args:{name:`radio-button-group`,label:`Detailed Radio Button Group`,variant:`detailed`,options:L}},V={args:{name:`radio-button-group`,label:`Detailed Radio Button Group`,variant:`detailed`,sizing:`hug`,options:L}},H={args:{name:`radio-button-group`,label:`Horizontal Radio Button Group`,variant:`detailed`,display:`horizontal`,sizing:`fill`,options:L}},U={args:{name:`radio-button-group`,label:`Hugged Horizontal Radio Button Group`,variant:`detailed`,display:`horizontal`,sizing:`hug`,options:L}},W={args:{name:`radio-button-group`,label:`Disabled Radio Button Group`,disabled:!0,variant:`detailed`,options:L}},G={args:{name:`radio-button-group`,label:`Radio Button Group with Description`,description:`This is a description for the radio button group.`,options:L}},K={args:{name:`radio-button-group`,label:(0,F.jsx)(`h2`,{style:{fontFamily:S.typography.title2.fontFamily,lineHeight:S.typography.title2.lineHeight,fontSize:S.typography.title2.fontSize},children:`Radio Button Group with Heading Tag as Title`}),options:L,description:`This is a description for the radio button group.`}},q={args:{name:`radio-button-group`,label:`Radio Button Group with Error`,error:`This is an error message.`,options:L}},J={args:{name:`radio-button-group`,label:`Radio Button Group with Common Tag`,variant:`detailed`,asset:{variant:`tag`,tag:{label:`Tag`,variant:d.SUCCESS}},options:L}},Y={args:{name:`radio-button-group`,label:`Radio Button Group with Common Text`,variant:`detailed`,asset:{variant:`text`,text:`19€`},options:L}},X={args:{name:`radio-button-group`,label:`Radio Button Group with Common Icon`,variant:`detailed`,asset:{variant:`icon`,src:ee},options:L}},Z={args:{name:`radio-button-group`,label:`Radio Button Group with Common Image`,variant:`detailed`,asset:{variant:`image`,src:x,size:`s`},options:L}},Q={render:()=>{let[e,t]=(0,P.useState)(R.value);return(0,F.jsx)(M,{name:`radio-button-group`,label:`Radio Button Group with Collapsed Option`,variant:`detailed`,checkedOption:e,onChange:e=>t(e.target.value),options:[...L,R]})}},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group',
    options
  }
}`,...z.parameters?.docs?.source}}},B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    options
  }
}`,...B.parameters?.docs?.source}}},V.parameters={...V.parameters,docs:{...V.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    sizing: 'hug',
    options
  }
}`,...V.parameters?.docs?.source}}},H.parameters={...H.parameters,docs:{...H.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'fill',
    options
  }
}`,...H.parameters?.docs?.source}}},U.parameters={...U.parameters,docs:{...U.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Hugged Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'hug',
    options
  }
}`,...U.parameters?.docs?.source}}},W.parameters={...W.parameters,docs:{...W.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Disabled Radio Button Group',
    disabled: true,
    variant: 'detailed',
    options
  }
}`,...W.parameters?.docs?.source}}},G.parameters={...G.parameters,docs:{...G.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Description',
    description: 'This is a description for the radio button group.',
    options
  }
}`,...G.parameters?.docs?.source}}},K.parameters={...K.parameters,docs:{...K.parameters?.docs,source:{originalSource:`{
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
}`,...K.parameters?.docs?.source}}},q.parameters={...q.parameters,docs:{...q.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Error',
    error: 'This is an error message.',
    options
  }
}`,...q.parameters?.docs?.source}}},J.parameters={...J.parameters,docs:{...J.parameters?.docs,source:{originalSource:`{
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
}`,...J.parameters?.docs?.source}}},Y.parameters={...Y.parameters,docs:{...Y.parameters?.docs,source:{originalSource:`{
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
}`,...Y.parameters?.docs?.source}}},X.parameters={...X.parameters,docs:{...X.parameters?.docs,source:{originalSource:`{
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
}`,...X.parameters?.docs?.source}}},Z.parameters={...Z.parameters,docs:{...Z.parameters?.docs,source:{originalSource:`{
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
}`,...Z.parameters?.docs?.source}}},Q.parameters={...Q.parameters,docs:{...Q.parameters?.docs,source:{originalSource:`{
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [checkedOption, setCheckedOption] = useState<string>(collapsedOption.value);
    return <RadioButtonGroup name="radio-button-group" label="Radio Button Group with Collapsed Option" variant="detailed" checkedOption={checkedOption} onChange={e => setCheckedOption(e.target.value)} options={[...options, collapsedOption]} />;
  }
}`,...Q.parameters?.docs?.source}}},$=[`Default`,`Detailed`,`DetailedHugged`,`FilledHorizontalDisplay`,`HuggedHorizontalDisplay`,`Disabled`,`WithDescription`,`WithHeadingTagAsTitle`,`WithError`,`WithCommonTag`,`WithCommonText`,`WithCommonIcon`,`WithCommonImage`,`WithCollapsed`]}))();export{z as Default,B as Detailed,V as DetailedHugged,W as Disabled,H as FilledHorizontalDisplay,U as HuggedHorizontalDisplay,Q as WithCollapsed,X as WithCommonIcon,Z as WithCommonImage,J as WithCommonTag,Y as WithCommonText,G as WithDescription,q as WithError,K as WithHeadingTagAsTitle,$ as __namedExportsOrder,I as default};