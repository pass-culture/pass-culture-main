import{j as t}from"./jsx-runtime-X2b_N9AH.js";import{c as f}from"./index-BpvXyOxN.js";import{f as z}from"./full-clear-CvNWe6Ae.js";import{s as D}from"./shadow-tips-help-BWD8Tj4_.js";import{s as F}from"./shadow-tips-warning-Cyw-iOmq.js";import{s as G}from"./stroke-close-C6KSko98.js";import{S as i}from"./SvgIcon-DP_815J1.js";import{L as J}from"./LinkNodes-hyHv6AWL.js";import"./index-uCp2LrAq.js";import"./_commonjsHelpers-BosuxZz1.js";import"./full-link-Ct7SQyQr.js";import"./full-next-DBJ5r-A4.js";import"./ButtonLink-Djmtr6Gs.js";import"./index-CWNn-QuQ.js";import"./index-NGkXgOa-.js";import"./index-DoMt6nTV.js";import"./Button.module-CvAyM0-b.js";import"./types-DjX_gQD6.js";const K="_attention_13of8_7",Q="_title_13of8_10",X="_icon_13of8_26",Y="_provider_13of8_42",Z="_light_13of8_91",$="_content_13of8_99",ee="_image_13of8_116",te="_container_13of8_154",e={"bi-banner":"_bi-banner_13of8_2",attention:K,"notification-info":"_notification-info_13of8_7",title:Q,"close-icon-banner":"_close-icon-banner_13of8_14",icon:X,"bi-banner-text":"_bi-banner-text_13of8_39",provider:Y,"bi-link":"_bi-link_13of8_47","is-minimal":"_is-minimal_13of8_52","border-cut":"_border-cut_13of8_57","close-icon":"_close-icon_13of8_14",light:Z,new:"_new_13of8_95",content:$,"ico-new":"_ico-new_13of8_103",image:ee,"with-margin":"_with-margin_13of8_145",container:te,"container-title":"_container-title_13of8_166"},_=({children:u,type:a="attention",closable:O=!1,minimalStyle:P=!1,handleOnClick:R,className:U,links:h,showTitle:p=!0,isProvider:H=!1})=>t.jsxs("div",{className:f(e["bi-banner"],e[a],P&&e["is-minimal"],p&&e.title,U),children:[a==="notification-info"&&p&&t.jsxs("div",{className:e.container,children:[t.jsx(i,{src:D,alt:"",className:e.icon,width:"24"}),t.jsx("span",{className:e["container-title"],children:"À SAVOIR"})]}),a==="attention"&&p&&t.jsxs("div",{className:e.container,children:[t.jsx(i,{src:F,alt:"",className:e.icon,width:"24"}),t.jsx("span",{className:e["container-title"],children:"IMPORTANT"})]}),t.jsxs("div",{className:e["border-cut"],children:[O&&t.jsx("button",{onClick:R,type:"button",children:a!=="light"?t.jsx(i,{src:z,alt:"Masquer le bandeau",className:f(e["close-icon-banner"])}):t.jsx(i,{src:G,alt:"Masquer le bandeau",className:e["close-icon"]})}),t.jsx("div",{className:e.content,children:t.jsxs("div",{children:[u&&t.jsx("div",{className:f(e["bi-banner-text"],{[e["with-margin"]]:!!h},{[e.provider]:!!H}),children:u}),t.jsx(J,{links:h})]})})]})]});try{_.displayName="Banner",_.__docgenInfo={description:"",displayName:"Banner",props:{links:{defaultValue:null,description:"",name:"links",required:!1,type:{name:"Link[]"}},type:{defaultValue:{value:"attention"},description:"",name:"type",required:!1,type:{name:"enum",value:[{value:'"notification-info"'},{value:'"attention"'},{value:'"light"'}]}},closable:{defaultValue:{value:"false"},description:"",name:"closable",required:!1,type:{name:"boolean"}},minimalStyle:{defaultValue:{value:"false"},description:"",name:"minimalStyle",required:!1,type:{name:"boolean"}},handleOnClick:{defaultValue:null,description:"",name:"handleOnClick",required:!1,type:{name:"(() => void)"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},showTitle:{defaultValue:{value:"true"},description:"",name:"showTitle",required:!1,type:{name:"boolean"}},isProvider:{defaultValue:{value:"false"},description:"",name:"isProvider",required:!1,type:{name:"boolean"}}}}}catch{}const ye={title:"ui-kit/Banner",component:_},n="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",o={args:{type:"attention",closable:!0,children:n}},r={args:{type:"attention",showTitle:!1,children:n}},s={args:{type:"notification-info",closable:!0,children:n}},l={args:{type:"notification-info",showTitle:!1,children:n}},c={args:{type:"light",closable:!0,children:n}},m={args:{minimalStyle:!0,children:n}},d={args:{links:[{href:"https://pro.testing.passculture.team",label:"Lien vers le pass culture",isExternal:!0},{href:"#",label:"Un autre lien",isExternal:!0}],minimalStyle:!1,closable:!1,type:"notification-info"}};var g,b,x;o.parameters={...o.parameters,docs:{...(g=o.parameters)==null?void 0:g.docs,source:{originalSource:`{
  args: {
    type: 'attention',
    closable: true,
    children: textMock
  }
}`,...(x=(b=o.parameters)==null?void 0:b.docs)==null?void 0:x.source}}};var y,v,k;r.parameters={...r.parameters,docs:{...(y=r.parameters)==null?void 0:y.docs,source:{originalSource:`{
  args: {
    type: 'attention',
    showTitle: false,
    children: textMock
  }
}`,...(k=(v=r.parameters)==null?void 0:v.docs)==null?void 0:k.source}}};var N,j,S;s.parameters={...s.parameters,docs:{...(N=s.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    type: 'notification-info',
    closable: true,
    children: textMock
  }
}`,...(S=(j=s.parameters)==null?void 0:j.docs)==null?void 0:S.source}}};var w,I,M;l.parameters={...l.parameters,docs:{...(w=l.parameters)==null?void 0:w.docs,source:{originalSource:`{
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
}`,...(C=(B=d.parameters)==null?void 0:B.docs)==null?void 0:C.source}}};const ve=["Attention","AttentionWithoutTitle","Info","InfoWithoutTitle","Light","Minimal","WithLink"];export{o as Attention,r as AttentionWithoutTitle,s as Info,l as InfoWithoutTitle,c as Light,m as Minimal,d as WithLink,ve as __namedExportsOrder,ye as default};
