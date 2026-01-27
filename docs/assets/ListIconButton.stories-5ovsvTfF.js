import{j as t}from"./jsx-runtime-C_uOM0Gm.js";import{f}from"./full-trash-CEfIUI4M.js";import{c as o}from"./index-TscbDd2H.js";import{r as I}from"./iframe-CTnXOULQ.js";import{L}from"./chunk-EPOLDU6W-u6n6pb5J.js";import{S as k}from"./SvgIcon-CJiY4LCz.js";import{T}from"./Tooltip-GJ5PEk5n.js";import"./preload-helper-PPVm8Dsz.js";const C="_button_1dy02_1",w="_tooltip_1dy02_36",e={button:C,"button-icon":"_button-icon_1dy02_24",tooltip:w,"variant-primary":"_variant-primary_1dy02_40"},E="16",i=I.forwardRef(({className:n,variant:s="default",tooltipContent:d,icon:h,onClick:l,url:u,isExternal:b=!0,dataTestid:g,target:p,...y},_)=>{const c=t.jsx(k,{src:h,alt:"",className:o(e["button-icon"]),width:E}),x=t.jsx("button",{className:o(e.button,e[`variant-${s}`],n),ref:_,...y,onClick:l,type:"button","data-testid":g,children:c}),v=b?t.jsx("a",{className:o(e.button,e[`variant-${s}`],n),href:u,onClick:l,target:p,rel:p==="_blank"?"noreferrer":void 0,children:c}):t.jsx(L,{className:o(e.button,e[`variant-${s}`],n),onClick:l,to:`${u}`,children:c}),m=u?v:x;return d?t.jsx(T,{content:d,children:m}):m});i.displayName="ListIconButton";try{i.displayName="ListIconButton",i.__docgenInfo={description:`The ListIconButton component is used to render an icon button that can be used as a link or a button.
It supports tooltips, external/internal links, and different button variants.

---
**Important: Use the \`url\` prop to create a link button, and the \`onClick\` prop to handle button actions.**
---`,displayName:"ListIconButton",props:{className:{defaultValue:null,description:"Custom CSS class for additional styling of the button.",name:"className",required:!1,type:{name:"string"}},onClick:{defaultValue:null,description:"Callback function triggered when the button is clicked.",name:"onClick",required:!1,type:{name:"((event: MouseEvent<Element, MouseEvent>) => void)"}},icon:{defaultValue:null,description:"The icon to display inside the button.",name:"icon",required:!0,type:{name:"string"}},variant:{defaultValue:{value:"ListIconButtonVariant.DEFAULT"},description:"The variant of the button.",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"primary"'}]}},tooltipContent:{defaultValue:null,description:"",name:"tooltipContent",required:!1,type:{name:"ReactNode"}},url:{defaultValue:null,description:"The URL to navigate to when the button is clicked.",name:"url",required:!1,type:{name:"string"}},target:{defaultValue:null,description:"Target attribute for the <a> tag",name:"target",required:!1,type:{name:"string"}},isExternal:{defaultValue:{value:"true"},description:"Indicates if the link is external.",name:"isExternal",required:!1,type:{name:"boolean"}},dataTestid:{defaultValue:null,description:"Custom test ID for targeting the component in tests.",name:"dataTestid",required:!1,type:{name:"string"}}}}}catch{}const $={title:"@/ui-kit/ListIconButton",component:i,decorators:[n=>t.jsx("div",{style:{margin:"50px",display:"flex"},children:t.jsx(n,{})})]},a={args:{icon:f,tooltipContent:t.jsx(t.Fragment,{children:"Duplicate"})}},r={args:{icon:f,tooltipContent:t.jsx(t.Fragment,{children:"Lire la FAQ"}),url:"http://wwww.test.com",onClick:()=>{},isExternal:!0}};a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{
  args: {
    icon: fullTrashIcon,
    tooltipContent: <>Duplicate</>
  }
}`,...a.parameters?.docs?.source}}};r.parameters={...r.parameters,docs:{...r.parameters?.docs,source:{originalSource:`{
  args: {
    icon: fullTrashIcon,
    tooltipContent: <>Lire la FAQ</>,
    url: 'http://wwww.test.com',
    onClick: () => {},
    isExternal: true
  }
}`,...r.parameters?.docs?.source}}};const R=["Default","Link"];export{a as Default,r as Link,R as __namedExportsOrder,$ as default};
