import{j as e}from"./jsx-runtime-CAkBUqSG.js";import{s as u,a as l}from"./stroke-right-DelDNWyg.js";import{S as i}from"./SvgIcon-Cfr_u84J.js";import"./iframe-7r54S_oo.js";import"./preload-helper-PPVm8Dsz.js";const p="_pagination_wrgeu_1",d="_button_wrgeu_11",o={pagination:p,button:d},r=({currentPage:t,onPreviousPageClick:s,onNextPageClick:c,pageCount:a})=>a>1?e.jsxs("div",{className:o.pagination,children:[e.jsx("button",{disabled:t===1,onClick:s,type:"button",className:o.button,children:e.jsx(i,{src:u,alt:"Page précédente",width:"16"})}),e.jsxs("span",{children:["Page ",t,"/",a]}),e.jsx("button",{disabled:t>=a,onClick:c,type:"button",className:o.button,"data-testid":"next-page-button",children:e.jsx(i,{src:l,alt:"Page suivante",width:"16"})})]}):null;try{r.displayName="Pagination",r.__docgenInfo={description:`The Pagination component allows navigation between different pages of content.
It includes buttons to move to the previous or next page, as well as an indicator for the current page.

---
**Important: Make sure to handle the \`onPreviousPageClick\` and \`onNextPageClick\` callbacks to update the page correctly.**
---`,displayName:"Pagination",props:{currentPage:{defaultValue:null,description:"The current page number.",name:"currentPage",required:!0,type:{name:"number"}},pageCount:{defaultValue:null,description:"The total number of pages.",name:"pageCount",required:!0,type:{name:"number"}},onPreviousPageClick:{defaultValue:null,description:"Callback function triggered when the previous page button is clicked.",name:"onPreviousPageClick",required:!0,type:{name:"() => void"}},onNextPageClick:{defaultValue:null,description:"Callback function triggered when the next page button is clicked.",name:"onNextPageClick",required:!0,type:{name:"() => void"}}}}}catch{}const f={title:"@/ui-kit/Pagination",component:r},n={args:{currentPage:3,pageCount:10}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 3,
    pageCount: 10
  }
}`,...n.parameters?.docs?.source}}};const k=["Default"];export{n as Default,k as __namedExportsOrder,f as default};
