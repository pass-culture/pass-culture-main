import{a as r}from"./useNotification-B9ZSSRl6.js";import{N as n}from"./NotificationToaster-byUF2wLH.js";import"./iframe-BxP3Y0_X.js";import"./preload-helper-PPVm8Dsz.js";import"./useAppDispatch-tk1F-JA2.js";import"./jsx-runtime-B_Iz8bUM.js";import"./index-CMdvf5F_.js";import"./full-error-BFAmjN4t.js";import"./full-info-D24AtBVt.js";import"./full-validate-CbMNulkZ.js";import"./SvgIcon-Dri04nvy.js";const y={title:"@/ui-kit/Notification",component:n},t={args:{notification:{text:"Une erreur fatale est survenue",type:r.ERROR,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},e={args:{notification:{text:"Vos modifications ont bien été prises en compte",type:r.SUCCESS,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},i={args:{notification:{text:"Ceci est une information",type:r.INFORMATION,duration:2e3},isVisible:!0,isStickyBarOpen:!1}};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Une erreur fatale est survenue',
      type: NotificationTypeEnum.ERROR,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...t.parameters?.docs?.source}}};e.parameters={...e.parameters,docs:{...e.parameters?.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Vos modifications ont bien été prises en compte',
      type: NotificationTypeEnum.SUCCESS,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...e.parameters?.docs?.source}}};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
  args: {
    notification: {
      text: 'Ceci est une information',
      type: NotificationTypeEnum.INFORMATION,
      duration: 2000
    },
    isVisible: true,
    isStickyBarOpen: false
  }
}`,...i.parameters?.docs?.source}}};const O=["Error","Success","Information"];export{t as Error,i as Information,e as Success,O as __namedExportsOrder,y as default};
