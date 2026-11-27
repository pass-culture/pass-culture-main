import{a as e,n as t}from"./rolldown-runtime-sJBDdmOt.js";import{f as n}from"./iframe-DcQLyldS.js";import{t as r}from"./jsx-runtime-MKhVqBIO.js";import{t as i}from"./classnames-DQoS6hca.js";import{c as a,n as o,o as s,r as c,s as l,t as u}from"./Button-BLyEoen1.js";import{n as d,t as f}from"./dist-DTb8-fIZ.js";import{n as p,t as m}from"./useFocus-lntqub91.js";var h;function g(){return(g=t((()=>{h={"menu-list":`_menu-list_81aqc_1`}})))()}var _,v,y,b,x,S;function C(){return(C=t((()=>{_=e(i(),1),v=n(),p(),o(),a(),g(),y=r(),b=e=>`tab-${e}`,x=e=>`panel-${e}`,S=({navLabel:e,items:t,onClick:n,selectedKey:r,className:i})=>{let a=(0,v.useRef)({}),o=(0,v.useRef)(null);(0,v.useEffect)(()=>{m(o.current??a.current[r??``])},[r]);let d=(e,n)=>{let r=null;switch(e.key){case`ArrowRight`:r=(n+1)%t.length;break;case`ArrowLeft`:r=(n-1+t.length)%t.length;break;case`Home`:r=0;break;case`End`:r=t.length-1;break;default:return}e.preventDefault();let i=a.current[t[r].key];i?.focus(),i?.click()};return(0,y.jsx)(`div`,{children:(0,y.jsx)(`div`,{role:`tablist`,"aria-label":e,className:(0,_.default)(h[`menu-list`],i),children:t.map(({key:e,label:t,baseId:i,url:f,icon:p,iconAlt:m,iconColor:h},g)=>{let _=r===e,v=i??e,S={id:b(v),ref:t=>{a.current[e]=t,_&&(o.current=t)},role:`tab`,label:t,icon:p,iconAlt:m,iconColor:h,iconPosition:l.RIGHT,variant:s.TERTIARY,color:_?c.BRAND:c.NEUTRAL,onClick:()=>n?.(e),onKeyDown:e=>d(e,g),"aria-selected":_,"aria-controls":x(v),tabIndex:_?0:-1};return f?(0,y.jsx)(u,{as:`router-link`,to:f,...S},e):(0,y.jsx)(u,{as:`button`,...S},e)})})})};try{b.displayName=`getTabId`,b.__docgenInfo={description:``,displayName:`getTabId`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Tabs/Tabs.tsx`,methods:[],props:{},tags:{}}}catch{}try{x.displayName=`getPanelId`,x.__docgenInfo={description:``,displayName:`getPanelId`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Tabs/Tabs.tsx`,methods:[],props:{},tags:{}}}catch{}try{S.displayName=`Tabs`,S.__docgenInfo={description:"The Tabs component is used to render tabs following ARIA best practices.\nIt supports both navigation links and interactive buttons:\n - If a tab has a `url` property, it is rendered as a router link\n - If a tab has no `url`, it's purely for handling onClick events",displayName:`Tabs`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Tabs/Tabs.tsx`,methods:[],props:{navLabel:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Tabs/Tabs.tsx`,name:`TypeLiteral`}],description:`Navigation accessible name`,name:`navLabel`,required:!0,tags:{},type:{name:`string`}},selectedKey:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Tabs/Tabs.tsx`,name:`TypeLiteral`}],description:`The key of the selected link.`,name:`selectedKey`,required:!1,tags:{},type:{name:`string`}},className:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Tabs/Tabs.tsx`,name:`TypeLiteral`}],description:``,name:`className`,required:!1,tags:{},type:{name:`string`}},items:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Tabs/Tabs.tsx`,name:`TypeLiteral`}],description:`An array of tabs to be rendered.
Each tab can optionally include a URL for navigation.
If a URL is provided, the tab is rendered as a router link.`,name:`items`,required:!0,tags:{},type:{name:`TabItem<T>[]`}},onClick:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Tabs/Tabs.tsx`,name:`TypeLiteral`}],description:"The function called when a tab is clicked or selected.\nFor tabs with a `url`, it is called in addition to the navigation.",name:`onClick`,required:!1,tags:{},type:{name:`((selectedKey: T) => void)`}}},tags:{example:`// With navigation
<Tabs
  items={[{
    key: 'home',
    label: 'Home',
    url: '/home',
  }, {
    key: 'profile',
    label: 'Profile',
    url: '/profile',
  }]}
  selectedKey="home"
  navLabel="Navigation"
/>

// With buttons (no navigation)
<Tabs
  items={[{
    key: 'details',
    label: 'Details',
  }, {
    key: 'reviews',
    label: 'Reviews',
  }]}
  selectedKey="details"
  onClick={(key) => setActiveTab(key)}
  navLabel="Content tabs"
/>`}}}catch{}})))()}var w,T,E,D;function O(){return(O=t((()=>{d(),C(),w={title:`@/ui-kit/Tabs`,decorators:[f],component:S},T={args:{selectedKey:`individual`,items:[{label:`Offres individuelles`,url:`#`,key:`individual`},{label:`Offres collectives`,url:`#`,key:`collective`}],navLabel:`Navigation example`,onClick:e=>console.log(`Clicked: ${e}`)}},E={args:{selectedKey:`tab1`,items:[{key:`tab1`,label:`Tab 1`},{key:`tab2`,label:`Tab 2`}],navLabel:`Tabs example`,onClick:e=>console.log(`Clicked: ${e}`)}},D=[`NavLinksMode`,`TabMode`],T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
  args: {
    selectedKey: 'individual',
    items: [{
      label: 'Offres individuelles',
      url: '#',
      key: 'individual'
    }, {
      label: 'Offres collectives',
      url: '#',
      key: 'collective'
    }],
    navLabel: 'Navigation example',
    onClick: key => console.log(\`Clicked: \${key}\`)
  }
}`,...T.parameters?.docs?.source}}},E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
  args: {
    selectedKey: 'tab1',
    items: [{
      key: 'tab1',
      label: 'Tab 1'
    }, {
      key: 'tab2',
      label: 'Tab 2'
    }],
    navLabel: 'Tabs example',
    onClick: key => console.log(\`Clicked: \${key}\`)
  }
}`,...E.parameters?.docs?.source}}}})))()}O();export{T as NavLinksMode,E as TabMode,D as __namedExportsOrder,w as default};