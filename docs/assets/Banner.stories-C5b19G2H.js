import{j as r}from"./jsx-runtime-CFw-YZxz.js";import{c as t}from"./index-DoYKShUP.js";import{f as L}from"./full-close-5Oxr7nnd.js";import{f as W}from"./full-info-D24AtBVt.js";import{B as j}from"./Button-BQhVOM2V.js";import{B as C}from"./ButtonLink-C6qWkUST.js";import{B as I}from"./types-yVZEaApa.js";import{S}from"./SvgIcon-u9qs7tKh.js";import{f as i}from"./full-link-CYVo23DH.js";import{V as D}from"./index-bhxcNJC2.js";import"./iframe-Btsl9WO5.js";import"./preload-helper-PPVm8Dsz.js";import"./stroke-pass-CALgybTM.js";import"./Tooltip-qj0hnQnZ.js";import"./Button.module-CY1ZDZvt.js";import"./chunk-WWGJGFF6-7GYn68dv.js";const B="_banner_19mrp_1",R="_success_19mrp_11",A="_warning_19mrp_17",q="_error_19mrp_23",w="_inner_19mrp_29",U="_header_19mrp_35",T="_info_19mrp_40",z="_title_19mrp_45",F="_content_19mrp_59",O="_link_19mrp_87",G="_image_19mrp_126",e={banner:B,success:R,warning:A,error:q,inner:w,header:U,info:T,title:z,"title-large":"_title-large_19mrp_53",content:F,"content-body":"_content-body_19mrp_66","content-body-large":"_content-body-large_19mrp_74","actions-list":"_actions-list_19mrp_80",link:O,"link-large":"_link-large_19mrp_98","close-button":"_close-button_19mrp_108",image:G};var o=(s=>(s.DEFAULT="default",s.SUCCESS="success",s.WARNING="warning",s.ERROR="error",s))(o||{});const v=({title:s,description:b,actions:y=[],icon:E=W,imageSrc:k,variant:x="default",size:l="default",closable:N=!1,onClose:V})=>r.jsx("div",{className:t(e.banner,e[x]),"data-testid":"banner",children:r.jsx("div",{className:e.inner,children:r.jsxs("div",{className:e.content,children:[r.jsx(S,{className:e.info,src:E,"aria-hidden":"true"}),r.jsxs("div",{className:t(e["content-body"],{[e["content-body-large"]]:l==="large"}),children:[r.jsx("span",{className:t(e.title,{[e["title-large"]]:l==="large"}),children:s}),b&&r.jsx("span",{className:e.description,children:b}),y.length>0&&r.jsx("ul",{className:e["actions-list"],children:y.map(a=>r.jsx("li",{children:a.type==="link"?r.jsx(C,{className:t(e.link,{[e["link-large"]]:l==="large"}),href:a.href,target:a.isExternal?"_blank":"_self",rel:a.isExternal?"noopener noreferrer":void 0,to:a.href,icon:a.icon,iconAlt:a.iconAlt,isExternal:a.isExternal,children:a.label}):r.jsx(j,{className:t(e.link,{[e["link-large"]]:l==="large"}),variant:I.TERNARY,icon:a.icon,onClick:()=>a.onClick?.(),children:a.label})},a.label))})]}),k&&r.jsx("img",{src:k,className:e.image,alt:"","aria-hidden":"true"}),N&&r.jsx("button",{type:"button",className:e["close-button"],onClick:V,"aria-label":"Fermer la bannière d’information",children:r.jsx(S,{src:L,width:"16"})})]})})});try{v.displayName="Banner",v.__docgenInfo={description:"",displayName:"Banner",props:{title:{defaultValue:null,description:"",name:"title",required:!0,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string | Element"}},actions:{defaultValue:{value:"[]"},description:"",name:"actions",required:!1,type:{name:"BannerLink[]"}},icon:{defaultValue:null,description:"",name:"icon",required:!1,type:{name:"string"}},imageSrc:{defaultValue:null,description:"",name:"imageSrc",required:!1,type:{name:"string"}},variant:{defaultValue:{value:"BannerVariants.DEFAULT"},description:"Visual style (defines colors)",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"success"'},{value:'"warning"'},{value:'"error"'}]}},size:{defaultValue:{value:"default"},description:"",name:"size",required:!1,type:{name:"enum",value:[{value:'"large"'},{value:'"default"'}]}},closable:{defaultValue:{value:"false"},description:"Show close button?",name:"closable",required:!1,type:{name:"boolean"}},onClose:{defaultValue:null,description:"Callback called on close button click",name:"onClose",required:!1,type:{name:"(() => void)"}}}}}catch{}const M=""+new URL("turtle-CX4Zo2gH.png",import.meta.url).href,oe={title:"@/design-system/Banner",component:v,decorators:[D,s=>r.jsx("div",{style:{width:"fit-content"},children:r.jsx(s,{})})]},n={args:{title:"Titre important très long très long très long très long très",description:"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris mattis libero ultrices sem scelerisque gravida. Lorem ipsum dolor sit amet, consectetur adipiscing elit. ",actions:[{label:"En savoir plus",href:"#",icon:i,type:"link"},{label:"En savoir plus",href:"#",icon:i,type:"link"},{label:"En savoir plus",href:"#",icon:i,type:"link"},{label:"En savoir plus",href:"#",icon:i,type:"link"}],imageSrc:M,variant:o.DEFAULT,size:"default",closable:!0}},c={args:{...n.args,variant:o.SUCCESS}},u={args:{...n.args,variant:o.WARNING}},m={args:{...n.args,variant:o.ERROR}},p={args:{...n.args,description:void 0}},d={args:{...n.args,actions:[]}},g={args:{...n.args,imageSrc:void 0}},f={args:{...n.args,closable:!1}},_={args:{...n.args,size:"large"}},h={args:{...n.args,icon:i}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
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
}`,...m.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    description: undefined
  }
}`,...p.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    actions: []
  }
}`,...d.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
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
}`,...h.parameters?.docs?.source}}};const le=["Default","WithSuccessVariant","WithWarningVariant","WithErrorVariant","WithoutDescription","WithoutActions","WithoutImage","WithoutCloseButton","LargeSize","CustomIcon"];export{h as CustomIcon,n as Default,_ as LargeSize,m as WithErrorVariant,c as WithSuccessVariant,u as WithWarningVariant,d as WithoutActions,f as WithoutCloseButton,p as WithoutDescription,g as WithoutImage,le as __namedExportsOrder,oe as default};
