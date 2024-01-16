import{N as i}from"./useNotification-BPUqD-_w.js";import{j as u}from"./jsx-runtime-iXOPPpZ7.js";import{c as j}from"./index-XNbs-YUW.js";import{a as h,s as R,f as T}from"./stroke-clock-MEAc7ymH.js";import{f as z}from"./full-validate-UsEvEnOv.js";import{S as B}from"./SvgIcon-UUSKXfrA.js";import"./index-7OBYoplD.js";import"./_commonjsHelpers-4gQjN7DL.js";import"./reducer-JjEnXI3X.js";const C="_notification_1kzpj_2",w="_show_1kzpj_16",P="_animatetop_1kzpj_1",U="_hide_1kzpj_48",v="_icon_1kzpj_76",e={notification:C,show:w,animatetop:P,"with-sticky-action-bar":"_with-sticky-action-bar_1kzpj_23",hide:U,"is-success":"_is-success_1kzpj_60","is-error":"_is-error_1kzpj_64","is-pending":"_is-pending_1kzpj_68","is-information":"_is-information_1kzpj_72",icon:v},c=({notification:p,isVisible:x,isStickyBarOpen:O})=>{const{text:I,type:t}=p,V={[i.ERROR]:"alert",[i.SUCCESS]:"status",[i.PENDING]:"progressbar",[i.INFORMATION]:"status"}[t];let n=z;return t==="error"?n=h:t==="pending"?n=R:t==="information"&&(n=T),u.jsxs("div",{"data-testid":`global-notification-${t}`,className:j(e.notification,e[`is-${t||"success"}`],x?e.show:e.hide,O&&e["with-sticky-action-bar"]),role:V??"status",children:[u.jsx(B,{className:e.icon,src:n,alt:""}),I]})},A=c;try{c.displayName="NotificationToaster",c.__docgenInfo={description:"",displayName:"NotificationToaster",props:{notification:{defaultValue:null,description:"",name:"notification",required:!0,type:{name:"Notification"}},isVisible:{defaultValue:null,description:"",name:"isVisible",required:!0,type:{name:"boolean"}},isStickyBarOpen:{defaultValue:null,description:"",name:"isStickyBarOpen",required:!0,type:{name:"boolean"}}}}}catch{}const L={title:"ui-kit/Notification",component:A},o={args:{notification:{text:"Une erreur fatale est survenue",type:i.ERROR,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},s={args:{notification:{text:"Vos modifications ont bien été prises en compte",type:i.SUCCESS,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},r={args:{notification:{text:"Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes",type:i.PENDING,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},a={args:{notification:{text:"Ceci est une information",type:i.INFORMATION,duration:2e3},isVisible:!0,isStickyBarOpen:!1}};var f,m,l;o.parameters={...o.parameters,docs:{...(f=o.parameters)==null?void 0:f.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Une erreur fatale est survenue',
      type: NotificationTypeEnum.ERROR,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(l=(m=o.parameters)==null?void 0:m.docs)==null?void 0:l.source}}};var d,_,y;s.parameters={...s.parameters,docs:{...(d=s.parameters)==null?void 0:d.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte',
      type: NotificationTypeEnum.SUCCESS,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(y=(_=s.parameters)==null?void 0:_.docs)==null?void 0:y.source}}};var N,S,k;r.parameters={...r.parameters,docs:{...(N=r.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes',
      type: NotificationTypeEnum.PENDING,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(k=(S=r.parameters)==null?void 0:S.docs)==null?void 0:k.source}}};var E,b,g;a.parameters={...a.parameters,docs:{...(E=a.parameters)==null?void 0:E.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Ceci est une information',
      type: NotificationTypeEnum.INFORMATION,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...(g=(b=a.parameters)==null?void 0:b.docs)==null?void 0:g.source}}};const Q=["Error","Success","Pending","Information"];export{o as Error,a as Information,r as Pending,s as Success,Q as __namedExportsOrder,L as default};
