import{j as n}from"./jsx-runtime-Nms4Y4qS.js";import{c as f}from"./index-BpvXyOxN.js";import{s as U}from"./shadow-tips-help-BWD8Tj4_.js";import{s as H}from"./shadow-tips-warning-Cyw-iOmq.js";import{S as h}from"./SvgIcon-Cibea2Sc.js";import{L as z}from"./LinkNodes-CyNwby4N.js";import"./index-BwDkhjyp.js";import"./_commonjsHelpers-BosuxZz1.js";import"./full-link-Ct7SQyQr.js";import"./full-next-DBJ5r-A4.js";import"./ButtonLink-Db606ZJm.js";import"./index-C_BCaKYK.js";import"./index-CReuRBEY.js";import"./Button.module-9zQJcsLA.js";import"./types-DjX_gQD6.js";const D="_attention_nd2l5_6",F="_title_nd2l5_9",G="_icon_nd2l5_18",J="_provider_nd2l5_28",K="_light_nd2l5_68",Q="_content_nd2l5_76",X="_image_nd2l5_92",Y="_container_nd2l5_125",e={"bi-banner":"_bi-banner_nd2l5_1",attention:D,"notification-info":"_notification-info_nd2l5_6",title:F,icon:G,"bi-banner-text":"_bi-banner-text_nd2l5_25",provider:J,"bi-link":"_bi-link_nd2l5_33","is-minimal":"_is-minimal_nd2l5_38","border-cut":"_border-cut_nd2l5_43",light:K,new:"_new_nd2l5_72",content:Q,"ico-new":"_ico-new_nd2l5_80",image:X,"with-margin":"_with-margin_nd2l5_116",container:Y,"container-title":"_container-title_nd2l5_137"},u=({children:d,type:m="attention",minimalStyle:P=!1,className:R,links:_,showTitle:p=!0,isProvider:C=!1})=>n.jsxs("div",{className:f(e["bi-banner"],e[m],P&&e["is-minimal"],p&&e.title,R),children:[m==="notification-info"&&p&&n.jsxs("div",{className:e.container,children:[n.jsx(h,{src:U,alt:"",className:e.icon,width:"24"}),n.jsx("span",{className:e["container-title"],children:"À SAVOIR"})]}),m==="attention"&&p&&n.jsxs("div",{className:e.container,children:[n.jsx(h,{src:H,alt:"",className:e.icon,width:"24"}),n.jsx("span",{className:e["container-title"],children:"IMPORTANT"})]}),n.jsx("div",{className:e["border-cut"],children:n.jsx("div",{className:e.content,children:n.jsxs("div",{children:[d&&n.jsx("div",{className:f(e["bi-banner-text"],{[e["with-margin"]]:!!_},{[e.provider]:!!C}),children:d}),n.jsx(z,{links:_})]})})})]});try{u.displayName="Banner",u.__docgenInfo={description:"",displayName:"Banner",props:{links:{defaultValue:null,description:"",name:"links",required:!1,type:{name:"Link[]"}},type:{defaultValue:{value:"attention"},description:"",name:"type",required:!1,type:{name:"enum",value:[{value:'"notification-info"'},{value:'"attention"'},{value:'"light"'}]}},minimalStyle:{defaultValue:{value:"false"},description:"",name:"minimalStyle",required:!1,type:{name:"boolean"}},handleOnClick:{defaultValue:null,description:"",name:"handleOnClick",required:!1,type:{name:"(() => void)"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},showTitle:{defaultValue:{value:"true"},description:"",name:"showTitle",required:!1,type:{name:"boolean"}},isProvider:{defaultValue:{value:"false"},description:"",name:"isProvider",required:!1,type:{name:"boolean"}}}}}catch{}const ue={title:"ui-kit/Banner",component:u},t="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",i={args:{type:"attention",children:t}},a={args:{type:"attention",showTitle:!1,children:t}},r={args:{type:"notification-info",children:t}},o={args:{type:"notification-info",showTitle:!1,children:t}},s={args:{type:"light",children:t}},l={args:{minimalStyle:!0,children:t}},c={args:{links:[{href:"https://pro.testing.passculture.team",label:"Lien vers le pass culture",isExternal:!0},{href:"#",label:"Un autre lien",isExternal:!0}],minimalStyle:!1,type:"notification-info"}};var g,x,y;i.parameters={...i.parameters,docs:{...(g=i.parameters)==null?void 0:g.docs,source:{originalSource:`{
  args: {
    type: 'attention',
    children: textMock
  }
}`,...(y=(x=i.parameters)==null?void 0:x.docs)==null?void 0:y.source}}};var b,v,k;a.parameters={...a.parameters,docs:{...(b=a.parameters)==null?void 0:b.docs,source:{originalSource:`{
  args: {
    type: 'attention',
    showTitle: false,
    children: textMock
  }
}`,...(k=(v=a.parameters)==null?void 0:v.docs)==null?void 0:k.source}}};var N,S,w;r.parameters={...r.parameters,docs:{...(N=r.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    type: 'notification-info',
    children: textMock
  }
}`,...(w=(S=r.parameters)==null?void 0:S.docs)==null?void 0:w.source}}};var j,T,I;o.parameters={...o.parameters,docs:{...(j=o.parameters)==null?void 0:j.docs,source:{originalSource:`{
  args: {
    type: 'notification-info',
    showTitle: false,
    children: textMock
  }
}`,...(I=(T=o.parameters)==null?void 0:T.docs)==null?void 0:I.source}}};var L,M,q;s.parameters={...s.parameters,docs:{...(L=s.parameters)==null?void 0:L.docs,source:{originalSource:`{
  args: {
    type: 'light',
    children: textMock
  }
}`,...(q=(M=s.parameters)==null?void 0:M.docs)==null?void 0:q.source}}};var V,W,A;l.parameters={...l.parameters,docs:{...(V=l.parameters)==null?void 0:V.docs,source:{originalSource:`{
  args: {
    minimalStyle: true,
    children: textMock
  }
}`,...(A=(W=l.parameters)==null?void 0:W.docs)==null?void 0:A.source}}};var E,B,O;c.parameters={...c.parameters,docs:{...(E=c.parameters)==null?void 0:E.docs,source:{originalSource:`{
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
    type: 'notification-info'
  }
}`,...(O=(B=c.parameters)==null?void 0:B.docs)==null?void 0:O.source}}};const _e=["Attention","AttentionWithoutTitle","Info","InfoWithoutTitle","Light","Minimal","WithLink"];export{i as Attention,a as AttentionWithoutTitle,r as Info,o as InfoWithoutTitle,s as Light,l as Minimal,c as WithLink,_e as __namedExportsOrder,ue as default};
