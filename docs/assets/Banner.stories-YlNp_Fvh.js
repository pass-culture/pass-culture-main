import{j as t}from"./jsx-runtime-Nms4Y4qS.js";import{c as g}from"./index-BpvXyOxN.js";import{s as C}from"./shadow-tips-help-BWD8Tj4_.js";import{s as U}from"./shadow-tips-warning-Cyw-iOmq.js";import{S as f}from"./SvgIcon-Cibea2Sc.js";import{L as H}from"./LinkNodes-Bn3Blhce.js";import"./index-BwDkhjyp.js";import"./_commonjsHelpers-BosuxZz1.js";import"./full-link-Ct7SQyQr.js";import"./full-next-DBJ5r-A4.js";import"./ButtonLink-DxjvDZG0.js";import"./index-C_BCaKYK.js";import"./index-CReuRBEY.js";import"./Button.module-B0CH5SHY.js";import"./types-DjX_gQD6.js";const D="_attention_16zcg_6",F="_title_16zcg_9",G="_icon_16zcg_18",J="_provider_16zcg_28",K="_light_16zcg_68",Q="_content_16zcg_76",X="_image_16zcg_92",Y="_container_16zcg_125",e={"bi-banner":"_bi-banner_16zcg_1",attention:D,"notification-info":"_notification-info_16zcg_6",title:F,icon:G,"bi-banner-text":"_bi-banner-text_16zcg_25",provider:J,"bi-link":"_bi-link_16zcg_33","is-minimal":"_is-minimal_16zcg_38","border-cut":"_border-cut_16zcg_43",light:K,new:"_new_16zcg_72",content:Q,"ico-new":"_ico-new_16zcg_80",image:X,"with-margin":"_with-margin_16zcg_116",container:Y,"container-title":"_container-title_16zcg_139"},u=({children:m,type:d="attention",minimalStyle:O=!1,className:P,links:_,showTitle:p=!0,isProvider:R=!1})=>t.jsxs("div",{className:g(e["bi-banner"],e[d],O&&e["is-minimal"],p&&e.title,P),children:[d==="notification-info"&&p&&t.jsxs("div",{className:e.container,children:[t.jsx(f,{src:C,alt:"",className:e.icon,width:"24"}),t.jsx("span",{className:e["container-title"],children:"À SAVOIR"})]}),d==="attention"&&p&&t.jsxs("div",{className:e.container,children:[t.jsx(f,{src:U,alt:"",className:e.icon,width:"24"}),t.jsx("span",{className:e["container-title"],children:"IMPORTANT"})]}),t.jsx("div",{className:e["border-cut"],children:t.jsx("div",{className:e.content,children:t.jsxs("div",{children:[m&&t.jsx("div",{className:g(e["bi-banner-text"],{[e["with-margin"]]:!!_},{[e.provider]:!!R}),children:m}),t.jsx(H,{links:_})]})})})]});try{u.displayName="Banner",u.__docgenInfo={description:"",displayName:"Banner",props:{links:{defaultValue:null,description:"",name:"links",required:!1,type:{name:"Link[]"}},type:{defaultValue:{value:"attention"},description:"",name:"type",required:!1,type:{name:"enum",value:[{value:'"notification-info"'},{value:'"attention"'},{value:'"light"'}]}},minimalStyle:{defaultValue:{value:"false"},description:"",name:"minimalStyle",required:!1,type:{name:"boolean"}},handleOnClick:{defaultValue:null,description:"",name:"handleOnClick",required:!1,type:{name:"(() => void)"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},showTitle:{defaultValue:{value:"true"},description:"",name:"showTitle",required:!1,type:{name:"boolean"}},isProvider:{defaultValue:{value:"false"},description:"",name:"isProvider",required:!1,type:{name:"boolean"}}}}}catch{}const ue={title:"ui-kit/Banner",component:u},n="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",i={args:{type:"attention",children:n}},a={args:{type:"attention",showTitle:!1,children:n}},r={args:{type:"notification-info",children:n}},o={args:{type:"notification-info",showTitle:!1,children:n}},s={args:{type:"light",children:n}},c={args:{minimalStyle:!0,children:n}},l={args:{links:[{href:"https://pro.testing.passculture.team",label:"Lien vers le pass culture",isExternal:!0},{href:"#",label:"Un autre lien",isExternal:!0}],minimalStyle:!1,type:"notification-info"}};var h,x,y;i.parameters={...i.parameters,docs:{...(h=i.parameters)==null?void 0:h.docs,source:{originalSource:`{
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
}`,...(k=(v=a.parameters)==null?void 0:v.docs)==null?void 0:k.source}}};var z,N,S;r.parameters={...r.parameters,docs:{...(z=r.parameters)==null?void 0:z.docs,source:{originalSource:`{
  args: {
    type: 'notification-info',
    children: textMock
  }
}`,...(S=(N=r.parameters)==null?void 0:N.docs)==null?void 0:S.source}}};var w,j,T;o.parameters={...o.parameters,docs:{...(w=o.parameters)==null?void 0:w.docs,source:{originalSource:`{
  args: {
    type: 'notification-info',
    showTitle: false,
    children: textMock
  }
}`,...(T=(j=o.parameters)==null?void 0:j.docs)==null?void 0:T.source}}};var I,L,M;s.parameters={...s.parameters,docs:{...(I=s.parameters)==null?void 0:I.docs,source:{originalSource:`{
  args: {
    type: 'light',
    children: textMock
  }
}`,...(M=(L=s.parameters)==null?void 0:L.docs)==null?void 0:M.source}}};var q,V,W;c.parameters={...c.parameters,docs:{...(q=c.parameters)==null?void 0:q.docs,source:{originalSource:`{
  args: {
    minimalStyle: true,
    children: textMock
  }
}`,...(W=(V=c.parameters)==null?void 0:V.docs)==null?void 0:W.source}}};var A,E,B;l.parameters={...l.parameters,docs:{...(A=l.parameters)==null?void 0:A.docs,source:{originalSource:`{
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
}`,...(B=(E=l.parameters)==null?void 0:E.docs)==null?void 0:B.source}}};const _e=["Attention","AttentionWithoutTitle","Info","InfoWithoutTitle","Light","Minimal","WithLink"];export{i as Attention,a as AttentionWithoutTitle,r as Info,o as InfoWithoutTitle,s as Light,c as Minimal,l as WithLink,_e as __namedExportsOrder,ue as default};
