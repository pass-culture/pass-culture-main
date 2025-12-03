import{j as e}from"./jsx-runtime-B8a8t_-W.js";import{V as C}from"./index-CACinmCu.js";import{r as m}from"./iframe-IMpKXUaK.js";import{c as p}from"./index-B0t6kxdL.js";import{f as k,a as y}from"./full-three-dots-9fnDZfZ9.js";import{f as S}from"./full-right-Dd3YsyCq.js";import{S as f}from"./SvgIcon-BmgrCBFi.js";import"./chunk-FGUA77HG-Bj5OxmDE.js";import"./preload-helper-PPVm8Dsz.js";function w(t,a){try{return t.addEventListener("change",a),()=>t.removeEventListener("change",a)}catch{return t.addListener(a),()=>t.removeListener(a)}}function E(t,a){return typeof window<"u"&&"matchMedia"in window?window.matchMedia(t).matches:!1}function F(t,a,{getInitialValueInEffect:n}={getInitialValueInEffect:!0}){const[s,o]=m.useState(n?a:E(t)),i=m.useRef();return m.useEffect(()=>{if("matchMedia"in window)return i.current=window.matchMedia(t),o(i.current.matches),w(i.current,c=>o(c.matches))},[t]),s}const r={"pagination-nav":"_pagination-nav_ya7tl_1","pagination-list":"_pagination-list_ya7tl_10","pagination-list-item":"_pagination-list-item_ya7tl_19","pagination-link":"_pagination-link_ya7tl_24","pagination-link-current":"_pagination-link-current_ya7tl_43","pagination-link-prev":"_pagination-link-prev_ya7tl_57","pagination-link-next":"_pagination-link-next_ya7tl_57","visually-hidden":"_visually-hidden_ya7tl_76"},L=2,I=1,A=8,O=(t,a,{isMobile:n=!1}={})=>{if(a<A)return Array.from({length:a},(l,g)=>g+2).slice(0,-2);const s=n?I:L;let o=t-s,i=t+s;const c=i-o;return o<2?(o=2,i=o+c):i>a-1&&(i=a-1,o=i-c),Array.from({length:i-o+1},(l,g)=>o+g)},N=({className:t,currentPage:a,pageCount:n,onPageClick:s,forceMobile:o=!1})=>{const i=F("(max-width: 38.125rem)"),c=o||i;if(n<=1)return null;const d=u=>u===a,l=a===1,g=a===n,j=O(a,n,{isMobile:c});return e.jsx("nav",{"aria-label":"Pagination navigation",className:p(r["pagination-nav"],t),children:e.jsxs("ul",{className:r["pagination-list"],children:[e.jsx("li",{className:r["pagination-list-item"],children:e.jsxs("button",{type:"button",disabled:l,"aria-label":l?void 0:`Aller à la page précédente (${a-1} sur ${n})`,className:p(r["pagination-link"],r["pagination-link-prev"]),onClick:()=>s(a-1),children:[e.jsx(f,{src:k,alt:"",width:"16"}),!c&&e.jsx(e.Fragment,{children:"Page précédente"})]})}),e.jsx("li",{className:r["pagination-list-item"],"aria-current":l?"page":void 0,children:e.jsx("button",{type:"button","aria-label":l?`Page 1 sur ${n}`:`Aller à la page 1 sur ${n}`,className:p(r["pagination-link"],{[r["pagination-link-current"]]:l}),onClick:()=>s(1),children:"1"})}),j.at(0)>2&&e.jsx("li",{className:r["pagination-list-item"],children:e.jsx(f,{src:y,alt:"",width:"16"})}),j.map(u=>e.jsx("li",{className:r["pagination-list-item"],"aria-current":d(u)?"page":void 0,children:e.jsx("button",{type:"button","aria-label":d(u)?`Page ${u} sur ${n}`:`Aller à la page ${u} sur ${n}`,className:p(r["pagination-link"],{[r["pagination-link-current"]]:d(u)}),onClick:()=>s(u),children:u})},u)),j.at(-1)<n-1&&e.jsx("li",{className:r["pagination-list-item"],children:e.jsx(f,{src:y,alt:"",width:"16"})}),e.jsx("li",{className:r["pagination-list-item"],"aria-current":g?"page":void 0,children:e.jsxs("button",{type:"button","aria-label":g?`Page ${n} sur ${n}`:`Aller à la page ${n} sur ${n}`,className:p(r["pagination-link"],{[r["pagination-link-current"]]:g}),onClick:()=>s(n),children:[n,e.jsx("span",{className:r["visually-hidden"],children:"Dernière page"})]})}),e.jsx("li",{className:r["pagination-list-item"],children:e.jsxs("button",{type:"button",disabled:g,"aria-label":g?void 0:`Aller à la page suivante (${a+1} sur ${n})`,className:p(r["pagination-link"],r["pagination-link-next"]),onClick:()=>s(a+1),children:[!c&&e.jsx(e.Fragment,{children:"Page suivante"}),e.jsx(f,{src:S,alt:"",width:"16"})]})})]})})};try{N.displayName="Pagination",N.__docgenInfo={description:"",displayName:"Pagination",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},currentPage:{defaultValue:null,description:"The current page number.",name:"currentPage",required:!0,type:{name:"number"}},pageCount:{defaultValue:null,description:"The total number of pages.",name:"pageCount",required:!0,type:{name:"number"}},onPageClick:{defaultValue:null,description:"Callback function triggered when a page is clicked.",name:"onPageClick",required:!0,type:{name:"(page: number) => void"}},forceMobile:{defaultValue:{value:"false"},description:"Force the mobile view mode.",name:"forceMobile",required:!1,type:{name:"boolean"}}}}}catch{}const q={title:"@/design-system/Pagination",decorators:[C],component:N},h={args:{currentPage:1,pageCount:7}},b={args:{currentPage:7,pageCount:7}},P={args:{currentPage:1,pageCount:42}},_={args:{currentPage:42,pageCount:42}},x={args:{currentPage:13,pageCount:42}},v={args:{currentPage:13,pageCount:42,forceMobile:!0}},M={args:{currentPage:1,pageCount:8,forceMobile:!1},render:t=>{const[a,n]=m.useState(t.currentPage),[s,o]=m.useState(t.pageCount),[i,c]=m.useState(t.forceMobile),d=Number.isNaN(s)?t.pageCount:s;return e.jsxs(e.Fragment,{children:["(You can click on any page)",e.jsx("br",{}),e.jsx("br",{}),e.jsx(N,{currentPage:a,pageCount:d,onPageClick:l=>n(l),forceMobile:i}),e.jsx("br",{}),e.jsxs("fieldset",{children:[e.jsx("legend",{children:"DEMO SETTINGS :"}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"demo_pageCount",children:"Page count :"})," ",e.jsx("input",{id:"demo_pageCount",type:"number",min:"1",onChange:l=>o(parseInt(l.target.value)),value:s})]}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"demo_forceMobile",children:"Force mobile view :"})," ",e.jsx("input",{id:"demo_forceMobile",type:"checkbox",onChange:l=>c(l.target.checked),checked:i})]})]})]})}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 7
  }
}`,...h.parameters?.docs?.source}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 7,
    pageCount: 7
  }
}`,...b.parameters?.docs?.source}}};P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 42
  }
}`,...P.parameters?.docs?.source}}};_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 42,
    pageCount: 42
  }
}`,..._.parameters?.docs?.source}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 13,
    pageCount: 42
  }
}`,...x.parameters?.docs?.source}}};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 13,
    pageCount: 42,
    forceMobile: true
  }
}`,...v.parameters?.docs?.source}}};M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
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
}`,...M.parameters?.docs?.source}}};const K=["FirstPage","LastPage","LotsOfPages","LotsOfPagesLast","LotsOfPagesMiddle","MobileViewForced","Playground"];export{h as FirstPage,b as LastPage,P as LotsOfPages,_ as LotsOfPagesLast,x as LotsOfPagesMiddle,v as MobileViewForced,M as Playground,K as __namedExportsOrder,q as default};
