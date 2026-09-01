import{a as e,n as t}from"./rolldown-runtime-DkW27tQK.js";import{d as n}from"./iframe-CXhpPddl.js";import{t as r}from"./jsx-runtime-DeHZSEgm.js";import{t as i}from"./classnames-D09xBJOL.js";import{n as a,t as ee}from"./Tooltip-DZgQXL3J.js";import{a as o,n as te,r as ne,s as re,t as s}from"./Button-D51yOdDO.js";import{n as c,t as l}from"./SvgIcon-DRPrlrFF.js";import{n as ie,t as ae}from"./full-down-CDfkw0UZ.js";import{n as oe,t as u}from"./full-refresh-D9Cy7hhS.js";import{n as d,t as se}from"./full-up-DOlcUefR.js";import{n as f,t as ce}from"./Checkbox-B4loOoaa.js";import{n as p,r as le,t as ue}from"./useMediaQuery-DhQwdNJv.js";import{n as m,t as de}from"./Pagination-CXhAR5kF.js";import{n as fe,t as pe}from"./Skeleton-yw7vvga_.js";var h,g,me;function _(){return(_=t((()=>{h=n(),g=function(e){return e.ASC=`asc`,e.DESC=`desc`,e.NONE=`none`,e}({}),me=()=>{let[e,t]=(0,h.useState)(null),[n,r]=(0,h.useState)(`none`);return{currentSortingColumn:e,currentSortingMode:n,onColumnHeaderClick:(0,h.useCallback)(i=>e===i?n===`asc`?(r(`desc`),`desc`):n===`desc`?(r(`none`),`none`):(r(`asc`),`asc`):(t(i),r(`asc`),`asc`),[e,n])}}})))()}var v;function y(){return(y=t((()=>{v={"sorting-icons":`_sorting-icons_cbxcb_1`,"both-icons":`_both-icons_cbxcb_17`}})))()}var b,he,x;function S(){return(S=t((()=>{_(),ie(),d(),c(),y(),b=r(),he=e=>e===g.DESC?(0,b.jsx)(l,{src:se,alt:`Ne plus trier`,width:`10`}):(0,b.jsx)(l,{src:ae,alt:`Trier par ordre décroissant`,width:`10`}),x=({sortingMode:e,onClick:t,children:n})=>(0,b.jsxs)(`button`,{type:`button`,className:v[`sorting-icons`],onClick:t,children:[n,e===g.NONE?(0,b.jsxs)(`span`,{className:v[`both-icons`],children:[(0,b.jsx)(l,{src:se,alt:`Trier par ordre croissant`,width:`10`}),(0,b.jsx)(l,{src:ae,alt:``,width:`10`})]}):he(e)]});try{x.displayName=`SortColumn`,x.__docgenInfo={description:``,displayName:`SortColumn`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,methods:[],props:{sortingMode:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`}],description:``,name:`sortingMode`,parent:{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`},required:!0,tags:{},type:{name:`enum`,raw:`SortingMode`,value:[{value:`"asc"`,description:``,fullComment:``,tags:{}},{value:`"desc"`,description:``,fullComment:``,tags:{}},{value:`"none"`,description:``,fullComment:``,tags:{}}]}},onClick:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`}],description:``,name:`onClick`,parent:{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`},required:!0,tags:{},type:{name:`() => void`}}},tags:{}}}catch{}})))()}var ge,C,w;function _e(){return(_e=t((()=>{ge=`_wrapper_4w4z5_1`,C=`_table_4w4z5_5`,w={wrapper:ge,table:C,"table-pagination":`_table-pagination_4w4z5_13`,"table-separate":`_table-separate_4w4z5_17`,"table-separate-cell":`_table-separate-cell_4w4z5_21`,"table-collapse":`_table-collapse_4w4z5_38`,"table-collapse-cell":`_table-collapse-cell_4w4z5_45`,"table-row":`_table-row_4w4z5_50`,"table-header":`_table-header_4w4z5_54`,"table-header-sticky":`_table-header-sticky_4w4z5_60`,"table-header-th":`_table-header-th_4w4z5_65`,"table-header-full-row":`_table-header-full-row_4w4z5_73`,"table-header-sortable-th":`_table-header-sortable-th_4w4z5_77`,"table-header-center-th":`_table-header-center-th_4w4z5_81`,"table-select-all":`_table-select-all_4w4z5_97`,"table-select-all-tooltip":`_table-select-all-tooltip_4w4z5_103`,"table-checkbox-label":`_table-checkbox-label_4w4z5_108`,"visually-hidden":`_visually-hidden_4w4z5_123`,"table-caption-no-display":`_table-caption-no-display_4w4z5_135`,"table-fullrow-content":`_table-fullrow-content_4w4z5_139`}})))()}var T;function E(){return(E=t((()=>{T={"no-data":`_no-data_kbtpu_1`,"no-data-icon":`_no-data-icon_kbtpu_8`,"no-data-title":`_no-data-title_kbtpu_12`,"no-data-subtitle":`_no-data-subtitle_kbtpu_19`,"no-data-cta":`_no-data-cta_kbtpu_24`}})))()}var D,O;function ve(){return(ve=t((()=>{c(),E(),D=r(),O=({noData:{icon:e,title:t,subtitle:n,cta:r}})=>(0,D.jsxs)(`div`,{className:T[`no-data`],children:[(0,D.jsx)(l,{src:e,alt:``,width:`80`,className:T[`no-data-icon`]}),(0,D.jsx)(`p`,{className:T[`no-data-title`],children:t}),n&&(0,D.jsx)(`p`,{className:T[`no-data-subtitle`],children:n}),(0,D.jsx)(`div`,{className:T[`no-data-cta`],children:r})]});try{O.displayName=`TableNoData`,O.__docgenInfo={description:``,displayName:`TableNoData`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/TableNoData/TableNoData.tsx`,methods:[],props:{noData:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/TableNoData/TableNoData.tsx`,name:`TableNoDataProps`}],description:``,name:`noData`,parent:{fileName:`pro/src/ui-kit/Table/TableNoData/TableNoData.tsx`,name:`TableNoDataProps`},required:!0,tags:{},type:{name:`{ icon: string; title: string; subtitle?: string | undefined; cta?: ReactNode; }`}}},tags:{}}}catch{}})))()}var ye;function be(){return(be=t((()=>{ye=``+new URL(`stroke-search-2-DXKdS1qm.svg`,import.meta.url).href})))()}var k;function xe(){return(xe=t((()=>{k={"search-no-results":`_search-no-results_1d56s_1`,"search-no-results-icon":`_search-no-results-icon_1d56s_8`,"search-no-results-title":`_search-no-results-title_1d56s_11`,"search-no-results-subtitle":`_search-no-results-subtitle_1d56s_18`,"search-no-results-cta":`_search-no-results-cta_1d56s_23`}})))()}var A,Se;function Ce(){return(Ce=t((()=>{te(),re(),oe(),be(),c(),xe(),A=r(),Se=({colSpan:e=1,message:t=`Pas de résultat pour votre recherche`,subtitle:n=`Vous pouvez modifier votre recherche ou`,resetMessage:r=`Réinitialiser les filtres`,resetFilters:i})=>(0,A.jsx)(`tr`,{children:(0,A.jsx)(`td`,{colSpan:e,children:(0,A.jsxs)(`div`,{className:k[`search-no-results`],children:[(0,A.jsx)(l,{src:ye,alt:`Illustration de recherche`,className:k[`search-no-results-icon`],width:`80`}),(0,A.jsx)(`p`,{className:k[`search-no-results-title`],children:t}),(0,A.jsx)(`p`,{className:k[`search-no-results-subtitle`],children:n}),(0,A.jsx)(`div`,{className:k[`search-no-results-cta`],children:(0,A.jsx)(s,{variant:o.TERTIARY,color:ne.NEUTRAL,icon:u,onClick:i,label:r})})]})})});try{Se.displayName=`TableNoFilterResult`,Se.__docgenInfo={description:``,displayName:`TableNoFilterResult`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,methods:[],props:{colSpan:{defaultValue:{value:`1`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`colSpan`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`number`}},message:{defaultValue:{value:`Pas de résultat pour votre recherche`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`message`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`string`}},subtitle:{defaultValue:{value:`Vous pouvez modifier votre recherche ou`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`subtitle`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`string`}},resetMessage:{defaultValue:{value:`Réinitialiser les filtres`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`resetMessage`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`string`}},resetFilters:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`resetFilters`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!0,tags:{},type:{name:`() => void`}}},tags:{}}}catch{}})))()}function we(e,t){if(t)return typeof t==`function`?t(e):typeof t==`string`?t.split(`.`).reduce((e,t)=>e?.[t],e):e[t]}function j({title:e=`Tableau de données`,columns:t,data:n,allData:r,selectable:i=!1,selectedNumber:a,selectedIds:o,className:te,isLoading:ne,isSticky:re,variant:s,noResult:c,noData:l,onSelectionChange:ie,getRowSelectionDateTime:ae,getFullRow:oe,isRowSelectable:u,pagination:d,children:se}){let f=r??n,{currentSortingColumn:p,currentSortingMode:m,onColumnHeaderClick:fe}=me(),[h,_]=(0,N.useState)(new Set),v=o!==void 0,y=v?o:h,b=le(ue),he=b?`presentation`:`table`,S=e=>{v||_(e),ie?.(f.filter(t=>e.has(t.id)))};function ge(e){fe(e)}let C=(0,N.useMemo)(()=>u?f.filter(u):f,[f,u]),_e=()=>{y.size===C.length?S(new Set):S(new Set(C.map(e=>e.id)))},T=e=>{let t=new Set(y);t.has(e.id)?t.delete(e.id):t.add(e.id),S(t)},E=(0,N.useMemo)(()=>{if(!p)return n;let e=t.find(e=>e.id===p);return e?[...f].sort((t,n)=>{let r=we(t,e.ordererField),i=we(n,e.ordererField);if(r===i)return 0;let a=m===g.ASC;return r<i?a?-1:1:a?1:-1}):n},[n,p,m,t,f]),D=y.size===C.length&&C.length>0,ve=y.size>0&&y.size<C.length,ye=D?`Tout désélectionner`:`Tout sélectionner`;return l.hasNoData?(0,P.jsx)(O,{noData:l.message}):(0,P.jsxs)(`div`,{className:(0,M.default)(w.wrapper,te),children:[(0,P.jsxs)(`table`,{className:(0,M.default)(w.table,{[w[`table-separate`]]:s===`separate`,[w[`table-collapse`]]:s===`collapse`}),role:he,children:[!b&&E.length>0&&(0,P.jsxs)(P.Fragment,{children:[(0,P.jsx)(`caption`,{className:w[`table-caption-no-display`],children:e}),(0,P.jsx)(`thead`,{children:(0,P.jsxs)(`tr`,{className:(0,M.default)(w[`table-header`],{[w[`table-header-sticky`]]:re}),children:[i&&(0,P.jsx)(`th`,{scope:`col`,className:w[`table-header-th`],children:(0,P.jsxs)(`div`,{className:w[`table-select-all`],children:[(0,P.jsx)(ee,{content:`Tout sélectionner`,className:w[`table-select-all-tooltip`],children:(0,P.jsx)(ce,{label:ye,title:ye,ariaLabel:`Sélectionner toutes les lignes`,checked:D,indeterminate:ve,onChange:_e,className:w[`table-checkbox-label`]})}),(0,P.jsx)(`span`,{className:w[`visually-hidden`],children:`Sélectionner toutes les lignes`}),(0,P.jsx)(`div`,{children:a})]})}),t.map(e=>{if(e.headerHidden)return null;let t=e.header??e.label??``;return(0,P.jsx)(`th`,{scope:`col`,id:e.id,colSpan:e.headerColSpan||1,className:(0,M.default)(w[`table-header-th`],{[w[`table-header-sortable-th`]]:e.sortable,[w[`table-header-center-th`]]:e.centerHeader,[w[`table-header-full-row`]]:e.headerForFullRowOnly}),children:e.sortable?(0,P.jsx)(x,{onClick:()=>ge(e.id),sortingMode:p===e.id?m:g.NONE,children:t}):t},`col-${e.id}`)})]})})]}),(0,P.jsxs)(`tbody`,{children:[ne&&Array.from({length:8}).map((e,n)=>(0,P.jsx)(`tr`,{children:(0,P.jsx)(`td`,{colSpan:t.length+1,children:(0,P.jsx)(pe,{height:`7rem`,width:`100%`})})},`loading-row-${t.length}-${n}`)),!E.length&&(0,P.jsx)(Se,{colSpan:t.length+ +!!i,message:c.message,subtitle:c.subtitle,resetMessage:c.resetMessage,resetFilters:c.onFilterReset}),E.map(e=>{let n=y.has(e.id),r=oe?.(e),a=ae?.(e),ee=a!==void 0,o=ee?`Sélectionner la ligne du ${a}`:`Sélectionner la ligne ${e.name||e.id}`,te=ee?o:e.name??`ligne ${e.id}`;return(0,P.jsxs)(N.Fragment,{children:[(0,P.jsxs)(`tr`,{"data-testid":`table-row`,className:(0,M.default)({[w[`table-row`]]:!r?.content}),children:[i&&(0,P.jsxs)(`td`,{className:(0,M.default)({[w[`table-separate-cell`]]:s===`separate`,[w[`table-collapse-cell`]]:s===`collapse`}),children:[(0,P.jsx)(ce,{label:te,title:o,checked:n,onChange:()=>T(e),className:w[`table-checkbox-label`],disabled:u?!u(e):!1}),(0,P.jsx)(`span`,{className:w[`visually-hidden`],children:o})]}),t.map(t=>{if(t.bodyHidden||t.headerForFullRowOnly)return null;let n=t.render?t.render(e):we(e,t.ordererField);return(0,P.jsx)(`td`,{className:(0,M.default)({[w[`table-separate-cell`]]:s===`separate`,[w[`table-collapse-cell`]]:s===`collapse`}),"data-label":t.label,headers:b?void 0:t.id,children:n},`col-${t.id}-${t.label}`)})]}),r?.content&&(0,P.jsx)(`tr`,{className:(0,M.default)(w[`table-row`]),children:(0,P.jsx)(`td`,{colSpan:t.length+ +!!i,headers:b?void 0:r.headerId,children:(0,P.jsx)(`div`,{className:w[`table-fullrow-content`],children:r?.content})})})]},e.id)})]})]}),se,d&&(0,P.jsx)(`div`,{className:w[`table-pagination`],children:(0,P.jsx)(de,{currentPage:d.currentPage,pageCount:d.pageCount,onPageClick:d.onPageClick})})]})}var M,N,P,F;function Te(){return(Te=t((()=>{M=e(i(),1),p(),N=e(n(),1),_(),f(),m(),fe(),a(),S(),_e(),ve(),Ce(),P=r(),F=function(e){return e.COLLAPSE=`collapse`,e.SEPARATE=`separate`,e}({});try{j.displayName=`Table`,j.__docgenInfo={description:``,displayName:`Table`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/Table.tsx`,methods:[],props:{title:{defaultValue:{value:`Tableau de données`},declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`title`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},columns:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`columns`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`Column<T>[]`}},data:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`data`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`T[]`}},allData:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`allData`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`T[]`}},selectable:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`selectable`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`boolean`}},className:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`className`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},isLoading:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`isLoading`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`boolean`}},isSticky:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`isSticky`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`boolean`}},variant:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`variant`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`enum`,raw:`TableVariant`,value:[{value:`"collapse"`,description:``,fullComment:``,tags:{}},{value:`"separate"`,description:``,fullComment:``,tags:{}}]}},selectedNumber:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`selectedNumber`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},selectedIds:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`selectedIds`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`Set<string | number>`}},onSelectionChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`onSelectionChange`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((rows: T[]) => void)`}},getRowSelectionDateTime:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`getRowSelectionDateTime`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((row: T) => string)`}},getFullRow:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`getFullRow`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((row: T) => FullRow | null)`}},isRowSelectable:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`isRowSelectable`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((row: T) => boolean)`}},noResult:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`noResult`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`NoResultProps`}},noData:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`noData`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`EmptyStateProps`}},pagination:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`pagination`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`PaginationProps`}}},tags:{}}}catch{}})))()}var Ee,I,L,De,R,Oe,ke,Ae,z,B,V,H,U,W,G,K,q,J,Y,X,Z,Q,$,je;function Me(){return(Me=t((()=>{Ee=n(),Te(),I=r(),L=[{id:1,name:`Alice`,email:`alice@example.com`,age:27,status:`active`,createdAt:`2024-01-05T10:00:00Z`,nested:{score:77}},{id:2,name:`Bob`,email:`bob@example.com`,age:34,status:`inactive`,createdAt:`2024-02-01T08:30:00Z`,nested:{score:65}},{id:3,name:`Chloe`,email:`chloe@example.com`,age:22,status:`active`,createdAt:`2024-03-12T12:45:00Z`,nested:{score:92}},{id:4,name:`Diego`,email:`diego@example.com`,age:41,status:`active`,createdAt:`2024-04-20T15:10:00Z`,nested:{score:58}},{id:5,name:`Elise`,email:`elise@example.com`,age:29,status:`inactive`,createdAt:`2024-05-11T09:00:00Z`,nested:{score:80}},{id:6,name:`Fares`,email:`fares@example.com`,age:37,status:`active`,createdAt:`2024-06-02T11:15:00Z`,nested:{score:71}},{id:7,name:`Gina`,email:`gina@example.com`,age:31,status:`active`,createdAt:`2024-06-18T16:20:00Z`,nested:{score:88}},{id:8,name:`Hugo`,email:`hugo@example.com`,age:25,status:`inactive`,createdAt:`2024-07-08T07:05:00Z`,nested:{score:54}}],De=e=>new Date(e).toLocaleDateString(`fr-FR`,{year:`numeric`,month:`short`,day:`2-digit`}),R=[{id:`name`,label:`Nom`,sortable:!0,ordererField:e=>e.name,render:e=>(0,I.jsx)(`strong`,{children:e.name})},{id:`age`,label:`Âge`,sortable:!0,ordererField:e=>e.age,render:e=>e.age},{id:`created`,label:`Créé le`,sortable:!0,ordererField:e=>new Date(e.createdAt).getTime(),render:e=>De(e.createdAt)},{id:`status`,label:`Statut`,render:e=>(0,I.jsx)(`span`,{"aria-label":`status-${e.id}`,children:e.status===`active`?`Actif`:`Inactif`})},{id:`score`,label:`Score`,sortable:!0,ordererField:e=>e.nested.score,render:e=>e.nested.score}],Oe={hasNoData:!1,message:{icon:`📄`,title:`Aucune donnée`,subtitle:`Commencez par créer un élément pour remplir ce tableau.`}},ke={message:`Aucun résultat pour ces filtres.`,resetMessage:`Réinitialiser les filtres`,onFilterReset:()=>alert(`reset filters`)},Ae={title:`Design System/Table`,component:j,args:{title:`Tableau de données`,columns:R,data:L,selectable:!1,isLoading:!1,isSticky:!1,variant:F.COLLAPSE,noData:Oe,noResult:ke},argTypes:{variant:{control:`inline-radio`,options:[F.SEPARATE,F.COLLAPSE]},isLoading:{control:`boolean`},selectable:{control:`boolean`},isSticky:{control:`boolean`}},parameters:{layout:`padded`}},z={render:e=>(0,I.jsx)(j,{...e})},B={args:{variant:F.SEPARATE}},V={args:{isLoading:!0}},H={args:{data:[],noData:{...Oe,hasNoData:!1},noResult:{...ke,onFilterReset:()=>alert(`Réinitialiser les filtres`)}}},U={args:{data:[],noData:{hasNoData:!0,message:{icon:`📭`,title:`Rien à afficher`,subtitle:`Aucun élément n’a encore été créé.`}}}},W={args:{selectable:!0,selectedNumber:`0 sélectionnée`}},G={render:e=>{let[t,n]=(0,Ee.useState)(new Set([2,4])),r=t.size;return(0,I.jsx)(j,{...e,selectable:!0,selectedIds:t,selectedNumber:`${r} sélectionnée${r>1?`s`:``}`,onSelectionChange:e=>{n(new Set(e.map(e=>e.id)))}})}},K={render:e=>(0,I.jsx)(j,{...e,selectable:!0,isRowSelectable:e=>e.status===`active`,selectedNumber:`—`})},q={args:{isSticky:!0},render:e=>(0,I.jsx)(`div`,{style:{height:260,overflow:`auto`,border:`1px solid #eee`},children:(0,I.jsx)(j,{...e,data:[...L,...L]})})},J={args:{columns:[{...R[0],headerHidden:!0},R[1],{...R[2],bodyHidden:!0},R[3],R[4]]}},Y={args:{columns:[{...R[0],headerColSpan:2},R[1],R[2],R[3]]}},X={render:e=>{let t=R;return(0,I.jsx)(j,{...e,variant:F.COLLAPSE,columns:t,getFullRow:e=>e.age>30?{content:(0,I.jsx)(`div`,{style:{padding:`8px`,margin:`8px`,backgroundColor:`violet`,borderRadius:`4px`},children:e.name},e.id),headerId:`score`}:null})}},Z={render:e=>{let[t,n]=(0,Ee.useState)(3),r=[...R.slice(0,4),{id:`actions`,label:`Actions`,render:e=>(0,I.jsx)(`button`,{onClick:t=>{t.stopPropagation(),n(t=>t===e.id?null:e.id)},children:t===e.id?`Fermer`:`Voir détails`})}];return(0,I.jsx)(j,{...e,columns:r,getFullRow:e=>e.id===t?{content:(0,I.jsxs)(`div`,{style:{padding:16},children:[(0,I.jsx)(`h4`,{style:{margin:0},children:e.name}),(0,I.jsxs)(`p`,{style:{margin:`8px 0`},children:[`Email: `,(0,I.jsx)(`strong`,{children:e.email})]}),(0,I.jsxs)(`p`,{style:{margin:0},children:[`Score: `,(0,I.jsx)(`strong`,{children:e.nested.score}),` — Statut:`,` `,(0,I.jsx)(`strong`,{children:e.status})]})]}),headerId:`name`}:null})}},Q={args:{},render:e=>(0,I.jsx)(j,{...e,data:[...L]})},$={args:{pagination:{currentPage:1,pageCount:3,onPageClick:e=>{alert(`Go to page ${e}`)}}},render:e=>(0,I.jsx)(j,{...e,data:[...L]})},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
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
    return <Table {...args} variant={TableVariant.COLLAPSE} columns={columns} getFullRow={row => {
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
    return <Table {...args} columns={columns} getFullRow={row => row.id === expandedId ? {
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
}`,...$.parameters?.docs?.source}}},je=[`Basic`,`SeparateVariant`,`Loading`,`NoResults`,`NoDataState`,`SelectableUncontrolled`,`SelectableControlled`,`SelectableWithDisabledRows`,`StickyHeaderInScrollContainer`,`WithHiddenColumns`,`WithHeaderColSpan`,`WithFullRowAlwaysDisplayedDetail`,`WithFullRowDetail`,`SortingShowcase`,`WithPagination`]})))()}Me();export{z as Basic,V as Loading,U as NoDataState,H as NoResults,G as SelectableControlled,W as SelectableUncontrolled,K as SelectableWithDisabledRows,B as SeparateVariant,Q as SortingShowcase,q as StickyHeaderInScrollContainer,X as WithFullRowAlwaysDisplayedDetail,Z as WithFullRowDetail,Y as WithHeaderColSpan,J as WithHiddenColumns,$ as WithPagination,je as __namedExportsOrder,Ae as default};