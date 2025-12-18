import{a as r}from"./useNotification-BkMmLjAH.js";import{N as n}from"./NotificationToaster-DS17PI1P.js";import"./iframe-BwS0vLmz.js";import"./preload-helper-PPVm8Dsz.js";import"./useAppDispatch-9uUNVQHU.js";import"./jsx-runtime-u9BubJ5t.js";import"./index-Nv1AjDZT.js";import"./full-error-BFAmjN4t.js";import"./full-info-D24AtBVt.js";import"./full-validate-CbMNulkZ.js";import"./SvgIcon-CYTW49oR.js";const y={title:"@/ui-kit/Notification",component:n},t={args:{notification:{text:"Une erreur fatale est survenue",type:r.ERROR,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},e={args:{notification:{text:"Vos modifications ont bien été prises en compte",type:r.SUCCESS,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},i={args:{notification:{text:"Ceci est une information",type:r.INFORMATION,duration:2e3},isVisible:!0,isStickyBarOpen:!1}};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
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
