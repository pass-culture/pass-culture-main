import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-CPENYtuq.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./classnames-MYlGWOUq.js";import{i,n as a,t as o}from"./Button-DkSlhLyy.js";import{t as s}from"./SvgIcon-DK-x56iF.js";import{t as c}from"./full-down-BRWJ0t1l.js";import{t as l}from"./full-refresh-BTqeqoRf.js";import{t as u}from"./full-up-9DeG_flt.js";import{t as d}from"./stroke-search-DVpFKH3D.js";import{t as f}from"./Checkbox-r7Y5Xyjw.js";import{t as p}from"./Pagination-N_X2Tcv_.js";import{t as m}from"./Skeleton-Bl0AbbYk.js";var h=e(r(),1),g=e(t(),1),_=function(e){return e.ASC=`asc`,e.DESC=`desc`,e.NONE=`none`,e}({}),v=()=>{let[e,t]=(0,g.useState)(null),[n,r]=(0,g.useState)(_.NONE);return{currentSortingColumn:e,currentSortingMode:n,onColumnHeaderClick:(0,g.useCallback)(i=>e===i?n===_.ASC?(r(_.DESC),_.DESC):n===_.DESC?(r(_.NONE),_.NONE):(r(_.ASC),_.ASC):(t(i),r(_.ASC),_.ASC),[e,n])}},y={"sorting-icons":`_sorting-icons_cbxcb_1`,"both-icons":`_both-icons_cbxcb_17`},b=n(),x=({sortingMode:e,onClick:t,children:n})=>(0,b.jsxs)(`button`,{type:`button`,className:y[`sorting-icons`],onClick:t,children:[n,e===_.NONE?(0,b.jsxs)(`span`,{className:y[`both-icons`],children:[(0,b.jsx)(s,{src:u,alt:`Trier par ordre croissant`,width:`10`}),(0,b.jsx)(s,{src:c,alt:``,width:`10`})]}):e===_.DESC?(0,b.jsx)(s,{src:u,alt:`Ne plus trier`,width:`10`}):(0,b.jsx)(s,{src:c,alt:`Trier par ordre décroissant`,width:`10`})]});try{x.displayName=`SortColumn`,x.__docgenInfo={description:``,displayName:`SortColumn`,props:{sortingMode:{defaultValue:null,description:``,name:`sortingMode`,required:!0,type:{name:`enum`,value:[{value:`"asc"`},{value:`"desc"`},{value:`"none"`}]}},onClick:{defaultValue:null,description:``,name:`onClick`,required:!0,type:{name:`() => void`}}}}}catch{}var S={wrapper:`_wrapper_my972_1`,table:`_table_my972_5`,"table-pagination":`_table-pagination_my972_13`,"table-separate":`_table-separate_my972_17`,"table-separate-cell":`_table-separate-cell_my972_21`,"table-collapse":`_table-collapse_my972_38`,"table-collapse-cell":`_table-collapse-cell_my972_45`,"table-row":`_table-row_my972_50`,"table-header":`_table-header_my972_54`,"table-header-sticky":`_table-header-sticky_my972_60`,"table-header-th":`_table-header-th_my972_65`,"table-header-sortable-th":`_table-header-sortable-th_my972_78`,"table-select-all":`_table-select-all_my972_83`,"table-checkbox-label":`_table-checkbox-label_my972_89`,"visually-hidden":`_visually-hidden_my972_104`,"table-caption-no-display":`_table-caption-no-display_my972_116`,"table-fullrow-content":`_table-fullrow-content_my972_120`},C={"no-data":`_no-data_10bkz_1`,"no-data-icon":`_no-data-icon_10bkz_7`,"no-data-title":`_no-data-title_10bkz_11`,"no-data-subtitle":`_no-data-subtitle_10bkz_19`},w=({noData:{icon:e,title:t,subtitle:n}})=>(0,b.jsxs)(`div`,{className:C[`no-data`],children:[(0,b.jsx)(s,{src:e,alt:``,width:`100`,className:C[`no-data-icon`]}),(0,b.jsx)(`p`,{className:C[`no-data-title`],children:t}),(0,b.jsx)(`p`,{className:C[`no-data-subtitle`],children:n})]});try{w.displayName=`TableNoData`,w.__docgenInfo={description:``,displayName:`TableNoData`,props:{noData:{defaultValue:null,description:``,name:`noData`,required:!0,type:{name:`{ icon: string; title: string; subtitle: string; }`}}}}}catch{}var T={"search-no-results":`_search-no-results_yb0tv_1`,"search-no-results-icon":`_search-no-results-icon_yb0tv_4`,"search-no-results-title4":`_search-no-results-title4_yb0tv_8`,"search-no-results-text":`_search-no-results-text_yb0tv_14`},E=({colSpan:e=1,message:t=`Pas de résultat pour votre recherche`,subtitle:n=`Vous pouvez modifier votre recherche ou`,resetMessage:r=`Réinitialiser les filtres`,resetFilters:c})=>(0,b.jsx)(`tr`,{children:(0,b.jsx)(`td`,{colSpan:e,children:(0,b.jsxs)(`div`,{className:T[`search-no-results`],children:[(0,b.jsx)(s,{src:d,alt:`Illustration de recherche`,className:T[`search-no-results-icon`],width:`124`}),(0,b.jsx)(`p`,{className:T[`search-no-results-title4`],children:t}),(0,b.jsx)(`p`,{className:T[`search-no-results-text`],children:n}),(0,b.jsx)(o,{variant:i.SECONDARY,color:a.BRAND,icon:l,onClick:c,label:r})]})})});try{E.displayName=`TableNoFilterResult`,E.__docgenInfo={description:``,displayName:`TableNoFilterResult`,props:{colSpan:{defaultValue:{value:`1`},description:``,name:`colSpan`,required:!1,type:{name:`number`}},message:{defaultValue:{value:`Pas de résultat pour votre recherche`},description:``,name:`message`,required:!1,type:{name:`string`}},subtitle:{defaultValue:{value:`Vous pouvez modifier votre recherche ou`},description:``,name:`subtitle`,required:!1,type:{name:`string`}},resetMessage:{defaultValue:{value:`Réinitialiser les filtres`},description:``,name:`resetMessage`,required:!1,type:{name:`string`}},resetFilters:{defaultValue:null,description:``,name:`resetFilters`,required:!0,type:{name:`() => void`}}}}}catch{}var D=function(e){return e.COLLAPSE=`collapse`,e.SEPARATE=`separate`,e}({});function O(e,t){if(t)return typeof t==`function`?t(e):typeof t==`string`?t.split(`.`).reduce((e,t)=>e?.[t],e):e[t]}function k({title:e=`Tableau de données`,columns:t,data:n,allData:r,selectable:i=!1,selectedNumber:a,selectedIds:o,className:s,isLoading:c,isSticky:l,variant:u,noResult:d,noData:y,onSelectionChange:C,getFullRowContent:T,isRowSelectable:k,pagination:A}){let j=r??n,{currentSortingColumn:M,currentSortingMode:N,onColumnHeaderClick:P}=v(),[F,I]=(0,g.useState)(new Set),L=o!==void 0,R=L?o:F,z=e=>{L||I(e),C?.(j.filter(t=>e.has(t.id)))};function B(e){P(e)}let V=(0,g.useMemo)(()=>k?j.filter(k):j,[j,k]),H=()=>{R.size===V.length?z(new Set):z(new Set(V.map(e=>e.id)))},U=e=>{let t=new Set(R);t.has(e.id)?t.delete(e.id):t.add(e.id),z(t)},W=(0,g.useMemo)(()=>{if(!M)return n;let e=t.find(e=>e.id===M);return e?[...j].sort((t,n)=>{let r=O(t,e.ordererField),i=O(n,e.ordererField);return r===i?0:r<i?N===_.ASC?-1:1:N===_.ASC?1:-1}):n},[n,M,N,t,j]),G=R.size===V.length&&V.length>0,K=R.size>0&&R.size<V.length,q=G?`Tout désélectionner`:`Tout sélectionner`;return y.hasNoData?(0,b.jsx)(w,{noData:y.message}):(0,b.jsxs)(`div`,{className:(0,h.default)(S.wrapper,s),children:[i&&(0,b.jsxs)(`div`,{className:S[`table-select-all`],children:[(0,b.jsx)(f,{label:q,checked:G,indeterminate:K,onChange:H}),(0,b.jsx)(`span`,{className:S[`visually-hidden`],children:`Sélectionner toutes les lignes`}),(0,b.jsx)(`div`,{children:a})]}),(0,b.jsxs)(`table`,{className:(0,h.default)(S.table,{[S[`table-separate`]]:u===D.SEPARATE,[S[`table-collapse`]]:u===D.COLLAPSE}),children:[(0,b.jsx)(`caption`,{className:S[`table-caption-no-display`],children:e}),(0,b.jsx)(`thead`,{children:(0,b.jsxs)(`tr`,{className:(0,h.default)(S[`table-header`],{[S[`table-header-sticky`]]:l}),children:[i&&(0,b.jsx)(`th`,{scope:`col`,className:S[`table-header-th`],children:(0,b.jsx)(`span`,{className:S[`visually-hidden`],children:`Sélectionner`})}),t.map(e=>{if(e.headerHidden)return null;let t=e.header??e.label??``;return(0,b.jsx)(`th`,{scope:`col`,id:e.id,colSpan:e.headerColSpan||1,className:(0,h.default)(S[`table-header-th`],{[S[`table-header-sortable-th`]]:e.sortable}),children:e.sortable?(0,b.jsx)(x,{onClick:()=>B(e.id),sortingMode:M===e.id?N:_.NONE,children:t}):t},`col-${e.id}`)})]})}),(0,b.jsxs)(`tbody`,{children:[c&&Array.from({length:8}).map((e,n)=>(0,b.jsx)(`tr`,{children:(0,b.jsx)(`td`,{colSpan:t.length+1,children:(0,b.jsx)(m,{height:`7rem`,width:`100%`})})},`loading-row-${t.length}-${n}`)),!W.length&&(0,b.jsx)(E,{colSpan:t.length+(i?1:0),message:d.message,subtitle:d.subtitle,resetMessage:d.resetMessage,resetFilters:d.onFilterReset}),W.map(e=>{let n=R.has(e.id),r=T?.(e);return(0,b.jsxs)(g.Fragment,{children:[(0,b.jsxs)(`tr`,{"data-testid":`table-row`,className:(0,h.default)({[S[`table-row`]]:!r}),children:[i&&(0,b.jsxs)(`td`,{className:(0,h.default)({[S[`table-separate-cell`]]:u===D.SEPARATE,[S[`table-collapse-cell`]]:u===D.COLLAPSE}),children:[(0,b.jsx)(f,{label:e.name??`ligne ${e.id}`,checked:n,onChange:()=>U(e),className:S[`table-checkbox-label`],disabled:k?!k(e):!1}),(0,b.jsxs)(`span`,{className:S[`visually-hidden`],children:[`Selectionner la ligne `,e.name||e.id]})]}),t.map(t=>{if(t.bodyHidden)return null;let n=t.render?t.render(e):O(e,t.ordererField);return(0,b.jsx)(`td`,{className:(0,h.default)({[S[`table-separate-cell`]]:u===D.SEPARATE,[S[`table-collapse-cell`]]:u===D.COLLAPSE}),"data-label":t.label,children:n},`col-${t.id}-${t.label}`)})]}),r&&(0,b.jsx)(`tr`,{className:(0,h.default)(S[`table-row`]),children:(0,b.jsx)(`td`,{colSpan:t.length+(i?1:0),children:(0,b.jsx)(`div`,{className:S[`table-fullrow-content`],children:r})})})]},e.id)})]})]}),A&&(0,b.jsx)(`div`,{className:S[`table-pagination`],children:(0,b.jsx)(p,{currentPage:A.currentPage,pageCount:A.pageCount,onPageClick:A.onPageClick})})]})}try{k.displayName=`Table`,k.__docgenInfo={description:``,displayName:`Table`,props:{title:{defaultValue:{value:`Tableau de données`},description:``,name:`title`,required:!1,type:{name:`string`}},columns:{defaultValue:null,description:``,name:`columns`,required:!0,type:{name:`Column<T>[]`}},data:{defaultValue:null,description:``,name:`data`,required:!0,type:{name:`T[]`}},allData:{defaultValue:null,description:``,name:`allData`,required:!1,type:{name:`T[]`}},selectable:{defaultValue:{value:`false`},description:``,name:`selectable`,required:!1,type:{name:`boolean`}},className:{defaultValue:null,description:``,name:`className`,required:!1,type:{name:`string`}},isLoading:{defaultValue:null,description:``,name:`isLoading`,required:!0,type:{name:`boolean`}},isSticky:{defaultValue:null,description:``,name:`isSticky`,required:!1,type:{name:`boolean`}},variant:{defaultValue:null,description:``,name:`variant`,required:!0,type:{name:`enum`,value:[{value:`"collapse"`},{value:`"separate"`}]}},selectedNumber:{defaultValue:null,description:``,name:`selectedNumber`,required:!1,type:{name:`string`}},selectedIds:{defaultValue:null,description:``,name:`selectedIds`,required:!1,type:{name:`Set<string | number>`}},onSelectionChange:{defaultValue:null,description:``,name:`onSelectionChange`,required:!1,type:{name:`((rows: T[]) => void)`}},getFullRowContent:{defaultValue:null,description:``,name:`getFullRowContent`,required:!1,type:{name:`((row: T) => ReactNode)`}},isRowSelectable:{defaultValue:null,description:``,name:`isRowSelectable`,required:!1,type:{name:`((row: T) => boolean)`}},noResult:{defaultValue:null,description:``,name:`noResult`,required:!0,type:{name:`NoResultProps`}},noData:{defaultValue:null,description:``,name:`noData`,required:!0,type:{name:`EmptyStateProps`}},pagination:{defaultValue:null,description:``,name:`pagination`,required:!1,type:{name:`PaginationProps`}}}}}catch{}var A=[{id:1,name:`Alice`,email:`alice@example.com`,age:27,status:`active`,createdAt:`2024-01-05T10:00:00Z`,nested:{score:77}},{id:2,name:`Bob`,email:`bob@example.com`,age:34,status:`inactive`,createdAt:`2024-02-01T08:30:00Z`,nested:{score:65}},{id:3,name:`Chloe`,email:`chloe@example.com`,age:22,status:`active`,createdAt:`2024-03-12T12:45:00Z`,nested:{score:92}},{id:4,name:`Diego`,email:`diego@example.com`,age:41,status:`active`,createdAt:`2024-04-20T15:10:00Z`,nested:{score:58}},{id:5,name:`Elise`,email:`elise@example.com`,age:29,status:`inactive`,createdAt:`2024-05-11T09:00:00Z`,nested:{score:80}},{id:6,name:`Fares`,email:`fares@example.com`,age:37,status:`active`,createdAt:`2024-06-02T11:15:00Z`,nested:{score:71}},{id:7,name:`Gina`,email:`gina@example.com`,age:31,status:`active`,createdAt:`2024-06-18T16:20:00Z`,nested:{score:88}},{id:8,name:`Hugo`,email:`hugo@example.com`,age:25,status:`inactive`,createdAt:`2024-07-08T07:05:00Z`,nested:{score:54}}],j=e=>new Date(e).toLocaleDateString(`fr-FR`,{year:`numeric`,month:`short`,day:`2-digit`}),M=[{id:`name`,label:`Nom`,sortable:!0,ordererField:e=>e.name,render:e=>(0,b.jsx)(`strong`,{children:e.name})},{id:`age`,label:`Âge`,sortable:!0,ordererField:e=>e.age,render:e=>e.age},{id:`created`,label:`Créé le`,sortable:!0,ordererField:e=>new Date(e.createdAt).getTime(),render:e=>j(e.createdAt)},{id:`status`,label:`Statut`,render:e=>(0,b.jsx)(`span`,{"aria-label":`status-${e.id}`,children:e.status===`active`?`Actif`:`Inactif`})},{id:`score`,label:`Score`,sortable:!0,ordererField:e=>e.nested.score,render:e=>e.nested.score}],N={hasNoData:!1,message:{icon:`📄`,title:`Aucune donnée`,subtitle:`Commencez par créer un élément pour remplir ce tableau.`}},P={message:`Aucun résultat pour ces filtres.`,resetMessage:`Réinitialiser les filtres`,onFilterReset:()=>alert(`reset filters`)},F={title:`Design System/Table`,component:k,args:{title:`Tableau de données`,columns:M,data:A,selectable:!1,isLoading:!1,isSticky:!1,variant:D.COLLAPSE,noData:N,noResult:P},argTypes:{variant:{control:`inline-radio`,options:[D.SEPARATE,D.COLLAPSE]},isLoading:{control:`boolean`},selectable:{control:`boolean`},isSticky:{control:`boolean`}},parameters:{layout:`padded`}},I={render:e=>(0,b.jsx)(k,{...e})},L={args:{variant:D.SEPARATE}},R={args:{isLoading:!0}},z={args:{data:[],noData:{...N,hasNoData:!1},noResult:{...P,onFilterReset:()=>alert(`Réinitialiser les filtres`)}}},B={args:{data:[],noData:{hasNoData:!0,message:{icon:`📭`,title:`Rien à afficher`,subtitle:`Aucun élément n’a encore été créé.`}}}},V={args:{selectable:!0,selectedNumber:`0 sélectionnée`}},H={render:e=>{let[t,n]=(0,g.useState)(new Set([2,4])),r=t.size;return(0,b.jsx)(k,{...e,selectable:!0,selectedIds:t,selectedNumber:`${r} sélectionnée${r>1?`s`:``}`,onSelectionChange:e=>{n(new Set(e.map(e=>e.id)))}})}},U={render:e=>(0,b.jsx)(k,{...e,selectable:!0,isRowSelectable:e=>e.status===`active`,selectedNumber:`—`})},W={args:{isSticky:!0},render:e=>(0,b.jsx)(`div`,{style:{height:260,overflow:`auto`,border:`1px solid #eee`},children:(0,b.jsx)(k,{...e,data:[...A,...A]})})},G={args:{columns:[{...M[0],headerHidden:!0},M[1],{...M[2],bodyHidden:!0},M[3],M[4]]}},K={args:{columns:[{...M[0],headerColSpan:2},M[1],M[2],M[3]]}},q={render:e=>{let t=M;return(0,b.jsx)(k,{...e,variant:D.COLLAPSE,columns:t,getFullRowContent:e=>e.age>30?(0,b.jsx)(`div`,{style:{padding:`8px`,margin:`8px`,backgroundColor:`violet`,borderRadius:`4px`},children:e.name},e.id):null})}},J={render:e=>{let[t,n]=(0,g.useState)(3),r=[...M.slice(0,4),{id:`actions`,label:`Actions`,render:e=>(0,b.jsx)(`button`,{onClick:t=>{t.stopPropagation(),n(t=>t===e.id?null:e.id)},children:t===e.id?`Fermer`:`Voir détails`})}];return(0,b.jsx)(k,{...e,columns:r,getFullRowContent:e=>e.id===t?(0,b.jsxs)(`div`,{style:{padding:16},children:[(0,b.jsx)(`h4`,{style:{margin:0},children:e.name}),(0,b.jsxs)(`p`,{style:{margin:`8px 0`},children:[`Email: `,(0,b.jsx)(`strong`,{children:e.email})]}),(0,b.jsxs)(`p`,{style:{margin:0},children:[`Score: `,(0,b.jsx)(`strong`,{children:e.nested.score}),` — Statut:`,` `,(0,b.jsx)(`strong`,{children:e.status})]})]}):null})}},Y={args:{},render:e=>(0,b.jsx)(k,{...e,data:[...A]})},X={args:{pagination:{currentPage:1,pageCount:3,onPageClick:e=>{alert(`Go to page ${e}`)}}},render:e=>(0,b.jsx)(k,{...e,data:[...A]})};I.parameters={...I.parameters,docs:{...I.parameters?.docs,source:{originalSource:`{
  render: args => <Table {...args} />
}`,...I.parameters?.docs?.source}}},L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
  args: {
    variant: TableVariant.SEPARATE
  }
}`,...L.parameters?.docs?.source}}},R.parameters={...R.parameters,docs:{...R.parameters?.docs,source:{originalSource:`{
  args: {
    isLoading: true
  }
}`,...R.parameters?.docs?.source}}},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
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
}`,...z.parameters?.docs?.source}}},B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
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
}`,...B.parameters?.docs?.source}}},V.parameters={...V.parameters,docs:{...V.parameters?.docs,source:{originalSource:`{
  args: {
    selectable: true,
    selectedNumber: '0 sélectionnée'
  }
}`,...V.parameters?.docs?.source}}},H.parameters={...H.parameters,docs:{...H.parameters?.docs,source:{originalSource:`{
  render: args => {
    const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set([2, 4]));
    const selectedCount = selectedIds.size;
    return <Table {...args} selectable selectedIds={selectedIds} selectedNumber={\`\${selectedCount} sélectionnée\${selectedCount > 1 ? 's' : ''}\`} onSelectionChange={rows => {
      setSelectedIds(new Set(rows.map(r => r.id)));
    }} />;
  }
}`,...H.parameters?.docs?.source}}},U.parameters={...U.parameters,docs:{...U.parameters?.docs,source:{originalSource:`{
  render: args => <Table {...args} selectable isRowSelectable={row => row.status === 'active'} // disable inactive rows
  selectedNumber="—" />
}`,...U.parameters?.docs?.source}}},W.parameters={...W.parameters,docs:{...W.parameters?.docs,source:{originalSource:`{
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
}`,...W.parameters?.docs?.source}}},G.parameters={...G.parameters,docs:{...G.parameters?.docs,source:{originalSource:`{
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
}`,...G.parameters?.docs?.source}}},K.parameters={...K.parameters,docs:{...K.parameters?.docs,source:{originalSource:`{
  args: {
    columns: [{
      ...baseColumns[0],
      headerColSpan: 2
    },
    // spans two header columns
    baseColumns[1], baseColumns[2], baseColumns[3]]
  }
}`,...K.parameters?.docs?.source}}},q.parameters={...q.parameters,docs:{...q.parameters?.docs,source:{originalSource:`{
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
}`,...q.parameters?.docs?.source},description:{story:`Full-row (colspan) detail row
Your Table renders a second <tr> with a single <td colSpan=...>
whenever getFullRowContent(row) returns a ReactNode.`,...q.parameters?.docs?.description}}},J.parameters={...J.parameters,docs:{...J.parameters?.docs,source:{originalSource:`{
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
}`,...J.parameters?.docs?.source},description:{story:`Full-row (colspan) detail row
Your Table renders a second <tr> with a single <td colSpan=...>
whenever getFullRowContent(row) returns a ReactNode.`,...J.parameters?.docs?.description}}},Y.parameters={...Y.parameters,docs:{...Y.parameters?.docs,source:{originalSource:`{
  args: {
    // keep default columns (sortable on name, age, created, score)
  },
  render: args => <Table {...args} data={[...sampleData]} />
}`,...Y.parameters?.docs?.source}}},X.parameters={...X.parameters,docs:{...X.parameters?.docs,source:{originalSource:`{
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
}`,...X.parameters?.docs?.source}}};var Z=[`Basic`,`SeparateVariant`,`Loading`,`NoResults`,`NoDataState`,`SelectableUncontrolled`,`SelectableControlled`,`SelectableWithDisabledRows`,`StickyHeaderInScrollContainer`,`WithHiddenColumns`,`WithHeaderColSpan`,`WithFullRowAlwaysDisplayedDetail`,`WithFullRowDetail`,`SortingShowcase`,`WithPagination`];export{I as Basic,R as Loading,B as NoDataState,z as NoResults,H as SelectableControlled,V as SelectableUncontrolled,U as SelectableWithDisabledRows,L as SeparateVariant,Y as SortingShowcase,W as StickyHeaderInScrollContainer,q as WithFullRowAlwaysDisplayedDetail,J as WithFullRowDetail,K as WithHeaderColSpan,G as WithHiddenColumns,X as WithPagination,Z as __namedExportsOrder,F as default};