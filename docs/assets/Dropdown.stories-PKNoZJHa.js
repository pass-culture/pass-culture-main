import{a as e,n as t}from"./rolldown-runtime-DaJ6WEGw.js";import{t as n}from"./react-DvlgmmzG.js";import{t as r}from"./jsx-runtime-cM__dR4X.js";import{t as i}from"./classnames-Bkdxq3RN.js";import{a,i as o,n as s,r as c,s as l,t as u}from"./Button-z_PnfM00.js";import{n as d,t as f}from"./SvgIcon-Zw_1PgY_.js";import{i as p,n as m,o as h,r as g,s as _,t as v}from"./dist-DNZiVIjF.js";import{n as y}from"./full-three-dots--Qqvr3Z0.js";var b,x=t((()=>{b={"menu-list":`_menu-list_11euo_1`,"menu-item":`_menu-item_11euo_12`,"menu-item-disabled":`_menu-item-disabled_11euo_27`,"menu-item-icon":`_menu-item-icon_11euo_31`,"menu-item-danger":`_menu-item-danger_11euo_35`}}));function S({title:e,trigger:t,open:n,defaultOpen:r,onOpenChange:i,children:s,align:l=`end`,sideOffset:d=4,contentClassName:f,dropdownTriggerRef:m,triggerTooltip:_,side:y}){return(0,w.jsxs)(p,{open:n,defaultOpen:r,onOpenChange:i,children:[(0,w.jsx)(h,{"data-testid":`dropdown-menu-trigger`,asChild:!0,children:t??(0,w.jsx)(u,{ref:m,variant:a.SECONDARY,color:c.NEUTRAL,size:o.SMALL,icon:``+new URL(`full-three-dots-TvLEwYVc.svg`,import.meta.url).href,tooltip:_?e:void 0,"aria-label":e})}),(0,w.jsx)(g,{children:(0,w.jsx)(v,{className:(0,C.default)(b[`menu-list`],f),align:l,sideOffset:d,side:y,children:s})})]})}var C,w,T=t((()=>{_(),C=e(i(),1),s(),l(),y(),x(),w=r();try{S.displayName=`Dropdown`,S.__docgenInfo={description:``,displayName:`Dropdown`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Dropdown/Dropdown.tsx`,methods:[],props:{title:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Dropdown/Dropdown.tsx`,name:`TypeLiteral`}],description:``,name:`title`,required:!0,tags:{},type:{name:`string`}},trigger:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Dropdown/Dropdown.tsx`,name:`TypeLiteral`}],description:`Trigger slot rendered with Radix Trigger asChild`,name:`trigger`,required:!1,tags:{},type:{name:`ReactNode`}},open:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Dropdown/Dropdown.tsx`,name:`TypeLiteral`}],description:`Controlled/uncontrolled open state (optional)`,name:`open`,required:!1,tags:{},type:{name:`boolean`}},defaultOpen:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Dropdown/Dropdown.tsx`,name:`TypeLiteral`}],description:``,name:`defaultOpen`,required:!1,tags:{},type:{name:`boolean`}},onOpenChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Dropdown/Dropdown.tsx`,name:`TypeLiteral`}],description:``,name:`onOpenChange`,required:!1,tags:{},type:{name:`((open: boolean) => void)`}},children:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Dropdown/Dropdown.tsx`,name:`TypeLiteral`}],description:`Content`,name:`children`,required:!1,tags:{},type:{name:`ReactNode`}},align:{defaultValue:{value:`end`},declarations:[{fileName:`pro/src/ui-kit/Dropdown/Dropdown.tsx`,name:`TypeLiteral`}],description:`Radix content config`,name:`align`,required:!1,tags:{},type:{name:`enum`,raw:`"start" | "center" | "end"`,value:[{value:`"start"`},{value:`"center"`},{value:`"end"`}]}},side:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Dropdown/Dropdown.tsx`,name:`TypeLiteral`}],description:``,name:`side`,required:!1,tags:{},type:{name:`enum`,raw:`"top" | "right" | "bottom" | "left"`,value:[{value:`"top"`},{value:`"right"`},{value:`"bottom"`},{value:`"left"`}]}},sideOffset:{defaultValue:{value:`4`},declarations:[{fileName:`pro/src/ui-kit/Dropdown/Dropdown.tsx`,name:`TypeLiteral`}],description:``,name:`sideOffset`,required:!1,tags:{},type:{name:`number`}},contentClassName:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Dropdown/Dropdown.tsx`,name:`TypeLiteral`}],description:`Styling`,name:`contentClassName`,required:!1,tags:{},type:{name:`string`}},dropdownTriggerRef:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Dropdown/Dropdown.tsx`,name:`TypeLiteral`}],description:``,name:`dropdownTriggerRef`,required:!1,tags:{},type:{name:`RefObject<HTMLButtonElement | null>`}},triggerTooltip:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Dropdown/Dropdown.tsx`,name:`TypeLiteral`}],description:``,name:`triggerTooltip`,required:!1,tags:{},type:{name:`boolean`}}},tags:{deprecated:"Use `<Dropdown />` from /design-system/ folder instead"}}}catch{}})),E,D=t((()=>{E=function(e){return e.NEUTRAL=`neutral`,e.DANGER=`danger`,e}({})}));function O({title:e,children:t,onSelect:n,disabled:r,icon:i,color:a=E.NEUTRAL,...o}){return(0,A.jsxs)(m,{className:(0,k.default)(b[`menu-item`],{[b[`menu-item-disabled`]]:r,[b[`menu-item-danger`]]:a===E.DANGER}),onSelect:n,disabled:r,...e?{title:e}:{},...o,children:[i&&(0,A.jsx)(f,{className:b[`menu-item-icon`],src:i}),e,t]})}var k,A,j=t((()=>{_(),k=e(i(),1),d(),x(),D(),A=r();try{O.displayName=`DropdownItem`,O.__docgenInfo={description:`The DropdownItem component represents an item within a dropdown menu.
It allows users to select an option, which can trigger a callback function.

