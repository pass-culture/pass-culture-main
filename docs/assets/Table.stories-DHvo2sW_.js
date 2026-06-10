import{i as e,s as t}from"./preload-helper-xPQekRTU.js";import{C as n}from"./iframe-CriMFUz6.js";import{t as r}from"./jsx-runtime-CaZkqeYb.js";import{t as i}from"./classnames-Dm_LJ4P4.js";import{a as ee,n as a,r as te,s as ne,t as re}from"./Button-B9BTmyw_.js";import{n as o,t as s}from"./SvgIcon-DVxB_oBw.js";import{n as ie,t as ae}from"./full-down-CXDwsvNu.js";import{n as oe,t as c}from"./full-refresh-D8Ja_sd6.js";import{n as l,t as u}from"./full-up-CP6OC8Ny.js";import{n as d,t as f}from"./stroke-search-hvN1lQvr.js";import{n as se,t as ce}from"./Checkbox-Cl5dIJ31.js";import{n as le,t as ue}from"./Pagination-CGDiYWwd.js";import{n as de,t as fe}from"./Skeleton-BV2vub-j.js";var p,m,pe,h=e((()=>{p=t(n(),1),m=function(e){return e.ASC=`asc`,e.DESC=`desc`,e.NONE=`none`,e}({}),pe=()=>{let[e,t]=(0,p.useState)(null),[n,r]=(0,p.useState)(`none`);return{currentSortingColumn:e,currentSortingMode:n,onColumnHeaderClick:(0,p.useCallback)(i=>e===i?n===`asc`?(r(`desc`),`desc`):n===`desc`?(r(`none`),`none`):(r(`asc`),`asc`):(t(i),r(`asc`),`asc`),[e,n])}}})),g,me=e((()=>{g={"sorting-icons":`_sorting-icons_cbxcb_1`,"both-icons":`_both-icons_cbxcb_17`}})),_,v,he=e((()=>{h(),ie(),l(),o(),me(),_=r(),v=({sortingMode:e,onClick:t,children:n})=>(0,_.jsxs)(`button`,{type:`button`,className:g[`sorting-icons`],onClick:t,children:[n,e===m.NONE?(0,_.jsxs)(`span`,{className:g[`both-icons`],children:[(0,_.jsx)(s,{src:u,alt:`Trier par ordre croissant`,width:`10`}),(0,_.jsx)(s,{src:ae,alt:``,width:`10`})]}):e===m.DESC?(0,_.jsx)(s,{src:u,alt:`Ne plus trier`,width:`10`}):(0,_.jsx)(s,{src:ae,alt:`Trier par ordre décroissant`,width:`10`})]});try{v.displayName=`SortColumn`,v.__docgenInfo={description:``,displayName:`SortColumn`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,methods:[],props:{sortingMode:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`}],description:``,name:`sortingMode`,parent:{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`},required:!0,tags:{},type:{name:`enum`,raw:`SortingMode`,value:[{value:`"asc"`,description:``,fullComment:``,tags:{}},{value:`"desc"`,description:``,fullComment:``,tags:{}},{value:`"none"`,description:``,fullComment:``,tags:{}}]}},onClick:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`}],description:``,name:`onClick`,parent:{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`},required:!0,tags:{},type:{name:`() => void`}}},tags:{}}}catch{}})),ge,y,b,x=e((()=>{ge=`_wrapper_my972_1`,y=`_table_my972_5`,b={wrapper:ge,table:y,"table-pagination":`_table-pagination_my972_13`,"table-separate":`_table-separate_my972_17`,"table-separate-cell":`_table-separate-cell_my972_21`,"table-collapse":`_table-collapse_my972_38`,"table-collapse-cell":`_table-collapse-cell_my972_45`,"table-row":`_table-row_my972_50`,"table-header":`_table-header_my972_54`,"table-header-sticky":`_table-header-sticky_my972_60`,"table-header-th":`_table-header-th_my972_65`,"table-header-sortable-th":`_table-header-sortable-th_my972_78`,"table-select-all":`_table-select-all_my972_83`,"table-checkbox-label":`_table-checkbox-label_my972_89`,"visually-hidden":`_visually-hidden_my972_104`,"table-caption-no-display":`_table-caption-no-display_my972_116`,"table-fullrow-content":`_table-fullrow-content_my972_120`}})),S,_e=e((()=>{S={"no-data":`_no-data_10bkz_1`,"no-data-icon":`_no-data-icon_10bkz_7`,"no-data-title":`_no-data-title_10bkz_11`,"no-data-subtitle":`_no-data-subtitle_10bkz_19`}})),C,w,ve=e((()=>{o(),_e(),C=r(),w=({noData:{icon:e,title:t,subtitle:n}})=>(0,C.jsxs)(`div`,{className:S[`no-data`],children:[(0,C.jsx)(s,{src:e,alt:``,width:`100`,className:S[`no-data-icon`]}),(0,C.jsx)(`p`,{className:S[`no-data-title`],children:t}),(0,C.jsx)(`p`,{className:S[`no-data-subtitle`],children:n})]});try{w.displayName=`TableNoData`,w.__docgenInfo={description:``,displayName:`TableNoData`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/TableNoData/TableNoData.tsx`,methods:[],props:{noData:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/TableNoData/TableNoData.tsx`,name:`TableNoDataProps`}],description:``,name:`noData`,parent:{fileName:`pro/src/ui-kit/Table/TableNoData/TableNoData.tsx`,name:`TableNoDataProps`},required:!0,tags:{},type:{name:`{ icon: string; title: string; subtitle: string; }`}}},tags:{}}}catch{}})),T,ye=e((()=>{T={"search-no-results":`_search-no-results_yb0tv_1`,"search-no-results-icon":`_search-no-results-icon_yb0tv_4`,"search-no-results-title4":`_search-no-results-title4_yb0tv_8`,"search-no-results-text":`_search-no-results-text_yb0tv_14`}})),E,D,be=e((()=>{a(),ne(),oe(),f(),o(),ye(),E=r(),D=({colSpan:e=1,message:t=`Pas de résultat pour votre recherche`,subtitle:n=`Vous pouvez modifier votre recherche ou`,resetMessage:r=`Réinitialiser les filtres`,resetFilters:i})=>(0,E.jsx)(`tr`,{children:(0,E.jsx)(`td`,{colSpan:e,children:(0,E.jsxs)(`div`,{className:T[`search-no-results`],children:[(0,E.jsx)(s,{src:d,alt:`Illustration de recherche`,className:T[`search-no-results-icon`],width:`124`}),(0,E.jsx)(`p`,{className:T[`search-no-results-title4`],children:t}),(0,E.jsx)(`p`,{className:T[`search-no-results-text`],children:n}),(0,E.jsx)(re,{variant:ee.SECONDARY,color:te.BRAND,icon:c,onClick:i,label:r})]})})});try{D.displayName=`TableNoFilterResult`,D.__docgenInfo={description:``,displayName:`TableNoFilterResult`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,methods:[],props:{colSpan:{defaultValue:{value:`1`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`colSpan`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`number`}},message:{defaultValue:{value:`Pas de résultat pour votre recherche`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`message`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`string`}},subtitle:{defaultValue:{value:`Vous pouvez modifier votre recherche ou`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`subtitle`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`string`}},resetMessage:{defaultValue:{value:`Réinitialiser les filtres`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`resetMessage`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`string`}},resetFilters:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`resetFilters`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!0,tags:{},type:{name:`() => void`}}},tags:{}}}catch{}}));function xe(e,t){if(t)return typeof t==`function`?t(e):typeof t==`string`?t.split(`.`).reduce((e,t)=>e?.[t],e):e[t]}function O({title:e=`Tableau de données`,columns:t,data:n,allData:r,selectable:i=!1,selectedNumber:ee,selectedIds:a,className:te,isLoading:ne,isSticky:re,variant:o,noResult:s,noData:ie,onSelectionChange:ae,getFullRowContent:oe,isRowSelectable:c,pagination:l}){let u=r??n,{currentSortingColumn:d,currentSortingMode:f,onColumnHeaderClick:se}=pe(),[le,de]=(0,A.useState)(new Set),p=a!==void 0,h=p?a:le,g=e=>{p||de(e),ae?.(u.filter(t=>e.has(t.id)))};function me(e){se(e)}let _=(0,A.useMemo)(()=>c?u.filter(c):u,[u,c]),he=()=>{h.size===_.length?g(new Set):g(new Set(_.map(e=>e.id)))},ge=e=>{let t=new Set(h);t.has(e.id)?t.delete(e.id):t.add(e.id),g(t)},y=(0,A.useMemo)(()=>{if(!d)return n;let e=t.find(e=>e.id===d);return e?[...u].sort((t,n)=>{let r=xe(t,e.ordererField),i=xe(n,e.ordererField);return r===i?0:r<i?f===m.ASC?-1:1:f===m.ASC?1:-1}):n},[n,d,f,t,u]),x=h.size===_.length&&_.length>0,S=h.size>0&&h.size<_.length,_e=x?`Tout désélectionner`:`Tout sélectionner`;return ie.hasNoData?(0,j.jsx)(w,{noData:ie.message}):(0,j.jsxs)(`div`,{className:(0,k.default)(b.wrapper,te),children:[i&&(0,j.jsxs)(`div`,{className:b[`table-select-all`],children:[(0,j.jsx)(ce,{label:_e,checked:x,indeterminate:S,onChange:he}),(0,j.jsx)(`span`,{className:b[`visually-hidden`],children:`Sélectionner toutes les lignes`}),(0,j.jsx)(`div`,{children:ee})]}),(0,j.jsxs)(`table`,{className:(0,k.default)(b.table,{[b[`table-separate`]]:o===`separate`,[b[`table-collapse`]]:o===`collapse`}),children:[(0,j.jsx)(`caption`,{className:b[`table-caption-no-display`],children:e}),(0,j.jsx)(`thead`,{children:(0,j.jsxs)(`tr`,{className:(0,k.default)(b[`table-header`],{[b[`table-header-sticky`]]:re}),children:[i&&(0,j.jsx)(`th`,{scope:`col`,className:b[`table-header-th`],children:(0,j.jsx)(`span`,{className:b[`visually-hidden`],children:`Sélectionner`})}),t.map(e=>{if(e.headerHidden)return null;let t=e.header??e.label??``;return(0,j.jsx)(`th`,{scope:`col`,id:e.id,colSpan:e.headerColSpan||1,className:(0,k.default)(b[`table-header-th`],{[b[`table-header-sortable-th`]]:e.sortable}),children:e.sortable?(0,j.jsx)(v,{onClick:()=>me(e.id),sortingMode:d===e.id?f:m.NONE,children:t}):t},`col-${e.id}`)})]})}),(0,j.jsxs)(`tbody`,{children:[ne&&Array.from({length:8}).map((e,n)=>(0,j.jsx)(`tr`,{children:(0,j.jsx)(`td`,{colSpan:t.length+1,children:(0,j.jsx)(fe,{height:`7rem`,width:`100%`})})},`loading-row-${t.length}-${n}`)),!y.length&&(0,j.jsx)(D,{colSpan:t.length+ +!!i,message:s.message,subtitle:s.subtitle,resetMessage:s.resetMessage,resetFilters:s.onFilterReset}),y.map(e=>{let n=h.has(e.id),r=oe?.(e);return(0,j.jsxs)(A.Fragment,{children:[(0,j.jsxs)(`tr`,{"data-testid":`table-row`,className:(0,k.default)({[b[`table-row`]]:!r}),children:[i&&(0,j.jsxs)(`td`,{className:(0,k.default)({[b[`table-separate-cell`]]:o===`separate`,[b[`table-collapse-cell`]]:o===`collapse`}),children:[(0,j.jsx)(ce,{label:e.name??`ligne ${e.id}`,checked:n,onChange:()=>ge(e),className:b[`table-checkbox-label`],disabled:c?!c(e):!1}),(0,j.jsxs)(`span`,{className:b[`visually-hidden`],children:[`Selectionner la ligne `,e.name||e.id]})]}),t.map(t=>{if(t.bodyHidden)return null;let n=t.render?t.render(e):xe(e,t.ordererField);return(0,j.jsx)(`td`,{className:(0,k.default)({[b[`table-separate-cell`]]:o===`separate`,[b[`table-collapse-cell`]]:o===`collapse`}),"data-label":t.label,children:n},`col-${t.id}-${t.label}`)})]}),r&&(0,j.jsx)(`tr`,{className:(0,k.default)(b[`table-row`]),children:(0,j.jsx)(`td`,{colSpan:t.length+ +!!i,children:(0,j.jsx)(`div`,{className:b[`table-fullrow-content`],children:r})})})]},e.id)})]})]}),l&&(0,j.jsx)(`div`,{className:b[`table-pagination`],children:(0,j.jsx)(ue,{currentPage:l.currentPage,pageCount:l.pageCount,onPageClick:l.onPageClick})})]})}var k,A,j,M,Se=e((()=>{k=t(i(),1),A=t(n(),1),h(),se(),le(),de(),he(),x(),ve(),be(),j=r(),M=function(e){return e.COLLAPSE=`collapse`,e.SEPARATE=`separate`,e}({});try{O.displayName=`Table`,O.__docgenInfo={description:``,displayName:`Table`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/Table.tsx`,methods:[],props:{title:{defaultValue:{value:`Tableau de données`},declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`title`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},columns:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`columns`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`Column<T>[]`}},data:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`data`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`T[]`}},allData:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`allData`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`T[]`}},selectable:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`selectable`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`boolean`}},className:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`className`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},isLoading:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`isLoading`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`boolean`}},isSticky:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`isSticky`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`boolean`}},variant:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`variant`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`enum`,raw:`TableVariant`,value:[{value:`"collapse"`,description:``,fullComment:``,tags:{}},{value:`"separate"`,description:``,fullComment:``,tags:{}}]}},selectedNumber:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`selectedNumber`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},selectedIds:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`selectedIds`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`Set<string | number>`}},onSelectionChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`onSelectionChange`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((rows: T[]) => void)`}},getFullRowContent:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`getFullRowContent`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((row: T) => ReactNode)`}},isRowSelectable:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`isRowSelectable`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((row: T) => boolean)`}},noResult:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`noResult`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`NoResultProps`}},noData:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`noData`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`EmptyStateProps`}},pagination:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`pagination`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`PaginationProps`}}},tags:{}}}catch{}})),N,P,F,Ce,I,L,R,we,z,B,V,H,U,W,G,K,q,J,Y,X,Z,Q,$,Te;e((()=>{N=t(n(),1),Se(),P=r(),F=[{id:1,name:`Alice`,email:`alice@example.com`,age:27,status:`active`,createdAt:`2024-01-05T10:00:00Z`,nested:{score:77}},{id:2,name:`Bob`,email:`bob@example.com`,age:34,status:`inactive`,createdAt:`2024-02-01T08:30:00Z`,nested:{score:65}},{id:3,name:`Chloe`,email:`chloe@example.com`,age:22,status:`active`,createdAt:`2024-03-12T12:45:00Z`,nested:{score:92}},{id:4,name:`Diego`,email:`diego@example.com`,age:41,status:`active`,createdAt:`2024-04-20T15:10:00Z`,nested:{score:58}},{id:5,name:`Elise`,email:`elise@example.com`,age:29,status:`inactive`,createdAt:`2024-05-11T09:00:00Z`,nested:{score:80}},{id:6,name:`Fares`,email:`fares@example.com`,age:37,status:`active`,createdAt:`2024-06-02T11:15:00Z`,nested:{score:71}},{id:7,name:`Gina`,email:`gina@example.com`,age:31,status:`active`,createdAt:`2024-06-18T16:20:00Z`,nested:{score:88}},{id:8,name:`Hugo`,email:`hugo@example.com`,age:25,status:`inactive`,createdAt:`2024-07-08T07:05:00Z`,nested:{score:54}}],Ce=e=>new Date(e).toLocaleDateString(`fr-FR`,{year:`numeric`,month:`short`,day:`2-digit`}),I=[{id:`name`,label:`Nom`,sortable:!0,ordererField:e=>e.name,render:e=>(0,P.jsx)(`strong`,{children:e.name})},{id:`age`,label:`Âge`,sortable:!0,ordererField:e=>e.age,render:e=>e.age},{id:`created`,label:`Créé le`,sortable:!0,ordererField:e=>new Date(e.createdAt).getTime(),render:e=>Ce(e.createdAt)},{id:`status`,label:`Statut`,render:e=>(0,P.jsx)(`span`,{"aria-label":`status-${e.id}`,children:e.status===`active`?`Actif`:`Inactif`})},{id:`score`,label:`Score`,sortable:!0,ordererField:e=>e.nested.score,render:e=>e.nested.score}],L={hasNoData:!1,message:{icon:`📄`,title:`Aucune donnée`,subtitle:`Commencez par créer un élément pour remplir ce tableau.`}},R={message:`Aucun résultat pour ces filtres.`,resetMessage:`Réinitialiser les filtres`,onFilterReset:()=>alert(`reset filters`)},we={title:`Design System/Table`,component:O,args:{title:`Tableau de données`,columns:I,data:F,selectable:!1,isLoading:!1,isSticky:!1,variant:M.COLLAPSE,noData:L,noResult:R},argTypes:{variant:{control:`inline-radio`,options:[M.SEPARATE,M.COLLAPSE]},isLoading:{control:`boolean`},selectable:{control:`boolean`},isSticky:{control:`boolean`}},parameters:{layout:`padded`}},z={render:e=>(0,P.jsx)(O,{...e})},B={args:{variant:M.SEPARATE}},V={args:{isLoading:!0}},H={args:{data:[],noData:{...L,hasNoData:!1},noResult:{...R,onFilterReset:()=>alert(`Réinitialiser les filtres`)}}},U={args:{data:[],noData:{hasNoData:!0,message:{icon:`📭`,title:`Rien à afficher`,subtitle:`Aucun élément n’a encore été créé.`}}}},W={args:{selectable:!0,selectedNumber:`0 sélectionnée`}},G={render:e=>{let[t,n]=(0,N.useState)(new Set([2,4])),r=t.size;return(0,P.jsx)(O,{...e,selectable:!0,selectedIds:t,selectedNumber:`${r} sélectionnée${r>1?`s`:``}`,onSelectionChange:e=>{n(new Set(e.map(e=>e.id)))}})}},K={render:e=>(0,P.jsx)(O,{...e,selectable:!0,isRowSelectable:e=>e.status===`active`,selectedNumber:`—`})},q={args:{isSticky:!0},render:e=>(0,P.jsx)(`div`,{style:{height:260,overflow:`auto`,border:`1px solid #eee`},children:(0,P.jsx)(O,{...e,data:[...F,...F]})})},J={args:{columns:[{...I[0],headerHidden:!0},I[1],{...I[2],bodyHidden:!0},I[3],I[4]]}},Y={args:{columns:[{...I[0],headerColSpan:2},I[1],I[2],I[3]]}},X={render:e=>{let t=I;return(0,P.jsx)(O,{...e,variant:M.COLLAPSE,columns:t,getFullRowContent:e=>e.age>30?(0,P.jsx)(`div`,{style:{padding:`8px`,margin:`8px`,backgroundColor:`violet`,borderRadius:`4px`},children:e.name},e.id):null})}},Z={render:e=>{let[t,n]=(0,N.useState)(3),r=[...I.slice(0,4),{id:`actions`,label:`Actions`,render:e=>(0,P.jsx)(`button`,{onClick:t=>{t.stopPropagation(),n(t=>t===e.id?null:e.id)},children:t===e.id?`Fermer`:`Voir détails`})}];return(0,P.jsx)(O,{...e,columns:r,getFullRowContent:e=>e.id===t?(0,P.jsxs)(`div`,{style:{padding:16},children:[(0,P.jsx)(`h4`,{style:{margin:0},children:e.name}),(0,P.jsxs)(`p`,{style:{margin:`8px 0`},children:[`Email: `,(0,P.jsx)(`strong`,{children:e.email})]}),(0,P.jsxs)(`p`,{style:{margin:0},children:[`Score: `,(0,P.jsx)(`strong`,{children:e.nested.score}),` — Statut:`,` `,(0,P.jsx)(`strong`,{children:e.status})]})]}):null})}},Q={args:{},render:e=>(0,P.jsx)(O,{...e,data:[...F]})},$={args:{pagination:{currentPage:1,pageCount:3,onPageClick:e=>{alert(`Go to page ${e}`)}}},render:e=>(0,P.jsx)(O,{...e,data:[...F]})},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
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
    return <Table {...args} variant={TableVariant.COLLAPSE} columns={columns} getFullRowContent={row => {
      if (row.age > 30) {
        return <div key={row.id} style={{
          padding: '8px',
          margin: '8px',
          backgroundColor: 'violet',
          borderRadius: '4px'
        }}>
                {row.name}
              </div>;
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
    return <Table {...args} columns={columns} getFullRowContent={row => row.id === expandedId ? <div style={{
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
            </div> : null} />;
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
}`,...$.parameters?.docs?.source}}},Te=[`Basic`,`SeparateVariant`,`Loading`,`NoResults`,`NoDataState`,`SelectableUncontrolled`,`SelectableControlled`,`SelectableWithDisabledRows`,`StickyHeaderInScrollContainer`,`WithHiddenColumns`,`WithHeaderColSpan`,`WithFullRowAlwaysDisplayedDetail`,`WithFullRowDetail`,`SortingShowcase`,`WithPagination`]}))();export{z as Basic,V as Loading,U as NoDataState,H as NoResults,G as SelectableControlled,W as SelectableUncontrolled,K as SelectableWithDisabledRows,B as SeparateVariant,Q as SortingShowcase,q as StickyHeaderInScrollContainer,X as WithFullRowAlwaysDisplayedDetail,Z as WithFullRowDetail,Y as WithHeaderColSpan,J as WithHiddenColumns,$ as WithPagination,Te as __namedExportsOrder,we as default};