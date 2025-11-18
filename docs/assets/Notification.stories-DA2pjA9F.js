import{N as r}from"./useNotification-C0LXNklT.js";import{N as n}from"./NotificationToaster-DZnR52BW.js";import"./iframe-D_D4c47g.js";import"./preload-helper-PPVm8Dsz.js";import"./reducer-Ctaoq3dz.js";import"./jsx-runtime-CMYnqTIL.js";import"./index-BxVkhXlM.js";import"./full-error-BFAmjN4t.js";import"./full-info-D24AtBVt.js";import"./full-validate-CbMNulkZ.js";import"./SvgIcon-CwC58bdP.js";const y={title:"@/ui-kit/Notification",component:n},t={args:{notification:{text:"Une erreur fatale est survenue",type:r.ERROR,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},e={args:{notification:{text:"Vos modifications ont bien été prises en compte",type:r.SUCCESS,duration:2e3},isVisible:!0,isStickyBarOpen:!1}},i={args:{notification:{text:"Ceci est une information",type:r.INFORMATION,duration:2e3},isVisible:!0,isStickyBarOpen:!1}};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
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
}`,...i.parameters?.docs?.source}}};const N=["Error","Success","Information"];export{t as Error,i as Information,e as Success,N as __namedExportsOrder,y as default};
