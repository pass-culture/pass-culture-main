import{i as e,s as t}from"./preload-helper-CT_b8DTk.js";import{C as n}from"./iframe-Gsk6aIKs.js";import{t as r}from"./jsx-runtime-DqZldVDK.js";import{t as i}from"./classnames-DyhsJ24V.js";import{a as ee,n as a,r as te,s as ne,t as re}from"./Button-BqKr_ywJ.js";import{n as o,t as s}from"./SvgIcon-BdMUh4wU.js";import{n as c,t as l}from"./full-down-R6Z3dws5.js";import{n as ie,t as u}from"./full-refresh-DlqCI11w.js";import{n as d,t as f}from"./full-up-B8KxZakU.js";import{n as p,t as m}from"./stroke-search-QSRZFfdr.js";import{n as ae,t as oe}from"./Checkbox-OTFYUCBo.js";import{n as se,t as ce}from"./Pagination-Cg9TH31z.js";import{n as le,t as ue}from"./Skeleton-CymeTt1f.js";var h,g,de,_=e((()=>{h=t(n(),1),g=function(e){return e.ASC=`asc`,e.DESC=`desc`,e.NONE=`none`,e}({}),de=()=>{let[e,t]=(0,h.useState)(null),[n,r]=(0,h.useState)(`none`);return{currentSortingColumn:e,currentSortingMode:n,onColumnHeaderClick:(0,h.useCallback)(i=>e===i?n===`asc`?(r(`desc`),`desc`):n===`desc`?(r(`none`),`none`):(r(`asc`),`asc`):(t(i),r(`asc`),`asc`),[e,n])}}})),v,fe=e((()=>{v={"sorting-icons":`_sorting-icons_cbxcb_1`,"both-icons":`_both-icons_cbxcb_17`}})),y,pe,b,me=e((()=>{_(),c(),d(),o(),fe(),y=r(),pe=e=>e===g.DESC?(0,y.jsx)(s,{src:f,alt:`Ne plus trier`,width:`10`}):(0,y.jsx)(s,{src:l,alt:`Trier par ordre décroissant`,width:`10`}),b=({sortingMode:e,onClick:t,children:n})=>(0,y.jsxs)(`button`,{type:`button`,className:v[`sorting-icons`],onClick:t,children:[n,e===g.NONE?(0,y.jsxs)(`span`,{className:v[`both-icons`],children:[(0,y.jsx)(s,{src:f,alt:`Trier par ordre croissant`,width:`10`}),(0,y.jsx)(s,{src:l,alt:``,width:`10`})]}):pe(e)]});try{b.displayName=`SortColumn`,b.__docgenInfo={description:``,displayName:`SortColumn`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,methods:[],props:{sortingMode:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`}],description:``,name:`sortingMode`,parent:{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`},required:!0,tags:{},type:{name:`enum`,raw:`SortingMode`,value:[{value:`"asc"`,description:``,fullComment:``,tags:{}},{value:`"desc"`,description:``,fullComment:``,tags:{}},{value:`"none"`,description:``,fullComment:``,tags:{}}]}},onClick:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`}],description:``,name:`onClick`,parent:{fileName:`pro/src/ui-kit/Table/SortColumn/SortColumn.tsx`,name:`SortColumnProps`},required:!0,tags:{},type:{name:`() => void`}}},tags:{}}}catch{}})),x,S,C,he=e((()=>{x=`_wrapper_my972_1`,S=`_table_my972_5`,C={wrapper:x,table:S,"table-pagination":`_table-pagination_my972_13`,"table-separate":`_table-separate_my972_17`,"table-separate-cell":`_table-separate-cell_my972_21`,"table-collapse":`_table-collapse_my972_38`,"table-collapse-cell":`_table-collapse-cell_my972_45`,"table-row":`_table-row_my972_50`,"table-header":`_table-header_my972_54`,"table-header-sticky":`_table-header-sticky_my972_60`,"table-header-th":`_table-header-th_my972_65`,"table-header-sortable-th":`_table-header-sortable-th_my972_78`,"table-select-all":`_table-select-all_my972_83`,"table-checkbox-label":`_table-checkbox-label_my972_89`,"visually-hidden":`_visually-hidden_my972_104`,"table-caption-no-display":`_table-caption-no-display_my972_116`,"table-fullrow-content":`_table-fullrow-content_my972_120`}})),w,ge=e((()=>{w={"no-data":`_no-data_10bkz_1`,"no-data-icon":`_no-data-icon_10bkz_7`,"no-data-title":`_no-data-title_10bkz_11`,"no-data-subtitle":`_no-data-subtitle_10bkz_19`}})),T,E,_e=e((()=>{o(),ge(),T=r(),E=({noData:{icon:e,title:t,subtitle:n}})=>(0,T.jsxs)(`div`,{className:w[`no-data`],children:[(0,T.jsx)(s,{src:e,alt:``,width:`100`,className:w[`no-data-icon`]}),(0,T.jsx)(`p`,{className:w[`no-data-title`],children:t}),(0,T.jsx)(`p`,{className:w[`no-data-subtitle`],children:n})]});try{E.displayName=`TableNoData`,E.__docgenInfo={description:``,displayName:`TableNoData`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/TableNoData/TableNoData.tsx`,methods:[],props:{noData:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/TableNoData/TableNoData.tsx`,name:`TableNoDataProps`}],description:``,name:`noData`,parent:{fileName:`pro/src/ui-kit/Table/TableNoData/TableNoData.tsx`,name:`TableNoDataProps`},required:!0,tags:{},type:{name:`{ icon: string; title: string; subtitle: string; }`}}},tags:{}}}catch{}})),D,ve=e((()=>{D={"search-no-results":`_search-no-results_yb0tv_1`,"search-no-results-icon":`_search-no-results-icon_yb0tv_4`,"search-no-results-title4":`_search-no-results-title4_yb0tv_8`,"search-no-results-text":`_search-no-results-text_yb0tv_14`}})),O,k,ye=e((()=>{a(),ne(),ie(),m(),o(),ve(),O=r(),k=({colSpan:e=1,message:t=`Pas de résultat pour votre recherche`,subtitle:n=`Vous pouvez modifier votre recherche ou`,resetMessage:r=`Réinitialiser les filtres`,resetFilters:i})=>(0,O.jsx)(`tr`,{children:(0,O.jsx)(`td`,{colSpan:e,children:(0,O.jsxs)(`div`,{className:D[`search-no-results`],children:[(0,O.jsx)(s,{src:p,alt:`Illustration de recherche`,className:D[`search-no-results-icon`],width:`124`}),(0,O.jsx)(`p`,{className:D[`search-no-results-title4`],children:t}),(0,O.jsx)(`p`,{className:D[`search-no-results-text`],children:n}),(0,O.jsx)(re,{variant:ee.SECONDARY,color:te.BRAND,icon:u,onClick:i,label:r})]})})});try{k.displayName=`TableNoFilterResult`,k.__docgenInfo={description:``,displayName:`TableNoFilterResult`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,methods:[],props:{colSpan:{defaultValue:{value:`1`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`colSpan`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`number`}},message:{defaultValue:{value:`Pas de résultat pour votre recherche`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`message`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`string`}},subtitle:{defaultValue:{value:`Vous pouvez modifier votre recherche ou`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`subtitle`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`string`}},resetMessage:{defaultValue:{value:`Réinitialiser les filtres`},declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`resetMessage`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!1,tags:{},type:{name:`string`}},resetFilters:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`}],description:``,name:`resetFilters`,parent:{fileName:`pro/src/ui-kit/Table/TableNoFilterResult/TableNoFilterResult.tsx`,name:`NoResultsProps`},required:!0,tags:{},type:{name:`() => void`}}},tags:{}}}catch{}}));function A(e,t){if(t)return typeof t==`function`?t(e):typeof t==`string`?t.split(`.`).reduce((e,t)=>e?.[t],e):e[t]}function j({title:e=`Tableau de données`,columns:t,data:n,allData:r,selectable:i=!1,selectedNumber:ee,selectedIds:a,className:te,isLoading:ne,isSticky:re,variant:o,noResult:s,noData:c,onSelectionChange:l,getFullRowContent:ie,isRowSelectable:u,pagination:d}){let f=r??n,{currentSortingColumn:p,currentSortingMode:m,onColumnHeaderClick:ae}=de(),[se,le]=(0,N.useState)(new Set),h=a!==void 0,_=h?a:se,v=e=>{h||le(e),l?.(f.filter(t=>e.has(t.id)))};function fe(e){ae(e)}let y=(0,N.useMemo)(()=>u?f.filter(u):f,[f,u]),pe=()=>{_.size===y.length?v(new Set):v(new Set(y.map(e=>e.id)))},me=e=>{let t=new Set(_);t.has(e.id)?t.delete(e.id):t.add(e.id),v(t)},x=(0,N.useMemo)(()=>{if(!p)return n;let e=t.find(e=>e.id===p);return e?[...f].sort((t,n)=>{let r=A(t,e.ordererField),i=A(n,e.ordererField);return r===i?0:r<i?m===g.ASC?-1:1:m===g.ASC?1:-1}):n},[n,p,m,t,f]),S=_.size===y.length&&y.length>0,he=_.size>0&&_.size<y.length,w=S?`Tout désélectionner`:`Tout sélectionner`;return c.hasNoData?(0,P.jsx)(E,{noData:c.message}):(0,P.jsxs)(`div`,{className:(0,M.default)(C.wrapper,te),children:[i&&(0,P.jsxs)(`div`,{className:C[`table-select-all`],children:[(0,P.jsx)(oe,{label:w,checked:S,indeterminate:he,onChange:pe}),(0,P.jsx)(`span`,{className:C[`visually-hidden`],children:`Sélectionner toutes les lignes`}),(0,P.jsx)(`div`,{children:ee})]}),(0,P.jsxs)(`table`,{className:(0,M.default)(C.table,{[C[`table-separate`]]:o===`separate`,[C[`table-collapse`]]:o===`collapse`}),children:[(0,P.jsx)(`caption`,{className:C[`table-caption-no-display`],children:e}),(0,P.jsx)(`thead`,{children:(0,P.jsxs)(`tr`,{className:(0,M.default)(C[`table-header`],{[C[`table-header-sticky`]]:re}),children:[i&&(0,P.jsx)(`th`,{scope:`col`,className:C[`table-header-th`],children:(0,P.jsx)(`span`,{className:C[`visually-hidden`],children:`Sélectionner`})}),t.map(e=>{if(e.headerHidden)return null;let t=e.header??e.label??``;return(0,P.jsx)(`th`,{scope:`col`,id:e.id,colSpan:e.headerColSpan||1,className:(0,M.default)(C[`table-header-th`],{[C[`table-header-sortable-th`]]:e.sortable}),children:e.sortable?(0,P.jsx)(b,{onClick:()=>fe(e.id),sortingMode:p===e.id?m:g.NONE,children:t}):t},`col-${e.id}`)})]})}),(0,P.jsxs)(`tbody`,{children:[ne&&Array.from({length:8}).map((e,n)=>(0,P.jsx)(`tr`,{children:(0,P.jsx)(`td`,{colSpan:t.length+1,children:(0,P.jsx)(ue,{height:`7rem`,width:`100%`})})},`loading-row-${t.length}-${n}`)),!x.length&&(0,P.jsx)(k,{colSpan:t.length+ +!!i,message:s.message,subtitle:s.subtitle,resetMessage:s.resetMessage,resetFilters:s.onFilterReset}),x.map(e=>{let n=_.has(e.id),r=ie?.(e);return(0,P.jsxs)(N.Fragment,{children:[(0,P.jsxs)(`tr`,{"data-testid":`table-row`,className:(0,M.default)({[C[`table-row`]]:!r}),children:[i&&(0,P.jsxs)(`td`,{className:(0,M.default)({[C[`table-separate-cell`]]:o===`separate`,[C[`table-collapse-cell`]]:o===`collapse`}),children:[(0,P.jsx)(oe,{label:e.name??`ligne ${e.id}`,checked:n,onChange:()=>me(e),className:C[`table-checkbox-label`],disabled:u?!u(e):!1}),(0,P.jsxs)(`span`,{className:C[`visually-hidden`],children:[`Selectionner la ligne `,e.name||e.id]})]}),t.map(t=>{if(t.bodyHidden)return null;let n=t.render?t.render(e):A(e,t.ordererField);return(0,P.jsx)(`td`,{className:(0,M.default)({[C[`table-separate-cell`]]:o===`separate`,[C[`table-collapse-cell`]]:o===`collapse`}),"data-label":t.label,children:n},`col-${t.id}-${t.label}`)})]}),r&&(0,P.jsx)(`tr`,{className:(0,M.default)(C[`table-row`]),children:(0,P.jsx)(`td`,{colSpan:t.length+ +!!i,children:(0,P.jsx)(`div`,{className:C[`table-fullrow-content`],children:r})})})]},e.id)})]})]}),d&&(0,P.jsx)(`div`,{className:C[`table-pagination`],children:(0,P.jsx)(ce,{currentPage:d.currentPage,pageCount:d.pageCount,onPageClick:d.onPageClick})})]})}var M,N,P,F,be=e((()=>{M=t(i(),1),N=t(n(),1),_(),ae(),se(),le(),me(),he(),_e(),ye(),P=r(),F=function(e){return e.COLLAPSE=`collapse`,e.SEPARATE=`separate`,e}({});try{j.displayName=`Table`,j.__docgenInfo={description:``,displayName:`Table`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/Table/Table.tsx`,methods:[],props:{title:{defaultValue:{value:`Tableau de données`},declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`title`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},columns:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`columns`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`Column<T>[]`}},data:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`data`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`T[]`}},allData:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`allData`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`T[]`}},selectable:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`selectable`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`boolean`}},className:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`className`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},isLoading:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`isLoading`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`boolean`}},isSticky:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`isSticky`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`boolean`}},variant:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`variant`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`enum`,raw:`TableVariant`,value:[{value:`"collapse"`,description:``,fullComment:``,tags:{}},{value:`"separate"`,description:``,fullComment:``,tags:{}}]}},selectedNumber:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`selectedNumber`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`string`}},selectedIds:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`selectedIds`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`Set<string | number>`}},onSelectionChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`onSelectionChange`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((rows: T[]) => void)`}},getFullRowContent:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`getFullRowContent`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((row: T) => ReactNode)`}},isRowSelectable:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`isRowSelectable`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`((row: T) => boolean)`}},noResult:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`noResult`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`NoResultProps`}},noData:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`noData`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!0,tags:{},type:{name:`EmptyStateProps`}},pagination:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`}],description:``,name:`pagination`,parent:{fileName:`pro/src/ui-kit/Table/Table.tsx`,name:`TableProps`},required:!1,tags:{},type:{name:`PaginationProps`}}},tags:{}}}catch{}})),xe,I,L,Se,R,Ce,we,Te,z,B,V,H,U,W,G,K,q,J,Y,X,Z,Q,$,Ee;e((()=>{xe=t(n(),1),be(),I=r(),L=[{id:1,name:`Alice`,email:`alice@example.com`,age:27,status:`active`,createdAt:`2024-01-05T10:00:00Z`,nested:{score:77}},{id:2,name:`Bob`,email:`bob@example.com`,age:34,status:`inactive`,createdAt:`2024-02-01T08:30:00Z`,nested:{score:65}},{id:3,name:`Chloe`,email:`chloe@example.com`,age:22,status:`active`,createdAt:`2024-03-12T12:45:00Z`,nested:{score:92}},{id:4,name:`Diego`,email:`diego@example.com`,age:41,status:`active`,createdAt:`2024-04-20T15:10:00Z`,nested:{score:58}},{id:5,name:`Elise`,email:`elise@example.com`,age:29,status:`inactive`,createdAt:`2024-05-11T09:00:00Z`,nested:{score:80}},{id:6,name:`Fares`,email:`fares@example.com`,age:37,status:`active`,createdAt:`2024-06-02T11:15:00Z`,nested:{score:71}},{id:7,name:`Gina`,email:`gina@example.com`,age:31,status:`active`,createdAt:`2024-06-18T16:20:00Z`,nested:{score:88}},{id:8,name:`Hugo`,email:`hugo@example.com`,age:25,status:`inactive`,createdAt:`2024-07-08T07:05:00Z`,nested:{score:54}}],Se=e=>new Date(e).toLocaleDateString(`fr-FR`,{year:`numeric`,month:`short`,day:`2-digit`}),R=[{id:`name`,label:`Nom`,sortable:!0,ordererField:e=>e.name,render:e=>(0,I.jsx)(`strong`,{children:e.name})},{id:`age`,label:`Âge`,sortable:!0,ordererField:e=>e.age,render:e=>e.age},{id:`created`,label:`Créé le`,sortable:!0,ordererField:e=>new Date(e.createdAt).getTime(),render:e=>Se(e.createdAt)},{id:`status`,label:`Statut`,render:e=>(0,I.jsx)(`span`,{"aria-label":`status-${e.id}`,children:e.status===`active`?`Actif`:`Inactif`})},{id:`score`,label:`Score`,sortable:!0,ordererField:e=>e.nested.score,render:e=>e.nested.score}],Ce={hasNoData:!1,message:{icon:`📄`,title:`Aucune donnée`,subtitle:`Commencez par créer un élément pour remplir ce tableau.`}},we={message:`Aucun résultat pour ces filtres.`,resetMessage:`Réinitialiser les filtres`,onFilterReset:()=>alert(`reset filters`)},Te={title:`Design System/Table`,component:j,args:{title:`Tableau de données`,columns:R,data:L,selectable:!1,isLoading:!1,isSticky:!1,variant:F.COLLAPSE,noData:Ce,noResult:we},argTypes:{variant:{control:`inline-radio`,options:[F.SEPARATE,F.COLLAPSE]},isLoading:{control:`boolean`},selectable:{control:`boolean`},isSticky:{control:`boolean`}},parameters:{layout:`padded`}},z={render:e=>(0,I.jsx)(j,{...e})},B={args:{variant:F.SEPARATE}},V={args:{isLoading:!0}},H={args:{data:[],noData:{...Ce,hasNoData:!1},noResult:{...we,onFilterReset:()=>alert(`Réinitialiser les filtres`)}}},U={args:{data:[],noData:{hasNoData:!0,message:{icon:`📭`,title:`Rien à afficher`,subtitle:`Aucun élément n’a encore été créé.`}}}},W={args:{selectable:!0,selectedNumber:`0 sélectionnée`}},G={render:e=>{let[t,n]=(0,xe.useState)(new Set([2,4])),r=t.size;return(0,I.jsx)(j,{...e,selectable:!0,selectedIds:t,selectedNumber:`${r} sélectionnée${r>1?`s`:``}`,onSelectionChange:e=>{n(new Set(e.map(e=>e.id)))}})}},K={render:e=>(0,I.jsx)(j,{...e,selectable:!0,isRowSelectable:e=>e.status===`active`,selectedNumber:`—`})},q={args:{isSticky:!0},render:e=>(0,I.jsx)(`div`,{style:{height:260,overflow:`auto`,border:`1px solid #eee`},children:(0,I.jsx)(j,{...e,data:[...L,...L]})})},J={args:{columns:[{...R[0],headerHidden:!0},R[1],{...R[2],bodyHidden:!0},R[3],R[4]]}},Y={args:{columns:[{...R[0],headerColSpan:2},R[1],R[2],R[3]]}},X={render:e=>{let t=R;return(0,I.jsx)(j,{...e,variant:F.COLLAPSE,columns:t,getFullRowContent:e=>e.age>30?(0,I.jsx)(`div`,{style:{padding:`8px`,margin:`8px`,backgroundColor:`violet`,borderRadius:`4px`},children:e.name},e.id):null})}},Z={render:e=>{let[t,n]=(0,xe.useState)(3),r=[...R.slice(0,4),{id:`actions`,label:`Actions`,render:e=>(0,I.jsx)(`button`,{onClick:t=>{t.stopPropagation(),n(t=>t===e.id?null:e.id)},children:t===e.id?`Fermer`:`Voir détails`})}];return(0,I.jsx)(j,{...e,columns:r,getFullRowContent:e=>e.id===t?(0,I.jsxs)(`div`,{style:{padding:16},children:[(0,I.jsx)(`h4`,{style:{margin:0},children:e.name}),(0,I.jsxs)(`p`,{style:{margin:`8px 0`},children:[`Email: `,(0,I.jsx)(`strong`,{children:e.email})]}),(0,I.jsxs)(`p`,{style:{margin:0},children:[`Score: `,(0,I.jsx)(`strong`,{children:e.nested.score}),` — Statut:`,` `,(0,I.jsx)(`strong`,{children:e.status})]})]}):null})}},Q={args:{},render:e=>(0,I.jsx)(j,{...e,data:[...L]})},$={args:{pagination:{currentPage:1,pageCount:3,onPageClick:e=>{alert(`Go to page ${e}`)}}},render:e=>(0,I.jsx)(j,{...e,data:[...L]})},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
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
}`,...$.parameters?.docs?.source}}},Ee=[`Basic`,`SeparateVariant`,`Loading`,`NoResults`,`NoDataState`,`SelectableUncontrolled`,`SelectableControlled`,`SelectableWithDisabledRows`,`StickyHeaderInScrollContainer`,`WithHiddenColumns`,`WithHeaderColSpan`,`WithFullRowAlwaysDisplayedDetail`,`WithFullRowDetail`,`SortingShowcase`,`WithPagination`]}))();export{z as Basic,V as Loading,U as NoDataState,H as NoResults,G as SelectableControlled,W as SelectableUncontrolled,K as SelectableWithDisabledRows,B as SeparateVariant,Q as SortingShowcase,q as StickyHeaderInScrollContainer,X as WithFullRowAlwaysDisplayedDetail,Z as WithFullRowDetail,Y as WithHeaderColSpan,J as WithHiddenColumns,$ as WithPagination,Ee as __namedExportsOrder,Te as default};