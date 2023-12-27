import{j as t}from"./jsx-runtime-4cb93332.js";import"./Divider-18a8873c.js";import"./SubmitButton-d256fa4a.js";import{B as n,a as u}from"./Button-4114e005.js";import"./Thumb-a6470343.js";import"./stroke-offer-c4ecfb28.js";import"./Banner-786d7667.js";import"./InfoBox-2e607825.js";import{c as y}from"./index-e2bfc4ae.js";import{r as _}from"./index-83a10e79.js";import{u as h,s as c}from"./reducer-1b342222.js";import"./index-4a87243b.js";import"./index-a9c6ff12.js";import"./_commonjsHelpers-de833af9.js";import"./full-right-83efe067.js";import"./SvgIcon-04d0ac1c.js";import"./Button.module-ec1646c9.js";import"./stroke-pass-cf331655.js";import"./Tooltip-e788be74.js";import"./useTooltipProps-e39310f5.js";import"./formik.esm-8d42c991.js";import"./full-next-ebff3494.js";import"./BaseCheckbox-3c32db71.js";import"./BaseFileInput-74e97976.js";import"./BaseRadio-50c25ccc.js";import"./FieldError-c6f3f130.js";import"./stroke-error-ed5fe82d.js";import"./FieldSuccess-9f5fbaa8.js";import"./stroke-valid-9c345a33.js";import"./full-clear-9268779e.js";import"./index-9d475cdf.js";import"./SelectInput-badf7177.js";import"./stroke-down-3d79f44b.js";import"./typeof-7fd5df1e.js";import"./BaseInput-5798c6b4.js";import"./stroke-close-3a7bfe9e.js";import"./shadow-tips-help-841f916a.js";import"./shadow-tips-warning-66fb0429.js";import"./LinkNodes-cde989c8.js";import"./full-link-9eb5e1cb.js";const B="_left_1gdw7_23",g="_right_1gdw7_29",e={"actions-bar":"_actions-bar_1gdw7_2","actions-bar-content":"_actions-bar-content_1gdw7_14",left:B,right:g},f=({children:i})=>i?t.jsx("div",{className:e.left,children:i}):null;try{ActionsBarStickyLeft.displayName="ActionsBarStickyLeft",ActionsBarStickyLeft.__docgenInfo={description:"",displayName:"ActionsBarStickyLeft",props:{}}}catch{}const x=({children:i})=>i?t.jsx("div",{className:e.right,children:i}):null;try{ActionsBarStickyRight.displayName="ActionsBarStickyRight",ActionsBarStickyRight.__docgenInfo={description:"",displayName:"ActionsBarStickyRight",props:{}}}catch{}const o=({children:i,className:l})=>{const a=h();return _.useEffect(()=>(a(c(!0)),()=>{a(c(!1))}),[]),t.jsx("div",{className:y(e["actions-bar"],l),"data-testid":"actions-bar",children:t.jsx("div",{className:e["actions-bar-content"],children:i})})};o.Left=f;o.Right=x;const s=o;try{o.displayName="ActionsBarSticky",o.__docgenInfo={description:"",displayName:"ActionsBarSticky",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const ct={title:"components/ActionsBarSticky",component:s},A=()=>t.jsx("div",{style:{position:"fixed",left:"0",right:"0"},children:t.jsx("div",{style:{width:"874px",height:"1500px",backgroundColor:"lightblue",margin:"auto"},children:t.jsxs(s,{children:[t.jsx(s.Left,{children:t.jsx(n,{children:"Bouton Gauche"})}),t.jsxs(s.Right,{children:[t.jsx(n,{children:"Bouton Droite"}),t.jsx(n,{children:"Autre bouton"}),t.jsx(n,{variant:u.SECONDARY,children:"Encore un"})]})]})})}),r=A.bind({});r.args={};var p,m,d;r.parameters={...r.parameters,docs:{...(p=r.parameters)==null?void 0:p.docs,source:{originalSource:`() => <div style={{
  position: 'fixed',
  left: '0',
  right: '0'
}}>
    <div style={{
    width: '874px',
    height: '1500px',
    backgroundColor: 'lightblue',
    margin: 'auto'
  }}>
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <Button>Bouton Gauche</Button>
        </ActionsBarSticky.Left>

        <ActionsBarSticky.Right>
          <Button>Bouton Droite</Button>
          <Button>Autre bouton</Button>
          <Button variant={ButtonVariant.SECONDARY}>Encore un</Button>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </div>
  </div>`,...(d=(m=r.parameters)==null?void 0:m.docs)==null?void 0:d.source}}};const pt=["Default"];export{r as Default,pt as __namedExportsOrder,ct as default};
