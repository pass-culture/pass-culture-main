import{N as e}from"./useNotification-CK9wL7PI.js";import{j as t}from"./jsx-runtime-B1DX2IId.js";import{c as _}from"./index-SiKpzPJp.js";import{f as y}from"./full-error-BFAmjN4t.js";import{f as h}from"./full-info-D24AtBVt.js";import{f as N}from"./full-validate-CbMNulkZ.js";import{S as b}from"./SvgIcon-C2_OssJo.js";import"./iframe-DDnyRwP2.js";import"./preload-helper-PPVm8Dsz.js";import"./reducer-ral43S_Z.js";const S="_notification_1hwe5_1",g="_show_1hwe5_15",I="_animatetop_1hwe5_1",O="_hide_1hwe5_21",w="_icon_1hwe5_60",o={notification:S,show:g,animatetop:I,hide:O,"with-sticky-action-bar":"_with-sticky-action-bar_1hwe5_35",icon:w,"is-success":"_is-success_1hwe5_66","is-error":"_is-error_1hwe5_72","is-information":"_is-information_1hwe5_78"},f={[e.ERROR]:{role:"alert"},[e.SUCCESS]:{role:"status"},[e.INFORMATION]:{role:"status"}};function x(i){const r=i.type;let n=N;return r==="error"?n=y:r==="information"&&(n=h),t.jsxs(t.Fragment,{children:[t.jsx(b,{className:o.icon,src:n,alt:""}),i.text]})}const l=({notification:i,isVisible:r,isStickyBarOpen:n})=>{const d=Object.values(e),m=i?x(i):null;return t.jsx(t.Fragment,{children:d.map(s=>{const u=s===i?.type;return t.jsx("div",{"data-testid":`global-notification-${s}`,...f[s],children:t.jsx("div",{className:_(o.notification,o[`is-${s}`],r&&u?o.show:o.hide,n&&o["with-sticky-action-bar"]),children:u?m:null})},s)})})};try{f.displayName="notificationAdditionalAttributes",f.__docgenInfo={description:"Additional attributes for notifications based on their type.",displayName:"notificationAdditionalAttributes",props:{}}}catch{}try{l.displayName="NotificationToaster",l.__docgenInfo={description:`The NotificationToaster component is used to display notifications of different types.
It supports displaying notifications such as errors, information, success, or pending messages.

---
**Important: Use \`notification\` prop to provide the information to be displayed.**
---`,displayName:"NotificationToaster",props:{notification:{defaultValue:null,description:"The notification to display.",name:"notification",required:!0,type:{name:"Notification | null"}},isVisible:{defaultValue:null,description:"Indicates if the notification toaster is visible.",name:"isVisible",required:!0,type:{name:"boolean"}},isStickyBarOpen:{defaultValue:null,description:"Indicates if the sticky action bar is open.",name:"isStickyBarOpen",required:!0,type:{name:"boolean"}}}}}catch{}const U={title:"@/ui-kit/Notification",component:l},a={args:{notification:{text:"Une erreur fatale est survenue",type:e.ERROR,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},c={args:{notification:{text:"Vos modifications ont bien été prises en compte",type:e.SUCCESS,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},p={args:{notification:{text:"Ceci est une information",type:e.INFORMATION,duration:2e3},isVisible:!0,isStickyBarOpen:!1}};a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Une erreur fatale est survenue',
      type: NotificationTypeEnum.ERROR,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...a.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte',
      type: NotificationTypeEnum.SUCCESS,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...c.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Ceci est une information',
      type: NotificationTypeEnum.INFORMATION,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...p.parameters?.docs?.source}}};const F=["Error","Success","Information"];export{a as Error,p as Information,c as Success,F as __namedExportsOrder,U as default};
