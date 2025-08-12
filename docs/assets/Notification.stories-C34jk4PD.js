import{N as e}from"./useNotification-B77nyyBk.js";import{j as i}from"./jsx-runtime-DF2Pcvd1.js";import{c as O}from"./index-DeARc5FM.js";import{f as w}from"./full-error-BFAmjN4t.js";import{f as x}from"./full-info-D24AtBVt.js";import{f as E}from"./full-validate-CbMNulkZ.js";import{S as T}from"./SvgIcon-DfLnDDE5.js";import"./index-B2-qRKKC.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./reducer-XOjost4E.js";const V="_notification_8wck4_1",R="_show_8wck4_15",C="_animatetop_8wck4_1",A="_hide_8wck4_21",j="_icon_8wck4_64",o={notification:V,show:R,animatetop:C,hide:A,"with-sticky-action-bar":"_with-sticky-action-bar_8wck4_36",icon:j,"is-success":"_is-success_8wck4_70","is-error":"_is-error_8wck4_76","is-information":"_is-information_8wck4_82"},l={[e.ERROR]:{role:"alert"},[e.SUCCESS]:{role:"status"},[e.INFORMATION]:{role:"status"}};function v(t){const r=t.type;let n=E;return r==="error"?n=w:r==="information"&&(n=x),i.jsxs(i.Fragment,{children:[i.jsx(T,{className:o.icon,src:n,alt:""}),t.text]})}const f=({notification:t,isVisible:r,isStickyBarOpen:n})=>{const g=Object.values(e),I=t?v(t):null;return i.jsx(i.Fragment,{children:g.map(s=>{const u=s===(t==null?void 0:t.type);return i.jsx("div",{"data-testid":`global-notification-${s}`,...l[s],children:i.jsx("div",{className:O(o.notification,o[`is-${s}`],r&&u?o.show:o.hide,n&&o["with-sticky-action-bar"]),children:u?I:null})},s)})})};try{l.displayName="notificationAdditionalAttributes",l.__docgenInfo={description:"Additional attributes for notifications based on their type.",displayName:"notificationAdditionalAttributes",props:{}}}catch{}try{f.displayName="NotificationToaster",f.__docgenInfo={description:`The NotificationToaster component is used to display notifications of different types.
It supports displaying notifications such as errors, information, success, or pending messages.

---
**Important: Use \`notification\` prop to provide the information to be displayed.**
---`,displayName:"NotificationToaster",props:{notification:{defaultValue:null,description:"The notification to display.",name:"notification",required:!0,type:{name:"Notification | null"}},isVisible:{defaultValue:null,description:"Indicates if the notification toaster is visible.",name:"isVisible",required:!0,type:{name:"boolean"}},isStickyBarOpen:{defaultValue:null,description:"Indicates if the sticky action bar is open.",name:"isStickyBarOpen",required:!0,type:{name:"boolean"}}}}}catch{}const J={title:"@/ui-kit/Notification",component:f},a={args:{notification:{text:"Une erreur fatale est survenue",type:e.ERROR,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},c={args:{notification:{text:"Vos modifications ont bien été prises en compte",type:e.SUCCESS,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},p={args:{notification:{text:"Ceci est une information",type:e.INFORMATION,duration:2e3},isVisible:!0,isStickyBarOpen:!1}};var d,m,_;a.parameters={...a.parameters,docs:{...(d=a.parameters)==null?void 0:d.docs,source:{originalSource:`{
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
}`,...(b=(N=c.parameters)==null?void 0:N.docs)==null?void 0:b.source}}};var h,S,k;p.parameters={...p.parameters,docs:{...(h=p.parameters)==null?void 0:h.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Ceci est une information',
      type: NotificationTypeEnum.INFORMATION,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(k=(S=p.parameters)==null?void 0:S.docs)==null?void 0:k.source}}};const K=["Error","Success","Information"];export{a as Error,p as Information,c as Success,K as __namedExportsOrder,J as default};
