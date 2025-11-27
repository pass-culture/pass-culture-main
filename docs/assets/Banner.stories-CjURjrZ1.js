import{j as r}from"./jsx-runtime-_2L9Ji7D.js";import{c as t}from"./index-nh49huUo.js";import{f as V}from"./full-close-5Oxr7nnd.js";import{f as L}from"./full-info-D24AtBVt.js";import{B as W}from"./Button-DBQytiGX.js";import{B as j}from"./ButtonLink-CsKRdAOX.js";import{B as C}from"./types-yVZEaApa.js";import{S}from"./SvgIcon-CXe80ba4.js";import{f as i}from"./full-link-CYVo23DH.js";import{V as I}from"./index-CrvjzoHR.js";import"./iframe-CALpjyN2.js";import"./preload-helper-PPVm8Dsz.js";import"./stroke-pass-CALgybTM.js";import"./Tooltip-C2UW_GrO.js";import"./Button.module-CY1ZDZvt.js";import"./chunk-4WY6JWTD-B2VDXGlI.js";const D="_banner_1485q_1",B="_success_1485q_11",R="_warning_1485q_17",A="_error_1485q_23",w="_inner_1485q_29",U="_header_1485q_35",T="_info_1485q_40",z="_title_1485q_45",F="_content_1485q_59",O="_link_1485q_80",G="_image_1485q_126",e={banner:D,success:B,warning:R,error:A,inner:w,header:U,info:T,title:z,"title-large":"_title-large_1485q_53",content:F,"content-body":"_content-body_1485q_66","content-body-large":"_content-body-large_1485q_74","links-list":"_links-list_1485q_80",link:O,"link-large":"_link-large_1485q_98","close-button":"_close-button_1485q_108",image:G};var o=(s=>(s.DEFAULT="default",s.SUCCESS="success",s.WARNING="warning",s.ERROR="error",s))(o||{});const v=({title:s,description:b,actions:k=[],icon:q=L,imageSrc:y,variant:E="default",size:l="default",closable:x=!1,onClose:N})=>r.jsx("div",{className:t(e.banner,e[E]),"data-testid":"banner",children:r.jsx("div",{className:e.inner,children:r.jsxs("div",{className:e.content,children:[r.jsx(S,{className:e.info,src:q,"aria-hidden":"true"}),r.jsxs("div",{className:t(e["content-body"],{[e["content-body-large"]]:l==="large"}),children:[r.jsx("span",{className:t(e.title,{[e["title-large"]]:l==="large"}),children:s}),b&&r.jsx("span",{className:e.description,children:b}),k.length>0&&r.jsx("ul",{className:e["actions-list"],children:k.map(a=>r.jsx("li",{children:a.type==="link"?r.jsx(j,{className:t(e.link,{[e["link-large"]]:l==="large"}),href:a.href,target:a.isExternal?"_blank":"_self",rel:a.isExternal?"noopener noreferrer":void 0,to:a.href,icon:a.icon,iconAlt:a.iconAlt,isExternal:a.isExternal,children:a.label}):r.jsx(W,{className:t(e.link,{[e["link-large"]]:l==="large"}),variant:C.TERNARY,icon:a.icon,onClick:()=>a.onClick?.(),children:a.label})},a.label))})]}),y&&r.jsx("img",{src:y,className:e.image,alt:"","aria-hidden":"true"}),x&&r.jsx("button",{type:"button",className:e["close-button"],onClick:N,"aria-label":"Fermer la bannière d’information",children:r.jsx(S,{src:V,width:"16"})})]})})});try{v.displayName="Banner",v.__docgenInfo={description:"",displayName:"Banner",props:{title:{defaultValue:null,description:"",name:"title",required:!0,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string | Element"}},actions:{defaultValue:{value:"[]"},description:"",name:"actions",required:!1,type:{name:"BannerLink[]"}},icon:{defaultValue:null,description:"",name:"icon",required:!1,type:{name:"string"}},imageSrc:{defaultValue:null,description:"",name:"imageSrc",required:!1,type:{name:"string"}},variant:{defaultValue:{value:"BannerVariants.DEFAULT"},description:"Visual style (defines colors)",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"success"'},{value:'"warning"'},{value:'"error"'}]}},size:{defaultValue:{value:"default"},description:"",name:"size",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"large"'}]}},closable:{defaultValue:{value:"false"},description:"Show close button?",name:"closable",required:!1,type:{name:"boolean"}},onClose:{defaultValue:null,description:"Callback called on close button click",name:"onClose",required:!1,type:{name:"(() => void)"}}}}}catch{}const M=""+new URL("turtle-CX4Zo2gH.png",import.meta.url).href,oe={title:"@/design-system/Banner",component:v,decorators:[I,s=>r.jsx("div",{style:{width:"fit-content"},children:r.jsx(s,{})})]},n={args:{title:"Titre important très long très long très long très long très",description:"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris mattis libero ultrices sem scelerisque gravida. Lorem ipsum dolor sit amet, consectetur adipiscing elit. ",actions:[{label:"En savoir plus",href:"#",icon:i,type:"link"},{label:"En savoir plus",href:"#",icon:i,type:"link"},{label:"En savoir plus",href:"#",icon:i,type:"link"},{label:"En savoir plus",href:"#",icon:i,type:"link"}],imageSrc:M,variant:o.DEFAULT,size:"default",closable:!0}},c={args:{...n.args,variant:o.SUCCESS}},u={args:{...n.args,variant:o.WARNING}},m={args:{...n.args,variant:o.ERROR}},d={args:{...n.args,description:void 0}},p={args:{...n.args,actions:[]}},g={args:{...n.args,imageSrc:void 0}},f={args:{...n.args,closable:!1}},_={args:{...n.args,size:"large"}},h={args:{...n.args,icon:i}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    title: 'Titre important très long très long très long très long très',
    description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris mattis libero ultrices sem scelerisque gravida. Lorem ipsum dolor sit amet, consectetur adipiscing elit. ",
    actions: [{
      label: 'En savoir plus',
      href: '#',
      icon: fullLinkIcon,
      type: 'link'
    }, {
      label: 'En savoir plus',
      href: '#',
      icon: fullLinkIcon,
      type: 'link'
    }, {
      label: 'En savoir plus',
      href: '#',
      icon: fullLinkIcon,
      type: 'link'
    }, {
      label: 'En savoir plus',
      href: '#',
      icon: fullLinkIcon,
      type: 'link'
    }],
    imageSrc: turtle,
    variant: BannerVariants.DEFAULT,
    size: 'default',
    closable: true
  }
}`,...n.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    variant: BannerVariants.SUCCESS
  }
}`,...c.parameters?.docs?.source}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    variant: BannerVariants.WARNING
  }
}`,...u.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    variant: BannerVariants.ERROR
  }
}`,...m.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    description: undefined
  }
}`,...d.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    actions: []
  }
}`,...p.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    imageSrc: undefined
  }
}`,...g.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    closable: false
  }
}`,...f.parameters?.docs?.source}}};_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    size: 'large'
  }
}`,..._.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    icon: fullLinkIcon
  }
}`,...h.parameters?.docs?.source}}};const le=["Default","WithSuccessVariant","WithWarningVariant","WithErrorVariant","WithoutDescription","WithoutActions","WithoutImage","WithoutCloseButton","LargeSize","CustomIcon"];export{h as CustomIcon,n as Default,_ as LargeSize,m as WithErrorVariant,c as WithSuccessVariant,u as WithWarningVariant,p as WithoutActions,f as WithoutCloseButton,d as WithoutDescription,g as WithoutImage,le as __namedExportsOrder,oe as default};
