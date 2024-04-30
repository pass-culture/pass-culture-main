import{j as n}from"./jsx-runtime-Nms4Y4qS.js";import{c as _}from"./index-BpvXyOxN.js";import{f as z}from"./full-clear-CvNWe6Ae.js";import{s as D}from"./shadow-tips-help-BWD8Tj4_.js";import{s as F}from"./shadow-tips-warning-Cyw-iOmq.js";import{s as G}from"./stroke-close-C6KSko98.js";import{S as i}from"./SvgIcon-Cibea2Sc.js";import{L as J}from"./LinkNodes-ClhRStM3.js";import"./index-BwDkhjyp.js";import"./_commonjsHelpers-BosuxZz1.js";import"./full-link-Ct7SQyQr.js";import"./full-next-DBJ5r-A4.js";import"./ButtonLink-B7ix98yg.js";import"./index-CxAicSnZ.js";import"./index-QeuA_w2N.js";import"./Button.module-CwyaUOYU.js";import"./types-DjX_gQD6.js";const K="_attention_1a04i_7",Q="_title_1a04i_10",X="_icon_1a04i_26",Y="_provider_1a04i_42",Z="_light_1a04i_91",$="_content_1a04i_99",ee="_image_1a04i_116",ne="_container_1a04i_158",e={"bi-banner":"_bi-banner_1a04i_2",attention:K,"notification-info":"_notification-info_1a04i_7",title:Q,"close-icon-banner":"_close-icon-banner_1a04i_14",icon:X,"bi-banner-text":"_bi-banner-text_1a04i_39",provider:Y,"bi-link":"_bi-link_1a04i_47","is-minimal":"_is-minimal_1a04i_52","border-cut":"_border-cut_1a04i_57","close-icon":"_close-icon_1a04i_14",light:Z,new:"_new_1a04i_95",content:$,"ico-new":"_ico-new_1a04i_103",image:ee,"with-margin":"_with-margin_1a04i_145","domain-name-banner":"_domain-name-banner_1a04i_154",container:ne,"container-title":"_container-title_1a04i_170"},f=({children:u,type:a="attention",closable:O=!1,minimalStyle:P=!1,handleOnClick:R,className:U,links:h,showTitle:p=!0,isProvider:H=!1})=>n.jsxs("div",{className:_(e["bi-banner"],e[a],P&&e["is-minimal"],p&&e.title,U),children:[a==="notification-info"&&p&&n.jsxs("div",{className:e.container,children:[n.jsx(i,{src:D,alt:"",className:e.icon,width:"24"}),n.jsx("span",{className:e["container-title"],children:"À SAVOIR"})]}),a==="attention"&&p&&n.jsxs("div",{className:e.container,children:[n.jsx(i,{src:F,alt:"",className:e.icon,width:"24"}),n.jsx("span",{className:e["container-title"],children:"IMPORTANT"})]}),n.jsxs("div",{className:e["border-cut"],children:[O&&n.jsx("button",{onClick:R,type:"button",children:a!=="light"?n.jsx(i,{src:z,alt:"Masquer le bandeau",className:_(e["close-icon-banner"])}):n.jsx(i,{src:G,alt:"Masquer le bandeau",className:e["close-icon"]})}),n.jsx("div",{className:e.content,children:n.jsxs("div",{children:[u&&n.jsx("div",{className:_(e["bi-banner-text"],{[e["with-margin"]]:!!h},{[e.provider]:!!H}),children:u}),n.jsx(J,{links:h})]})})]})]});try{f.displayName="Banner",f.__docgenInfo={description:"",displayName:"Banner",props:{links:{defaultValue:null,description:"",name:"links",required:!1,type:{name:"Link[]"}},type:{defaultValue:{value:"attention"},description:"",name:"type",required:!1,type:{name:"enum",value:[{value:'"notification-info"'},{value:'"attention"'},{value:'"light"'}]}},closable:{defaultValue:{value:"false"},description:"",name:"closable",required:!1,type:{name:"boolean"}},minimalStyle:{defaultValue:{value:"false"},description:"",name:"minimalStyle",required:!1,type:{name:"boolean"}},handleOnClick:{defaultValue:null,description:"",name:"handleOnClick",required:!1,type:{name:"(() => void)"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},showTitle:{defaultValue:{value:"true"},description:"",name:"showTitle",required:!1,type:{name:"boolean"}},isProvider:{defaultValue:{value:"false"},description:"",name:"isProvider",required:!1,type:{name:"boolean"}}}}}catch{}const xe={title:"ui-kit/Banner",component:f},t="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",r={args:{type:"attention",closable:!0,children:t}},s={args:{type:"attention",showTitle:!1,children:t}},o={args:{type:"notification-info",closable:!0,children:t}},l={args:{type:"notification-info",showTitle:!1,children:t}},c={args:{type:"light",closable:!0,children:t}},m={args:{minimalStyle:!0,children:t}},d={args:{links:[{href:"https://pro.testing.passculture.team",label:"Lien vers le pass culture",isExternal:!0},{href:"#",label:"Un autre lien",isExternal:!0}],minimalStyle:!1,closable:!1,type:"notification-info"}};var b,g,x;r.parameters={...r.parameters,docs:{...(b=r.parameters)==null?void 0:b.docs,source:{originalSource:`{
  args: {
    type: 'attention',
    closable: true,
    children: textMock
  }
}`,...(x=(g=r.parameters)==null?void 0:g.docs)==null?void 0:x.source}}};var y,v,k;s.parameters={...s.parameters,docs:{...(y=s.parameters)==null?void 0:y.docs,source:{originalSource:`{
  args: {
    type: 'attention',
    showTitle: false,
    children: textMock
  }
}`,...(k=(v=s.parameters)==null?void 0:v.docs)==null?void 0:k.source}}};var N,j,S;o.parameters={...o.parameters,docs:{...(N=o.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    type: 'notification-info',
    closable: true,
    children: textMock
  }
}`,...(S=(j=o.parameters)==null?void 0:j.docs)==null?void 0:S.source}}};var w,I,M;l.parameters={...l.parameters,docs:{...(w=l.parameters)==null?void 0:w.docs,source:{originalSource:`{
  args: {
    type: 'notification-info',
    showTitle: false,
    children: textMock
  }
}`,...(M=(I=l.parameters)==null?void 0:I.docs)==null?void 0:M.source}}};var T,q,L;c.parameters={...c.parameters,docs:{...(T=c.parameters)==null?void 0:T.docs,source:{originalSource:`{
  args: {
    type: 'light',
    closable: true,
    children: textMock
  }
}`,...(L=(q=c.parameters)==null?void 0:q.docs)==null?void 0:L.source}}};var V,W,A;m.parameters={...m.parameters,docs:{...(V=m.parameters)==null?void 0:V.docs,source:{originalSource:`{
  args: {
    minimalStyle: true,
    children: textMock
  }
}`,...(A=(W=m.parameters)==null?void 0:W.docs)==null?void 0:A.source}}};var E,B,C;d.parameters={...d.parameters,docs:{...(E=d.parameters)==null?void 0:E.docs,source:{originalSource:`{
  args: {
    links: [{
      href: 'https://pro.testing.passculture.team',
      label: 'Lien vers le pass culture',
      isExternal: true
    }, {
      href: '#',
      label: 'Un autre lien',
      isExternal: true
    }],
    minimalStyle: false,
    closable: false,
    type: 'notification-info'
  }
}`,...(C=(B=d.parameters)==null?void 0:B.docs)==null?void 0:C.source}}};const ye=["Attention","AttentionWithoutTitle","Info","InfoWithoutTitle","Light","Minimal","WithLink"];export{r as Attention,s as AttentionWithoutTitle,o as Info,l as InfoWithoutTitle,c as Light,m as Minimal,d as WithLink,ye as __namedExportsOrder,xe as default};
