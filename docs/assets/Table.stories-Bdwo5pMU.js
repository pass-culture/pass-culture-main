import{a as e,n as t}from"./rolldown-runtime-sJBDdmOt.js";import{f as n}from"./iframe-DDrY5Qix.js";import{t as r}from"./jsx-runtime-MKhVqBIO.js";import{t as i}from"./classnames-DQoS6hca.js";import{n as a,t as ee}from"./Tooltip-vRoh0Jj2.js";import{a as o,n as s,r as te,s as ne,t as re}from"./Button-BzlP3edT.js";import{n as c,t as l}from"./SvgIcon-CzZXj8Lg.js";import{n as ie,t as ae}from"./Checkbox-CB7cO4GU.js";import{n as oe,t as se}from"./full-down-3k6yj_Bm.js";import{n as ce,t as u}from"./full-refresh-D2Aqp5zl.js";import{n as d,t as le}from"./full-up-DAFDFG4Y.js";import{n as f,r as ue,t as de}from"./useMediaQuery-Cl44xxiO.js";import{n as p,t as fe}from"./Pagination-C5IJEaTX.js";import{n as m,t as pe}from"./Skeleton-C2hEg3dz.js";var h,g,me;function he(){return(he=t((()=>{h=n(),g=function(e){return e.ASC=`asc`,e.DESC=`desc`,e.NONE=`none`,e}({}),me=()=>{let[e,t]=(0,h.useState)(null),[n,r]=(0,h.useState)(`none`);return{currentSortingColumn:e,currentSortingMode:n,onColumnHeaderClick:(0,h.useCallback)(i=>e===i?n===`asc`?(r(`desc`),`desc`):n===`desc`?(r(`none`),`none`):(r(`asc`),`asc`):(t(i),r(`asc`),`asc`),[e,n])}}})))()}var _;function v(){return(v=t((()=>{_={"sorting-icons":`_sorting-icons_cbxcb_1`,"both-icons":`_both-icons_cbxcb_17`}})))()}var y,b,ge;function _e(){return(_e=t((()=>{he(),oe(),d(),c(),v(),y=r(),b=e=>e===g.DESC?(0,y.jsx)(l,{src:le,alt:`Ne plus trier`,width:`10`}):(0,y.jsx)(l,{src:se,alt:`Trier par ordre décroissant`,width:`10`}),ge=({sortingMode:e,onClick:t,children:n})=>(0,y.jsxs)(`button`,{type:`button`,className:_[`sorting-icons`],onClick:t,children:[n,e===g.NONE?(0,y.jsxs)(`span`,{className:_[`both-icons`],children:[(0,y.jsx)(l,{src:le,alt:`Trier par ordre croissant`,width:`10`}),(0,y.jsx)(l,{src:se,alt:``,width:`10`})]}):b(e)]});try{ge.displayName=`SortColumn`,ge.__docgenInfo={description:``,displayName:`SortColumn`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,methods:[],props:{sortingMode:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`}],description:``,name:`sortingMode`,parent:{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`},required:!0,tags:{},type:{name:`enum`,raw:`SortingMode`,value:[{value:`"asc"`,description:``,fullComment:``,tags:{}},{value:`"desc"`,description:``,fullComment:``,tags:{}},{value:`"none"`,description:``,fullComment:``,tags:{}}]}},onClick:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`}],description:``,name:`onClick`,parent:{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`},required:!0,tags:{},type:{name:`() => void`}}},tags:{}}}catch{}})))()}var x,ve,S;function C(){return(C=t((()=>{x=`_wrapper_17olv_1`,ve=`_table_17olv_5`,S={wrapper:x,table:ve,"table-pagination":`_table-pagination_17olv_13`,"table-separate":`_table-separate_17olv_17`,"table-separate-cell":`_table-separate-cell_17olv_21`,"table-collapse":`_table-collapse_17olv_38`,"table-collapse-cell":`_table-collapse-cell_17olv_42`,"table-row":`_table-row_17olv_50`,"table-header":`_table-header_17olv_54`,"table-header-sticky":`_table-header-sticky_17olv_60`,"table-header-th":`_table-header-th_17olv_65`,"table-header-full-row":`_table-header-full-row_17olv_74`,"table-header-sortable-th":`_table-header-sortable-th_17olv_78`,"table-header-center-th":`_table-header-center-th_17olv_82`,"table-select-all":`_table-select-all_17olv_98`,"table-select-all-tooltip":`_table-select-all-tooltip_17olv_104`,"table-checkbox-label":`_table-checkbox-label_17olv_109`,"visually-hidden":`_visually-hidden_17olv_124`,"table-fullrow-content":`_table-fullrow-content_17olv_136`,"table-fullrow-content-raw":`_table-fullrow-content-raw_17olv_139`}})))()}var w;function ye(){return(ye=t((()=>{w={"no-data":`_no-data_19ruh_1`,"no-data-icon":`_no-data-icon_19ruh_8`,"no-data-title":`_no-data-title_19ruh_12`,"no-data-subtitle":`_no-data-subtitle_19ruh_19`,"no-data-cta":`_no-data-cta_19ruh_24`,"visually-hidden":`_visually-hidden_19ruh_28`}})))()}var T,E,be;function xe(){return(xe=t((()=>{T=e(i(),1),c(),ye(),E=r(),be=({noData:e})=>{let{icon:t,title:n,subtitle:r,cta:i}=e.message;return(0,E.jsx)(`div`,{className:(0,T.default)({[w[`no-data`]]:e.hasNoData,[w[`visually-hidden`]]:!e.hasNoData}),role:`status`,children:e.hasNoData?(0,E.jsxs)(E.Fragment,{children:[(0,E.jsx)(l,{src:t,alt:``,width:`80`,className:w[`no-data-icon`],"aria-hidden":!0}),(0,E.jsx)(`p`,{className:w[`no-data-title`],children:n}),r&&(0,E.jsx)(`p`,{className:w[`no-data-subtitle`],children:r}),(0,E.jsx)(`div`,{className:w[`no-data-cta`],children:i})]}):(0,E.jsx)(`span`,{children:`\xA0`})})};try{be.displayName=`TableNoData`,be.__docgenInfo={description:``,displayName:`TableNoData`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/TableNoData/TableNoData.tsx`,methods:[],props:{noData:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/TableNoData/TableNoData.tsx`,name:`TypeLiteral`}],description:``,name:`noData`,required:!0,tags:{},type:{name:`EmptyStateProps`}}},tags:{}}}catch{}})))()}var D;function Se(){return(Se=t((()=>{D=new URL(`stroke-search-2-DXKdS1qm.svg`,import.meta.url).href})))()}var O;function Ce(){return(Ce=t((()=>{O={"search-no-results":`_search-no-results_1p61o_1`,"search-no-results-icon":`_search-no-results-icon_1p61o_8`,"search-no-results-title":`_search-no-results-title_1p61o_11`,"search-no-results-subtitle":`_search-no-results-subtitle_1p61o_18`,"search-no-results-cta":`_search-no-results-cta_1p61o_23`,"visually-hidden":`_visually-hidden_1p61o_27`}})))()}var we,k,A;function Te(){return(Te=t((()=>{we=e(i(),1),s(),ne(),ce(),Se(),c(),Ce(),k=r(),A=({colSpan:e=1,message:t=`Pas de résultat pour votre recherche`,subtitle:n=`Vous pouvez modifier votre recherche ou`,resetMessage:r=`Réinitialiser les filtres`,resetFilters:i,hasNoResult:a=!1})=>(0,k.jsx)(`tr`,{children:(0,k.jsx)(`td`,{colSpan:e,className:(0,we.default)({[O[`search-no-results`]]:a,[O[`visually-hidden`]]:!a}),role:`status`,children:a?(0,k.jsxs)(k.Fragment,{children:[(0,k.jsx)(l,{src:D,alt:``,className:O[`search-no-results-icon`],width:`80`,"aria-hidden":!0}),(0,k.jsx)(`p`,{className:O[`search-no-results-title`],children:t}),(0,k.jsx)(`p`,{className:O[`search-no-results-subtitle`],children:n}),(0,k.jsx)(`div`,{className:O[`search-no-results-cta`],children:(0,k.jsx)(re,{variant:o.TERTIARY,color:te.NEUTRAL,icon:u,onClick:i,label:r})})]}):(0,k.jsx)(`span`,{children:`\xA0`})})});try{A.displayName=`TableNoFilterResult`,A.__docgenInfo={description:``,displayName:`TableNoFilterResult`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,methods:[],props:{colSpan:{defaultValue:{value:`1`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`colSpan`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`number`}},message:{defaultValue:{value:`Pas de résultat pour votre recherche`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`message`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`string`}},subtitle:{defaultValue:{value:`Vous pouvez modifier votre recherche ou`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`subtitle`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`string`}},resetMessage:{defaultValue:{value:`Réinitialiser les filtres`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`resetMessage`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`string`}},resetFilters:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`resetFilters`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!0,tags:{},type:{name:`() => void`}},hasNoResult:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`hasNoResult`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`boolean`}}},tags:{}}}catch{}})))()}function Ee(e,t){if(t)return typeof t==`function`?t(e):typeof t==`string`?t.split(`.`).reduce((e,t)=>e?.[t],e):e[t]}function j({title:e=`Tableau de données`,a11ySummary:t,columns:n,data:r,allData:i,selectable:a=!1,selectedNumber:o,selectedIds:s,className:te,isLoading:ne,isSticky:re,variant:c,noResult:l,noData:ie,onSelectionChange:oe,getRowSelectionDateTime:se,getFullRow:ce,isRowSelectable:u,pagination:d,children:le}){let f=i??r,{currentSortingColumn:p,currentSortingMode:m,onColumnHeaderClick:h}=me(),[he,_]=(0,N.useState)(new Set),v=s!==void 0,y=v?s:he,b=ue(de),_e=b?`presentation`:`table`,x=e=>{v||_(e),oe?.(f.filter(t=>e.has(t.id)))};function ve(e){h(e)}let C=(0,N.useMemo)(()=>u?f.filter(u):f,[f,u]),w=()=>{y.size===C.length?x(new Set):x(new Set(C.map(e=>e.id)))},ye=e=>{let t=new Set(y);t.has(e.id)?t.delete(e.id):t.add(e.id),x(t)},T=(0,N.useMemo)(()=>{if(!p)return r;let e=n.find(e=>e.id===p);return e?[...f].sort((t,n)=>{let r=Ee(t,e.ordererField),i=Ee(n,e.ordererField);if(r===i)return 0;let a=m===g.ASC;return r<i?a?-1:1:a?1:-1}):r},[r,p,m,n,f]),E=y.size===C.length&&C.length>0,xe=y.size>0&&y.size<C.length,D=E?`Tout désélectionner`:`Tout sélectionner`;return(0,P.jsxs)(P.Fragment,{children:[(0,P.jsxs)(`div`,{className:(0,M.default)(S.wrapper,te),children:[(0,P.jsxs)(`table`,{className:(0,M.default)(S.table,{[S[`table-separate`]]:c===`separate`,[S[`table-collapse`]]:c===`collapse`}),role:_e,children:[!b&&T.length>0&&(0,P.jsxs)(P.Fragment,{children:[(0,P.jsxs)(`caption`,{className:S[`visually-hidden`],children:[e,t?(0,P.jsxs)(`span`,{children:[`. `,t]}):null]}),(0,P.jsx)(`thead`,{children:(0,P.jsxs)(`tr`,{className:(0,M.default)(S[`table-header`],{[S[`table-header-sticky`]]:re}),children:[a&&(0,P.jsx)(`th`,{scope:`col`,className:S[`table-header-th`],children:(0,P.jsxs)(`div`,{className:S[`table-select-all`],children:[(0,P.jsx)(ee,{content:`Tout sélectionner`,className:S[`table-select-all-tooltip`],children:(0,P.jsx)(ae,{label:D,title:D,ariaLabel:`Sélectionner toutes les lignes`,checked:E,indeterminate:xe,onChange:w,className:S[`table-checkbox-label`]})}),(0,P.jsx)(`div`,{children:o})]})}),n.map(e=>{if(e.headerHidden)return null;let t=e.header??e.label??``,n=m===g.ASC?`ascending`:`descending`;return(0,P.jsx)(`th`,{"aria-sort":p===e.id&&m!==g.NONE?n:void 0,scope:`col`,id:e.id,colSpan:e.headerColSpan||1,className:(0,M.default)(S[`table-header-th`],{[S[`table-header-sortable-th`]]:e.sortable,[S[`table-header-center-th`]]:e.centerHeader,[S[`table-header-full-row`]]:e.headerForFullRowOnly}),children:e.sortable?(0,P.jsx)(ge,{onClick:()=>ve(e.id),sortingMode:p===e.id?m:g.NONE,children:t}):t},`col-${e.id}`)})]})})]}),(0,P.jsxs)(`tbody`,{children:[ne&&Array.from({length:8}).map((e,t)=>(0,P.jsx)(`tr`,{children:(0,P.jsx)(`td`,{colSpan:n.length+1,children:(0,P.jsx)(pe,{height:`7rem`,width:`100%`})})},`loading-row-${n.length}-${t}`)),(0,P.jsx)(A,{colSpan:n.length+ +!!a,message:l.message,subtitle:l.subtitle,resetMessage:l.resetMessage,resetFilters:l.onFilterReset,hasNoResult:!ie.hasNoData&&!T.length}),T.map(e=>{let t=y.has(e.id),r=ce?.(e),i=se?.(e),ee=i!==void 0,o=ee?`Sélectionner la ligne du ${i}`:`Sélectionner la ligne ${e.name||e.id}`,s=ee?o:e.name??`ligne ${e.id}`;return(0,P.jsxs)(N.Fragment,{children:[(0,P.jsxs)(`tr`,{"data-testid":`table-row`,className:(0,M.default)({[S[`table-row`]]:!r?.content}),children:[a&&(0,P.jsx)(`td`,{className:(0,M.default)({[S[`table-separate-cell`]]:c===`separate`,[S[`table-collapse-cell`]]:c===`collapse`}),children:(0,P.jsx)(ae,{label:s,title:o,ariaLabel:o,checked:t,onChange:()=>ye(e),className:S[`table-checkbox-label`],disabled:u?!u(e):!1})}),n.map(t=>{if(t.bodyHidden||t.headerForFullRowOnly)return null;let n=t.render?t.render(e):Ee(e,t.ordererField);return(0,P.jsx)(`td`,{className:(0,M.default)({[S[`table-separate-cell`]]:c===`separate`,[S[`table-collapse-cell`]]:c===`collapse`}),"data-label":t.label,headers:b?void 0:t.id,children:n},`col-${t.id}-${t.label}`)})]}),r?.content&&(0,P.jsx)(`tr`,{className:(0,M.default)(S[`table-row`]),children:(0,P.jsx)(`td`,{colSpan:n.length+ +!!a,headers:b?void 0:r.headerId,children:(0,P.jsx)(`div`,{className:(0,M.default)(S[`table-fullrow-content`],{[S[`table-fullrow-content-raw`]]:r?.rawDisplay}),children:r?.content})})})]},e.id)})]})]}),le,d&&(0,P.jsx)(`div`,{className:S[`table-pagination`],children:(0,P.jsx)(fe,{currentPage:d.currentPage,pageCount:d.pageCount,onPageClick:d.onPageClick})})]}),(0,P.jsx)(be,{noData:ie})]})}var M,N,P,F;function De(){return(De=t((()=>{M=e(i(),1),f(),N=e(n(),1),he(),ie(),p(),m(),a(),_e(),C(),xe(),Te(),P=r(),F=function(e){return e.COLLAPSE=`collapse`,e.SEPARATE=`separate`,e}({});try{j.displayName=`Table`,j.__docgenInfo={description:``,displayName:`Table`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/Table.tsx`,methods:[],props:{title:{defaultValue:{value:`Tableau de données`},declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`title`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},a11ySummary:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:`Résumé de la structure d’un tableau, lu par les lecteurs d’écran`,name:`a11ySummary`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},columns:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`columns`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`Column<T>[]`}},data:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`data`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`T[]`}},allData:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`allData`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`T[]`}},selectable:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`selectable`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`boolean`}},className:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`className`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},isLoading:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`isLoading`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`boolean`}},isSticky:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`isSticky`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`boolean`}},variant:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`variant`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`enum`,raw:`TableVariant`,value:[{value:`"collapse"`,description:``,fullComment:``,tags:{}},{value:`"separate"`,description:``,fullComment:``,tags:{}}]}},selectedNumber:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`selectedNumber`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},selectedIds:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`selectedIds`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`Set<string | number>`}},onSelectionChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`onSelectionChange`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((rows: T[]) => void)`}},getRowSelectionDateTime:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`getRowSelectionDateTime`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((row: T) => string)`}},getFullRow:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`getFullRow`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((row: T) => FullRow | null)`}},isRowSelectable:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`isRowSelectable`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((row: T) => boolean)`}},noResult:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`noResult`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`NoResultProps`}},noData:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`noData`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`EmptyStateProps`}},pagination:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`pagination`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`PaginationProps`}}},tags:{}}}catch{}})))()}var Oe,I,L,ke,R,Ae,je,Me,z,B,V,H,U,W,G,K,q,J,Y,X,Z,Q,$,Ne;function Pe(){return(Pe=t((()=>{Oe=n(),De(),I=r(),L=[{id:1,name:`Alice`,email:`alice@example.com`,age:27,status:`active`,createdAt:`2024-01-05T10:00:00Z`,nested:{score:77}},{id:2,name:`Bob`,email:`bob@example.com`,age:34,status:`inactive`,createdAt:`2024-02-01T08:30:00Z`,nested:{score:65}},{id:3,name:`Chloe`,email:`chloe@example.com`,age:22,status:`active`,createdAt:`2024-03-12T12:45:00Z`,nested:{score:92}},{id:4,name:`Diego`,email:`diego@example.com`,age:41,status:`active`,createdAt:`2024-04-20T15:10:00Z`,nested:{score:58}},{id:5,name:`Elise`,email:`elise@example.com`,age:29,status:`inactive`,createdAt:`2024-05-11T09:00:00Z`,nested:{score:80}},{id:6,name:`Fares`,email:`fares@example.com`,age:37,status:`active`,createdAt:`2024-06-02T11:15:00Z`,nested:{score:71}},{id:7,name:`Gina`,email:`gina@example.com`,age:31,status:`active`,createdAt:`2024-06-18T16:20:00Z`,nested:{score:88}},{id:8,name:`Hugo`,email:`hugo@example.com`,age:25,status:`inactive`,createdAt:`2024-07-08T07:05:00Z`,nested:{score:54}}],ke=e=>new Date(e).toLocaleDateString(`fr-FR`,{year:`numeric`,month:`short`,day:`2-digit`}),R=[{id:`name`,label:`Nom`,sortable:!0,ordererField:e=>e.name,render:e=>(0,I.jsx)(`strong`,{children:e.name})},{id:`age`,label:`Âge`,sortable:!0,ordererField:e=>e.age,render:e=>e.age},{id:`created`,label:`Créé le`,sortable:!0,ordererField:e=>new Date(e.createdAt).getTime(),render:e=>ke(e.createdAt)},{id:`status`,label:`Statut`,render:e=>(0,I.jsx)(`span`,{"aria-label":`status-${e.id}`,children:e.status===`active`?`Actif`:`Inactif`})},{id:`score`,label:`Score`,sortable:!0,ordererField:e=>e.nested.score,render:e=>e.nested.score}],Ae={hasNoData:!1,message:{icon:`📄`,title:`Aucune donnée`,subtitle:`Commencez par créer un élément pour remplir ce tableau.`}},je={message:`Aucun résultat pour ces filtres.`,resetMessage:`Réinitialiser les filtres`,onFilterReset:()=>alert(`reset filters`)},Me={title:`Design System/Table`,component:j,args:{title:`Tableau de données`,a11ySummary:`Chaque ligne correspond à une personne. Les colonnes présentent son nom, son âge, sa date de création, son statut et son score.`,columns:R,data:L,selectable:!1,isLoading:!1,isSticky:!1,variant:F.COLLAPSE,noData:Ae,noResult:je},argTypes:{variant:{control:`inline-radio`,options:[F.SEPARATE,F.COLLAPSE]},isLoading:{control:`boolean`},selectable:{control:`boolean`},isSticky:{control:`boolean`}},parameters:{layout:`padded`}},z={render:e=>(0,I.jsx)(j,{...e})},B={args:{variant:F.SEPARATE}},V={args:{isLoading:!0}},H={args:{data:[],noData:{...Ae,hasNoData:!1},noResult:{...je,onFilterReset:()=>alert(`Réinitialiser les filtres`)}}},U={args:{data:[],noData:{hasNoData:!0,message:{icon:`📭`,title:`Rien à afficher`,subtitle:`Aucun élément n’a encore été créé.`}}}},W={args:{selectable:!0,selectedNumber:`0 sélectionnée`}},G={render:e=>{let[t,n]=(0,Oe.useState)(new Set([2,4])),r=t.size;return(0,I.jsx)(j,{...e,selectable:!0,selectedIds:t,selectedNumber:`${r} sélectionnée${r>1?`s`:``}`,onSelectionChange:e=>{n(new Set(e.map(e=>e.id)))}})}},K={render:e=>(0,I.jsx)(j,{...e,selectable:!0,isRowSelectable:e=>e.status===`active`,selectedNumber:`—`})},q={args:{isSticky:!0},render:e=>(0,I.jsx)(`div`,{style:{height:260,overflow:`auto`,border:`1px solid #eee`},children:(0,I.jsx)(j,{...e,data:[...L,...L]})})},J={args:{a11ySummary:`Chaque ligne correspond à une personne. Les colonnes présentent son nom, son âge, son statut et son score.`,columns:[{...R[0],headerHidden:!0},R[1],{...R[2],bodyHidden:!0},R[3],R[4]]}},Y={args:{a11ySummary:`Chaque ligne correspond à une personne. Les colonnes présentent son nom, son âge, sa date de création et son statut. L’en-tête du nom s’étend sur deux colonnes.`,columns:[{...R[0],headerColSpan:2},R[1],R[2],R[3]]}},X={render:e=>{let t=R;return(0,I.jsx)(j,{...e,a11ySummary:`Chaque ligne correspond à une personne et présente son nom, son âge, sa date de création, son statut et son score. Une ligne complémentaire affiche le nom des personnes de plus de 30 ans.`,variant:F.COLLAPSE,columns:t,getFullRow:e=>e.age>30?{content:(0,I.jsx)(`div`,{style:{padding:`8px`,margin:`8px`,backgroundColor:`violet`,borderRadius:`4px`},children:e.name},e.id),headerId:`score`}:null})}},Z={render:e=>{let[t,n]=(0,Oe.useState)(3),r=[...R.slice(0,4),{id:`actions`,label:`Actions`,render:e=>(0,I.jsx)(`button`,{onClick:t=>{t.stopPropagation(),n(t=>t===e.id?null:e.id)},children:t===e.id?`Fermer`:`Voir détails`})}];return(0,I.jsx)(j,{...e,a11ySummary:`Chaque ligne correspond à une personne et présente son nom, son âge, sa date de création et son statut. Le bouton « Voir détails » affiche son adresse électronique, son score et son statut sous la ligne.`,columns:r,getFullRow:e=>e.id===t?{content:(0,I.jsxs)(`div`,{style:{padding:16},children:[(0,I.jsx)(`h4`,{style:{margin:0},children:e.name}),(0,I.jsxs)(`p`,{style:{margin:`8px 0`},children:[`Email: `,(0,I.jsx)(`strong`,{children:e.email})]}),(0,I.jsxs)(`p`,{style:{margin:0},children:[`Score: `,(0,I.jsx)(`strong`,{children:e.nested.score}),` — Statut:`,` `,(0,I.jsx)(`strong`,{children:e.status})]})]}),headerId:`name`}:null})}},Q={args:{},render:e=>(0,I.jsx)(j,{...e,data:[...L]})},$={args:{pagination:{currentPage:1,pageCount:3,onPageClick:e=>{alert(`Go to page ${e}`)}}},render:e=>(0,I.jsx)(j,{...e,data:[...L]})},Ne=[`Basic`,`SeparateVariant`,`Loading`,`NoResults`,`NoDataState`,`SelectableUncontrolled`,`SelectableControlled`,`SelectableWithDisabledRows`,`StickyHeaderInScrollContainer`,`WithHiddenColumns`,`WithHeaderColSpan`,`WithFullRowAlwaysDisplayedDetail`,`WithFullRowDetail`,`SortingShowcase`,`WithPagination`],z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
  render: args => <Table {...args} />
}`,...z.parameters?.docs?.source}}},B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  args: {
    variant: TableVariant.SEPARATE
  }
}`,...B.parameters?.docs?.source}}},V.parameters={...V.parameters,docs:{...V.parameters?.docs,source:{originalSource:`{
  args: {
    isLoading: true
  }
}`,...V.parameters?.docs?.source}}},H.parameters={...H.parameters,docs:{...H.parameters?.docs,source:{originalSource:`{
  args: {
    data: [],
    noData: {
      ...noData,
      hasNoData: false
    },
    noResult: {
      ...noResult,
      onFilterReset: () => alert('Réinitialiser les filtres')
    }
  }
}`,...H.parameters?.docs?.source}}},U.parameters={...U.parameters,docs:{...U.parameters?.docs,source:{originalSource:`{
  args: {
    data: [],
    noData: {
      hasNoData: true,
      message: {
        icon: '📭',
        title: 'Rien à afficher',
        subtitle: 'Aucun élément n’a encore été créé.'
      }
    }
  }
}`,...U.parameters?.docs?.source}}},W.parameters={...W.parameters,docs:{...W.parameters?.docs,source:{originalSource:`{
  args: {
    selectable: true,
    selectedNumber: '0 sélectionnée'
  }
}`,...W.parameters?.docs?.source}}},G.parameters={...G.parameters,docs:{...G.parameters?.docs,source:{originalSource:`{
  render: args => {
    const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set([2, 4]));
    const selectedCount = selectedIds.size;
    return <Table {...args} selectable selectedIds={selectedIds} selectedNumber={\`\${selectedCount} sélectionnée\${selectedCount > 1 ? 's' : ''}\`} onSelectionChange={rows => {
      setSelectedIds(new Set(rows.map(r => r.id)));
    }} />;
  }
}`,...G.parameters?.docs?.source}}},K.parameters={...K.parameters,docs:{...K.parameters?.docs,source:{originalSource:`{
  render: args => <Table {...args} selectable isRowSelectable={row => row.status === 'active'} // disable inactive rows
  selectedNumber="—" />
}`,...K.parameters?.docs?.source}}},q.parameters={...q.parameters,docs:{...q.parameters?.docs,source:{originalSource:`{
  args: {
    isSticky: true
  },
  render: args => <div style={{
    height: 260,
    overflow: 'auto',
    border: '1px solid #eee'
  }}>
      <Table {...args} data={[...sampleData, ...sampleData]} />
    </div>
}`,...q.parameters?.docs?.source}}},J.parameters={...J.parameters,docs:{...J.parameters?.docs,source:{originalSource:`{
  args: {
    a11ySummary: 'Chaque ligne correspond à une personne. Les colonnes présentent son nom, son âge, son statut et son score.',
    columns: [{
      ...baseColumns[0],
      headerHidden: true
    },
    // hide header label for "Nom"
    baseColumns[1], {
      ...baseColumns[2],
      bodyHidden: true
    },
    // hide body cells for "Créé le"
    baseColumns[3], baseColumns[4]]
  }
}`,...J.parameters?.docs?.source}}},Y.parameters={...Y.parameters,docs:{...Y.parameters?.docs,source:{originalSource:`{
  args: {
    a11ySummary: 'Chaque ligne correspond à une personne. Les colonnes présentent son nom, son âge, sa date de création et son statut. L’en-tête du nom s’étend sur deux colonnes.',
    columns: [{
      ...baseColumns[0],
      headerColSpan: 2
    },
    // spans two header columns
    baseColumns[1], baseColumns[2], baseColumns[3]]
  }
}`,...Y.parameters?.docs?.source}}},X.parameters={...X.parameters,docs:{...X.parameters?.docs,source:{originalSource:`{
  render: args => {
    const columns: Column<Row>[] = baseColumns;
    return <Table {...args} a11ySummary="Chaque ligne correspond à une personne et présente son nom, son âge, sa date de création, son statut et son score. Une ligne complémentaire affiche le nom des personnes de plus de 30 ans." variant={TableVariant.COLLAPSE} columns={columns} getFullRow={row => {
      if (row.age > 30) {
        return {
          content: <div key={row.id} style={{
            padding: '8px',
            margin: '8px',
            backgroundColor: 'violet',
            borderRadius: '4px'
          }}>
                {row.name}
              </div>,
          headerId: 'score'
        };
      }
      return null;
    }} />;
  }
}`,...X.parameters?.docs?.source},description:{story:`Full-row (colspan) detail row
Your Table renders a second <tr> with a single <td colSpan=...>
whenever getFullRowContent(row) returns a ReactNode.`,...X.parameters?.docs?.description}}},Z.parameters={...Z.parameters,docs:{...Z.parameters?.docs,source:{originalSource:`{
  render: args => {
    const [expandedId, setExpandedId] = useState<number | null>(3);
    const columns: Column<Row>[] = [...baseColumns.slice(0, 4), {
      id: 'actions',
      label: 'Actions',
      render: r => <button onClick={e => {
        e.stopPropagation();
        setExpandedId(prev => prev === r.id ? null : r.id);
      }}>
            {expandedId === r.id ? 'Fermer' : 'Voir détails'}
          </button>
    }];
    return <Table {...args} a11ySummary="Chaque ligne correspond à une personne et présente son nom, son âge, sa date de création et son statut. Le bouton « Voir détails » affiche son adresse électronique, son score et son statut sous la ligne." columns={columns} getFullRow={row => row.id === expandedId ? {
      content: <div style={{
        padding: 16
      }}>
              <h4 style={{
          margin: 0
        }}>{row.name}</h4>
              <p style={{
          margin: '8px 0'
        }}>
                Email: <strong>{row.email}</strong>
              </p>
              <p style={{
          margin: 0
        }}>
                Score: <strong>{row.nested.score}</strong> — Statut:{' '}
                <strong>{row.status}</strong>
              </p>
            </div>,
      headerId: 'name'
    } : null} />;
  }
}`,...Z.parameters?.docs?.source},description:{story:`Full-row (colspan) detail row
Your Table renders a second <tr> with a single <td colSpan=...>
whenever getFullRowContent(row) returns a ReactNode.`,...Z.parameters?.docs?.description}}},Q.parameters={...Q.parameters,docs:{...Q.parameters?.docs,source:{originalSource:`{
  args: {
    // keep default columns (sortable on name, age, created, score)
  },
  render: args => <Table {...args} data={[...sampleData]} />
}`,...Q.parameters?.docs?.source}}},$.parameters={...$.parameters,docs:{...$.parameters?.docs,source:{originalSource:`{
  args: {
    pagination: {
      currentPage: 1,
      pageCount: 3,
      onPageClick: (page: number) => {
        alert(\`Go to page \${page}\`);
      }
    }
  },
  render: args => <Table {...args} data={[...sampleData]} />
}`,...$.parameters?.docs?.source}}}})))()}Pe();export{z as Basic,V as Loading,U as NoDataState,H as NoResults,G as SelectableControlled,W as SelectableUncontrolled,K as SelectableWithDisabledRows,B as SeparateVariant,Q as SortingShowcase,q as StickyHeaderInScrollContainer,X as WithFullRowAlwaysDisplayedDetail,Z as WithFullRowDetail,Y as WithHeaderColSpan,J as WithHiddenColumns,$ as WithPagination,Ne as __namedExportsOrder,Me as default};