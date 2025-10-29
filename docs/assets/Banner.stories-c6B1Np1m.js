import{j as r}from"./jsx-runtime-CAi7eUhW.js";import{c as o}from"./index-BbcbtrB-.js";import{f as N}from"./full-close-5Oxr7nnd.js";import{f as W}from"./full-info-D24AtBVt.js";import{B as I}from"./ButtonLink-BXeF6OTt.js";import{S as k}from"./SvgIcon-fLN3d87k.js";import{f as t}from"./full-link-CYVo23DH.js";import{V as D}from"./index-RVPY9xlK.js";import"./iframe-CcyYMgJE.js";import"./preload-helper-PPVm8Dsz.js";import"./chunk-OIYGIGL5-CB69KGgy.js";import"./Button.module-CY1ZDZvt.js";import"./types-yVZEaApa.js";const C="_banner_13gxi_1",j="_success_13gxi_9",R="_warning_13gxi_15",q="_error_13gxi_21",B="_inner_13gxi_27",A="_header_13gxi_33",w="_info_13gxi_38",U="_title_13gxi_43",z="_content_13gxi_57",T="_link_13gxi_78",F="_image_13gxi_124",e={banner:C,success:j,warning:R,error:q,inner:B,header:A,info:w,title:U,"title-large":"_title-large_13gxi_51",content:z,"content-body":"_content-body_13gxi_64","content-body-large":"_content-body-large_13gxi_72","links-list":"_links-list_13gxi_78",link:T,"link-large":"_link-large_13gxi_96","close-button":"_close-button_13gxi_106",image:F};var i=(s=>(s.DEFAULT="default",s.SUCCESS="success",s.WARNING="warning",s.ERROR="error",s))(i||{});const v=({title:s,description:b,links:x=[],icon:y=W,imageSrc:S,variant:E="default",size:h="default",closable:L=!1,onClose:V})=>r.jsx("div",{className:o(e.banner,e[E]),"data-testid":"banner",children:r.jsx("div",{className:e.inner,children:r.jsxs("div",{className:e.content,children:[r.jsx(k,{className:e.info,src:y,"aria-hidden":"true"}),r.jsxs("div",{className:o(e["content-body"],{[e["content-body-large"]]:h==="large"}),children:[r.jsx("span",{className:o(e.title,{[e["title-large"]]:h==="large"}),children:s}),b&&r.jsx("span",{className:e.description,children:b}),x.length>0&&r.jsx("ul",{className:e["links-list"],children:x.map(n=>r.jsx("li",{children:r.jsx(I,{className:o(e.link,{[e["link-large"]]:h==="large"}),href:n.href,target:n.external?"_blank":"_self",rel:n.external?"noopener noreferrer":void 0,to:n.href,icon:n.icon,iconAlt:n.iconAlt,children:n.label})},n.label))})]}),S&&r.jsx("img",{src:S,className:e.image,alt:"","aria-hidden":"true"}),L&&r.jsx("button",{type:"button",className:e["close-button"],onClick:V,"aria-label":"Fermer la bannière d’information",children:r.jsx(k,{src:N,width:"16"})})]})})});try{v.displayName="Banner",v.__docgenInfo={description:"",displayName:"Banner",props:{title:{defaultValue:null,description:"",name:"title",required:!0,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},links:{defaultValue:{value:"[]"},description:"",name:"links",required:!1,type:{name:"BannerLink[]"}},icon:{defaultValue:null,description:"",name:"icon",required:!1,type:{name:"string"}},imageSrc:{defaultValue:null,description:"",name:"imageSrc",required:!1,type:{name:"string"}},variant:{defaultValue:{value:"BannerVariants.DEFAULT"},description:"Visual style (defines colors)",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"success"'},{value:'"warning"'},{value:'"error"'}]}},size:{defaultValue:{value:"default"},description:"",name:"size",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"large"'}]}},closable:{defaultValue:{value:"false"},description:"Show close button?",name:"closable",required:!1,type:{name:"boolean"}},onClose:{defaultValue:null,description:"Callback called on close button click",name:"onClose",required:!1,type:{name:"(() => void)"}}}}}catch{}const O=""+new URL("turtle-CX4Zo2gH.png",import.meta.url).href,ae={title:"@/design-system/Banner",component:v,decorators:[D]},a={args:{title:"Titre important très long très long très long très long très",description:"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris mattis libero ultrices sem scelerisque gravida. Lorem ipsum dolor sit amet, consectetur adipiscing elit. ",links:[{label:"En savoir plus",href:"#",icon:t},{label:"En savoir plus",href:"#",icon:t},{label:"En savoir plus",href:"#",icon:t},{label:"En savoir plus",href:"#",icon:t}],imageSrc:O,variant:i.DEFAULT,size:"default",closable:!0}},l={args:{...a.args,variant:i.SUCCESS}},c={args:{...a.args,variant:i.WARNING}},u={args:{...a.args,variant:i.ERROR}},m={args:{...a.args,description:void 0}},d={args:{...a.args,links:[]}},g={args:{...a.args,imageSrc:void 0}},p={args:{...a.args,closable:!1}},f={args:{...a.args,size:"large"}},_={args:{...a.args,icon:t}};a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{
  args: {
    title: 'Titre important très long très long très long très long très',
    description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris mattis libero ultrices sem scelerisque gravida. Lorem ipsum dolor sit amet, consectetur adipiscing elit. ",
    links: [{
      label: 'En savoir plus',
      href: '#',
      icon: fullLinkIcon
    }, {
      label: 'En savoir plus',
      href: '#',
      icon: fullLinkIcon
    }, {
      label: 'En savoir plus',
      href: '#',
      icon: fullLinkIcon
    }, {
      label: 'En savoir plus',
      href: '#',
      icon: fullLinkIcon
    }],
    imageSrc: turtle,
    variant: BannerVariants.DEFAULT,
    size: 'default',
    closable: true
  }
}`,...a.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    variant: BannerVariants.SUCCESS
  }
}`,...l.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    variant: BannerVariants.WARNING
  }
}`,...c.parameters?.docs?.source}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    variant: BannerVariants.ERROR
  }
}`,...u.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    description: undefined
  }
}`,...m.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    links: []
  }
}`,...d.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    imageSrc: undefined
  }
}`,...g.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    closable: false
  }
}`,...p.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    size: 'large'
  }
}`,...f.parameters?.docs?.source}}};_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    icon: fullLinkIcon
  }
}`,..._.parameters?.docs?.source}}};const se=["Default","WithSuccessVariant","WithWarningVariant","WithErrorVariant","WithoutDescription","WithoutLinks","WithoutImage","WithoutCloseButton","LargeSize","CustomIcon"];export{_ as CustomIcon,a as Default,f as LargeSize,u as WithErrorVariant,l as WithSuccessVariant,c as WithWarningVariant,p as WithoutCloseButton,m as WithoutDescription,g as WithoutImage,d as WithoutLinks,se as __namedExportsOrder,ae as default};
