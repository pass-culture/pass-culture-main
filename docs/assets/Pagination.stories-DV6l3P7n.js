import{n as e}from"./rolldown-runtime-DkW27tQK.js";import{d as t}from"./iframe-DVL5UwC3.js";import{t as n}from"./jsx-runtime-DeHZSEgm.js";import{n as r,t as i}from"./dist-BTiz9SF9.js";import{n as a,t as o}from"./Pagination-CoFz0xhQ.js";var s,c,l,u,d,f,p,m,h,g,_;function v(){return(v=e((()=>{r(),s=t(),a(),c=n(),l={title:`@/design-system/Pagination`,decorators:[i],component:o},u={args:{currentPage:1,pageCount:7}},d={args:{currentPage:7,pageCount:7}},f={args:{currentPage:1,pageCount:42}},p={args:{currentPage:42,pageCount:42}},m={args:{currentPage:13,pageCount:42}},h={args:{currentPage:13,pageCount:42,forceMobile:!0}},g={args:{currentPage:1,pageCount:8,forceMobile:!1},render:e=>{let[t,n]=(0,s.useState)(e.currentPage),[r,i]=(0,s.useState)(e.pageCount),[a,l]=(0,s.useState)(e.forceMobile),u=Number.isNaN(r)?e.pageCount:r;return(0,c.jsxs)(c.Fragment,{children:[`(You can click on any page)`,(0,c.jsx)(`br`,{}),(0,c.jsx)(`br`,{}),(0,c.jsx)(o,{currentPage:t,pageCount:u,onPageClick:e=>n(e),forceMobile:a}),(0,c.jsx)(`br`,{}),(0,c.jsxs)(`fieldset`,{children:[(0,c.jsx)(`legend`,{children:`DEMO SETTINGS :`}),(0,c.jsxs)(`div`,{children:[(0,c.jsx)(`label`,{htmlFor:`demo_pageCount`,children:`Page count :`}),` `,(0,c.jsx)(`input`,{id:`demo_pageCount`,type:`number`,min:`1`,onChange:e=>i(Number.parseInt(e.target.value)),value:r})]}),(0,c.jsxs)(`div`,{children:[(0,c.jsx)(`label`,{htmlFor:`demo_forceMobile`,children:`Force mobile view :`}),` `,(0,c.jsx)(`input`,{id:`demo_forceMobile`,type:`checkbox`,onChange:e=>l(e.target.checked),checked:a})]})]})]})}},u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 7
  }
}`,...u.parameters?.docs?.source}}},d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 7,
    pageCount: 7
  }
}`,...d.parameters?.docs?.source}}},f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 42
  }
}`,...f.parameters?.docs?.source}}},p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 42,
    pageCount: 42
  }
}`,...p.parameters?.docs?.source}}},m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 13,
    pageCount: 42
  }
}`,...m.parameters?.docs?.source}}},h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 13,
    pageCount: 42,
    forceMobile: true
  }
}`,...h.parameters?.docs?.source}}},g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
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
            <input id="demo_pageCount" type="number" min="1" onChange={e => setPageCount(Number.parseInt(e.target.value))} value={pageCount} />
          </div>

          <div>
            <label htmlFor='demo_forceMobile'>Force mobile view :</label>{' '}
            <input id="demo_forceMobile" type="checkbox" onChange={e => setForceMobile(e.target.checked)} checked={forceMobile} />
          </div>
          
        </fieldset>
      </>;
  }
}`,...g.parameters?.docs?.source}}},_=[`FirstPage`,`LastPage`,`LotsOfPages`,`LotsOfPagesLast`,`LotsOfPagesMiddle`,`MobileViewForced`,`Playground`]})))()}v();export{u as FirstPage,d as LastPage,f as LotsOfPages,p as LotsOfPagesLast,m as LotsOfPagesMiddle,h as MobileViewForced,g as Playground,_ as __namedExportsOrder,l as default};