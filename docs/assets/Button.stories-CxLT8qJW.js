import{i as e}from"./preload-helper-xPQekRTU.js";import{C as t}from"./iframe-BQI7D1yK.js";import{t as n}from"./jsx-runtime-CaZkqeYb.js";import{a as r,i,n as a,o,r as s,s as c,t as l}from"./Button-D6o-ZqCG.js";import{n as u,r as d}from"./dist-CNin-GHh.js";import{n as f,t as p}from"./full-next-DpcTohxt.js";import{n as m,t as h}from"./iconsList-Dk5_jNaI.js";var g,_,v,y,b,x,S,C,w,T,E,D,O,k,A,j,M,N,P,F,I,L,R;e((()=>{t(),d(),f(),m(),a(),c(),g=n(),_={none:null,...Object.fromEntries(h.map(e=>[e.src.split(`/`).pop()?.replace(`.svg`,``)||``,e.src]))},v={title:`@/design-system/Button`,component:l,decorators:[u],args:{as:`button`,type:`button`,color:s.BRAND,variant:r.PRIMARY,size:i.DEFAULT,label:``,disabled:!1,hovered:!1,isLoading:!1,transparent:!1,fullWidth:!1,tooltip:``,icon:void 0,iconAlt:``,iconPosition:o.LEFT,iconClassName:``},argTypes:{as:{control:`select`,options:[`button`,`a`]},type:{control:`select`,options:[`button`,`submit`,`reset`],if:{arg:`as`,eq:`button`}},size:{control:`select`,options:Object.values(i)},variant:{control:`select`,options:Object.values(r)},icon:{control:`select`,options:Object.keys(_),mapping:_},iconPosition:{control:`select`,options:Object.values(o)},color:{control:`select`,options:Object.values(s)},disabled:{control:`boolean`},hovered:{control:`boolean`},isLoading:{control:`boolean`},transparent:{control:`boolean`},fullWidth:{control:`boolean`},tooltip:{control:`text`},to:{control:`text`,if:{arg:`as`,eq:`a`}},opensInNewTab:{control:`boolean`,if:{arg:`as`,eq:`a`}},isExternal:{control:`boolean`,if:{arg:`as`,eq:`a`}},isSectionLink:{control:`boolean`,if:{arg:`as`,eq:`a`}}},parameters:{docs:{description:{component:`Meta object for the Button component.`}}}},y={alignItems:`center`,display:`flex`,flexDirection:`row`,gap:`12px`},b=e=>(0,g.jsx)(l,{...e}),x={render:e=>(0,g.jsx)(b,{...e}),args:{label:`Button Label`}},S={render:()=>(0,g.jsxs)(`div`,{style:y,children:[(0,g.jsx)(b,{label:`Primary`}),(0,g.jsx)(b,{variant:r.SECONDARY,label:`Secondary`}),(0,g.jsx)(b,{variant:r.TERTIARY,label:`Tertiary`})]})},C={render:()=>(0,g.jsxs)(`div`,{style:y,children:[(0,g.jsx)(b,{variant:r.PRIMARY,label:`Primary Neutral`,color:s.NEUTRAL}),(0,g.jsx)(b,{variant:r.SECONDARY,label:`Secondary Neutral`,color:s.NEUTRAL}),(0,g.jsx)(b,{variant:r.TERTIARY,label:`Tertiary Neutral`,color:s.NEUTRAL})]})},w={render:()=>(0,g.jsxs)(`div`,{style:y,children:[(0,g.jsx)(b,{variant:r.PRIMARY,label:`Primary Danger`,color:s.DANGER}),(0,g.jsx)(b,{variant:r.SECONDARY,label:`Secondary Danger`,color:s.DANGER}),(0,g.jsx)(b,{variant:r.TERTIARY,label:`Tertiary Danger`,color:s.DANGER})]})},T={render:()=>(0,g.jsxs)(`div`,{style:y,children:[(0,g.jsx)(b,{size:i.SMALL,label:`Small`,variant:r.PRIMARY}),(0,g.jsx)(b,{label:`Default`,variant:r.PRIMARY})]})},E={render:()=>(0,g.jsxs)(`div`,{style:y,children:[(0,g.jsx)(b,{icon:p,iconPosition:o.LEFT,label:`Icon Left`}),(0,g.jsx)(b,{icon:p,iconPosition:o.RIGHT,label:`Icon Right`}),(0,g.jsx)(b,{icon:p})]})},D={render:()=>(0,g.jsxs)(`div`,{style:y,children:[(0,g.jsx)(b,{size:i.SMALL,icon:p,iconPosition:o.LEFT,label:`Icon Left`}),(0,g.jsx)(b,{size:i.SMALL,icon:p,iconPosition:o.RIGHT,label:`Icon Right`}),(0,g.jsx)(b,{size:i.SMALL,icon:p})]})},O={render:()=>(0,g.jsx)(`div`,{style:{...y,maxWidth:`400px`},children:(0,g.jsx)(b,{label:`Full Width`,fullWidth:!0})})},k={render:()=>(0,g.jsxs)(`div`,{style:y,children:[(0,g.jsx)(b,{label:`Disabled`,disabled:!0}),(0,g.jsx)(b,{label:`Disabled`,variant:r.SECONDARY,disabled:!0}),(0,g.jsx)(b,{label:`Disabled`,variant:r.TERTIARY,disabled:!0})]})},A={render:()=>(0,g.jsxs)(`div`,{style:y,children:[(0,g.jsx)(b,{label:`Loading`,isLoading:!0}),(0,g.jsx)(b,{label:`Loading`,variant:r.SECONDARY,isLoading:!0}),(0,g.jsx)(b,{label:`Loading`,variant:r.TERTIARY,isLoading:!0}),(0,g.jsx)(b,{isLoading:!0,icon:p}),(0,g.jsx)(b,{size:i.SMALL,isLoading:!0,icon:p})]})},j={render:()=>(0,g.jsxs)(`div`,{style:y,children:[(0,g.jsx)(b,{tooltip:`Tooltip text`,icon:p}),(0,g.jsx)(b,{tooltip:`Tooltip text`,icon:p,disabled:!0})]})},M={render:()=>(0,g.jsxs)(`div`,{style:{...y,backgroundColor:`#F2F2F2`,padding:`10px`},children:[(0,g.jsx)(b,{label:`Transparent`,variant:r.SECONDARY,transparent:!0}),(0,g.jsx)(b,{label:`Not Transparent`,variant:r.SECONDARY,transparent:!1})]})},N={render:()=>(0,g.jsx)(`div`,{style:y,children:(0,g.jsx)(b,{as:`a`,to:`https://pass-culture.github.io/pass-culture-main/`,label:`Lien externe`,isExternal:!0})})},P={render:()=>(0,g.jsx)(`div`,{style:y,children:(0,g.jsx)(b,{as:`a`,to:`https://pass-culture.github.io/pass-culture-main/`,label:`Lien externe avec nouvelle fenêtre`,isExternal:!0,opensInNewTab:!0})})},F={display:`flex`,flexDirection:`column`,gap:`12px`,marginBottom:24},I={marginBottom:16},L={render:()=>(0,g.jsxs)(g.Fragment,{children:[(0,g.jsxs)(`div`,{children:[(0,g.jsx)(`h2`,{style:I,children:`Brand`}),(0,g.jsxs)(`div`,{style:F,children:[(0,g.jsx)(b,{label:`Primary`,variant:r.PRIMARY}),(0,g.jsx)(b,{label:`Primary Hovered`,variant:r.PRIMARY,hovered:!0}),(0,g.jsx)(b,{label:`Tertiary Disabled`,variant:r.TERTIARY,disabled:!0})]}),(0,g.jsxs)(`div`,{style:F,children:[(0,g.jsx)(b,{label:`Secondary`,variant:r.SECONDARY}),(0,g.jsx)(b,{label:`Secondary Hovered`,variant:r.SECONDARY,hovered:!0}),(0,g.jsx)(b,{label:`Secondary Disabled`,variant:r.SECONDARY,disabled:!0})]}),(0,g.jsxs)(`div`,{style:F,children:[(0,g.jsx)(b,{label:`Tertiary`,variant:r.TERTIARY}),(0,g.jsx)(b,{label:`Tertiary Hovered`,variant:r.TERTIARY,hovered:!0}),(0,g.jsx)(b,{label:`Primary Disabled`,variant:r.PRIMARY,disabled:!0})]})]}),(0,g.jsxs)(`div`,{style:{marginTop:24},children:[(0,g.jsx)(`h2`,{style:I,children:`Neutral`}),(0,g.jsxs)(`div`,{style:F,children:[(0,g.jsx)(b,{label:`Primary`,variant:r.PRIMARY,color:s.NEUTRAL}),(0,g.jsx)(b,{label:`Primary Hovered`,variant:r.PRIMARY,color:s.NEUTRAL,hovered:!0}),(0,g.jsx)(b,{label:`Primary Disabled`,variant:r.PRIMARY,color:s.NEUTRAL,disabled:!0})]}),(0,g.jsxs)(`div`,{style:F,children:[(0,g.jsx)(b,{label:`Secondary`,variant:r.SECONDARY,color:s.NEUTRAL}),(0,g.jsx)(b,{label:`Secondary Hovered`,variant:r.SECONDARY,color:s.NEUTRAL,hovered:!0}),(0,g.jsx)(b,{label:`Secondary Disabled`,variant:r.SECONDARY,color:s.NEUTRAL,disabled:!0})]}),(0,g.jsxs)(`div`,{style:F,children:[(0,g.jsx)(b,{label:`Tertiary`,variant:r.TERTIARY,color:s.NEUTRAL}),(0,g.jsx)(b,{label:`Tertiary Hovered`,variant:r.TERTIARY,color:s.NEUTRAL,hovered:!0}),(0,g.jsx)(b,{label:`Tertiary Disabled`,variant:r.TERTIARY,color:s.NEUTRAL,disabled:!0})]})]}),(0,g.jsxs)(`div`,{style:{marginTop:24},children:[(0,g.jsx)(`h2`,{style:I,children:`Danger`}),(0,g.jsxs)(`div`,{style:F,children:[(0,g.jsx)(b,{label:`Primary`,variant:r.PRIMARY,color:s.DANGER}),(0,g.jsx)(b,{label:`Primary Hovered`,variant:r.PRIMARY,color:s.DANGER,hovered:!0}),(0,g.jsx)(b,{label:`Primary Disabled`,variant:r.PRIMARY,color:s.DANGER,disabled:!0})]}),(0,g.jsxs)(`div`,{style:F,children:[(0,g.jsx)(b,{label:`Secondary`,variant:r.SECONDARY,color:s.DANGER}),(0,g.jsx)(b,{label:`Secondary Hovered`,variant:r.SECONDARY,color:s.DANGER,hovered:!0}),(0,g.jsx)(b,{label:`Secondary Disabled`,variant:r.SECONDARY,color:s.DANGER,disabled:!0})]}),(0,g.jsxs)(`div`,{style:F,children:[(0,g.jsx)(b,{label:`Tertiary`,variant:r.TERTIARY,color:s.DANGER}),(0,g.jsx)(b,{label:`Tertiary Hovered`,variant:r.TERTIARY,color:s.DANGER,hovered:!0}),(0,g.jsx)(b,{label:`Tertiary Disabled`,variant:r.TERTIARY,color:s.DANGER,disabled:!0})]})]})]})},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  render: (args: ButtonProps) => <Button {...args} />,
  args: {
    label: 'Button Label'
  }
}`,...x.parameters?.docs?.source},description:{story:`Story for the default Button component.`,...x.parameters?.docs?.description}}},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Primary" />
      <Button variant={ButtonVariant.SECONDARY} label="Secondary" />
      <Button variant={ButtonVariant.TERTIARY} label="Tertiary" />
    </div>
}`,...S.parameters?.docs?.source},description:{story:`Story for the default button variants.`,...S.parameters?.docs?.description}}},C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button variant={ButtonVariant.PRIMARY} label='Primary Neutral' color={ButtonColor.NEUTRAL} />
      <Button variant={ButtonVariant.SECONDARY} label="Secondary Neutral" color={ButtonColor.NEUTRAL} />
      <Button variant={ButtonVariant.TERTIARY} label="Tertiary Neutral" color={ButtonColor.NEUTRAL} />
    </div>
}`,...C.parameters?.docs?.source},description:{story:`Story for the neutral button variants.`,...C.parameters?.docs?.description}}},w.parameters={...w.parameters,docs:{...w.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button variant={ButtonVariant.PRIMARY} label='Primary Danger' color={ButtonColor.DANGER} />
      <Button variant={ButtonVariant.SECONDARY} label="Secondary Danger" color={ButtonColor.DANGER} />
      <Button variant={ButtonVariant.TERTIARY} label="Tertiary Danger" color={ButtonColor.DANGER} />
    </div>
}`,...w.parameters?.docs?.source}}},T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button size={ButtonSize.SMALL} label="Small" variant={ButtonVariant.PRIMARY} />
      <Button label="Default" variant={ButtonVariant.PRIMARY} />
    </div>
}`,...T.parameters?.docs?.source},description:{story:`Story for the button sizes`,...T.parameters?.docs?.description}}},E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.LEFT} label="Icon Left" />
      <Button icon={fullNextIcon} iconPosition={IconPositionEnum.RIGHT} label="Icon Right" />
      <Button icon={fullNextIcon} />
    </div>
}`,...E.parameters?.docs?.source},description:{story:`Story for the icons with large size`,...E.parameters?.docs?.description}}},D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.LEFT} label="Icon Left" />
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} iconPosition={IconPositionEnum.RIGHT} label="Icon Right" />
      <Button size={ButtonSize.SMALL} icon={fullNextIcon} />
    </div>
}`,...D.parameters?.docs?.source},description:{story:`Story for the icons with small size`,...D.parameters?.docs?.description}}},O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
  render: () => <div style={{
    ...styles,
    maxWidth: '400px'
  }}>
      <Button label="Full Width" fullWidth />
    </div>
}`,...O.parameters?.docs?.source},description:{story:`Story for the full width button, the button will take the full width of the container (for example, max width 400px)`,...O.parameters?.docs?.description}}},k.parameters={...k.parameters,docs:{...k.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Disabled" disabled />
      <Button label="Disabled" variant={ButtonVariant.SECONDARY} disabled />
      <Button label="Disabled" variant={ButtonVariant.TERTIARY} disabled />
    </div>
}`,...k.parameters?.docs?.source},description:{story:`Story for the disabled button.`,...k.parameters?.docs?.description}}},A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button label="Loading" isLoading />
      <Button label="Loading" variant={ButtonVariant.SECONDARY} isLoading />
      <Button label="Loading" variant={ButtonVariant.TERTIARY} isLoading />
      <Button isLoading icon={fullNextIcon} />
      <Button size={ButtonSize.SMALL} isLoading icon={fullNextIcon} />
    </div>
}`,...A.parameters?.docs?.source},description:{story:`Story for the loading button.`,...A.parameters?.docs?.description}}},j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button tooltip="Tooltip text" icon={fullNextIcon} />
      <Button tooltip="Tooltip text" icon={fullNextIcon} disabled />
    </div>
}`,...j.parameters?.docs?.source},description:{story:`Story for the button with a tooltip.`,...j.parameters?.docs?.description}}},M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
  render: () => <div style={{
    ...styles,
    backgroundColor: '#F2F2F2',
    padding: '10px'
  }}>
      <Button label="Transparent" variant={ButtonVariant.SECONDARY} transparent />
      <Button label="Not Transparent" variant={ButtonVariant.SECONDARY} transparent={false} />
    </div>
}`,...M.parameters?.docs?.source},description:{story:`Story for the transparent button.`,...M.parameters?.docs?.description}}},N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button as='a' to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe" isExternal />
    </div>
}`,...N.parameters?.docs?.source},description:{story:`Story for the button with an external link (uses <a> tag)`,...N.parameters?.docs?.description}}},P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  render: () => <div style={styles}>
      <Button as="a" to="https://pass-culture.github.io/pass-culture-main/" label="Lien externe avec nouvelle fenêtre" isExternal opensInNewTab />
    </div>
}`,...P.parameters?.docs?.source},description:{story:`Story for the button with an external link and target _blank`,...P.parameters?.docs?.description}}},L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
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
}`,...L.parameters?.docs?.source},description:{story:`Story for all button variants.`,...L.parameters?.docs?.description}}},R=[`DefaultButton`,`DefaultButtonVariants`,`NeutralButtonVariants`,`DangerButtonVariants`,`ButtonSizes`,`ButtonIconsLarge`,`ButtonIconsSmall`,`ButtonFullWidth`,`ButtonDisabled`,`ButtonLoading`,`ButtonTooltip`,`ButtonTransparent`,`ButtonWithExternalLink`,`ButtonWithExternalLinkAndTargetBlank`,`ButtonVariants`]}))();export{k as ButtonDisabled,O as ButtonFullWidth,E as ButtonIconsLarge,D as ButtonIconsSmall,A as ButtonLoading,T as ButtonSizes,j as ButtonTooltip,M as ButtonTransparent,L as ButtonVariants,N as ButtonWithExternalLink,P as ButtonWithExternalLinkAndTargetBlank,w as DangerButtonVariants,x as DefaultButton,S as DefaultButtonVariants,C as NeutralButtonVariants,R as __namedExportsOrder,v as default};