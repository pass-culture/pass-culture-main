import{j as t}from"./jsx-runtime-BWUBZ1mK.js";import{V as st}from"./index-BmElJbZE.js";import{c as W}from"./index-DddOqnhX.js";import{r as lt}from"./iframe-BCi_b9Dw.js";import{T as ut}from"./Tooltip-3iLB8djW.js";import{S as $}from"./SvgIcon-QszmaC-j.js";import{s as dt}from"./stroke-pass-CALgybTM.js";import{L as ct}from"./chunk-EPOLDU6W-DML6Xnxi.js";import{f as pt}from"./iconsList-BuldLOnt.js";import{f as c}from"./full-next-B_76kGmE.js";import"./preload-helper-PPVm8Dsz.js";import"./full-back-DIKqgBhG.js";import"./full-thumb-up-Bb4kpRpM.js";import"./full-bulb-PM9lEXbZ.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-down-Cmbtr9nI.js";import"./full-download-XQM5pv74.js";import"./full-duplicate-BZV8LNX-.js";import"./full-edit-CxAaM2Fv.js";import"./full-error-BFAmjN4t.js";import"./full-help-blUMxBcv.js";import"./full-show-DR1VeCnl.js";import"./full-info-D24AtBVt.js";import"./full-three-dots-DhyQI2cN.js";import"./full-link-CYVo23DH.js";import"./full-location-CVEaH-Cp.js";import"./full-more-DLJb58kc.js";import"./full-refresh-BZh6W0mB.js";import"./full-right-Dd3YsyCq.js";import"./full-trash-CEfIUI4M.js";import"./full-up-D6TPt2ju.js";import"./full-validate-CbMNulkZ.js";import"./stroke-close-DnlFsd1c.js";import"./stroke-date-CWTXq8J4.js";import"./stroke-price-CbFScctA.js";import"./stroke-error-DSZD431a.js";import"./stroke-picture-VF2OicDu.js";import"./stroke-search-Bph5aoaJ.js";import"./stroke-thing-O6UIROL8.js";import"./stroke-trash-Cc_5v2lW.js";import"./stroke-user-u-f9pznf.js";import"./stroke-valid-CzTQYCoV.js";import"./stroke-video-Cd5kQZzx.js";import"./stroke-wrong-BAouvvNg.js";const mt="_button_15lut_1",u={button:mt,"btn-default":"_btn-default_15lut_13","btn-label":"_btn-label_15lut_19","btn-icon-only":"_btn-icon-only_15lut_25","btn-tertiary":"_btn-tertiary_15lut_28","btn-small":"_btn-small_15lut_31","btn-full-width":"_btn-full-width_15lut_48","btn-brand":"_btn-brand_15lut_51","btn-primary":"_btn-primary_15lut_51","btn-hovered":"_btn-hovered_15lut_56","btn-disabled":"_btn-disabled_15lut_56","btn-secondary":"_btn-secondary_15lut_64","btn-transparent":"_btn-transparent_15lut_69","btn-icon":"_btn-icon_15lut_25","btn-neutral":"_btn-neutral_15lut_101"};var a=(n=>(n.PRIMARY="primary",n.SECONDARY="secondary",n.TERTIARY="tertiary",n))(a||{}),r=(n=>(n.LEFT="left",n.RIGHT="right",n.CENTER="center",n))(r||{}),i=(n=>(n.BRAND="brand",n.NEUTRAL="neutral",n))(i||{}),l=(n=>(n.DEFAULT="default",n.SMALL="small",n))(l||{});const G={[l.DEFAULT]:"16",[l.SMALL]:"14"},V=({icon:n,iconAlt:o,className:s,iconClassName:m,size:p=l.DEFAULT})=>t.jsx($,{src:n,alt:o,className:W(s,m),width:G[p]});try{V.displayName="Icon",V.__docgenInfo={description:"",displayName:"Icon",props:{icon:{defaultValue:null,description:"",name:"icon",required:!0,type:{name:"string"}},iconAlt:{defaultValue:null,description:"",name:"iconAlt",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},iconClassName:{defaultValue:null,description:"",name:"iconClassName",required:!1,type:{name:"string"}},size:{defaultValue:{value:"ButtonSize.DEFAULT"},description:"",name:"size",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"small"'}]}}}}}catch{}const w={"spinner-icon":"_spinner-icon_su701_1","spinner-svg":"_spinner-svg_su701_9"},M=({size:n=l.DEFAULT})=>t.jsx("div",{className:w["spinner-icon"],"data-testid":"spinner",children:t.jsx($,{src:dt,alt:"",width:G[n],className:w["spinner-svg"],"data-testid":"spinner-svg"})});try{M.displayName="Spinner",M.__docgenInfo={description:"",displayName:"Spinner",props:{size:{defaultValue:{value:"ButtonSize.DEFAULT"},description:"",name:"size",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"small"'}]}}}}}catch{}const bt=(n,o,s)=>n==="button"?"button":o||s?"a":ct,vt=(n,o)=>({disabled:n||o}),yt=(n,o,s)=>({href:o?void 0:n,rel:"noopener noreferrer",target:s?"_blank":void 0,"aria-disabled":o||void 0}),ft=(n,o,s)=>({to:o?"":n,target:s?"_blank":void 0}),Rt=(n,o,s,m,p)=>{switch(n){case"button":return vt(s,m);case"a":return yt(o,s,p);default:return ft(o,s,p)}},I=lt.forwardRef(({as:n="button",color:o=i.BRAND,variant:s=a.PRIMARY,label:m,disabled:p,hovered:J=!1,isLoading:j,size:P=l.DEFAULT,transparent:K=!1,fullWidth:Q=!1,tooltip:O,icon:Y,iconAlt:X,iconPosition:_=r.LEFT,iconClassName:Z,opensInNewTab:tt=!1,to:D="",isExternal:U=!1,isSectionLink:F=!1,...et},nt)=>{const at=W(u.button,u[`btn-${o}`],u[`btn-${s}`],u[`btn-${P}`],{[u["btn-icon-only"]]:Y&&_===r.CENTER,[u["btn-hovered"]]:J,[u["btn-disabled"]]:p,[u["btn-loading"]]:j,[u["btn-transparent"]]:K,[u["btn-full-width"]]:Q}),rt=F||U||D.startsWith("/")?D:`/${D}`,q=bt(n,U,F),ot=Rt(q,rt,p,j,tt),C=Y&&!j&&t.jsx(V,{icon:Y,iconAlt:X,className:u["btn-icon"],iconClassName:Z,size:P}),it=t.jsxs(t.Fragment,{children:[_===r.LEFT&&C,j&&t.jsx(M,{size:P}),m&&t.jsx("span",{className:u["btn-label"],children:m}),_===r.RIGHT&&C,_===r.CENTER&&!m&&C]}),z=t.jsx(q,{ref:nt,className:at,...ot,...et,children:it});return O&&!p?t.jsx(ut,{content:O,children:z}):z});I.displayName="Button";try{I.displayName="Button",I.__docgenInfo={description:"",displayName:"Button",props:{color:{defaultValue:{value:"ButtonColor.BRAND"},description:"The color of the button",name:"color",required:!1,type:{name:"enum",value:[{value:'"brand"'},{value:'"neutral"'}]}},variant:{defaultValue:{value:"ButtonVariant.PRIMARY"},description:"The variant of the button",name:"variant",required:!1,type:{name:"enum",value:[{value:'"primary"'},{value:'"secondary"'},{value:'"tertiary"'}]}},label:{defaultValue:null,description:"The label of the button",name:"label",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"If the button is disabled",name:"disabled",required:!1,type:{name:"boolean"}},hovered:{defaultValue:{value:"false"},description:"If the button is hovered",name:"hovered",required:!1,type:{name:"boolean"}},isLoading:{defaultValue:null,description:"If the button is loading",name:"isLoading",required:!1,type:{name:"boolean"}},size:{defaultValue:{value:"ButtonSize.DEFAULT"},description:"The size of the button",name:"size",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"small"'}]}},transparent:{defaultValue:{value:"false"},description:"If the button has a transparent background (principally used with secondary variant)",name:"transparent",required:!1,type:{name:"boolean"}},fullWidth:{defaultValue:{value:"false"},description:"If the button is full width",name:"fullWidth",required:!1,type:{name:"boolean"}},tooltip:{defaultValue:null,description:"The tooltip of the button",name:"tooltip",required:!1,type:{name:"string"}},icon:{defaultValue:null,description:"The icon of the button",name:"icon",required:!1,type:{name:"string"}},iconAlt:{defaultValue:null,description:"The alternative text of the icon",name:"iconAlt",required:!1,type:{name:"string"}},iconPosition:{defaultValue:{value:"IconPositionEnum.LEFT"},description:"The position of the icon",name:"iconPosition",required:!1,type:{name:"enum",value:[{value:'"left"'},{value:'"right"'},{value:'"center"'}]}},iconClassName:{defaultValue:null,description:"The class name of the icon",name:"iconClassName",required:!1,type:{name:"string"}},as:{defaultValue:{value:"button"},description:"The type of component",name:"as",required:!1,type:{name:"enum",value:[{value:'"button"'},{value:'"a"'}]}},to:{defaultValue:{value:""},description:"",name:"to",required:!1,type:{name:"string"}},opensInNewTab:{defaultValue:{value:"false"},description:"",name:"opensInNewTab",required:!1,type:{name:"boolean"}},isExternal:{defaultValue:{value:"false"},description:"",name:"isExternal",required:!1,type:{name:"boolean"}},isSectionLink:{defaultValue:{value:"false"},description:"",name:"isSectionLink",required:!1,type:{name:"boolean"}}}}}catch{}const k={none:null,...Object.fromEntries(pt.map(n=>[n.src.split("/").pop()?.replace(".svg","")||"",n.src]))},de={title:"@/design-system/Button",component:I,decorators:[st],args:{as:"button",color:i.BRAND,variant:a.PRIMARY,size:l.DEFAULT,label:"",disabled:!1,hovered:!1,isLoading:!1,transparent:!1,fullWidth:!1,tooltip:"",icon:void 0,iconAlt:"",iconPosition:r.LEFT,iconClassName:""},argTypes:{as:{control:"select",options:["button","a"]},size:{control:"select",options:Object.values(l)},variant:{control:"select",options:Object.values(a)},icon:{control:"select",options:Object.keys(k),mapping:k},iconPosition:{control:"select",options:Object.values(r)},color:{control:"select",options:Object.values(i)},disabled:{control:"boolean"},hovered:{control:"boolean"},isLoading:{control:"boolean"},transparent:{control:"boolean"},fullWidth:{control:"boolean"},tooltip:{control:"text"},to:{control:"text",if:{arg:"as",eq:"a"}},opensInNewTab:{control:"boolean",if:{arg:"as",eq:"a"}},isExternal:{control:"boolean",if:{arg:"as",eq:"a"}},isSectionLink:{control:"boolean",if:{arg:"as",eq:"a"}}},parameters:{docs:{description:{component:"Meta object for the Button component."}}}},d={alignItems:"center",display:"flex",flexDirection:"row",gap:"12px"},e=n=>t.jsx(I,{...n}),v={render:n=>t.jsx(e,{...n}),args:{label:"Button Label"}},y={render:()=>t.jsxs("div",{style:d,children:[t.jsx(e,{label:"Primary"}),t.jsx(e,{variant:a.SECONDARY,label:"Secondary"}),t.jsx(e,{variant:a.TERTIARY,label:"Tertiary"})]})},f={render:()=>t.jsxs("div",{style:d,children:[t.jsx(e,{variant:a.PRIMARY,label:"Primary Neutral",color:i.NEUTRAL}),t.jsx(e,{variant:a.SECONDARY,label:"Secondary Neutral",color:i.NEUTRAL}),t.jsx(e,{variant:a.TERTIARY,label:"Tertiary Neutral",color:i.NEUTRAL})]})},R={render:()=>t.jsxs("div",{style:d,children:[t.jsx(e,{size:l.SMALL,label:"Small",variant:a.PRIMARY}),t.jsx(e,{label:"Default",variant:a.PRIMARY})]})},T={render:()=>t.jsxs("div",{style:d,children:[t.jsx(e,{icon:c,iconPosition:r.LEFT,label:"Icon Left"}),t.jsx(e,{icon:c,iconPosition:r.RIGHT,label:"Icon Right"}),t.jsx(e,{icon:c,iconPosition:r.CENTER})]})},h={render:()=>t.jsxs("div",{style:d,children:[t.jsx(e,{size:l.SMALL,icon:c,iconPosition:r.LEFT,label:"Icon Left"}),t.jsx(e,{size:l.SMALL,icon:c,iconPosition:r.RIGHT,label:"Icon Right"}),t.jsx(e,{size:l.SMALL,icon:c,iconPosition:r.CENTER})]})},B={render:()=>t.jsx("div",{style:{...d,maxWidth:"400px"},children:t.jsx(e,{label:"Full Width",fullWidth:!0})})},E={render:()=>t.jsxs("div",{style:d,children:[t.jsx(e,{label:"Disabled",disabled:!0}),t.jsx(e,{label:"Disabled",variant:a.SECONDARY,disabled:!0}),t.jsx(e,{label:"Disabled",variant:a.TERTIARY,disabled:!0})]})},x={render:()=>t.jsxs("div",{style:d,children:[t.jsx(e,{label:"Loading",isLoading:!0}),t.jsx(e,{label:"Loading",variant:a.SECONDARY,isLoading:!0}),t.jsx(e,{label:"Loading",variant:a.TERTIARY,isLoading:!0}),t.jsx(e,{isLoading:!0,icon:c,iconPosition:r.CENTER}),t.jsx(e,{size:l.SMALL,isLoading:!0,icon:c,iconPosition:r.CENTER})]})},A={render:()=>t.jsxs("div",{style:d,children:[t.jsx(e,{tooltip:"Tooltip text",icon:c,iconPosition:r.CENTER}),t.jsx(e,{tooltip:"Tooltip text",icon:c,iconPosition:r.CENTER,disabled:!0})]})},N={render:()=>t.jsxs("div",{style:{...d,backgroundColor:"#F2F2F2",padding:"10px"},children:[t.jsx(e,{label:"Transparent",variant:a.SECONDARY,transparent:!0}),t.jsx(e,{label:"Not Transparent",variant:a.SECONDARY,transparent:!1})]})},S={render:()=>t.jsx("div",{style:d,children:t.jsx(e,{as:"a",to:"https://pass-culture.github.io/pass-culture-main/",label:"Lien externe",isExternal:!0})})},g={render:()=>t.jsx("div",{style:d,children:t.jsx(e,{as:"a",to:"https://pass-culture.github.io/pass-culture-main/",label:"Lien externe avec nouvelle fenêtre",isExternal:!0,opensInNewTab:!0})})},b={display:"flex",flexDirection:"column",gap:"12px",marginBottom:24},H={marginBottom:16},L={render:()=>t.jsxs(t.Fragment,{children:[t.jsxs("div",{children:[t.jsx("h2",{style:H,children:"Brand"}),t.jsxs("div",{style:b,children:[t.jsx(e,{label:"Primary",variant:a.PRIMARY}),t.jsx(e,{label:"Primary Hovered",variant:a.PRIMARY,hovered:!0}),t.jsx(e,{label:"Tertiary Disabled",variant:a.TERTIARY,disabled:!0})]}),t.jsxs("div",{style:b,children:[t.jsx(e,{label:"Secondary",variant:a.SECONDARY}),t.jsx(e,{label:"Secondary Hovered",variant:a.SECONDARY,hovered:!0}),t.jsx(e,{label:"Secondary Disabled",variant:a.SECONDARY,disabled:!0})]}),t.jsxs("div",{style:b,children:[t.jsx(e,{label:"Tertiary",variant:a.TERTIARY}),t.jsx(e,{label:"Tertiary Hovered",variant:a.TERTIARY,hovered:!0}),t.jsx(e,{label:"Primary Disabled",variant:a.PRIMARY,disabled:!0})]})]}),t.jsxs("div",{style:{marginTop:24},children:[t.jsx("h2",{style:H,children:"Neutral"}),t.jsxs("div",{style:b,children:[t.jsx(e,{label:"Primary",variant:a.PRIMARY,color:i.NEUTRAL}),t.jsx(e,{label:"Primary Hovered",variant:a.PRIMARY,color:i.NEUTRAL,hovered:!0}),t.jsx(e,{label:"Primary Disabled",variant:a.PRIMARY,color:i.NEUTRAL,disabled:!0})]}),t.jsxs("div",{style:b,children:[t.jsx(e,{label:"Secondary",variant:a.SECONDARY,color:i.NEUTRAL}),t.jsx(e,{label:"Secondary Hovered",variant:a.SECONDARY,color:i.NEUTRAL,hovered:!0}),t.jsx(e,{label:"Secondary Disabled",variant:a.SECONDARY,color:i.NEUTRAL,disabled:!0})]}),t.jsxs("div",{style:b,children:[t.jsx(e,{label:"Tertiary",variant:a.TERTIARY,color:i.NEUTRAL}),t.jsx(e,{label:"Tertiary Hovered",variant:a.TERTIARY,color:i.NEUTRAL,hovered:!0}),t.jsx(e,{label:"Tertiary Disabled",variant:a.TERTIARY,color:i.NEUTRAL,disabled:!0})]})]})]})};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
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
}`,...R.parameters?.docs?.source},description:{story:"Story for the button sizes",...R.parameters?.docs?.description}}};T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.LEFT} label="Icon Left" />
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.RIGHT} label="Icon Right" />
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} />
    </div>
}`,...T.parameters?.docs?.source},description:{story:"Story for the icons with large size",...T.parameters?.docs?.description}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.LEFT} label="Icon Left" />
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.RIGHT} label="Icon Right" />
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} />
    </div>
}`,...h.parameters?.docs?.source},description:{story:"Story for the icons with small size",...h.parameters?.docs?.description}}};B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  render: () => <div style={{
    ...styles,
    maxWidth: '400px'
  }}>
      <Button label="Full Width" fullWidth />
    </div>
}`,...B.parameters?.docs?.source},description:{story:"Story for the full width button, the button will take the full width of the container (for example, max width 400px)",...B.parameters?.docs?.description}}};E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Disabled" disabled />
      <Button label="Disabled" variant={ButtonVariant.SECONDARY} disabled />
      <Button label="Disabled" variant={ButtonVariant.TERTIARY} disabled />
    </div>
}`,...E.parameters?.docs?.source},description:{story:"Story for the disabled button.",...E.parameters?.docs?.description}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Loading" isLoading />
      <Button label="Loading" variant={ButtonVariant.SECONDARY} isLoading />
      <Button label="Loading" variant={ButtonVariant.TERTIARY} isLoading />
      <Button isLoading icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} />
      <Button size={ButtonSize.SMALL} isLoading icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} />
    </div>
}`,...x.parameters?.docs?.source},description:{story:"Story for the loading button.",...x.parameters?.docs?.description}}};A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button tooltip="Tooltip text" icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} />
      <Button tooltip="Tooltip text" icon={fullNextIcon} iconPosition={IconPositionEnum.CENTER} disabled />
    </div>
}`,...A.parameters?.docs?.source},description:{story:"Story for the button with a tooltip.",...A.parameters?.docs?.description}}};N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
  render: () => <div style={{
    ...styles,
    backgroundColor: '#F2F2F2',
    padding: '10px'
  }}>
      <Button label="Transparent" variant={ButtonVariant.SECONDARY} transparent />
      <Button label="Not Transparent" variant={ButtonVariant.SECONDARY} transparent={false} />
    </div>
}`,...N.parameters?.docs?.source},description:{story:"Story for the transparent button.",...N.parameters?.docs?.description}}};S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button as='a' to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe" isExternal />
    </div>
}`,...S.parameters?.docs?.source},description:{story:"Story for the button with an external link (uses <a> tag)",...S.parameters?.docs?.description}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button as="a" to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe avec nouvelle fenêtre" isExternal opensInNewTab />
    </div>
}`,...g.parameters?.docs?.source},description:{story:"Story for the button with an external link and target _blank",...g.parameters?.docs?.description}}};L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
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
}`,...L.parameters?.docs?.source},description:{story:"Story for all button variants.",...L.parameters?.docs?.description}}};const ce=["DefaultButton","DefaultButtonVariants","NeutralButtonVariants","ButtonSizes","ButtonIconsLarge","ButtonIconsSmall","ButtonFullWidth","ButtonDisabled","ButtonLoading","ButtonTooltip","ButtonTransparent","ButtonWithExternalLink","ButtonWithExternalLinkAndTargetBlank","ButtonVariants"];export{E as ButtonDisabled,B as ButtonFullWidth,T as ButtonIconsLarge,h as ButtonIconsSmall,x as ButtonLoading,R as ButtonSizes,A as ButtonTooltip,N as ButtonTransparent,L as ButtonVariants,S as ButtonWithExternalLink,g as ButtonWithExternalLinkAndTargetBlank,v as DefaultButton,y as DefaultButtonVariants,f as NeutralButtonVariants,ce as __namedExportsOrder,de as default};
