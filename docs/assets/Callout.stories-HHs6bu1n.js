import{j as t}from"./jsx-runtime-vNq4Oc-g.js";import{c as E}from"./index-XNbs-YUW.js";import{f as C,a as I}from"./full-info-y_GgizFl.js";import{f as W}from"./full-validate-UsEvEnOv.js";import{f as y}from"./full-warning-sCBth3ad.js";import{s as S}from"./stroke-close-KQNU-49n.js";import{S as d}from"./SvgIcon-QVOPtTle.js";import{L as j}from"./LinkNodes-LX9WZqgT.js";import"./index-4g5l5LRQ.js";import"./_commonjsHelpers-4gQjN7DL.js";import"./full-link-GGegv9yK.js";import"./full-next-6FYpialQ.js";import"./ButtonLink-iC8iNd8u.js";import"./index-VkxvJQxW.js";import"./index-CQtvWCGL.js";import"./Button.module-fn58QZwY.js";var l=(e=>(e.DEFAULT="default",e.INFO="info",e.SUCCESS="success",e.WARNING="warning",e.ERROR="error",e))(l||{});const R="_callout_vq7gw_2",A="_icon_vq7gw_13",F="_content_vq7gw_54",U="_title_vq7gw_60",a={callout:R,"callout-default":"_callout-default_vq7gw_10",icon:A,"callout-info":"_callout-info_vq7gw_16","callout-success":"_callout-success_vq7gw_22","callout-warning":"_callout-warning_vq7gw_28","callout-error":"_callout-error_vq7gw_34","close-icon":"_close-icon_vq7gw_45",content:F,"bi-link-item":"_bi-link-item_vq7gw_57",title:U,"small-callout":"_small-callout_vq7gw_64"},u=({children:e,className:k,title:n,links:c,closable:x=!1,onClose:L,variant:m=l.DEFAULT})=>{let o;switch(m){case l.WARNING:o={src:y,alt:"Attention"};break;case l.SUCCESS:o={src:W,alt:"Confirmation"};break;case l.ERROR:o={src:I,alt:"Erreur"};break;default:o={src:C,alt:"Information"};break}const N=(!e||!n)&&!c;return t.jsxs("div",{className:E(a.callout,a[`callout-${m}`],N?a["small-callout"]:"",k),children:[t.jsx(d,{src:o.src,alt:o.alt,className:a.icon,width:"20"}),t.jsxs("div",{className:a.content,children:[n&&t.jsx("div",{className:a.title,children:n}),e&&t.jsx("div",{className:a["callout-text"],children:e}),c&&t.jsx(j,{links:c})]}),x&&t.jsx("button",{onClick:L,type:"button",className:a["close-icon"],children:t.jsx(d,{src:S,alt:"Fermer le message",width:"20"})})]})},O=u;try{u.displayName="Callout",u.__docgenInfo={description:"",displayName:"Callout",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},title:{defaultValue:null,description:"",name:"title",required:!1,type:{name:"string"}},links:{defaultValue:null,description:"",name:"links",required:!1,type:{name:"Link[]"}},closable:{defaultValue:{value:"false"},description:"",name:"closable",required:!1,type:{name:"boolean"}},onClose:{defaultValue:null,description:"",name:"onClose",required:!1,type:{name:"(() => void)"}},variant:{defaultValue:{value:"CalloutVariant.DEFAULT"},description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"info"'},{value:'"success"'},{value:'"warning"'},{value:'"error"'}]}}}}}catch{}const ee={title:"components/Callout",component:O},r={args:{children:"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",title:"Without link warning callout"}},s={args:{children:"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",title:"Without link warning callout",closable:!0}},i={args:{children:"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",title:"With link warning callout",links:[{href:"https://pro.testing.passculture.team",label:"Lien interne au pass culture pro",isExternal:!0},{href:"https://pro.testing.passculture.team",label:"Lien externe",isExternal:!0}]}};var p,g,f;r.parameters={...r.parameters,docs:{...(p=r.parameters)==null?void 0:p.docs,source:{originalSource:`{
  args: {
    children: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
    title: 'Without link warning callout'
  }
}`,...(f=(g=r.parameters)==null?void 0:g.docs)==null?void 0:f.source}}};var _,h,v;s.parameters={...s.parameters,docs:{...(_=s.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    children: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
    title: 'Without link warning callout',
    closable: true
  }
}`,...(v=(h=s.parameters)==null?void 0:h.docs)==null?void 0:v.source}}};var b,w,q;i.parameters={...i.parameters,docs:{...(b=i.parameters)==null?void 0:b.docs,source:{originalSource:`{
  args: {
    children: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
    title: 'With link warning callout',
    links: [{
      href: 'https://pro.testing.passculture.team',
      label: 'Lien interne au pass culture pro',
      isExternal: true
    }, {
      href: 'https://pro.testing.passculture.team',
      label: 'Lien externe',
      isExternal: true
    }]
  }
}`,...(q=(w=i.parameters)==null?void 0:w.docs)==null?void 0:q.source}}};const te=["WithoutLink","Closable","WithLink"];export{s as Closable,i as WithLink,r as WithoutLink,te as __namedExportsOrder,ee as default};
