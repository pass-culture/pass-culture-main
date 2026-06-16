import{i as e,s as t}from"./preload-helper-xPQekRTU.js";import{C as n}from"./iframe-C9q6i3zL.js";import{t as r}from"./jsx-runtime-CaZkqeYb.js";import{n as i,r as a}from"./dist-BUkniBaw.js";import{n as o,t as s}from"./Pagination-BJTh9pfJ.js";var c,l,u,d,f,p,m,h,g,_,v;e((()=>{a(),c=t(n(),1),o(),l=r(),u={title:`@/design-system/Pagination`,decorators:[i],component:s},d={args:{currentPage:1,pageCount:7}},f={args:{currentPage:7,pageCount:7}},p={args:{currentPage:1,pageCount:42}},m={args:{currentPage:42,pageCount:42}},h={args:{currentPage:13,pageCount:42}},g={args:{currentPage:13,pageCount:42,forceMobile:!0}},_={args:{currentPage:1,pageCount:8,forceMobile:!1},render:e=>{let[t,n]=(0,c.useState)(e.currentPage),[r,i]=(0,c.useState)(e.pageCount),[a,o]=(0,c.useState)(e.forceMobile),u=Number.isNaN(r)?e.pageCount:r;return(0,l.jsxs)(l.Fragment,{children:[`(You can click on any page)`,(0,l.jsx)(`br`,{}),(0,l.jsx)(`br`,{}),(0,l.jsx)(s,{currentPage:t,pageCount:u,onPageClick:e=>n(e),forceMobile:a}),(0,l.jsx)(`br`,{}),(0,l.jsxs)(`fieldset`,{children:[(0,l.jsx)(`legend`,{children:`DEMO SETTINGS :`}),(0,l.jsxs)(`div`,{children:[(0,l.jsx)(`label`,{htmlFor:`demo_pageCount`,children:`Page count :`}),` `,(0,l.jsx)(`input`,{id:`demo_pageCount`,type:`number`,min:`1`,onChange:e=>i(Number.parseInt(e.target.value)),value:r})]}),(0,l.jsxs)(`div`,{children:[(0,l.jsx)(`label`,{htmlFor:`demo_forceMobile`,children:`Force mobile view :`}),` `,(0,l.jsx)(`input`,{id:`demo_forceMobile`,type:`checkbox`,onChange:e=>o(e.target.checked),checked:a})]})]})]})}},d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 7
  }
}`,...d.parameters?.docs?.source}}},f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 7,
    pageCount: 7
  }
}`,...f.parameters?.docs?.source}}},p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 42
  }
}`,...p.parameters?.docs?.source}}},m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 42,
    pageCount: 42
  }
}`,...m.parameters?.docs?.source}}},h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 13,
    pageCount: 42
  }
}`,...h.parameters?.docs?.source}}},g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 13,
    pageCount: 42,
    forceMobile: true
  }
}`,...g.parameters?.docs?.source}}},_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
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
}`,..._.parameters?.docs?.source}}},v=[`FirstPage`,`LastPage`,`LotsOfPages`,`LotsOfPagesLast`,`LotsOfPagesMiddle`,`MobileViewForced`,`Playground`]}))();export{d as FirstPage,f as LastPage,p as LotsOfPages,m as LotsOfPagesLast,h as LotsOfPagesMiddle,g as MobileViewForced,_ as Playground,v as __namedExportsOrder,u as default};