import{N as t}from"./useNotification-Dc9G6tZq.js";import{j as e}from"./jsx-runtime-Nms4Y4qS.js";import{c as h}from"./index-BpvXyOxN.js";import{a as R,f as T}from"./full-info-CjIBQLHx.js";import{f as C}from"./full-validate-C6eD2hog.js";import{s as B}from"./stroke-clock-q3bMT6Oq.js";import{S as j}from"./SvgIcon-Cibea2Sc.js";import"./index-BwDkhjyp.js";import"./_commonjsHelpers-BosuxZz1.js";import"./reducer-CrdWV-jI.js";const v="_notification_kyoit_1",w="_show_kyoit_15",A="_animatetop_kyoit_1",F="_hide_kyoit_47",P="_icon_kyoit_75",o={notification:v,show:w,animatetop:A,"with-sticky-action-bar":"_with-sticky-action-bar_kyoit_22",hide:F,"is-success":"_is-success_kyoit_59","is-error":"_is-error_kyoit_63","is-pending":"_is-pending_kyoit_67","is-information":"_is-information_kyoit_71",icon:P},U={[t.ERROR]:{role:"alert"},[t.SUCCESS]:{role:"status"},[t.PENDING]:{"aria-live":"polite"},[t.INFORMATION]:{role:"status"}};function q(i){const s=i.type;let n=C;return s==="error"?n=R:s==="pending"?n=B:s==="information"&&(n=T),e.jsxs(e.Fragment,{children:[e.jsx(j,{className:o.icon,src:n,alt:""}),i.text]})}const l=({notification:i,isVisible:s,isStickyBarOpen:n})=>{const I=Object.values(t),V=i?q(i):null;return e.jsx(e.Fragment,{children:I.map(r=>{const m=r===(i==null?void 0:i.type);return e.jsx("div",{"data-testid":`global-notification-${r}`,...U[r],children:e.jsx("div",{className:h(o.notification,o[`is-${r}`],s&&m?o.show:o.hide,n&&o["with-sticky-action-bar"]),children:m?V:null})},r)})})};try{l.displayName="NotificationToaster",l.__docgenInfo={description:"",displayName:"NotificationToaster",props:{notification:{defaultValue:null,description:"",name:"notification",required:!0,type:{name:"Notification | null"}},isVisible:{defaultValue:null,description:"",name:"isVisible",required:!0,type:{name:"boolean"}},isStickyBarOpen:{defaultValue:null,description:"",name:"isStickyBarOpen",required:!0,type:{name:"boolean"}}}}}catch{}const W={title:"ui-kit/Notification",component:l},a={args:{notification:{text:"Une erreur fatale est survenue",type:t.ERROR,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},c={args:{notification:{text:"Vos modifications ont bien été prises en compte",type:t.SUCCESS,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},p={args:{notification:{text:"Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes",type:t.PENDING,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},u={args:{notification:{text:"Ceci est une information",type:t.INFORMATION,duration:2e3},isVisible:!0,isStickyBarOpen:!1}};var f,d,y;a.parameters={...a.parameters,docs:{...(f=a.parameters)==null?void 0:f.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Une erreur fatale est survenue',
      type: NotificationTypeEnum.ERROR,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(y=(d=a.parameters)==null?void 0:d.docs)==null?void 0:y.source}}};var _,N,S;c.parameters={...c.parameters,docs:{...(_=c.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte',
      type: NotificationTypeEnum.SUCCESS,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(S=(N=c.parameters)==null?void 0:N.docs)==null?void 0:S.source}}};var k,g,b;p.parameters={...p.parameters,docs:{...(k=p.parameters)==null?void 0:k.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes',
      type: NotificationTypeEnum.PENDING,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(b=(g=p.parameters)==null?void 0:g.docs)==null?void 0:b.source}}};var O,E,x;u.parameters={...u.parameters,docs:{...(O=u.parameters)==null?void 0:O.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Ceci est une information',
      type: NotificationTypeEnum.INFORMATION,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(x=(E=u.parameters)==null?void 0:E.docs)==null?void 0:x.source}}};const X=["Error","Success","Pending","Information"];export{a as Error,u as Information,p as Pending,c as Success,X as __namedExportsOrder,W as default};
