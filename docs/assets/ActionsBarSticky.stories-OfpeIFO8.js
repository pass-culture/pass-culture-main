import{j as t}from"./jsx-runtime-iXOPPpZ7.js";import"./Divider-f9FLuLUl.js";import"./SubmitButton-Ge6mKZ3q.js";import{B as u}from"./ButtonLink-F8DjXt38.js";import{B as n}from"./Button-cvvoQF_u.js";import"./Thumb-guOMJzTh.js";import"./stroke-offer-IDmBYzSD.js";import"./Banner-zdVJZGFG.js";import"./InfoBox-NzD_Rw55.js";import{c as y}from"./index-XNbs-YUW.js";import{r as _}from"./index-7OBYoplD.js";import{u as h,s as a}from"./reducer-ZpzU-k3-.js";import"./index-wDWIojKA.js";import"./index-NZh7eYUr.js";import"./_commonjsHelpers-4gQjN7DL.js";import"./SvgIcon-UUSKXfrA.js";import"./Button.module-fn58QZwY.js";import"./stroke-pass-84wyy11D.js";import"./Tooltip-eetddggC.js";import"./useTooltipProps-Xf9SOXrU.js";import"./formik.esm-y2tUiI7x.js";import"./full-next-6FYpialQ.js";import"./BaseRadio-xu3uA8eL.js";import"./FieldError-_oiQB8Lp.js";import"./stroke-error-U5wg3Vd5.js";import"./FieldSuccess-KBPQwpG2.js";import"./stroke-valid-qcZpl8lN.js";import"./full-clear-0L2gsxg_.js";import"./index-VFMbf6KQ.js";import"./SelectInput-jQXa9fZk.js";import"./stroke-down-4xbrRvHV.js";import"./BaseCheckbox-RovcbSrG.js";import"./typeof-Q9eVcF_1.js";import"./BaseInput-pWPiF78D.js";import"./shadow-tips-help-vs0tLBP5.js";import"./shadow-tips-warning-og_aO0Ug.js";import"./stroke-close-KQNU-49n.js";import"./LinkNodes-0xDMeRU2.js";import"./full-link-GGegv9yK.js";const B="_left_1rp61_23",f="_right_1rp61_29",e={"actions-bar":"_actions-bar_1rp61_2","actions-bar-content":"_actions-bar-content_1rp61_14",left:B,right:f},g=({children:r})=>r?t.jsx("div",{className:e.left,children:r}):null;try{ActionsBarStickyLeft.displayName="ActionsBarStickyLeft",ActionsBarStickyLeft.__docgenInfo={description:"",displayName:"ActionsBarStickyLeft",props:{}}}catch{}const x=({children:r})=>r?t.jsx("div",{className:e.right,children:r}):null;try{ActionsBarStickyRight.displayName="ActionsBarStickyRight",ActionsBarStickyRight.__docgenInfo={description:"",displayName:"ActionsBarStickyRight",props:{}}}catch{}const o=({children:r,className:d})=>{const c=h();return _.useEffect(()=>(c(a(!0)),()=>{c(a(!1))}),[]),t.jsx("div",{className:y(e["actions-bar"],d),"data-testid":"actions-bar",children:t.jsx("div",{className:e["actions-bar-content"],children:r})})};o.Left=g;o.Right=x;const s=o;try{o.displayName="ActionsBarSticky",o.__docgenInfo={description:"",displayName:"ActionsBarSticky",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const ct={title:"components/ActionsBarSticky",component:s},A=()=>t.jsx("div",{style:{position:"fixed",left:"0",right:"0"},children:t.jsx("div",{style:{width:"874px",height:"1500px",backgroundColor:"lightblue",margin:"auto"},children:t.jsxs(s,{children:[t.jsx(s.Left,{children:t.jsx(n,{children:"Bouton Gauche"})}),t.jsxs(s.Right,{children:[t.jsx(n,{children:"Bouton Droite"}),t.jsx(n,{children:"Autre bouton"}),t.jsx(n,{variant:u.SECONDARY,children:"Encore un"})]})]})})}),i=A.bind({});i.args={};var p,m,l;i.parameters={...i.parameters,docs:{...(p=i.parameters)==null?void 0:p.docs,source:{originalSource:`() => <div style={{
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
  </div>`,...(l=(m=i.parameters)==null?void 0:m.docs)==null?void 0:l.source}}};const at=["Default"];export{i as Default,at as __namedExportsOrder,ct as default};
