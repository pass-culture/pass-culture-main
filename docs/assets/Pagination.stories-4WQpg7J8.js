import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-CS1SLfKD.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./dist-Br1ZADm5.js";import{t as i}from"./Pagination-BnPPzRb6.js";var a=e(t(),1),o=n(),s={title:`@/design-system/Pagination`,decorators:[r],component:i},c={args:{currentPage:1,pageCount:7}},l={args:{currentPage:7,pageCount:7}},u={args:{currentPage:1,pageCount:42}},d={args:{currentPage:42,pageCount:42}},f={args:{currentPage:13,pageCount:42}},p={args:{currentPage:13,pageCount:42,forceMobile:!0}},m={args:{currentPage:1,pageCount:8,forceMobile:!1},render:e=>{let[t,n]=(0,a.useState)(e.currentPage),[r,s]=(0,a.useState)(e.pageCount),[c,l]=(0,a.useState)(e.forceMobile),u=Number.isNaN(r)?e.pageCount:r;return(0,o.jsxs)(o.Fragment,{children:[`(You can click on any page)`,(0,o.jsx)(`br`,{}),(0,o.jsx)(`br`,{}),(0,o.jsx)(i,{currentPage:t,pageCount:u,onPageClick:e=>n(e),forceMobile:c}),(0,o.jsx)(`br`,{}),(0,o.jsxs)(`fieldset`,{children:[(0,o.jsx)(`legend`,{children:`DEMO SETTINGS :`}),(0,o.jsxs)(`div`,{children:[(0,o.jsx)(`label`,{htmlFor:`demo_pageCount`,children:`Page count :`}),` `,(0,o.jsx)(`input`,{id:`demo_pageCount`,type:`number`,min:`1`,onChange:e=>s(Number.parseInt(e.target.value)),value:r})]}),(0,o.jsxs)(`div`,{children:[(0,o.jsx)(`label`,{htmlFor:`demo_forceMobile`,children:`Force mobile view :`}),` `,(0,o.jsx)(`input`,{id:`demo_forceMobile`,type:`checkbox`,onChange:e=>l(e.target.checked),checked:c})]})]})]})}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 7
  }
}`,...c.parameters?.docs?.source}}},l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 7,
    pageCount: 7
  }
}`,...l.parameters?.docs?.source}}},u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 1,
    pageCount: 42
  }
}`,...u.parameters?.docs?.source}}},d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 42,
    pageCount: 42
  }
}`,...d.parameters?.docs?.source}}},f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 13,
    pageCount: 42
  }
}`,...f.parameters?.docs?.source}}},p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    currentPage: 13,
    pageCount: 42,
    forceMobile: true
  }
}`,...p.parameters?.docs?.source}}},m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
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
}`,...m.parameters?.docs?.source}}};var h=[`FirstPage`,`LastPage`,`LotsOfPages`,`LotsOfPagesLast`,`LotsOfPagesMiddle`,`MobileViewForced`,`Playground`];export{c as FirstPage,l as LastPage,u as LotsOfPages,d as LotsOfPagesLast,f as LotsOfPagesMiddle,p as MobileViewForced,m as Playground,h as __namedExportsOrder,s as default};