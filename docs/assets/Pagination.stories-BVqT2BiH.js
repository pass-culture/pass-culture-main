import{j as e}from"./jsx-runtime-C_uOM0Gm.js";import{V as k}from"./index-vSssAp4U.js";import{r as C}from"./iframe-CTnXOULQ.js";import{c as p}from"./index-TscbDd2H.js";import{u as M}from"./useMediaQuery-DeNVqfPX.js";import{f as S,t as v}from"./full-three-dots-DhyQI2cN.js";import{f as F}from"./full-right-Dd3YsyCq.js";import{S as m}from"./SvgIcon-CJiY4LCz.js";import"./chunk-EPOLDU6W-u6n6pb5J.js";import"./preload-helper-PPVm8Dsz.js";const n={"pagination-nav":"_pagination-nav_ya7tl_1","pagination-list":"_pagination-list_ya7tl_10","pagination-list-item":"_pagination-list-item_ya7tl_19","pagination-link":"_pagination-link_ya7tl_24","pagination-link-current":"_pagination-link-current_ya7tl_43","pagination-link-prev":"_pagination-link-prev_ya7tl_57","pagination-link-next":"_pagination-link-next_ya7tl_57","visually-hidden":"_visually-hidden_ya7tl_76"},A=2,E=1,O=8,$=(l,r,{isMobile:a=!1}={})=>{if(r<O)return Array.from({length:r},(t,u)=>u+2).slice(0,-2);const s=a?E:A;let i=l-s,o=l+s;const g=o-i;return i<2?(i=2,o=i+g):o>r-1&&(o=r-1,i=o-g),Array.from({length:o-i+1},(t,u)=>i+u)},N=({className:l,currentPage:r,pageCount:a,onPageClick:s,forceMobile:i=!1})=>{const o=M("(max-width: 38.125rem)"),g=i||o;if(a<=1)return null;const d=c=>c===r,t=r===1,u=r===a,j=$(r,a,{isMobile:g});return e.jsx("nav",{"aria-label":"Pagination navigation",className:p(n["pagination-nav"],l),children:e.jsxs("ul",{className:n["pagination-list"],children:[e.jsx("li",{className:n["pagination-list-item"],children:e.jsxs("button",{type:"button",disabled:t,"aria-label":t?void 0:`Aller à la page précédente (${r-1} sur ${a})`,className:p(n["pagination-link"],n["pagination-link-prev"]),onClick:()=>s(r-1),children:[e.jsx(m,{src:S,alt:"",width:"16"}),!g&&e.jsx(e.Fragment,{children:"Page précédente"})]})}),e.jsx("li",{className:n["pagination-list-item"],"aria-current":t?"page":void 0,children:e.jsx("button",{type:"button","aria-label":t?`Page 1 sur ${a}`:`Aller à la page 1 sur ${a}`,className:p(n["pagination-link"],{[n["pagination-link-current"]]:t}),onClick:()=>s(1),children:"1"})}),j.at(0)>2&&e.jsx("li",{className:n["pagination-list-item"],children:e.jsx(m,{src:v,alt:"",width:"16"})}),j.map(c=>e.jsx("li",{className:n["pagination-list-item"],"aria-current":d(c)?"page":void 0,children:e.jsx("button",{type:"button","aria-label":d(c)?`Page ${c} sur ${a}`:`Aller à la page ${c} sur ${a}`,className:p(n["pagination-link"],{[n["pagination-link-current"]]:d(c)}),onClick:()=>s(c),children:c})},c)),j.at(-1)<a-1&&e.jsx("li",{className:n["pagination-list-item"],children:e.jsx(m,{src:v,alt:"",width:"16"})}),e.jsx("li",{className:n["pagination-list-item"],"aria-current":u?"page":void 0,children:e.jsxs("button",{type:"button","aria-label":u?`Page ${a} sur ${a}`:`Aller à la page ${a} sur ${a}`,className:p(n["pagination-link"],{[n["pagination-link-current"]]:u}),onClick:()=>s(a),children:[a,e.jsx("span",{className:n["visually-hidden"],children:"Dernière page"})]})}),e.jsx("li",{className:n["pagination-list-item"],children:e.jsxs("button",{type:"button",disabled:u,"aria-label":u?void 0:`Aller à la page suivante (${r+1} sur ${a})`,className:p(n["pagination-link"],n["pagination-link-next"]),onClick:()=>s(r+1),children:[!g&&e.jsx(e.Fragment,{children:"Page suivante"}),e.jsx(m,{src:F,alt:"",width:"16"})]})})]})})};try{N.displayName="Pagination",N.__docgenInfo={description:"",displayName:"Pagination",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},currentPage:{defaultValue:null,description:"The current page number.",name:"currentPage",required:!0,type:{name:"number"}},pageCount:{defaultValue:null,description:"The total number of pages.",name:"pageCount",required:!0,type:{name:"number"}},onPageClick:{defaultValue:null,description:"Callback function triggered when a page is clicked.",name:"onPageClick",required:!0,type:{name:"(page: number) => void"}},forceMobile:{defaultValue:{value:"false"},description:"Force the mobile view mode.",name:"forceMobile",required:!1,type:{name:"boolean"}}}}}catch{}const U={title:"@/design-system/Pagination",decorators:[k],component:N},b={args:{currentPage:1,pageCount:7}},f={args:{currentPage:7,pageCount:7}},P={args:{currentPage:1,pageCount:42}},h={args:{currentPage:42,pageCount:42}},_={args:{currentPage:13,pageCount:42}},x={args:{currentPage:13,pageCount:42,forceMobile:!0}},y={args:{currentPage:1,pageCount:8,forceMobile:!1},render:l=>{const[r,a]=C.useState(l.currentPage),[s,i]=C.useState(l.pageCount),[o,g]=C.useState(l.forceMobile),d=Number.isNaN(s)?l.pageCount:s;return e.jsxs(e.Fragment,{children:["(You can click on any page)",e.jsx("br",{}),e.jsx("br",{}),e.jsx(N,{currentPage:r,pageCount:d,onPageClick:t=>a(t),forceMobile:o}),e.jsx("br",{}),e.jsxs("fieldset",{children:[e.jsx("legend",{children:"DEMO SETTINGS :"}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"demo_pageCount",children:"Page count :"})," ",e.jsx("input",{id:"demo_pageCount",type:"number",min:"1",onChange:t=>i(parseInt(t.target.value)),value:s})]}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"demo_forceMobile",children:"Force mobile view :"})," ",e.jsx("input",{id:"demo_forceMobile",type:"checkbox",onChange:t=>g(t.target.checked),checked:o})]})]})]})}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 7
  }
}`,...b.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 7,
    pageCount: 7
  }
}`,...f.parameters?.docs?.source}}};P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 42
  }
}`,...P.parameters?.docs?.source}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 42,
    pageCount: 42
  }
}`,...h.parameters?.docs?.source}}};_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 13,
    pageCount: 42
  }
}`,..._.parameters?.docs?.source}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 13,
    pageCount: 42,
    forceMobile: true
  }
}`,...x.parameters?.docs?.source}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 8,
    forceMobile: false
  },
  render: args => {
    const [currentPage, setCurrentPage] = useState(args.currentPage);
    const [pageCount, setPageCount] = useState(args.pageCount);
    const [forceMobile, setForceMobile] = useState(args.forceMobile);
    const safePageCount = Number.isNaN(pageCount) ? args.pageCount : pageCount;
    return <>
        (You can click on any page)
        <br />
        <br />
        <Pagination currentPage={currentPage} pageCount={safePageCount} onPageClick={page => setCurrentPage(page)} forceMobile={forceMobile} />
        
        <br />
        <fieldset>
          <legend>DEMO SETTINGS :</legend>

          <div>
            <label htmlFor="demo_pageCount">Page count :</label>{' '}
            <input id="demo_pageCount" type="number" min="1" onChange={e => setPageCount(parseInt(e.target.value))} value={pageCount} />
          </div>

          <div>
            <label htmlFor='demo_forceMobile'>Force mobile view :</label>{' '}
            <input id="demo_forceMobile" type="checkbox" onChange={e => setForceMobile(e.target.checked)} checked={forceMobile} />
          </div>
          
        </fieldset>
      </>;
  }
}`,...y.parameters?.docs?.source}}};const Y=["FirstPage","LastPage","LotsOfPages","LotsOfPagesLast","LotsOfPagesMiddle","MobileViewForced","Playground"];export{b as FirstPage,f as LastPage,P as LotsOfPages,h as LotsOfPagesLast,_ as LotsOfPagesMiddle,x as MobileViewForced,y as Playground,Y as __namedExportsOrder,U as default};
