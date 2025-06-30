import{j as e}from"./jsx-runtime-DF2Pcvd1.js";import{s as d,a as g}from"./stroke-right-DelDNWyg.js";import{S as i}from"./SvgIcon-DfLnDDE5.js";import"./index-B2-qRKKC.js";import"./_commonjsHelpers-Cpj98o6Y.js";const m="_pagination_y4xzm_1",b="_button_y4xzm_11",o={pagination:m,button:b},r=({currentPage:t,onPreviousPageClick:l,onNextPageClick:p,pageCount:a})=>a>1?e.jsxs("div",{className:o.pagination,children:[e.jsx("button",{disabled:t===1,onClick:l,type:"button",className:o.button,children:e.jsx(i,{src:d,alt:"Page précédente",width:"16"})}),e.jsxs("span",{children:["Page ",t,"/",a]}),e.jsx("button",{disabled:t>=a,onClick:p,type:"button",className:o.button,"data-testid":"next-page-button",children:e.jsx(i,{src:g,alt:"Page suivante",width:"16"})})]}):null;try{r.displayName="Pagination",r.__docgenInfo={description:`The Pagination component allows navigation between different pages of content.
It includes buttons to move to the previous or next page, as well as an indicator for the current page.

---
**Important: Make sure to handle the \`onPreviousPageClick\` and \`onNextPageClick\` callbacks to update the page correctly.**
---`,displayName:"Pagination",props:{currentPage:{defaultValue:null,description:"The current page number.",name:"currentPage",required:!0,type:{name:"number"}},pageCount:{defaultValue:null,description:"The total number of pages.",name:"pageCount",required:!0,type:{name:"number"}},onPreviousPageClick:{defaultValue:null,description:"Callback function triggered when the previous page button is clicked.",name:"onPreviousPageClick",required:!0,type:{name:"() => void"}},onNextPageClick:{defaultValue:null,description:"Callback function triggered when the next page button is clicked.",name:"onNextPageClick",required:!0,type:{name:"() => void"}}}}}catch{}const _={title:"ui-kit/Pagination",component:r},n={args:{currentPage:3,pageCount:10}};var s,c,u;n.parameters={...n.parameters,docs:{...(s=n.parameters)==null?void 0:s.docs,source:{originalSource:`{
  args: {
    currentPage: 3,
    pageCount: 10
  }
}`,...(u=(c=n.parameters)==null?void 0:c.docs)==null?void 0:u.source}}};const y=["Default"];export{n as Default,y as __namedExportsOrder,_ as default};
