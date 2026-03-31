import"./chunk-DseTPa7n.js";import{r as e}from"./iframe-BI_y8cM8.js";import{t}from"./jsx-runtime-BuabnPLX.js";import{a as n,i as r,n as i,r as a,t as o}from"./Button-5_ZjCtjb.js";import{t as s}from"./dist-DgLY4RXk.js";import{t as c}from"./full-next-CPXOvcO1.js";import{t as l}from"./iconsList-DsXSjL2h.js";e();var u=t(),d={none:null,...Object.fromEntries(l.map(e=>[e.src.split(`/`).pop()?.replace(`.svg`,``)||``,e.src]))},f={title:`@/design-system/Button`,component:o,decorators:[s],args:{as:`button`,type:`button`,color:i.BRAND,variant:r.PRIMARY,size:a.DEFAULT,label:``,disabled:!1,hovered:!1,isLoading:!1,transparent:!1,fullWidth:!1,tooltip:``,icon:void 0,iconAlt:``,iconPosition:n.LEFT,iconClassName:``},argTypes:{as:{control:`select`,options:[`button`,`a`]},type:{control:`select`,options:[`button`,`submit`,`reset`],if:{arg:`as`,eq:`button`}},size:{control:`select`,options:Object.values(a)},variant:{control:`select`,options:Object.values(r)},icon:{control:`select`,options:Object.keys(d),mapping:d},iconPosition:{control:`select`,options:Object.values(n)},color:{control:`select`,options:Object.values(i)},disabled:{control:`boolean`},hovered:{control:`boolean`},isLoading:{control:`boolean`},transparent:{control:`boolean`},fullWidth:{control:`boolean`},tooltip:{control:`text`},to:{control:`text`,if:{arg:`as`,eq:`a`}},opensInNewTab:{control:`boolean`,if:{arg:`as`,eq:`a`}},isExternal:{control:`boolean`,if:{arg:`as`,eq:`a`}},isSectionLink:{control:`boolean`,if:{arg:`as`,eq:`a`}}},parameters:{docs:{description:{component:`Meta object for the Button component.`}}}},p={alignItems:`center`,display:`flex`,flexDirection:`row`,gap:`12px`},m=e=>(0,u.jsx)(o,{...e}),h={render:e=>(0,u.jsx)(m,{...e}),args:{label:`Button Label`}},g={render:()=>(0,u.jsxs)(`div`,{style:p,children:[(0,u.jsx)(m,{label:`Primary`}),(0,u.jsx)(m,{variant:r.SECONDARY,label:`Secondary`}),(0,u.jsx)(m,{variant:r.TERTIARY,label:`Tertiary`})]})},_={render:()=>(0,u.jsxs)(`div`,{style:p,children:[(0,u.jsx)(m,{variant:r.PRIMARY,label:`Primary Neutral`,color:i.NEUTRAL}),(0,u.jsx)(m,{variant:r.SECONDARY,label:`Secondary Neutral`,color:i.NEUTRAL}),(0,u.jsx)(m,{variant:r.TERTIARY,label:`Tertiary Neutral`,color:i.NEUTRAL})]})},v={render:()=>(0,u.jsxs)(`div`,{style:p,children:[(0,u.jsx)(m,{variant:r.PRIMARY,label:`Primary Danger`,color:i.DANGER}),(0,u.jsx)(m,{variant:r.SECONDARY,label:`Secondary Danger`,color:i.DANGER}),(0,u.jsx)(m,{variant:r.TERTIARY,label:`Tertiary Danger`,color:i.DANGER})]})},y={render:()=>(0,u.jsxs)(`div`,{style:p,children:[(0,u.jsx)(m,{size:a.SMALL,label:`Small`,variant:r.PRIMARY}),(0,u.jsx)(m,{label:`Default`,variant:r.PRIMARY})]})},b={render:()=>(0,u.jsxs)(`div`,{style:p,children:[(0,u.jsx)(m,{icon:c,iconPosition:n.LEFT,label:`Icon Left`}),(0,u.jsx)(m,{icon:c,iconPosition:n.RIGHT,label:`Icon Right`}),(0,u.jsx)(m,{icon:c})]})},x={render:()=>(0,u.jsxs)(`div`,{style:p,children:[(0,u.jsx)(m,{size:a.SMALL,icon:c,iconPosition:n.LEFT,label:`Icon Left`}),(0,u.jsx)(m,{size:a.SMALL,icon:c,iconPosition:n.RIGHT,label:`Icon Right`}),(0,u.jsx)(m,{size:a.SMALL,icon:c})]})},S={render:()=>(0,u.jsx)(`div`,{style:{...p,maxWidth:`400px`},children:(0,u.jsx)(m,{label:`Full Width`,fullWidth:!0})})},C={render:()=>(0,u.jsxs)(`div`,{style:p,children:[(0,u.jsx)(m,{label:`Disabled`,disabled:!0}),(0,u.jsx)(m,{label:`Disabled`,variant:r.SECONDARY,disabled:!0}),(0,u.jsx)(m,{label:`Disabled`,variant:r.TERTIARY,disabled:!0})]})},w={render:()=>(0,u.jsxs)(`div`,{style:p,children:[(0,u.jsx)(m,{label:`Loading`,isLoading:!0}),(0,u.jsx)(m,{label:`Loading`,variant:r.SECONDARY,isLoading:!0}),(0,u.jsx)(m,{label:`Loading`,variant:r.TERTIARY,isLoading:!0}),(0,u.jsx)(m,{isLoading:!0,icon:c}),(0,u.jsx)(m,{size:a.SMALL,isLoading:!0,icon:c})]})},T={render:()=>(0,u.jsxs)(`div`,{style:p,children:[(0,u.jsx)(m,{tooltip:`Tooltip text`,icon:c}),(0,u.jsx)(m,{tooltip:`Tooltip text`,icon:c,disabled:!0})]})},E={render:()=>(0,u.jsxs)(`div`,{style:{...p,backgroundColor:`#F2F2F2`,padding:`10px`},children:[(0,u.jsx)(m,{label:`Transparent`,variant:r.SECONDARY,transparent:!0}),(0,u.jsx)(m,{label:`Not Transparent`,variant:r.SECONDARY,transparent:!1})]})},D={render:()=>(0,u.jsx)(`div`,{style:p,children:(0,u.jsx)(m,{as:`a`,to:`https://pass-culture.github.io/pass-culture-main/`,label:`Lien externe`,isExternal:!0})})},O={render:()=>(0,u.jsx)(`div`,{style:p,children:(0,u.jsx)(m,{as:`a`,to:`https://pass-culture.github.io/pass-culture-main/`,label:`Lien externe avec nouvelle fenêtre`,isExternal:!0,opensInNewTab:!0})})},k={display:`flex`,flexDirection:`column`,gap:`12px`,marginBottom:24},A={marginBottom:16},j={render:()=>(0,u.jsxs)(u.Fragment,{children:[(0,u.jsxs)(`div`,{children:[(0,u.jsx)(`h2`,{style:A,children:`Brand`}),(0,u.jsxs)(`div`,{style:k,children:[(0,u.jsx)(m,{label:`Primary`,variant:r.PRIMARY}),(0,u.jsx)(m,{label:`Primary Hovered`,variant:r.PRIMARY,hovered:!0}),(0,u.jsx)(m,{label:`Tertiary Disabled`,variant:r.TERTIARY,disabled:!0})]}),(0,u.jsxs)(`div`,{style:k,children:[(0,u.jsx)(m,{label:`Secondary`,variant:r.SECONDARY}),(0,u.jsx)(m,{label:`Secondary Hovered`,variant:r.SECONDARY,hovered:!0}),(0,u.jsx)(m,{label:`Secondary Disabled`,variant:r.SECONDARY,disabled:!0})]}),(0,u.jsxs)(`div`,{style:k,children:[(0,u.jsx)(m,{label:`Tertiary`,variant:r.TERTIARY}),(0,u.jsx)(m,{label:`Tertiary Hovered`,variant:r.TERTIARY,hovered:!0}),(0,u.jsx)(m,{label:`Primary Disabled`,variant:r.PRIMARY,disabled:!0})]})]}),(0,u.jsxs)(`div`,{style:{marginTop:24},children:[(0,u.jsx)(`h2`,{style:A,children:`Neutral`}),(0,u.jsxs)(`div`,{style:k,children:[(0,u.jsx)(m,{label:`Primary`,variant:r.PRIMARY,color:i.NEUTRAL}),(0,u.jsx)(m,{label:`Primary Hovered`,variant:r.PRIMARY,color:i.NEUTRAL,hovered:!0}),(0,u.jsx)(m,{label:`Primary Disabled`,variant:r.PRIMARY,color:i.NEUTRAL,disabled:!0})]}),(0,u.jsxs)(`div`,{style:k,children:[(0,u.jsx)(m,{label:`Secondary`,variant:r.SECONDARY,color:i.NEUTRAL}),(0,u.jsx)(m,{label:`Secondary Hovered`,variant:r.SECONDARY,color:i.NEUTRAL,hovered:!0}),(0,u.jsx)(m,{label:`Secondary Disabled`,variant:r.SECONDARY,color:i.NEUTRAL,disabled:!0})]}),(0,u.jsxs)(`div`,{style:k,children:[(0,u.jsx)(m,{label:`Tertiary`,variant:r.TERTIARY,color:i.NEUTRAL}),(0,u.jsx)(m,{label:`Tertiary Hovered`,variant:r.TERTIARY,color:i.NEUTRAL,hovered:!0}),(0,u.jsx)(m,{label:`Tertiary Disabled`,variant:r.TERTIARY,color:i.NEUTRAL,disabled:!0})]})]}),(0,u.jsxs)(`div`,{style:{marginTop:24},children:[(0,u.jsx)(`h2`,{style:A,children:`Danger`}),(0,u.jsxs)(`div`,{style:k,children:[(0,u.jsx)(m,{label:`Primary`,variant:r.PRIMARY,color:i.DANGER}),(0,u.jsx)(m,{label:`Primary Hovered`,variant:r.PRIMARY,color:i.DANGER,hovered:!0}),(0,u.jsx)(m,{label:`Primary Disabled`,variant:r.PRIMARY,color:i.DANGER,disabled:!0})]}),(0,u.jsxs)(`div`,{style:k,children:[(0,u.jsx)(m,{label:`Secondary`,variant:r.SECONDARY,color:i.DANGER}),(0,u.jsx)(m,{label:`Secondary Hovered`,variant:r.SECONDARY,color:i.DANGER,hovered:!0}),(0,u.jsx)(m,{label:`Secondary Disabled`,variant:r.SECONDARY,color:i.DANGER,disabled:!0})]}),(0,u.jsxs)(`div`,{style:k,children:[(0,u.jsx)(m,{label:`Tertiary`,variant:r.TERTIARY,color:i.DANGER}),(0,u.jsx)(m,{label:`Tertiary Hovered`,variant:r.TERTIARY,color:i.DANGER,hovered:!0}),(0,u.jsx)(m,{label:`Tertiary Disabled`,variant:r.TERTIARY,color:i.DANGER,disabled:!0})]})]})]})};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  render: (args: ButtonProps) => <Button {...args} />,
  args: {
    label: 'Button Label'
  }
}`,...h.parameters?.docs?.source},description:{story:`Story for the default Button component.`,...h.parameters?.docs?.description}}},g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Primary" />
      <Button variant={ButtonVariant.SECONDARY} label="Secondary" />
      <Button variant={ButtonVariant.TERTIARY} label="Tertiary" />
    </div>
}`,...g.parameters?.docs?.source},description:{story:`Story for the default button variants.`,...g.parameters?.docs?.description}}},_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button variant={ButtonVariant.PRIMARY} label='Primary Neutral' color={ButtonColor.NEUTRAL} />
      <Button variant={ButtonVariant.SECONDARY} label="Secondary Neutral" color={ButtonColor.NEUTRAL} />
      <Button variant={ButtonVariant.TERTIARY} label="Tertiary Neutral" color={ButtonColor.NEUTRAL} />
    </div>
}`,..._.parameters?.docs?.source},description:{story:`Story for the neutral button variants.`,..._.parameters?.docs?.description}}},v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button variant={ButtonVariant.PRIMARY} label='Primary Danger' color={ButtonColor.DANGER} />
      <Button variant={ButtonVariant.SECONDARY} label="Secondary Danger" color={ButtonColor.DANGER} />
      <Button variant={ButtonVariant.TERTIARY} label="Tertiary Danger" color={ButtonColor.DANGER} />
    </div>
}`,...v.parameters?.docs?.source}}},y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button size={ButtonSize.SMALL} label="Small" variant={ButtonVariant.PRIMARY} />
      <Button label="Default" variant={ButtonVariant.PRIMARY} />
    </div>
}`,...y.parameters?.docs?.source},description:{story:`Story for the button sizes`,...y.parameters?.docs?.description}}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.LEFT} label="Icon Left" />
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.RIGHT} label="Icon Right" />
      <Button icon={fullNextIcon} />
    </div>
}`,...b.parameters?.docs?.source},description:{story:`Story for the icons with large size`,...b.parameters?.docs?.description}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.LEFT} label="Icon Left" />
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.RIGHT} label="Icon Right" />
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} />
    </div>
}`,...x.parameters?.docs?.source},description:{story:`Story for the icons with small size`,...x.parameters?.docs?.description}}},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  render: () => <div style={{
    ...styles,
    maxWidth: '400px'
  }}>
      <Button label="Full Width" fullWidth />
    </div>
}`,...S.parameters?.docs?.source},description:{story:`Story for the full width button, the button will take the full width of the container (for example, max width 400px)`,...S.parameters?.docs?.description}}},C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Disabled" disabled />
      <Button label="Disabled" variant={ButtonVariant.SECONDARY} disabled />
      <Button label="Disabled" variant={ButtonVariant.TERTIARY} disabled />
    </div>
}`,...C.parameters?.docs?.source},description:{story:`Story for the disabled button.`,...C.parameters?.docs?.description}}},w.parameters={...w.parameters,docs:{...w.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Loading" isLoading />
      <Button label="Loading" variant={ButtonVariant.SECONDARY} isLoading />
      <Button label="Loading" variant={ButtonVariant.TERTIARY} isLoading />
      <Button isLoading icon={fullNextIcon} />
      <Button size={ButtonSize.SMALL} isLoading icon={fullNextIcon} />
    </div>
}`,...w.parameters?.docs?.source},description:{story:`Story for the loading button.`,...w.parameters?.docs?.description}}},T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button tooltip="Tooltip text" icon={fullNextIcon} />
      <Button tooltip="Tooltip text" icon={fullNextIcon} disabled />
    </div>
}`,...T.parameters?.docs?.source},description:{story:`Story for the button with a tooltip.`,...T.parameters?.docs?.description}}},E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
  render: () => <div style={{
    ...styles,
    backgroundColor: '#F2F2F2',
    padding: '10px'
  }}>
      <Button label="Transparent" variant={ButtonVariant.SECONDARY} transparent />
      <Button label="Not Transparent" variant={ButtonVariant.SECONDARY} transparent={false} />
    </div>
}`,...E.parameters?.docs?.source},description:{story:`Story for the transparent button.`,...E.parameters?.docs?.description}}},D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button as='a' to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe" isExternal />
    </div>
}`,...D.parameters?.docs?.source},description:{story:`Story for the button with an external link (uses <a> tag)`,...D.parameters?.docs?.description}}},O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button as="a" to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe avec nouvelle fenêtre" isExternal opensInNewTab />
    </div>
}`,...O.parameters?.docs?.source},description:{story:`Story for the button with an external link and target _blank`,...O.parameters?.docs?.description}}},j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
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
      <div style={{
      marginTop: 24
    }}>
        <h2 style={titleStyles}>Danger</h2>
        <div style={columnStyles}>
          <Button label="Primary" variant={ButtonVariant.PRIMARY} color={ButtonColor.DANGER} />
          <Button label="Primary Hovered" variant={ButtonVariant.PRIMARY} color={ButtonColor.DANGER} hovered />
          <Button label="Primary Disabled" variant={ButtonVariant.PRIMARY} color={ButtonColor.DANGER} disabled />
        </div>
        <div style={columnStyles}>
          <Button label="Secondary" variant={ButtonVariant.SECONDARY} color={ButtonColor.DANGER} />
          <Button label="Secondary Hovered" variant={ButtonVariant.SECONDARY} color={ButtonColor.DANGER} hovered />
          <Button label="Secondary Disabled" variant={ButtonVariant.SECONDARY} color={ButtonColor.DANGER} disabled />
        </div>
        <div style={columnStyles}>
          <Button label="Tertiary" variant={ButtonVariant.TERTIARY} color={ButtonColor.DANGER} />
          <Button label="Tertiary Hovered" variant={ButtonVariant.TERTIARY} color={ButtonColor.DANGER} hovered />
          <Button label="Tertiary Disabled" variant={ButtonVariant.TERTIARY} color={ButtonColor.DANGER} disabled />
        </div>
      </div>
    </>
}`,...j.parameters?.docs?.source},description:{story:`Story for all button variants.`,...j.parameters?.docs?.description}}};var M=[`DefaultButton`,`DefaultButtonVariants`,`NeutralButtonVariants`,`DangerButtonVariants`,`ButtonSizes`,`ButtonIconsLarge`,`ButtonIconsSmall`,`ButtonFullWidth`,`ButtonDisabled`,`ButtonLoading`,`ButtonTooltip`,`ButtonTransparent`,`ButtonWithExternalLink`,`ButtonWithExternalLinkAndTargetBlank`,`ButtonVariants`];export{C as ButtonDisabled,S as ButtonFullWidth,b as ButtonIconsLarge,x as ButtonIconsSmall,w as ButtonLoading,y as ButtonSizes,T as ButtonTooltip,E as ButtonTransparent,j as ButtonVariants,D as ButtonWithExternalLink,O as ButtonWithExternalLinkAndTargetBlank,v as DangerButtonVariants,h as DefaultButton,g as DefaultButtonVariants,_ as NeutralButtonVariants,M as __namedExportsOrder,f as default};