---
**Important: Use the \`onSelect\` prop to handle actions when the dropdown item is selected.**
---`,displayName:`DropdownItem`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Dropdown/DropdownItem.tsx`,methods:[],props:{asChild:{defaultValue:null,declarations:[{fileName:`pro/node_modules/.pnpm/@radix-ui+react-primitive@2.1.7_@types+react-dom@19.2.3_@types+react@19.2.17__@types+re_6d8fb7f79176be78f7d41dc3e06e6146/node_modules/@radix-ui/react-primitive/dist/index.d.mts`,name:`TypeLiteral`}],description:``,name:`asChild`,required:!1,tags:{},type:{name:`boolean`}},icon:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Dropdown/DropdownItem.tsx`,name:`TypeLiteral`}],description:`The icon of the dropdown item`,name:`icon`,required:!1,tags:{},type:{name:`string`}}},tags:{param:`props - The props for the DropdownItem component.`,returns:`The rendered DropdownItem component.`,example:`<DropdownItem title="Settings" onSelect={() => console.log('Settings selected')}>
  Settings
</DropdownItem>`,accessibility:"- If present, the `title` attribute provides additional context for the dropdown item.",deprecated:"Use `<Dropdown />` from /design-system/ folder instead"}}}catch{}})),M,N,P,F,I,L,R,z,B;t((()=>{M=e(n(),1),T(),s(),l(),j(),D(),N=r(),P={title:`@/ui-kit/Dropdown`,component:S,parameters:{layout:`centered`},args:{align:`end`}},F={args:{trigger:(0,N.jsx)(u,{label:`Ouvrir`,variant:a.PRIMARY})},render:e=>(0,N.jsxs)(S,{...e,children:[(0,N.jsx)(O,{onSelect:()=>console.log(`Profil`),children:`Profil`}),(0,N.jsx)(O,{onSelect:()=>console.log(`Paramètres`),children:`Paramètres`}),(0,N.jsx)(O,{onSelect:()=>console.log(`Déconnexion`),children:`Déconnexion`})]})},I={args:{title:`dropdown`,trigger:(0,N.jsx)(u,{label:`Options (API simple)`,variant:a.PRIMARY})},render:e=>(0,N.jsxs)(S,{...e,children:[(0,N.jsx)(O,{onSelect:()=>console.log(`Profil`),children:`Profil`}),(0,N.jsx)(O,{onSelect:()=>console.log(`Paramètres`),children:`Paramètres`}),(0,N.jsx)(O,{onSelect:()=>console.log(`Déconnexion`),children:`Déconnexion`})]})},L={args:{trigger:(0,N.jsx)(u,{label:`Controlled`,variant:a.PRIMARY})},render:e=>{let[t,n]=M.useState(!1);return(0,N.jsxs)(S,{...e,open:t,onOpenChange:n,children:[(0,N.jsx)(O,{onSelect:()=>console.log(`A`),children:`Action A`}),(0,N.jsx)(O,{onSelect:()=>console.log(`B`),children:`Action B`})]})}},R={args:{trigger:(0,N.jsx)(u,{label:`Long content`,variant:a.PRIMARY}),contentClassName:`storybookDropdownLong`},render:e=>(0,N.jsx)(S,{...e,children:Array.from({length:20}).map((e,t)=>(0,N.jsx)(O,{onSelect:()=>console.log(`Action ${t+1}`),children:`Action ${t+1}`},`Action ${t+1}`))})},z={args:{trigger:(0,N.jsx)(u,{label:`Ouvrir`,variant:a.PRIMARY})},render:e=>(0,N.jsxs)(S,{...e,children:[(0,N.jsx)(O,{onSelect:()=>console.log(`Profil`),children:`Profil`}),(0,N.jsx)(O,{color:E.DANGER,onSelect:()=>console.log(`Déconnexion`),children:`Déconnexion`})]})},F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  args: {
    trigger: <Button label="Ouvrir" variant={ButtonVariant.PRIMARY} />
  },
  render: args => <Dropdown {...args}>
      <DropdownItem onSelect={() => console.log('Profil')}>Profil</DropdownItem>
      <DropdownItem onSelect={() => console.log('Paramètres')}>
        Paramètres
      </DropdownItem>

      <DropdownItem onSelect={() => console.log('Déconnexion')}>
        Déconnexion
      </DropdownItem>
    </Dropdown>
}`,...F.parameters?.docs?.source}}},I.parameters={...I.parameters,docs:{...I.parameters?.docs,source:{originalSource:`{
  args: {
    title: "dropdown",
    trigger: <Button label="Options (API simple)" variant={ButtonVariant.PRIMARY} />
  },
  render: args => <Dropdown {...args}>
      <DropdownItem onSelect={() => console.log('Profil')}>Profil</DropdownItem>
      <DropdownItem onSelect={() => console.log('Paramètres')}>Paramètres</DropdownItem>
      <DropdownItem onSelect={() => console.log('Déconnexion')}>Déconnexion</DropdownItem>
  </Dropdown>
}`,...I.parameters?.docs?.source}}},L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
  args: {
    trigger: <Button label="Controlled" variant={ButtonVariant.PRIMARY} />
  },
  render: args => {
    const [open, setOpen] = React.useState(false);
    return <Dropdown {...args} open={open} onOpenChange={setOpen}>
          <DropdownItem onSelect={() => console.log('A')}>Action A</DropdownItem>
          <DropdownItem onSelect={() => console.log('B')}>Action B</DropdownItem>
        </Dropdown>;
  }
}`,...L.parameters?.docs?.source}}},R.parameters={...R.parameters,docs:{...R.parameters?.docs,source:{originalSource:`{
  args: {
    trigger: <Button label="Long content" variant={ButtonVariant.PRIMARY} />,
    contentClassName: 'storybookDropdownLong'
  },
  render: args => <Dropdown {...args}>
    {Array.from({
      length: 20
    }).map((_, item) => <DropdownItem key={\`Action \${item + 1}\`} onSelect={() => console.log(\`Action \${item + 1}\`)}> 
        {\`Action \${item + 1}\`}
        </DropdownItem>)}
  </Dropdown>
}`,...R.parameters?.docs?.source}}},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
  args: {
    trigger: <Button label="Ouvrir" variant={ButtonVariant.PRIMARY} />
  },
  render: args => <Dropdown {...args}>
      <DropdownItem onSelect={() => console.log('Profil')}>Profil</DropdownItem>

      <DropdownItem color={DropdownItemColor.DANGER} onSelect={() => console.log('Déconnexion')}>
        Déconnexion
      </DropdownItem>
    </Dropdown>
}`,...z.parameters?.docs?.source}}},B=[`WithChildren`,`WithOptions`,`ControlledOpen`,`LongContent`,`WithDangerChildren`]}))();export{L as ControlledOpen,R as LongContent,F as WithChildren,z as WithDangerChildren,I as WithOptions,B as __namedExportsOrder,P as default};