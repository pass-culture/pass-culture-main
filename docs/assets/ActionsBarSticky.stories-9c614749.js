import{j as t}from"./jsx-runtime-4cb93332.js";import"./Divider-98b6f559.js";import"./SubmitButton-5794aeb7.js";import{B as n,a as u}from"./Button-a27a2a57.js";import"./Thumb-5b544978.js";import"./stroke-offer-db646768.js";import"./Banner-f287853f.js";import"./InfoBox-910ddbb0.js";import{c as y}from"./index-a587463d.js";import{r as _}from"./index-83a10e79.js";import{u as h,s as c}from"./reducer-486709eb.js";import"./index-4a87243b.js";import"./index-a9c6ff12.js";import"./_commonjsHelpers-de833af9.js";import"./full-right-83efe067.js";import"./SvgIcon-04d0ac1c.js";import"./Button.module-ec1646c9.js";import"./stroke-pass-cf331655.js";import"./Tooltip-1aec8863.js";import"./useTooltipProps-e39310f5.js";import"./formik.esm-8d42c991.js";import"./full-next-ebff3494.js";import"./BaseCheckbox-a0b74514.js";import"./BaseFileInput-baa5bac9.js";import"./BaseRadio-4cf2ec4b.js";import"./FieldError-66875701.js";import"./stroke-error-ed5fe82d.js";import"./FieldSuccess-7104acd6.js";import"./stroke-valid-9c345a33.js";import"./full-clear-9268779e.js";import"./index-9d475cdf.js";import"./SelectInput-394a5c6a.js";import"./stroke-down-3d79f44b.js";import"./typeof-7fd5df1e.js";import"./BaseInput-0dfdd1cf.js";import"./stroke-close-3a7bfe9e.js";import"./shadow-tips-help-841f916a.js";import"./shadow-tips-warning-66fb0429.js";import"./LinkNodes-b886ae87.js";import"./full-link-9eb5e1cb.js";const B="_left_1gdw7_23",g="_right_1gdw7_29",e={"actions-bar":"_actions-bar_1gdw7_2","actions-bar-content":"_actions-bar-content_1gdw7_14",left:B,right:g},f=({children:i})=>i?t.jsx("div",{className:e.left,children:i}):null;try{ActionsBarStickyLeft.displayName="ActionsBarStickyLeft",ActionsBarStickyLeft.__docgenInfo={description:"",displayName:"ActionsBarStickyLeft",props:{}}}catch{}const x=({children:i})=>i?t.jsx("div",{className:e.right,children:i}):null;try{ActionsBarStickyRight.displayName="ActionsBarStickyRight",ActionsBarStickyRight.__docgenInfo={description:"",displayName:"ActionsBarStickyRight",props:{}}}catch{}const o=({children:i,className:l})=>{const a=h();return _.useEffect(()=>(a(c(!0)),()=>{a(c(!1))}),[]),t.jsx("div",{className:y(e["actions-bar"],l),"data-testid":"actions-bar",children:t.jsx("div",{className:e["actions-bar-content"],children:i})})};o.Left=f;o.Right=x;const s=o;try{o.displayName="ActionsBarSticky",o.__docgenInfo={description:"",displayName:"ActionsBarSticky",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const ct={title:"components/ActionsBarSticky",component:s},A=()=>t.jsx("div",{style:{position:"fixed",left:"0",right:"0"},children:t.jsx("div",{style:{width:"874px",height:"1500px",backgroundColor:"lightblue",margin:"auto"},children:t.jsxs(s,{children:[t.jsx(s.Left,{children:t.jsx(n,{children:"Bouton Gauche"})}),t.jsxs(s.Right,{children:[t.jsx(n,{children:"Bouton Droite"}),t.jsx(n,{children:"Autre bouton"}),t.jsx(n,{variant:u.SECONDARY,children:"Encore un"})]})]})})}),r=A.bind({});r.args={};var p,m,d;r.parameters={...r.parameters,docs:{...(p=r.parameters)==null?void 0:p.docs,source:{originalSource:`() => <div style={{
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
