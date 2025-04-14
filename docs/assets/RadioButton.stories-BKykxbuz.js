import{j as e}from"./jsx-runtime-BYYWji4R.js";import{u as E,a as M,F as O}from"./index.esm-Z2NZos4s.js";import{l as w}from"./logo-pass-culture-S_OdLkOk.js";import{B as I,R as P}from"./BaseRadio-DON7-zCJ.js";import{c as S}from"./index-DeARc5FM.js";import{r as L}from"./index-ClcD9ViR.js";import"./SvgIcon-CyWUmZpn.js";import"./_commonjsHelpers-Cpj98o6Y.js";const n=L.forwardRef(({disabled:r,name:a,label:l,value:d,variant:t,className:u,hasError:B,checked:F,ariaDescribedBy:R,childrenOnChecked:D,icon:W,iconPosition:k,description:q,..._},C)=>e.jsx(I,{ref:C,..._,name:a,disabled:r,id:a,label:l,value:d,className:S(u),checked:F,hasError:B,variant:t,ariaDescribedBy:R,childrenOnChecked:D,icon:W,iconPosition:k,description:q}));n.displayName="RadioButton";try{n.displayName="RadioButton",n.__docgenInfo={description:"",displayName:"RadioButton",props:{name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string | Element"}},value:{defaultValue:null,description:"",name:"value",required:!0,type:{name:"string"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"DEFAULT"'},{value:'"BOX"'}]}},hasError:{defaultValue:null,description:"",name:"hasError",required:!1,type:{name:"boolean"}},checked:{defaultValue:null,description:"",name:"checked",required:!1,type:{name:"boolean"}},ariaDescribedBy:{defaultValue:null,description:"",name:"ariaDescribedBy",required:!1,type:{name:"string"}},childrenOnChecked:{defaultValue:null,description:"",name:"childrenOnChecked",required:!1,type:{name:"Element"}},icon:{defaultValue:null,description:"",name:"icon",required:!1,type:{name:"string"}},iconPosition:{defaultValue:null,description:"",name:"iconPosition",required:!1,type:{name:"enum",value:[{value:'"center"'},{value:'"right"'}]}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}}}}}catch{}const Q={title:"ui-kit/formsV2/RadioButton",component:n},c={wrapper:{color:"#666",fontSize:"0.8rem",padding:"0 1rem",backgroundColor:"#f5f5f5",borderRadius:"0.2rem",border:"thin solid #e1e1e1",marginTop:"1rem"},pre:{display:"inline-block",padding:"0.5rem"},link:{textDecoration:"underline"}},N=({children:r})=>{const a=M({defaultValues:{gender:""}}),{reset:l,watch:d}=a,t=d("gender");return e.jsxs(O,{...a,children:[e.jsx("form",{children:r}),e.jsxs("div",{style:c.wrapper,children:["RAW value: ",e.jsx("pre",{style:c.pre,children:t}),t&&e.jsx("a",{href:"#",onClick:u=>{u.preventDefault(),l()},style:c.link,children:"(Reset value)"})]})]})},m=r=>e.jsx(N,{children:e.jsx(r,{})}),p=r=>{const{register:a}=E();return e.jsx(n,{...r,...a("gender")})},o={decorators:[m],args:{label:"Male",value:"M"},render:p},s={decorators:[m],args:{variant:P.BOX,label:"Male",value:"M"},render:p},T=({src:r})=>e.jsxs("div",{style:{display:"flex",gap:"1rem"},children:[e.jsx("img",{src:r,width:100}),e.jsxs("p",{style:{display:"flex",flexDirection:"column"},children:[e.jsx("strong",{children:"Long titre lorem ipsum mon offre"}),"Test de sous-titre"]})]}),i={decorators:[m],args:{label:e.jsx(T,{src:w}),value:"Long titre"},render:p};var f,g,h;o.parameters={...o.parameters,docs:{...(f=o.parameters)==null?void 0:f.docs,source:{originalSource:`{
  decorators: [WithinFormDecorator],
  args: {
    label: 'Male',
    value: 'M'
  },
  render: renderFx
}`,...(h=(g=o.parameters)==null?void 0:g.docs)==null?void 0:h.source}}};var x,y,v;s.parameters={...s.parameters,docs:{...(x=s.parameters)==null?void 0:x.docs,source:{originalSource:`{
  decorators: [WithinFormDecorator],
  args: {
    variant: RadioVariant.BOX,
    label: 'Male',
    value: 'M'
  },
  render: renderFx
}`,...(v=(y=s.parameters)==null?void 0:y.docs)==null?void 0:v.source}}};var b,j,V;i.parameters={...i.parameters,docs:{...(b=i.parameters)==null?void 0:b.docs,source:{originalSource:`{
  decorators: [WithinFormDecorator],
  args: {
    label: <WithImage src={logoPassCultureIcon} />,
    value: 'Long titre'
  },
  render: renderFx
}`,...(V=(j=i.parameters)==null?void 0:j.docs)==null?void 0:V.source}}};const Y=["Default","WithBorder","WithChildren"];export{o as Default,s as WithBorder,i as WithChildren,Y as __namedExportsOrder,Q as default};
