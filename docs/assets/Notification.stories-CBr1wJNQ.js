import{N as e}from"./useNotification-CZUtWPba.js";import{j as i}from"./jsx-runtime-X2b_N9AH.js";import{c as h}from"./index-BpvXyOxN.js";import{a as k,f as q}from"./full-info-CjIBQLHx.js";import{f as R}from"./full-validate-C6eD2hog.js";import{s as T}from"./stroke-clock-q3bMT6Oq.js";import{S as C}from"./SvgIcon-DP_815J1.js";import"./index-uCp2LrAq.js";import"./_commonjsHelpers-BosuxZz1.js";import"./reducer-Dy_COtve.js";const B="_notification_etgvq_2",j="_show_etgvq_16",w="_animatetop_etgvq_1",A="_hide_etgvq_48",F="_icon_etgvq_76",o={notification:B,show:j,animatetop:w,"with-sticky-action-bar":"_with-sticky-action-bar_etgvq_23",hide:A,"is-success":"_is-success_etgvq_60","is-error":"_is-error_etgvq_64","is-pending":"_is-pending_etgvq_68","is-information":"_is-information_etgvq_72",icon:F},P={[e.ERROR]:{role:"alert"},[e.SUCCESS]:{role:"status"},[e.PENDING]:{"aria-live":"polite"},[e.INFORMATION]:{role:"status"}};function U(t){const s=t.type;let n=R;return s==="error"?n=k:s==="pending"?n=T:s==="information"&&(n=q),i.jsxs(i.Fragment,{children:[i.jsx(C,{className:o.icon,src:n,alt:""}),t.text]})}const l=({notification:t,isVisible:s,isStickyBarOpen:n})=>{const V=Object.values(e),v=t?U(t):null;return i.jsx(i.Fragment,{children:V.map(r=>{const m=r===(t==null?void 0:t.type);return i.jsx("div",{"data-testid":`global-notification-${r}`,...P[r],children:i.jsx("div",{className:h(o.notification,o[`is-${r}`],s&&m?o.show:o.hide,n&&o["with-sticky-action-bar"]),children:m?v:null})},r)})})};try{l.displayName="NotificationToaster",l.__docgenInfo={description:"",displayName:"NotificationToaster",props:{notification:{defaultValue:null,description:"",name:"notification",required:!0,type:{name:"Notification | null"}},isVisible:{defaultValue:null,description:"",name:"isVisible",required:!0,type:{name:"boolean"}},isStickyBarOpen:{defaultValue:null,description:"",name:"isStickyBarOpen",required:!0,type:{name:"boolean"}}}}}catch{}const W={title:"ui-kit/Notification",component:l},a={args:{notification:{text:"Une erreur fatale est survenue",type:e.ERROR,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},c={args:{notification:{text:"Vos modifications ont bien été prises en compte",type:e.SUCCESS,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},p={args:{notification:{text:"Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes",type:e.PENDING,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},u={args:{notification:{text:"Ceci est une information",type:e.INFORMATION,duration:2e3},isVisible:!0,isStickyBarOpen:!1}};var f,d,_;a.parameters={...a.parameters,docs:{...(f=a.parameters)==null?void 0:f.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Une erreur fatale est survenue',
      type: NotificationTypeEnum.ERROR,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(_=(d=a.parameters)==null?void 0:d.docs)==null?void 0:_.source}}};var y,g,N;c.parameters={...c.parameters,docs:{...(y=c.parameters)==null?void 0:y.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte',
      type: NotificationTypeEnum.SUCCESS,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(N=(g=c.parameters)==null?void 0:g.docs)==null?void 0:N.source}}};var S,E,x;p.parameters={...p.parameters,docs:{...(S=p.parameters)==null?void 0:S.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes',
      type: NotificationTypeEnum.PENDING,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(x=(E=p.parameters)==null?void 0:E.docs)==null?void 0:x.source}}};var b,O,I;u.parameters={...u.parameters,docs:{...(b=u.parameters)==null?void 0:b.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Ceci est une information',
      type: NotificationTypeEnum.INFORMATION,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(I=(O=u.parameters)==null?void 0:O.docs)==null?void 0:I.source}}};const X=["Error","Success","Pending","Information"];export{a as Error,u as Information,p as Pending,c as Success,X as __namedExportsOrder,W as default};
