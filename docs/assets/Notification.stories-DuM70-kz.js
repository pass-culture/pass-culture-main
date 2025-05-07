import{N as e}from"./useNotification-Hw1Ms4y_.js";import{j as i}from"./jsx-runtime-BYYWji4R.js";import{c as O}from"./index-DeARc5FM.js";import{f as E,a as T}from"./full-info-C4RdBA4U.js";import{f as V}from"./full-validate-CbMNulkZ.js";import{S as k}from"./SvgIcon-CyWUmZpn.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./reducer-DQPuV9Vk.js";const R="_notification_fq0xs_1",q="_show_fq0xs_16",C="_animatetop_fq0xs_1",A="_hide_fq0xs_48",j="_icon_fq0xs_60",o={notification:R,show:q,animatetop:C,"with-sticky-action-bar":"_with-sticky-action-bar_fq0xs_23",hide:A,icon:j,"is-success":"_is-success_fq0xs_66","is-error":"_is-error_fq0xs_72","is-information":"_is-information_fq0xs_78"},f={[e.ERROR]:{role:"alert"},[e.SUCCESS]:{role:"status"},[e.INFORMATION]:{role:"status"}};function v(t){const r=t.type;let n=V;return r==="error"?n=E:r==="information"&&(n=T),i.jsxs(i.Fragment,{children:[i.jsx(k,{className:o.icon,src:n,alt:""}),t.text]})}const l=({notification:t,isVisible:r,isStickyBarOpen:n})=>{const g=Object.values(e),I=t?v(t):null;return i.jsx(i.Fragment,{children:g.map(s=>{const u=s===(t==null?void 0:t.type);return i.jsx("div",{"data-testid":`global-notification-${s}`,...f[s],children:i.jsx("div",{className:O(o.notification,o[`is-${s}`],r&&u?o.show:o.hide,n&&o["with-sticky-action-bar"]),children:u?I:null})},s)})})};try{f.displayName="notificationAdditionalAttributes",f.__docgenInfo={description:"Additional attributes for notifications based on their type.",displayName:"notificationAdditionalAttributes",props:{}}}catch{}try{l.displayName="NotificationToaster",l.__docgenInfo={description:`The NotificationToaster component is used to display notifications of different types.
It supports displaying notifications such as errors, information, success, or pending messages.

---
**Important: Use \`notification\` prop to provide the information to be displayed.**
---`,displayName:"NotificationToaster",props:{notification:{defaultValue:null,description:"The notification to display.",name:"notification",required:!0,type:{name:"Notification | null"}},isVisible:{defaultValue:null,description:"Indicates if the notification toaster is visible.",name:"isVisible",required:!0,type:{name:"boolean"}},isStickyBarOpen:{defaultValue:null,description:"Indicates if the sticky action bar is open.",name:"isStickyBarOpen",required:!0,type:{name:"boolean"}}}}}catch{}const H={title:"ui-kit/Notification",component:l},a={args:{notification:{text:"Une erreur fatale est survenue",type:e.ERROR,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},c={args:{notification:{text:"Vos modifications ont bien été prises en compte",type:e.SUCCESS,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},p={args:{notification:{text:"Ceci est une information",type:e.INFORMATION,duration:2e3},isVisible:!0,isStickyBarOpen:!1}};var d,m,_;a.parameters={...a.parameters,docs:{...(d=a.parameters)==null?void 0:d.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Une erreur fatale est survenue',
      type: NotificationTypeEnum.ERROR,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(_=(m=a.parameters)==null?void 0:m.docs)==null?void 0:_.source}}};var y,N,b;c.parameters={...c.parameters,docs:{...(y=c.parameters)==null?void 0:y.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte',
      type: NotificationTypeEnum.SUCCESS,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(b=(N=c.parameters)==null?void 0:N.docs)==null?void 0:b.source}}};var x,h,S;p.parameters={...p.parameters,docs:{...(x=p.parameters)==null?void 0:x.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Ceci est une information',
      type: NotificationTypeEnum.INFORMATION,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(S=(h=p.parameters)==null?void 0:h.docs)==null?void 0:S.source}}};const J=["Error","Success","Information"];export{a as Error,p as Information,c as Success,J as __namedExportsOrder,H as default};
