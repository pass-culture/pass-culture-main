import{j as t}from"./jsx-runtime-DKKDLQjB.js";import{V as I}from"./index-UtnHzNQS.js";import{f as n}from"./full-next-B_76kGmE.js";import{f as g}from"./iconsList-C1D-i-wQ.js";import{I as d,c as i,a as r,b as o,B as j}from"./Button-CRTTfNRA.js";import"./iframe-CnfVxGgg.js";import"./preload-helper-PPVm8Dsz.js";import"./chunk-EPOLDU6W-WowPydQ5.js";import"./full-back-DIKqgBhG.js";import"./full-thumb-up-Bb4kpRpM.js";import"./full-bulb-PM9lEXbZ.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-down-Cmbtr9nI.js";import"./full-download-XQM5pv74.js";import"./full-duplicate-BZV8LNX-.js";import"./full-edit-CxAaM2Fv.js";import"./full-error-BFAmjN4t.js";import"./full-show-BUp4jmvL.js";import"./full-info-D24AtBVt.js";import"./full-three-dots-DhyQI2cN.js";import"./full-link-CYVo23DH.js";import"./full-location-CVEaH-Cp.js";import"./full-more-DLJb58kc.js";import"./full-refresh-BZh6W0mB.js";import"./full-right-Dd3YsyCq.js";import"./full-trash-CEfIUI4M.js";import"./full-up-D6TPt2ju.js";import"./full-validate-CbMNulkZ.js";import"./stroke-close-DnlFsd1c.js";import"./stroke-date-CWTXq8J4.js";import"./stroke-price-CbFScctA.js";import"./stroke-error-DSZD431a.js";import"./stroke-pass-CALgybTM.js";import"./stroke-picture-VF2OicDu.js";import"./stroke-search-Bph5aoaJ.js";import"./stroke-thing-O6UIROL8.js";import"./stroke-trash-Cc_5v2lW.js";import"./stroke-user-u-f9pznf.js";import"./stroke-video-Cd5kQZzx.js";import"./stroke-wrong-BAouvvNg.js";import"./index-DMt7lw30.js";import"./Tooltip-0Q1hzrna.js";import"./SvgIcon-BgRkYrhG.js";const E={none:null,...Object.fromEntries(g.map(s=>[s.src.split("/").pop()?.replace(".svg","")||"",s.src]))},Tt={title:"@/design-system/Button",component:j,decorators:[I],args:{as:"button",type:"button",color:o.BRAND,variant:r.PRIMARY,size:i.DEFAULT,label:"",disabled:!1,hovered:!1,isLoading:!1,transparent:!1,fullWidth:!1,tooltip:"",icon:void 0,iconAlt:"",iconPosition:d.LEFT,iconClassName:""},argTypes:{as:{control:"select",options:["button","a"]},type:{control:"select",options:["button","submit","reset"],if:{arg:"as",eq:"button"}},size:{control:"select",options:Object.values(i)},variant:{control:"select",options:Object.values(r)},icon:{control:"select",options:Object.keys(E),mapping:E},iconPosition:{control:"select",options:Object.values(d)},color:{control:"select",options:Object.values(o)},disabled:{control:"boolean"},hovered:{control:"boolean"},isLoading:{control:"boolean"},transparent:{control:"boolean"},fullWidth:{control:"boolean"},tooltip:{control:"text"},to:{control:"text",if:{arg:"as",eq:"a"}},opensInNewTab:{control:"boolean",if:{arg:"as",eq:"a"}},isExternal:{control:"boolean",if:{arg:"as",eq:"a"}},isSectionLink:{control:"boolean",if:{arg:"as",eq:"a"}}},parameters:{docs:{description:{component:"Meta object for the Button component."}}}},a={alignItems:"center",display:"flex",flexDirection:"row",gap:"12px"},e=s=>t.jsx(j,{...s}),c={render:s=>t.jsx(e,{...s}),args:{label:"Button Label"}},u={render:()=>t.jsxs("div",{style:a,children:[t.jsx(e,{label:"Primary"}),t.jsx(e,{variant:r.SECONDARY,label:"Secondary"}),t.jsx(e,{variant:r.TERTIARY,label:"Tertiary"})]})},p={render:()=>t.jsxs("div",{style:a,children:[t.jsx(e,{variant:r.PRIMARY,label:"Primary Neutral",color:o.NEUTRAL}),t.jsx(e,{variant:r.SECONDARY,label:"Secondary Neutral",color:o.NEUTRAL}),t.jsx(e,{variant:r.TERTIARY,label:"Tertiary Neutral",color:o.NEUTRAL})]})},m={render:()=>t.jsxs("div",{style:a,children:[t.jsx(e,{size:i.SMALL,label:"Small",variant:r.PRIMARY}),t.jsx(e,{label:"Default",variant:r.PRIMARY})]})},b={render:()=>t.jsxs("div",{style:a,children:[t.jsx(e,{icon:n,iconPosition:d.LEFT,label:"Icon Left"}),t.jsx(e,{icon:n,iconPosition:d.RIGHT,label:"Icon Right"}),t.jsx(e,{icon:n})]})},v={render:()=>t.jsxs("div",{style:a,children:[t.jsx(e,{size:i.SMALL,icon:n,iconPosition:d.LEFT,label:"Icon Left"}),t.jsx(e,{size:i.SMALL,icon:n,iconPosition:d.RIGHT,label:"Icon Right"}),t.jsx(e,{size:i.SMALL,icon:n})]})},y={render:()=>t.jsx("div",{style:{...a,maxWidth:"400px"},children:t.jsx(e,{label:"Full Width",fullWidth:!0})})},B={render:()=>t.jsxs("div",{style:a,children:[t.jsx(e,{label:"Disabled",disabled:!0}),t.jsx(e,{label:"Disabled",variant:r.SECONDARY,disabled:!0}),t.jsx(e,{label:"Disabled",variant:r.TERTIARY,disabled:!0})]})},R={render:()=>t.jsxs("div",{style:a,children:[t.jsx(e,{label:"Loading",isLoading:!0}),t.jsx(e,{label:"Loading",variant:r.SECONDARY,isLoading:!0}),t.jsx(e,{label:"Loading",variant:r.TERTIARY,isLoading:!0}),t.jsx(e,{isLoading:!0,icon:n}),t.jsx(e,{size:i.SMALL,isLoading:!0,icon:n})]})},x={render:()=>t.jsxs("div",{style:a,children:[t.jsx(e,{tooltip:"Tooltip text",icon:n}),t.jsx(e,{tooltip:"Tooltip text",icon:n,disabled:!0})]})},T={render:()=>t.jsxs("div",{style:{...a,backgroundColor:"#F2F2F2",padding:"10px"},children:[t.jsx(e,{label:"Transparent",variant:r.SECONDARY,transparent:!0}),t.jsx(e,{label:"Not Transparent",variant:r.SECONDARY,transparent:!1})]})},A={render:()=>t.jsx("div",{style:a,children:t.jsx(e,{as:"a",to:"https://pass-culture.github.io/pass-culture-main/",label:"Lien externe",isExternal:!0})})},S={render:()=>t.jsx("div",{style:a,children:t.jsx(e,{as:"a",to:"https://pass-culture.github.io/pass-culture-main/",label:"Lien externe avec nouvelle fenêtre",isExternal:!0,opensInNewTab:!0})})},l={display:"flex",flexDirection:"column",gap:"12px",marginBottom:24},L={marginBottom:16},h={render:()=>t.jsxs(t.Fragment,{children:[t.jsxs("div",{children:[t.jsx("h2",{style:L,children:"Brand"}),t.jsxs("div",{style:l,children:[t.jsx(e,{label:"Primary",variant:r.PRIMARY}),t.jsx(e,{label:"Primary Hovered",variant:r.PRIMARY,hovered:!0}),t.jsx(e,{label:"Tertiary Disabled",variant:r.TERTIARY,disabled:!0})]}),t.jsxs("div",{style:l,children:[t.jsx(e,{label:"Secondary",variant:r.SECONDARY}),t.jsx(e,{label:"Secondary Hovered",variant:r.SECONDARY,hovered:!0}),t.jsx(e,{label:"Secondary Disabled",variant:r.SECONDARY,disabled:!0})]}),t.jsxs("div",{style:l,children:[t.jsx(e,{label:"Tertiary",variant:r.TERTIARY}),t.jsx(e,{label:"Tertiary Hovered",variant:r.TERTIARY,hovered:!0}),t.jsx(e,{label:"Primary Disabled",variant:r.PRIMARY,disabled:!0})]})]}),t.jsxs("div",{style:{marginTop:24},children:[t.jsx("h2",{style:L,children:"Neutral"}),t.jsxs("div",{style:l,children:[t.jsx(e,{label:"Primary",variant:r.PRIMARY,color:o.NEUTRAL}),t.jsx(e,{label:"Primary Hovered",variant:r.PRIMARY,color:o.NEUTRAL,hovered:!0}),t.jsx(e,{label:"Primary Disabled",variant:r.PRIMARY,color:o.NEUTRAL,disabled:!0})]}),t.jsxs("div",{style:l,children:[t.jsx(e,{label:"Secondary",variant:r.SECONDARY,color:o.NEUTRAL}),t.jsx(e,{label:"Secondary Hovered",variant:r.SECONDARY,color:o.NEUTRAL,hovered:!0}),t.jsx(e,{label:"Secondary Disabled",variant:r.SECONDARY,color:o.NEUTRAL,disabled:!0})]}),t.jsxs("div",{style:l,children:[t.jsx(e,{label:"Tertiary",variant:r.TERTIARY,color:o.NEUTRAL}),t.jsx(e,{label:"Tertiary Hovered",variant:r.TERTIARY,color:o.NEUTRAL,hovered:!0}),t.jsx(e,{label:"Tertiary Disabled",variant:r.TERTIARY,color:o.NEUTRAL,disabled:!0})]})]})]})};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  render: (args: ButtonProps) => <Button {...args} />,
  args: {
    label: 'Button Label'
  }
}`,...c.parameters?.docs?.source},description:{story:"Story for the default Button component.",...c.parameters?.docs?.description}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Primary" />
      <Button variant={ButtonVariant.SECONDARY} label="Secondary" />
      <Button variant={ButtonVariant.TERTIARY} label="Tertiary" />
    </div>
}`,...u.parameters?.docs?.source},description:{story:"Story for the default button variants.",...u.parameters?.docs?.description}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button variant={ButtonVariant.PRIMARY} label='Primary Neutral' color={ButtonColor.NEUTRAL} />
      <Button variant={ButtonVariant.SECONDARY} label="Secondary Neutral" color={ButtonColor.NEUTRAL} />
      <Button variant={ButtonVariant.TERTIARY} label="Tertiary Neutral" color={ButtonColor.NEUTRAL} />
    </div>
}`,...p.parameters?.docs?.source},description:{story:"Story for the neutral button variants.",...p.parameters?.docs?.description}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button size={ButtonSize.SMALL} label="Small" variant={ButtonVariant.PRIMARY} />
      <Button label="Default" variant={ButtonVariant.PRIMARY} />
    </div>
}`,...m.parameters?.docs?.source},description:{story:"Story for the button sizes",...m.parameters?.docs?.description}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.LEFT} label="Icon Left" />
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.RIGHT} label="Icon Right" />
      <Button icon={fullNextIcon} />
    </div>
}`,...b.parameters?.docs?.source},description:{story:"Story for the icons with large size",...b.parameters?.docs?.description}}};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.LEFT} label="Icon Left" />
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.RIGHT} label="Icon Right" />
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} />
    </div>
}`,...v.parameters?.docs?.source},description:{story:"Story for the icons with small size",...v.parameters?.docs?.description}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  render: () => <div style={{
    ...styles,
    maxWidth: '400px'
  }}>
      <Button label="Full Width" fullWidth />
    </div>
}`,...y.parameters?.docs?.source},description:{story:"Story for the full width button, the button will take the full width of the container (for example, max width 400px)",...y.parameters?.docs?.description}}};B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Disabled" disabled />
      <Button label="Disabled" variant={ButtonVariant.SECONDARY} disabled />
      <Button label="Disabled" variant={ButtonVariant.TERTIARY} disabled />
    </div>
}`,...B.parameters?.docs?.source},description:{story:"Story for the disabled button.",...B.parameters?.docs?.description}}};R.parameters={...R.parameters,docs:{...R.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Loading" isLoading />
      <Button label="Loading" variant={ButtonVariant.SECONDARY} isLoading />
      <Button label="Loading" variant={ButtonVariant.TERTIARY} isLoading />
      <Button isLoading icon={fullNextIcon} />
      <Button size={ButtonSize.SMALL} isLoading icon={fullNextIcon} />
    </div>
}`,...R.parameters?.docs?.source},description:{story:"Story for the loading button.",...R.parameters?.docs?.description}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button tooltip="Tooltip text" icon={fullNextIcon} />
      <Button tooltip="Tooltip text" icon={fullNextIcon} disabled />
    </div>
}`,...x.parameters?.docs?.source},description:{story:"Story for the button with a tooltip.",...x.parameters?.docs?.description}}};T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
  render: () => <div style={{
    ...styles,
    backgroundColor: '#F2F2F2',
    padding: '10px'
  }}>
      <Button label="Transparent" variant={ButtonVariant.SECONDARY} transparent />
      <Button label="Not Transparent" variant={ButtonVariant.SECONDARY} transparent={false} />
    </div>
}`,...T.parameters?.docs?.source},description:{story:"Story for the transparent button.",...T.parameters?.docs?.description}}};A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button as='a' to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe" isExternal />
    </div>
}`,...A.parameters?.docs?.source},description:{story:"Story for the button with an external link (uses <a> tag)",...A.parameters?.docs?.description}}};S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button as="a" to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe avec nouvelle fenêtre" isExternal opensInNewTab />
    </div>
}`,...S.parameters?.docs?.source},description:{story:"Story for the button with an external link and target _blank",...S.parameters?.docs?.description}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
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
}`,...h.parameters?.docs?.source},description:{story:"Story for all button variants.",...h.parameters?.docs?.description}}};const At=["DefaultButton","DefaultButtonVariants","NeutralButtonVariants","ButtonSizes","ButtonIconsLarge","ButtonIconsSmall","ButtonFullWidth","ButtonDisabled","ButtonLoading","ButtonTooltip","ButtonTransparent","ButtonWithExternalLink","ButtonWithExternalLinkAndTargetBlank","ButtonVariants"];export{B as ButtonDisabled,y as ButtonFullWidth,b as ButtonIconsLarge,v as ButtonIconsSmall,R as ButtonLoading,m as ButtonSizes,x as ButtonTooltip,T as ButtonTransparent,h as ButtonVariants,A as ButtonWithExternalLink,S as ButtonWithExternalLinkAndTargetBlank,c as DefaultButton,u as DefaultButtonVariants,p as NeutralButtonVariants,At as __namedExportsOrder,Tt as default};
