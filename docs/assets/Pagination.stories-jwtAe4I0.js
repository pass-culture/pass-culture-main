import{j as e}from"./jsx-runtime-u17CrQMm.js";import{V as M}from"./index-BscxPrJB.js";import{r as p}from"./iframe-Cl1rLDZQ.js";import{P as d}from"./Pagination-CsFwSB2s.js";import"./chunk-LFPYN7LY-oiaQIIRL.js";import"./preload-helper-PPVm8Dsz.js";import"./index-CttdNlXk.js";import"./full-left-vjwAEs82.js";import"./full-right-Dd3YsyCq.js";import"./full-three-dots-C5Ey0HNi.js";import"./SvgIcon-DuZPzNRk.js";const N={title:"@/design-system/Pagination",decorators:[M],component:d},o={args:{currentPage:1,pageCount:7}},t={args:{currentPage:7,pageCount:7}},s={args:{currentPage:1,pageCount:42}},n={args:{currentPage:42,pageCount:42}},c={args:{currentPage:13,pageCount:42}},g={args:{currentPage:13,pageCount:42,forceMobile:!0}},u={args:{currentPage:1,pageCount:8,forceMobile:!1},render:a=>{const[m,P]=p.useState(a.currentPage),[i,C]=p.useState(a.pageCount),[l,b]=p.useState(a.forceMobile),f=Number.isNaN(i)?a.pageCount:i;return e.jsxs(e.Fragment,{children:["(You can click on any page)",e.jsx("br",{}),e.jsx("br",{}),e.jsx(d,{currentPage:m,pageCount:f,onPageClick:r=>P(r),forceMobile:l}),e.jsx("br",{}),e.jsxs("fieldset",{children:[e.jsx("legend",{children:"DEMO SETTINGS :"}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"demo_pageCount",children:"Page count :"})," ",e.jsx("input",{id:"demo_pageCount",type:"number",min:"1",onChange:r=>C(parseInt(r.target.value)),value:i})]}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"demo_forceMobile",children:"Force mobile view :"})," ",e.jsx("input",{id:"demo_forceMobile",type:"checkbox",onChange:r=>b(r.target.checked),checked:l})]})]})]})}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 7
  }
}`,...o.parameters?.docs?.source}}};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 7,
    pageCount: 7
  }
}`,...t.parameters?.docs?.source}}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 42
  }
}`,...s.parameters?.docs?.source}}};n.parameters={...n.parameters,docs:{...n.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 42,
    pageCount: 42
  }
}`,...n.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 13,
    pageCount: 42
  }
}`,...c.parameters?.docs?.source}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 13,
    pageCount: 42,
    forceMobile: true
  }
}`,...g.parameters?.docs?.source}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
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
}`,...u.parameters?.docs?.source}}};const E=["FirstPage","LastPage","LotsOfPages","LotsOfPagesLast","LotsOfPagesMiddle","MobileViewForced","Playground"];export{o as FirstPage,t as LastPage,s as LotsOfPages,n as LotsOfPagesLast,c as LotsOfPagesMiddle,g as MobileViewForced,u as Playground,E as __namedExportsOrder,N as default};
