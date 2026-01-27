import{j as t}from"./jsx-runtime-C_uOM0Gm.js";import{V as ot}from"./index-vSssAp4U.js";import{c as k}from"./index-TscbDd2H.js";import{r as st}from"./iframe-CTnXOULQ.js";import{T as it}from"./Tooltip-GJ5PEk5n.js";import{S as H}from"./SvgIcon-CJiY4LCz.js";import{s as lt}from"./stroke-pass-CALgybTM.js";import{L as dt}from"./chunk-EPOLDU6W-u6n6pb5J.js";import{f as ut}from"./iconsList-DgqnJnmb.js";import{f as d}from"./full-next-B_76kGmE.js";import"./preload-helper-PPVm8Dsz.js";import"./full-back-DIKqgBhG.js";import"./full-thumb-up-Bb4kpRpM.js";import"./full-bulb-PM9lEXbZ.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-down-Cmbtr9nI.js";import"./full-download-XQM5pv74.js";import"./full-duplicate-BZV8LNX-.js";import"./full-edit-CxAaM2Fv.js";import"./full-error-BFAmjN4t.js";import"./full-help-blUMxBcv.js";import"./full-show-BUp4jmvL.js";import"./full-info-D24AtBVt.js";import"./full-three-dots-DhyQI2cN.js";import"./full-link-CYVo23DH.js";import"./full-location-CVEaH-Cp.js";import"./full-more-DLJb58kc.js";import"./full-refresh-BZh6W0mB.js";import"./full-right-Dd3YsyCq.js";import"./full-trash-CEfIUI4M.js";import"./full-up-D6TPt2ju.js";import"./full-validate-CbMNulkZ.js";import"./stroke-close-DnlFsd1c.js";import"./stroke-date-CWTXq8J4.js";import"./stroke-price-CbFScctA.js";import"./stroke-error-DSZD431a.js";import"./stroke-picture-VF2OicDu.js";import"./stroke-search-Bph5aoaJ.js";import"./stroke-thing-O6UIROL8.js";import"./stroke-trash-Cc_5v2lW.js";import"./stroke-user-u-f9pznf.js";import"./stroke-video-Cd5kQZzx.js";import"./stroke-wrong-BAouvvNg.js";const ct="_button_1gypz_1",i={button:ct,"btn-default":"_btn-default_1gypz_13","btn-label":"_btn-label_1gypz_19","btn-icon-only":"_btn-icon-only_1gypz_25","btn-tertiary":"_btn-tertiary_1gypz_28","btn-small":"_btn-small_1gypz_31","btn-full-width":"_btn-full-width_1gypz_48","btn-brand":"_btn-brand_1gypz_51","btn-primary":"_btn-primary_1gypz_51","btn-hovered":"_btn-hovered_1gypz_56","btn-disabled":"_btn-disabled_1gypz_56","btn-secondary":"_btn-secondary_1gypz_64","btn-transparent":"_btn-transparent_1gypz_69","btn-icon":"_btn-icon_1gypz_25","btn-neutral":"_btn-neutral_1gypz_101"},D=({icon:n,iconAlt:r,className:s,iconClassName:p})=>t.jsx(H,{src:n,alt:r,className:k(s,p),width:"16"});try{D.displayName="Icon",D.__docgenInfo={description:"",displayName:"Icon",props:{icon:{defaultValue:null,description:"",name:"icon",required:!0,type:{name:"string"}},iconAlt:{defaultValue:null,description:"",name:"iconAlt",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},iconClassName:{defaultValue:null,description:"",name:"iconClassName",required:!1,type:{name:"string"}}}}}catch{}const q={"spinner-icon":"_spinner-icon_su701_1","spinner-svg":"_spinner-svg_su701_9"},pt=()=>t.jsx("div",{className:q["spinner-icon"],"data-testid":"spinner",children:t.jsx(H,{src:lt,alt:"",width:"16",className:q["spinner-svg"],"data-testid":"spinner-svg"})});var a=(n=>(n.PRIMARY="primary",n.SECONDARY="secondary",n.TERTIARY="tertiary",n))(a||{}),u=(n=>(n.LEFT="left",n.RIGHT="right",n))(u||{}),o=(n=>(n.BRAND="brand",n.NEUTRAL="neutral",n))(o||{}),c=(n=>(n.DEFAULT="default",n.SMALL="small",n))(c||{});const mt=(n,r,s)=>n==="button"?"button":r||s?"a":dt,bt=(n,r)=>({disabled:n||r}),vt=(n,r,s)=>({href:r?void 0:n,rel:"noopener noreferrer",target:s?"_blank":void 0,"aria-disabled":r||void 0}),yt=(n,r,s)=>({to:r?"":n,target:s?"_blank":void 0}),ft=(n,r,s,p,m)=>{switch(n){case"button":return bt(s,p);case"a":return vt(r,s,m);default:return yt(r,s,m)}},I=st.forwardRef(({as:n="button",color:r=o.BRAND,variant:s=a.PRIMARY,label:p,disabled:m,hovered:W=!1,isLoading:j,size:$=c.DEFAULT,transparent:G=!1,fullWidth:J=!1,tooltip:V,icon:_,iconAlt:K,iconPosition:P=u.LEFT,iconClassName:Q,opensInNewTab:X=!1,to:Y="",isExternal:C=!1,isSectionLink:z=!1,...Z},tt)=>{const et=k(i.button,i[`btn-${r}`],i[`btn-${s}`],i[`btn-${$}`],{[i["btn-icon-only"]]:_&&!p,[i["btn-hovered"]]:W,[i["btn-disabled"]]:m,[i["btn-loading"]]:j,[i["btn-transparent"]]:G,[i["btn-full-width"]]:J}),nt=z||C||Y.startsWith("/")?Y:`/${Y}`,M=mt(n,C,z),at=ft(M,nt,m,j,X),O=_&&!j&&t.jsx(D,{icon:_,iconAlt:K,className:i["btn-icon"],iconClassName:Q}),rt=t.jsxs(t.Fragment,{children:[P===u.LEFT&&O,j&&t.jsx(pt,{}),p&&t.jsx("span",{className:i["btn-label"],children:p}),P===u.RIGHT&&O]}),U=t.jsx(M,{ref:tt,className:et,...at,...Z,children:rt});return V&&!m?t.jsx(it,{content:V,children:U}):U});I.displayName="Button";try{I.displayName="Button",I.__docgenInfo={description:"",displayName:"Button",props:{color:{defaultValue:{value:"ButtonColor.BRAND"},description:"The color of the button",name:"color",required:!1,type:{name:"enum",value:[{value:'"brand"'},{value:'"neutral"'}]}},variant:{defaultValue:{value:"ButtonVariant.PRIMARY"},description:"The variant of the button",name:"variant",required:!1,type:{name:"enum",value:[{value:'"primary"'},{value:'"secondary"'},{value:'"tertiary"'}]}},label:{defaultValue:null,description:"The label of the button",name:"label",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"If the button is disabled",name:"disabled",required:!1,type:{name:"boolean"}},hovered:{defaultValue:{value:"false"},description:"If the button is hovered",name:"hovered",required:!1,type:{name:"boolean"}},isLoading:{defaultValue:null,description:"If the button is loading",name:"isLoading",required:!1,type:{name:"boolean"}},size:{defaultValue:{value:"ButtonSize.DEFAULT"},description:"The size of the button",name:"size",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"small"'}]}},transparent:{defaultValue:{value:"false"},description:"If the button has a transparent background (principally used with secondary variant)",name:"transparent",required:!1,type:{name:"boolean"}},fullWidth:{defaultValue:{value:"false"},description:"If the button is full width",name:"fullWidth",required:!1,type:{name:"boolean"}},tooltip:{defaultValue:null,description:"The tooltip of the button",name:"tooltip",required:!1,type:{name:"string"}},icon:{defaultValue:null,description:"The icon of the button",name:"icon",required:!1,type:{name:"string"}},iconAlt:{defaultValue:null,description:"The alternative text of the icon",name:"iconAlt",required:!1,type:{name:"string"}},iconPosition:{defaultValue:{value:"IconPositionEnum.LEFT"},description:"The position of the icon",name:"iconPosition",required:!1,type:{name:"enum",value:[{value:'"left"'},{value:'"right"'}]}},iconClassName:{defaultValue:null,description:"The class name of the icon",name:"iconClassName",required:!1,type:{name:"string"}},as:{defaultValue:{value:"button"},description:"The type of component",name:"as",required:!1,type:{name:"enum",value:[{value:'"button"'},{value:'"a"'}]}},to:{defaultValue:{value:""},description:"",name:"to",required:!1,type:{name:"string"}},opensInNewTab:{defaultValue:{value:"false"},description:"",name:"opensInNewTab",required:!1,type:{name:"boolean"}},isExternal:{defaultValue:{value:"false"},description:"",name:"isExternal",required:!1,type:{name:"boolean"}},isSectionLink:{defaultValue:{value:"false"},description:"",name:"isSectionLink",required:!1,type:{name:"boolean"}}}}}catch{}const F={none:null,...Object.fromEntries(ut.map(n=>[n.src.split("/").pop()?.replace(".svg","")||"",n.src]))},le={title:"@/design-system/Button",component:I,decorators:[ot],args:{as:"button",color:o.BRAND,variant:a.PRIMARY,size:c.DEFAULT,label:"",disabled:!1,hovered:!1,isLoading:!1,transparent:!1,fullWidth:!1,tooltip:"",icon:void 0,iconAlt:"",iconPosition:u.LEFT,iconClassName:""},argTypes:{as:{control:"select",options:["button","a"]},size:{control:"select",options:Object.values(c)},variant:{control:"select",options:Object.values(a)},icon:{control:"select",options:Object.keys(F),mapping:F},iconPosition:{control:"select",options:Object.values(u)},color:{control:"select",options:Object.values(o)},disabled:{control:"boolean"},hovered:{control:"boolean"},isLoading:{control:"boolean"},transparent:{control:"boolean"},fullWidth:{control:"boolean"},tooltip:{control:"text"},to:{control:"text",if:{arg:"as",eq:"a"}},opensInNewTab:{control:"boolean",if:{arg:"as",eq:"a"}},isExternal:{control:"boolean",if:{arg:"as",eq:"a"}},isSectionLink:{control:"boolean",if:{arg:"as",eq:"a"}}},parameters:{docs:{description:{component:"Meta object for the Button component."}}}},l={alignItems:"center",display:"flex",flexDirection:"row",gap:"12px"},e=n=>t.jsx(I,{...n}),v={render:n=>t.jsx(e,{...n}),args:{label:"Button Label"}},y={render:()=>t.jsxs("div",{style:l,children:[t.jsx(e,{label:"Primary"}),t.jsx(e,{variant:a.SECONDARY,label:"Secondary"}),t.jsx(e,{variant:a.TERTIARY,label:"Tertiary"})]})},f={render:()=>t.jsxs("div",{style:l,children:[t.jsx(e,{variant:a.PRIMARY,label:"Primary Neutral",color:o.NEUTRAL}),t.jsx(e,{variant:a.SECONDARY,label:"Secondary Neutral",color:o.NEUTRAL}),t.jsx(e,{variant:a.TERTIARY,label:"Tertiary Neutral",color:o.NEUTRAL})]})},R={render:()=>t.jsxs("div",{style:l,children:[t.jsx(e,{size:c.SMALL,label:"Small",variant:a.PRIMARY}),t.jsx(e,{label:"Default",variant:a.PRIMARY})]})},h={render:()=>t.jsxs("div",{style:l,children:[t.jsx(e,{icon:d,iconPosition:u.LEFT,label:"Icon Left"}),t.jsx(e,{icon:d,iconPosition:u.RIGHT,label:"Icon Right"}),t.jsx(e,{icon:d})]})},B={render:()=>t.jsxs("div",{style:l,children:[t.jsx(e,{size:c.SMALL,icon:d,iconPosition:u.LEFT,label:"Icon Left"}),t.jsx(e,{size:c.SMALL,icon:d,iconPosition:u.RIGHT,label:"Icon Right"}),t.jsx(e,{size:c.SMALL,icon:d})]})},T={render:()=>t.jsx("div",{style:{...l,maxWidth:"400px"},children:t.jsx(e,{label:"Full Width",fullWidth:!0})})},x={render:()=>t.jsxs("div",{style:l,children:[t.jsx(e,{label:"Disabled",disabled:!0}),t.jsx(e,{label:"Disabled",variant:a.SECONDARY,disabled:!0}),t.jsx(e,{label:"Disabled",variant:a.TERTIARY,disabled:!0})]})},g={render:()=>t.jsxs("div",{style:l,children:[t.jsx(e,{label:"Loading",isLoading:!0}),t.jsx(e,{label:"Loading",variant:a.SECONDARY,isLoading:!0}),t.jsx(e,{label:"Loading",variant:a.TERTIARY,isLoading:!0}),t.jsx(e,{isLoading:!0,icon:d}),t.jsx(e,{size:c.SMALL,isLoading:!0,icon:d})]})},A={render:()=>t.jsxs("div",{style:l,children:[t.jsx(e,{tooltip:"Tooltip text",icon:d}),t.jsx(e,{tooltip:"Tooltip text",icon:d,disabled:!0})]})},S={render:()=>t.jsxs("div",{style:{...l,backgroundColor:"#F2F2F2",padding:"10px"},children:[t.jsx(e,{label:"Transparent",variant:a.SECONDARY,transparent:!0}),t.jsx(e,{label:"Not Transparent",variant:a.SECONDARY,transparent:!1})]})},E={render:()=>t.jsx("div",{style:l,children:t.jsx(e,{as:"a",to:"https://pass-culture.github.io/pass-culture-main/",label:"Lien externe",isExternal:!0})})},L={render:()=>t.jsx("div",{style:l,children:t.jsx(e,{as:"a",to:"https://pass-culture.github.io/pass-culture-main/",label:"Lien externe avec nouvelle fenêtre",isExternal:!0,opensInNewTab:!0})})},b={display:"flex",flexDirection:"column",gap:"12px",marginBottom:24},w={marginBottom:16},N={render:()=>t.jsxs(t.Fragment,{children:[t.jsxs("div",{children:[t.jsx("h2",{style:w,children:"Brand"}),t.jsxs("div",{style:b,children:[t.jsx(e,{label:"Primary",variant:a.PRIMARY}),t.jsx(e,{label:"Primary Hovered",variant:a.PRIMARY,hovered:!0}),t.jsx(e,{label:"Tertiary Disabled",variant:a.TERTIARY,disabled:!0})]}),t.jsxs("div",{style:b,children:[t.jsx(e,{label:"Secondary",variant:a.SECONDARY}),t.jsx(e,{label:"Secondary Hovered",variant:a.SECONDARY,hovered:!0}),t.jsx(e,{label:"Secondary Disabled",variant:a.SECONDARY,disabled:!0})]}),t.jsxs("div",{style:b,children:[t.jsx(e,{label:"Tertiary",variant:a.TERTIARY}),t.jsx(e,{label:"Tertiary Hovered",variant:a.TERTIARY,hovered:!0}),t.jsx(e,{label:"Primary Disabled",variant:a.PRIMARY,disabled:!0})]})]}),t.jsxs("div",{style:{marginTop:24},children:[t.jsx("h2",{style:w,children:"Neutral"}),t.jsxs("div",{style:b,children:[t.jsx(e,{label:"Primary",variant:a.PRIMARY,color:o.NEUTRAL}),t.jsx(e,{label:"Primary Hovered",variant:a.PRIMARY,color:o.NEUTRAL,hovered:!0}),t.jsx(e,{label:"Primary Disabled",variant:a.PRIMARY,color:o.NEUTRAL,disabled:!0})]}),t.jsxs("div",{style:b,children:[t.jsx(e,{label:"Secondary",variant:a.SECONDARY,color:o.NEUTRAL}),t.jsx(e,{label:"Secondary Hovered",variant:a.SECONDARY,color:o.NEUTRAL,hovered:!0}),t.jsx(e,{label:"Secondary Disabled",variant:a.SECONDARY,color:o.NEUTRAL,disabled:!0})]}),t.jsxs("div",{style:b,children:[t.jsx(e,{label:"Tertiary",variant:a.TERTIARY,color:o.NEUTRAL}),t.jsx(e,{label:"Tertiary Hovered",variant:a.TERTIARY,color:o.NEUTRAL,hovered:!0}),t.jsx(e,{label:"Tertiary Disabled",variant:a.TERTIARY,color:o.NEUTRAL,disabled:!0})]})]})]})};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  render: (args: ButtonProps) => <Button {...args} />,
  args: {
    label: 'Button Label'
  }
}`,...v.parameters?.docs?.source},description:{story:"Story for the default Button component.",...v.parameters?.docs?.description}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Primary" />
      <Button variant={ButtonVariant.SECONDARY} label="Secondary" />
      <Button variant={ButtonVariant.TERTIARY} label="Tertiary" />
    </div>
}`,...y.parameters?.docs?.source},description:{story:"Story for the default button variants.",...y.parameters?.docs?.description}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button variant={ButtonVariant.PRIMARY} label='Primary Neutral' color={ButtonColor.NEUTRAL} />
      <Button variant={ButtonVariant.SECONDARY} label="Secondary Neutral" color={ButtonColor.NEUTRAL} />
      <Button variant={ButtonVariant.TERTIARY} label="Tertiary Neutral" color={ButtonColor.NEUTRAL} />
    </div>
}`,...f.parameters?.docs?.source},description:{story:"Story for the neutral button variants.",...f.parameters?.docs?.description}}};R.parameters={...R.parameters,docs:{...R.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button size={ButtonSize.SMALL} label="Small" variant={ButtonVariant.PRIMARY} />
      <Button label="Default" variant={ButtonVariant.PRIMARY} />
    </div>
}`,...R.parameters?.docs?.source},description:{story:"Story for the button sizes",...R.parameters?.docs?.description}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.LEFT} label="Icon Left" />
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.RIGHT} label="Icon Right" />
      <Button icon={fullNextIcon} />
    </div>
}`,...h.parameters?.docs?.source},description:{story:"Story for the icons with large size",...h.parameters?.docs?.description}}};B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.LEFT} label="Icon Left" />
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.RIGHT} label="Icon Right" />
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} />
    </div>
}`,...B.parameters?.docs?.source},description:{story:"Story for the icons with small size",...B.parameters?.docs?.description}}};T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
  render: () => <div style={{
    ...styles,
    maxWidth: '400px'
  }}>
      <Button label="Full Width" fullWidth />
    </div>
}`,...T.parameters?.docs?.source},description:{story:"Story for the full width button, the button will take the full width of the container (for example, max width 400px)",...T.parameters?.docs?.description}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Disabled" disabled />
      <Button label="Disabled" variant={ButtonVariant.SECONDARY} disabled />
      <Button label="Disabled" variant={ButtonVariant.TERTIARY} disabled />
    </div>
}`,...x.parameters?.docs?.source},description:{story:"Story for the disabled button.",...x.parameters?.docs?.description}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Loading" isLoading />
      <Button label="Loading" variant={ButtonVariant.SECONDARY} isLoading />
      <Button label="Loading" variant={ButtonVariant.TERTIARY} isLoading />
      <Button isLoading icon={fullNextIcon} />
      <Button size={ButtonSize.SMALL} isLoading icon={fullNextIcon} />
    </div>
}`,...g.parameters?.docs?.source},description:{story:"Story for the loading button.",...g.parameters?.docs?.description}}};A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button tooltip="Tooltip text" icon={fullNextIcon} />
      <Button tooltip="Tooltip text" icon={fullNextIcon} disabled />
    </div>
}`,...A.parameters?.docs?.source},description:{story:"Story for the button with a tooltip.",...A.parameters?.docs?.description}}};S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  render: () => <div style={{
    ...styles,
    backgroundColor: '#F2F2F2',
    padding: '10px'
  }}>
      <Button label="Transparent" variant={ButtonVariant.SECONDARY} transparent />
      <Button label="Not Transparent" variant={ButtonVariant.SECONDARY} transparent={false} />
    </div>
}`,...S.parameters?.docs?.source},description:{story:"Story for the transparent button.",...S.parameters?.docs?.description}}};E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button as='a' to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe" isExternal />
    </div>
}`,...E.parameters?.docs?.source},description:{story:"Story for the button with an external link (uses <a> tag)",...E.parameters?.docs?.description}}};L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button as="a" to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe avec nouvelle fenêtre" isExternal opensInNewTab />
    </div>
}`,...L.parameters?.docs?.source},description:{story:"Story for the button with an external link and target _blank",...L.parameters?.docs?.description}}};N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
  render: () => <>
      <div>
      <h2 style={titleStyles}>Brand</h2>
        <div style={columnStyles}>
          <Button label="Primary" variant={ButtonVariant.PRIMARY} />
          <Button label="Primary Hovered" variant={ButtonVariant.PRIMARY} hovered />
          <Button label="Tertiary Disabled" variant={ButtonVariant.TERTIARY} disabled />
        </div>
        <div style={columnStyles}>
          <Button label="Secondary" variant={ButtonVariant.SECONDARY} />
          <Button label="Secondary Hovered" variant={ButtonVariant.SECONDARY} hovered />
          <Button label="Secondary Disabled" variant={ButtonVariant.SECONDARY} disabled />
          
        </div>
        <div style={columnStyles}>
          <Button label="Tertiary" variant={ButtonVariant.TERTIARY} />
          <Button label="Tertiary Hovered" variant={ButtonVariant.TERTIARY} hovered />
          <Button label="Primary Disabled" variant={ButtonVariant.PRIMARY} disabled />
        </div>
      </div>
      <div style={{
      marginTop: 24
    }}>
        <h2 style={titleStyles}>Neutral</h2>
        <div style={columnStyles}>
          <Button label="Primary" variant={ButtonVariant.PRIMARY} color={ButtonColor.NEUTRAL} />
          <Button label="Primary Hovered" variant={ButtonVariant.PRIMARY} color={ButtonColor.NEUTRAL} hovered />
          <Button label="Primary Disabled" variant={ButtonVariant.PRIMARY} color={ButtonColor.NEUTRAL} disabled />
        </div>
        <div style={columnStyles}>
          <Button label="Secondary" variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} />
          <Button label="Secondary Hovered" variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} hovered />
          <Button label="Secondary Disabled" variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} disabled />
        </div>
        <div style={columnStyles}>
          <Button label="Tertiary" variant={ButtonVariant.TERTIARY} color={ButtonColor.NEUTRAL} />
          <Button label="Tertiary Hovered" variant={ButtonVariant.TERTIARY} color={ButtonColor.NEUTRAL} hovered />
          <Button label="Tertiary Disabled" variant={ButtonVariant.TERTIARY} color={ButtonColor.NEUTRAL} disabled />
        </div>
      </div>
    </>
}`,...N.parameters?.docs?.source},description:{story:"Story for all button variants.",...N.parameters?.docs?.description}}};const de=["DefaultButton","DefaultButtonVariants","NeutralButtonVariants","ButtonSizes","ButtonIconsLarge","ButtonIconsSmall","ButtonFullWidth","ButtonDisabled","ButtonLoading","ButtonTooltip","ButtonTransparent","ButtonWithExternalLink","ButtonWithExternalLinkAndTargetBlank","ButtonVariants"];export{x as ButtonDisabled,T as ButtonFullWidth,h as ButtonIconsLarge,B as ButtonIconsSmall,g as ButtonLoading,R as ButtonSizes,A as ButtonTooltip,S as ButtonTransparent,N as ButtonVariants,E as ButtonWithExternalLink,L as ButtonWithExternalLinkAndTargetBlank,v as DefaultButton,y as DefaultButtonVariants,f as NeutralButtonVariants,de as __namedExportsOrder,le as default};
