import{j as t}from"./jsx-runtime-ffb262ed.js";import"./Divider-7c035ea9.js";import"./SubmitButton-921b5e85.js";import{B as n,a as u}from"./Button-b5b8096d.js";import"./Thumb-f5d614ec.js";import"./stroke-offer-ff89e161.js";import"./Banner-de45740d.js";import"./InfoBox-660b7495.js";import{c as y}from"./index-a587463d.js";import{r as _}from"./index-76fb7be0.js";import{u as h,s as c}from"./notificationReducer-5f6175f5.js";import"./index-48a71f03.js";import"./hoist-non-react-statics.cjs-3f8ebaa8.js";import"./react-is.production.min-a192e302.js";import"./index-c6e8a24e.js";import"./full-right-83efe067.js";import"./SvgIcon-c0bf369c.js";import"./Button.module-ec1646c9.js";import"./stroke-pass-cf331655.js";import"./Tooltip-7f0a196a.js";import"./useTooltipProps-b20503ef.js";import"./formik.esm-49513253.js";import"./_commonjsHelpers-de833af9.js";import"./full-next-ebff3494.js";import"./BaseCheckbox-10462bad.js";import"./BaseFileInput-5ea36249.js";import"./BaseRadio-06d1d75a.js";import"./FieldError-10cbd29d.js";import"./stroke-error-ed5fe82d.js";import"./FieldSuccess-31bdacb0.js";import"./stroke-valid-9c345a33.js";import"./full-clear-9268779e.js";import"./index-9d475cdf.js";import"./SelectInput-cdc4214a.js";import"./stroke-down-3d79f44b.js";import"./typeof-7fd5df1e.js";import"./BaseInput-433b1c48.js";import"./stroke-close-3a7bfe9e.js";import"./shadow-tips-help-841f916a.js";import"./shadow-tips-warning-66fb0429.js";import"./LinkNodes-6435e7bb.js";import"./full-link-9eb5e1cb.js";const B="_left_1gdw7_23",g="_right_1gdw7_29",e={"actions-bar":"_actions-bar_1gdw7_2","actions-bar-content":"_actions-bar-content_1gdw7_14",left:B,right:g},f=({children:i})=>i?t.jsx("div",{className:e.left,children:i}):null;try{ActionsBarStickyLeft.displayName="ActionsBarStickyLeft",ActionsBarStickyLeft.__docgenInfo={description:"",displayName:"ActionsBarStickyLeft",props:{}}}catch{}const x=({children:i})=>i?t.jsx("div",{className:e.right,children:i}):null;try{ActionsBarStickyRight.displayName="ActionsBarStickyRight",ActionsBarStickyRight.__docgenInfo={description:"",displayName:"ActionsBarStickyRight",props:{}}}catch{}const o=({children:i,className:l})=>{const a=h();return _.useEffect(()=>(a(c(!0)),()=>{a(c(!1))}),[]),t.jsx("div",{className:y(e["actions-bar"],l),"data-testid":"actions-bar",children:t.jsx("div",{className:e["actions-bar-content"],children:i})})};o.Left=f;o.Right=x;const s=o;try{o.displayName="ActionsBarSticky",o.__docgenInfo={description:"",displayName:"ActionsBarSticky",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const mt={title:"components/ActionsBarSticky",component:s},A=()=>t.jsx("div",{style:{position:"fixed",left:"0",right:"0"},children:t.jsx("div",{style:{width:"874px",height:"1500px",backgroundColor:"lightblue",margin:"auto"},children:t.jsxs(s,{children:[t.jsx(s.Left,{children:t.jsx(n,{children:"Bouton Gauche"})}),t.jsxs(s.Right,{children:[t.jsx(n,{children:"Bouton Droite"}),t.jsx(n,{children:"Autre bouton"}),t.jsx(n,{variant:u.SECONDARY,children:"Encore un"})]})]})})}),r=A.bind({});r.args={};var p,m,d;r.parameters={...r.parameters,docs:{...(p=r.parameters)==null?void 0:p.docs,source:{originalSource:`() => <div style={{
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
  </div>`,...(d=(m=r.parameters)==null?void 0:m.docs)==null?void 0:d.source}}};const dt=["Default"];export{r as Default,dt as __namedExportsOrder,mt as default};
