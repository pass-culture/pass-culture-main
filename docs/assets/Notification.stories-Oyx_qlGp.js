import{N as t}from"./useNotification-DH1N_LNo.js";import{j as u}from"./jsx-runtime-CKrituN3.js";import{c as v}from"./index-BpvXyOxN.js";import{a as h,f as q}from"./full-info-CjIBQLHx.js";import{f as R}from"./full-validate-C6eD2hog.js";import{s as T}from"./stroke-clock-q3bMT6Oq.js";import{S as B}from"./SvgIcon-B4BQC89V.js";import"./index-CBqU2yxZ.js";import"./_commonjsHelpers-BosuxZz1.js";import"./reducer-BPMj4Pds.js";const C="_notification_etgvq_2",w="_show_etgvq_16",P="_animatetop_etgvq_1",U="_hide_etgvq_48",j="_icon_etgvq_76",e={notification:C,show:w,animatetop:P,"with-sticky-action-bar":"_with-sticky-action-bar_etgvq_23",hide:U,"is-success":"_is-success_etgvq_60","is-error":"_is-error_etgvq_64","is-pending":"_is-pending_etgvq_68","is-information":"_is-information_etgvq_72",icon:j},c=({notification:p,isVisible:O,isStickyBarOpen:I})=>{const{text:V,type:i}=p,k={[t.ERROR]:"alert",[t.SUCCESS]:"status",[t.PENDING]:"progressbar",[t.INFORMATION]:"status"}[i];let o=R;return i==="error"?o=h:i==="pending"?o=T:i==="information"&&(o=q),u.jsxs("div",{"data-testid":`global-notification-${i}`,className:v(e.notification,e[`is-${i}`],O?e.show:e.hide,I&&e["with-sticky-action-bar"]),role:k,children:[u.jsx(B,{className:e.icon,src:o,alt:""}),V]})},A=c;try{c.displayName="NotificationToaster",c.__docgenInfo={description:"",displayName:"NotificationToaster",props:{notification:{defaultValue:null,description:"",name:"notification",required:!0,type:{name:"Notification"}},isVisible:{defaultValue:null,description:"",name:"isVisible",required:!0,type:{name:"boolean"}},isStickyBarOpen:{defaultValue:null,description:"",name:"isStickyBarOpen",required:!0,type:{name:"boolean"}}}}}catch{}const Q={title:"ui-kit/Notification",component:A},n={args:{notification:{text:"Une erreur fatale est survenue",type:t.ERROR,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},s={args:{notification:{text:"Vos modifications ont bien été prises en compte",type:t.SUCCESS,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},r={args:{notification:{text:"Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes",type:t.PENDING,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},a={args:{notification:{text:"Ceci est une information",type:t.INFORMATION,duration:2e3},isVisible:!0,isStickyBarOpen:!1}};var m,f,l;n.parameters={...n.parameters,docs:{...(m=n.parameters)==null?void 0:m.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Une erreur fatale est survenue',
      type: NotificationTypeEnum.ERROR,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(l=(f=n.parameters)==null?void 0:f.docs)==null?void 0:l.source}}};var d,_,y;s.parameters={...s.parameters,docs:{...(d=s.parameters)==null?void 0:d.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte',
      type: NotificationTypeEnum.SUCCESS,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(y=(_=s.parameters)==null?void 0:_.docs)==null?void 0:y.source}}};var g,N,S;r.parameters={...r.parameters,docs:{...(g=r.parameters)==null?void 0:g.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes',
      type: NotificationTypeEnum.PENDING,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(S=(N=r.parameters)==null?void 0:N.docs)==null?void 0:S.source}}};var E,b,x;a.parameters={...a.parameters,docs:{...(E=a.parameters)==null?void 0:E.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Ceci est une information',
      type: NotificationTypeEnum.INFORMATION,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(x=(b=a.parameters)==null?void 0:b.docs)==null?void 0:x.source}}};const W=["Error","Success","Pending","Information"];export{n as Error,a as Information,r as Pending,s as Success,W as __namedExportsOrder,Q as default};
