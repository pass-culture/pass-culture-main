import{N as t}from"./useNotification-CD_dQXuX.js";import{j as e}from"./jsx-runtime-BYYWji4R.js";import{c as T}from"./index-DeARc5FM.js";import{f as R,a as C}from"./full-info-C4RdBA4U.js";import{f as A}from"./full-validate-CbMNulkZ.js";import{s as B}from"./stroke-clock-DmvBMnFt.js";import{S as v}from"./SvgIcon-CyWUmZpn.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./reducer-Crbp5051.js";const j="_notification_kyoit_1",w="_show_kyoit_15",U="_animatetop_kyoit_1",F="_hide_kyoit_47",P="_icon_kyoit_75",n={notification:j,show:w,animatetop:U,"with-sticky-action-bar":"_with-sticky-action-bar_kyoit_22",hide:F,"is-success":"_is-success_kyoit_59","is-error":"_is-error_kyoit_63","is-pending":"_is-pending_kyoit_67","is-information":"_is-information_kyoit_71",icon:P},l={[t.ERROR]:{role:"alert"},[t.SUCCESS]:{role:"status"},[t.PENDING]:{"aria-live":"polite"},[t.INFORMATION]:{role:"status"}};function q(i){const s=i.type;let o=A;return s==="error"?o=R:s==="pending"?o=B:s==="information"&&(o=C),e.jsxs(e.Fragment,{children:[e.jsx(v,{className:n.icon,src:o,alt:""}),i.text]})}const d=({notification:i,isVisible:s,isStickyBarOpen:o})=>{const x=Object.values(t),V=i?q(i):null;return e.jsx(e.Fragment,{children:x.map(r=>{const f=r===(i==null?void 0:i.type);return e.jsx("div",{"data-testid":`global-notification-${r}`,...l[r],children:e.jsx("div",{className:T(n.notification,n[`is-${r}`],s&&f?n.show:n.hide,o&&n["with-sticky-action-bar"]),children:f?V:null})},r)})})};try{l.displayName="notificationAdditionalAttributes",l.__docgenInfo={description:"Additional attributes for notifications based on their type.",displayName:"notificationAdditionalAttributes",props:{}}}catch{}try{d.displayName="NotificationToaster",d.__docgenInfo={description:`The NotificationToaster component is used to display notifications of different types.
It supports displaying notifications such as errors, information, success, or pending messages.

---
**Important: Use \`notification\` prop to provide the information to be displayed.**
---`,displayName:"NotificationToaster",props:{notification:{defaultValue:null,description:"The notification to display.",name:"notification",required:!0,type:{name:"Notification | null"}},isVisible:{defaultValue:null,description:"Indicates if the notification toaster is visible.",name:"isVisible",required:!0,type:{name:"boolean"}},isStickyBarOpen:{defaultValue:null,description:"Indicates if the sticky action bar is open.",name:"isStickyBarOpen",required:!0,type:{name:"boolean"}}}}}catch{}const W={title:"ui-kit/Notification",component:d},a={args:{notification:{text:"Une erreur fatale est survenue",type:t.ERROR,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},c={args:{notification:{text:"Vos modifications ont bien été prises en compte",type:t.SUCCESS,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},p={args:{notification:{text:"Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes",type:t.PENDING,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},u={args:{notification:{text:"Ceci est une information",type:t.INFORMATION,duration:2e3},isVisible:!0,isStickyBarOpen:!1}};var m,y,_;a.parameters={...a.parameters,docs:{...(m=a.parameters)==null?void 0:m.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Une erreur fatale est survenue',
      type: NotificationTypeEnum.ERROR,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(_=(y=a.parameters)==null?void 0:y.docs)==null?void 0:_.source}}};var N,b,g;c.parameters={...c.parameters,docs:{...(N=c.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte',
      type: NotificationTypeEnum.SUCCESS,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(g=(b=c.parameters)==null?void 0:b.docs)==null?void 0:g.source}}};var k,S,h;p.parameters={...p.parameters,docs:{...(k=p.parameters)==null?void 0:k.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes',
      type: NotificationTypeEnum.PENDING,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(h=(S=p.parameters)==null?void 0:S.docs)==null?void 0:h.source}}};var I,O,E;u.parameters={...u.parameters,docs:{...(I=u.parameters)==null?void 0:I.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Ceci est une information',
      type: NotificationTypeEnum.INFORMATION,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(E=(O=u.parameters)==null?void 0:O.docs)==null?void 0:E.source}}};const X=["Error","Success","Pending","Information"];export{a as Error,u as Information,p as Pending,c as Success,X as __namedExportsOrder,W as default};
