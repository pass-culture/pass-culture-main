import{j as a}from"./jsx-runtime-u17CrQMm.js";import{r as g,R as ve}from"./iframe-BK6j2GHw.js";import{c as p}from"./index-BNMUVP67.js";import{C as re}from"./Checkbox-Cydg--FO.js";import{P as Ne}from"./Pagination-DvziO01r.js";import{S as je}from"./Skeleton-QXLP77M_.js";import{f as ne}from"./full-down-Cmbtr9nI.js";import{f as le}from"./full-up-D6TPt2ju.js";import{S}from"./SvgIcon-DuZPzNRk.js";import{B as we,b as Re,a as De}from"./Button-HvO-BEv3.js";import{f as Te}from"./full-refresh-BZh6W0mB.js";import{s as ke}from"./stroke-search-Bph5aoaJ.js";import"./preload-helper-PPVm8Dsz.js";import"./Asset-bhMcET6u.js";import"./Tag-KuLR-njF.js";import"./full-thumb-up-Bb4kpRpM.js";import"./useMediaQuery-7NrhB8uJ.js";import"./full-left-vjwAEs82.js";import"./full-right-Dd3YsyCq.js";import"./full-three-dots-6wSZh7oi.js";import"./full-link-CYVo23DH.js";import"./Tooltip-CFSGbwGf.js";import"./stroke-pass-CALgybTM.js";import"./chunk-JZWAC4HX-BsXAfhWM.js";var _=(e=>(e.ASC="asc",e.DESC="desc",e.NONE="none",e))(_||{});const qe=()=>{const[e,s]=g.useState(null),[n,i]=g.useState("none"),l=g.useCallback(m=>e!==m?(s(m),i("asc"),"asc"):n==="asc"?(i("desc"),"desc"):n==="desc"?(i("none"),"none"):(i("asc"),"asc"),[e,n]);return{currentSortingColumn:e,currentSortingMode:n,onColumnHeaderClick:l}},N={"sorting-icons":"_sorting-icons_cbxcb_1","both-icons":"_both-icons_cbxcb_17"},K=({sortingMode:e,onClick:s,children:n})=>a.jsxs("button",{type:"button",className:N["sorting-icons"],onClick:s,children:[n,e!==_.NONE?e===_.DESC?a.jsx(S,{className:N["sort-icon"],src:le,alt:"Ne plus trier",width:"10"}):a.jsx(S,{className:N["sort-icon"],src:ne,alt:"Trier par ordre décroissant",width:"10"}):a.jsxs("span",{className:p(N["sort-icon"],N["both-icons"]),children:[a.jsx(S,{src:le,alt:"Trier par ordre croissant",width:"10"}),a.jsx(S,{src:ne,alt:"",width:"10"})]})]});try{K.displayName="SortColumn",K.__docgenInfo={description:"",displayName:"SortColumn",props:{sortingMode:{defaultValue:null,description:"",name:"sortingMode",required:!0,type:{name:"enum",value:[{value:'"asc"'},{value:'"desc"'},{value:'"none"'}]}},onClick:{defaultValue:null,description:"",name:"onClick",required:!0,type:{name:"() => void"}}}}}catch{}const Ae="_wrapper_1p1qv_1",Ve="_table_1p1qv_5",r={wrapper:Ae,table:Ve,"table-pagination":"_table-pagination_1p1qv_13","table-separate":"_table-separate_1p1qv_17","table-separate-cell":"_table-separate-cell_1p1qv_21","table-collapse":"_table-collapse_1p1qv_38","table-collapse-cell":"_table-collapse-cell_1p1qv_45","table-row":"_table-row_1p1qv_50","table-header":"_table-header_1p1qv_54","table-header-sticky":"_table-header-sticky_1p1qv_60","table-header-th":"_table-header-th_1p1qv_65","table-header-sortable-th":"_table-header-sortable-th_1p1qv_78","table-select-all":"_table-select-all_1p1qv_83","table-checkbox-label":"_table-checkbox-label_1p1qv_89","visually-hidden":"_visually-hidden_1p1qv_104","table-caption-no-display":"_table-caption-no-display_1p1qv_116","table-fullrow-content":"_table-fullrow-content_1p1qv_120"},I={"no-data":"_no-data_10bkz_1","no-data-icon":"_no-data-icon_10bkz_7","no-data-title":"_no-data-title_10bkz_11","no-data-subtitle":"_no-data-subtitle_10bkz_19"},Q=({noData:{icon:e,title:s,subtitle:n}})=>a.jsxs("div",{className:I["no-data"],children:[a.jsx(S,{src:e,alt:"",width:"100",className:I["no-data-icon"]}),a.jsx("p",{className:I["no-data-title"],children:s}),a.jsx("p",{className:I["no-data-subtitle"],children:n})]});try{Q.displayName="TableNoData",Q.__docgenInfo={description:"",displayName:"TableNoData",props:{noData:{defaultValue:null,description:"",name:"noData",required:!0,type:{name:"{ icon: string; title: string; subtitle: string; }"}}}}}catch{}const E={"search-no-results":"_search-no-results_yb0tv_1","search-no-results-icon":"_search-no-results-icon_yb0tv_4","search-no-results-title4":"_search-no-results-title4_yb0tv_8","search-no-results-text":"_search-no-results-text_yb0tv_14"},X=({colSpan:e=1,message:s="Pas de résultat pour votre recherche",subtitle:n="Vous pouvez modifier votre recherche ou",resetMessage:i="Réinitialiser les filtres",resetFilters:l})=>a.jsx("tr",{children:a.jsx("td",{colSpan:e,children:a.jsxs("div",{className:E["search-no-results"],children:[a.jsx(S,{src:ke,alt:"Illustration de recherche",className:E["search-no-results-icon"],width:"124"}),a.jsx("p",{className:E["search-no-results-title4"],children:s}),a.jsx("p",{className:E["search-no-results-text"],children:n}),a.jsx(we,{variant:De.SECONDARY,color:Re.BRAND,icon:Te,onClick:l,label:i})]})})});try{X.displayName="TableNoFilterResult",X.__docgenInfo={description:"",displayName:"TableNoFilterResult",props:{colSpan:{defaultValue:{value:"1"},description:"",name:"colSpan",required:!1,type:{name:"number"}},message:{defaultValue:{value:"Pas de résultat pour votre recherche"},description:"",name:"message",required:!1,type:{name:"string"}},subtitle:{defaultValue:{value:"Vous pouvez modifier votre recherche ou"},description:"",name:"subtitle",required:!1,type:{name:"string"}},resetMessage:{defaultValue:{value:"Réinitialiser les filtres"},description:"",name:"resetMessage",required:!1,type:{name:"string"}},resetFilters:{defaultValue:null,description:"",name:"resetFilters",required:!0,type:{name:"() => void"}}}}}catch{}var x=(e=>(e.COLLAPSE="collapse",e.SEPARATE="separate",e))(x||{});function J(e,s){if(s)return typeof s=="function"?s(e):typeof s=="string"?s.split(".").reduce((n,i)=>n?.[i],e):e[s]}function d({title:e="Tableau de données",columns:s,data:n,allData:i,selectable:l=!1,selectedNumber:m,selectedIds:D,className:ce,isLoading:de,isSticky:ue,variant:b,noResult:T,noData:ee,onSelectionChange:pe,getFullRowContent:me,isRowSelectable:y,pagination:k}){const h=i??n,{currentSortingColumn:q,currentSortingMode:A,onColumnHeaderClick:ge}=qe(),[be,he]=g.useState(new Set),ae=D!==void 0,f=ae?D:be,Y=t=>{ae||he(t),pe?.(h.filter(o=>t.has(o.id)))};function fe(t){ge(t)}const C=g.useMemo(()=>y?h.filter(y):h,[h,y]),Se=()=>{f.size===C.length?Y(new Set):Y(new Set(C.map(t=>t.id)))},_e=t=>{const o=new Set(f);o.has(t.id)?o.delete(t.id):o.add(t.id),Y(o)},te=g.useMemo(()=>{if(!q)return n;const t=s.find(o=>o.id===q);return t?[...h].sort((o,v)=>{const u=J(o,t.ordererField),V=J(v,t.ordererField);return u===V?0:u<V?A===_.ASC?-1:1:A===_.ASC?1:-1}):n},[n,q,A,s,h]),se=f.size===C.length&&C.length>0,xe=f.size>0&&f.size<C.length,ye=se?"Tout désélectionner":"Tout sélectionner";return ee.hasNoData?a.jsx(Q,{noData:ee.message}):a.jsxs("div",{className:p(r.wrapper,ce),children:[l&&a.jsxs("div",{className:r["table-select-all"],children:[a.jsx(re,{label:ye,checked:se,indeterminate:xe,onChange:Se}),a.jsx("span",{className:r["visually-hidden"],children:"Sélectionner toutes les lignes"}),a.jsx("div",{children:m})]}),a.jsxs("table",{className:p(r.table,{[r["table-separate"]]:b==="separate",[r["table-collapse"]]:b==="collapse"}),children:[a.jsx("caption",{className:r["table-caption-no-display"],children:e}),a.jsx("thead",{children:a.jsxs("tr",{className:p(r["table-header"],{[r["table-header-sticky"]]:ue}),children:[l&&a.jsx("th",{scope:"col",className:r["table-header-th"],children:a.jsx("span",{className:r["visually-hidden"],children:"Sélectionner"})}),s.map(t=>{if(t.headerHidden)return null;const o=t.header??t.label??"";return a.jsx("th",{scope:"col",id:t.id,colSpan:t.headerColSpan||1,className:p(r.columnWidth,r["table-header-th"],{[r["table-header-sortable-th"]]:t.sortable}),children:t.sortable?a.jsx(K,{onClick:()=>fe(t.id),sortingMode:q===t.id?A:_.NONE,children:o}):o},`col-${t.id}`)})]})}),a.jsxs("tbody",{children:[de&&Array.from({length:8}).map((t,o)=>a.jsx("tr",{children:a.jsx("td",{colSpan:s.length+1,children:a.jsx(je,{height:"7rem",width:"100%"})})},`loading-row-${s.length}-${o}`)),!te.length&&a.jsx(X,{colSpan:s.length+(l?1:0),message:T.message,subtitle:T.subtitle,resetMessage:T.resetMessage,resetFilters:T.onFilterReset}),te.map(t=>{const o=f.has(t.id),v=me?.(t);return a.jsxs(ve.Fragment,{children:[a.jsxs("tr",{"data-testid":"table-row",className:p({[r["table-row"]]:!v,[r.selected]:o}),children:[l&&a.jsxs("td",{className:p(r["table-checkbox-cell"],{[r["table-separate-cell"]]:b==="separate",[r["table-collapse-cell"]]:b==="collapse"}),children:[a.jsx(re,{label:t.name??`ligne ${t.id}`,checked:o,onChange:()=>_e(t),className:r["table-checkbox-label"],disabled:y?!y(t):!1}),a.jsxs("span",{className:r["visually-hidden"],children:["Selectionner la ligne ",t.name||t.id]})]}),s.map((u,V)=>{if(u.bodyHidden)return null;const Ce=u.render?u.render(t):J(t,u.ordererField);return a.jsx("td",{className:p({[r["table-separate-cell"]]:b==="separate",[r["table-collapse-cell"]]:b==="collapse"}),"data-label":u.label,children:Ce},`col-${u.id}-${V}`)})]}),v&&a.jsx("tr",{className:p(r["table-row"]),children:a.jsx("td",{colSpan:s.length+(l?1:0),children:a.jsx("div",{className:r["table-fullrow-content"],children:v})})})]},t.id)})]})]}),k&&a.jsx("div",{className:r["table-pagination"],children:a.jsx(Ne,{currentPage:k.currentPage,pageCount:k.pageCount,onPageClick:k.onPageClick})})]})}try{d.displayName="Table",d.__docgenInfo={description:"",displayName:"Table",props:{title:{defaultValue:{value:"Tableau de données"},description:"",name:"title",required:!1,type:{name:"string"}},columns:{defaultValue:null,description:"",name:"columns",required:!0,type:{name:"Column<T>[]"}},data:{defaultValue:null,description:"",name:"data",required:!0,type:{name:"T[]"}},allData:{defaultValue:null,description:"",name:"allData",required:!1,type:{name:"T[]"}},selectable:{defaultValue:{value:"false"},description:"",name:"selectable",required:!1,type:{name:"boolean"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},isLoading:{defaultValue:null,description:"",name:"isLoading",required:!0,type:{name:"boolean"}},isSticky:{defaultValue:null,description:"",name:"isSticky",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!0,type:{name:"enum",value:[{value:'"collapse"'},{value:'"separate"'}]}},selectedNumber:{defaultValue:null,description:"",name:"selectedNumber",required:!1,type:{name:"string"}},selectedIds:{defaultValue:null,description:"",name:"selectedIds",required:!1,type:{name:"Set<string | number>"}},onSelectionChange:{defaultValue:null,description:"",name:"onSelectionChange",required:!1,type:{name:"((rows: T[]) => void)"}},getFullRowContent:{defaultValue:null,description:"",name:"getFullRowContent",required:!1,type:{name:"((row: T) => ReactNode)"}},isRowSelectable:{defaultValue:null,description:"",name:"isRowSelectable",required:!1,type:{name:"((row: T) => boolean)"}},noResult:{defaultValue:null,description:"",name:"noResult",required:!0,type:{name:"NoResultProps"}},noData:{defaultValue:null,description:"",name:"noData",required:!0,type:{name:"EmptyStateProps"}},pagination:{defaultValue:null,description:"",name:"pagination",required:!1,type:{name:"PaginationProps"}}}}}catch{}const R=[{id:1,name:"Alice",email:"alice@example.com",age:27,status:"active",createdAt:"2024-01-05T10:00:00Z",nested:{score:77}},{id:2,name:"Bob",email:"bob@example.com",age:34,status:"inactive",createdAt:"2024-02-01T08:30:00Z",nested:{score:65}},{id:3,name:"Chloe",email:"chloe@example.com",age:22,status:"active",createdAt:"2024-03-12T12:45:00Z",nested:{score:92}},{id:4,name:"Diego",email:"diego@example.com",age:41,status:"active",createdAt:"2024-04-20T15:10:00Z",nested:{score:58}},{id:5,name:"Elise",email:"elise@example.com",age:29,status:"inactive",createdAt:"2024-05-11T09:00:00Z",nested:{score:80}},{id:6,name:"Fares",email:"fares@example.com",age:37,status:"active",createdAt:"2024-06-02T11:15:00Z",nested:{score:71}},{id:7,name:"Gina",email:"gina@example.com",age:31,status:"active",createdAt:"2024-06-18T16:20:00Z",nested:{score:88}},{id:8,name:"Hugo",email:"hugo@example.com",age:25,status:"inactive",createdAt:"2024-07-08T07:05:00Z",nested:{score:54}}],Ie=e=>new Date(e).toLocaleDateString("fr-FR",{year:"numeric",month:"short",day:"2-digit"}),c=[{id:"name",label:"Nom",sortable:!0,ordererField:e=>e.name,render:e=>a.jsx("strong",{children:e.name})},{id:"age",label:"Âge",sortable:!0,ordererField:e=>e.age,render:e=>e.age},{id:"created",label:"Créé le",sortable:!0,ordererField:e=>new Date(e.createdAt).getTime(),render:e=>Ie(e.createdAt)},{id:"status",label:"Statut",render:e=>a.jsx("span",{"aria-label":`status-${e.id}`,children:e.status==="active"?"Actif":"Inactif"})},{id:"score",label:"Score",sortable:!0,ordererField:e=>e.nested.score,render:e=>e.nested.score}],oe={hasNoData:!1,message:{icon:"📄",title:"Aucune donnée",subtitle:"Commencez par créer un élément pour remplir ce tableau."}},ie={message:"Aucun résultat pour ces filtres.",resetMessage:"Réinitialiser les filtres",onFilterReset:()=>alert("reset filters")},na={title:"Design System/Table",component:d,args:{title:"Tableau de données",columns:c,data:R,selectable:!1,isLoading:!1,isSticky:!1,variant:x.COLLAPSE,noData:oe,noResult:ie},argTypes:{variant:{control:"inline-radio",options:[x.SEPARATE,x.COLLAPSE]},isLoading:{control:"boolean"},selectable:{control:"boolean"},isSticky:{control:"boolean"}},parameters:{layout:"padded"}},F={render:e=>a.jsx(d,{...e})},P={args:{variant:x.SEPARATE}},L={args:{isLoading:!0}},$={args:{data:[],noData:{...oe,hasNoData:!1},noResult:{...ie,onFilterReset:()=>alert("Réinitialiser les filtres")}}},H={args:{data:[],noData:{hasNoData:!0,message:{icon:"📭",title:"Rien à afficher",subtitle:"Aucun élément n’a encore été créé."}}}},z={args:{selectable:!0,selectedNumber:"0 sélectionnée"}},W={render:e=>{const[s,n]=g.useState(new Set([2,4])),i=s.size;return a.jsx(d,{...e,selectable:!0,selectedIds:s,selectedNumber:`${i} sélectionnée${i>1?"s":""}`,onSelectionChange:l=>{n(new Set(l.map(m=>m.id)))}})}},M={render:e=>a.jsx(d,{...e,selectable:!0,isRowSelectable:s=>s.status==="active",selectedNumber:"—"})},O={args:{isSticky:!0},render:e=>a.jsx("div",{style:{height:260,overflow:"auto",border:"1px solid #eee"},children:a.jsx(d,{...e,data:[...R,...R]})})},B={args:{columns:[{...c[0],headerHidden:!0},c[1],{...c[2],bodyHidden:!0},c[3],c[4]]}},Z={args:{columns:[{...c[0],headerColSpan:2},c[1],c[2],c[3]]}},j={render:e=>{const s=c;return a.jsx(d,{...e,variant:x.COLLAPSE,columns:s,getFullRowContent:n=>n.age>30?a.jsx("div",{style:{padding:"8px",margin:"8px",backgroundColor:"violet",borderRadius:"4px"},children:n.name},n.id):null})}},w={render:e=>{const[s,n]=g.useState(3),i=[...c.slice(0,4),{id:"actions",label:"Actions",render:l=>a.jsx("button",{onClick:m=>{m.stopPropagation(),n(D=>D===l.id?null:l.id)},children:s===l.id?"Fermer":"Voir détails"})}];return a.jsx(d,{...e,columns:i,getFullRowContent:l=>l.id===s?a.jsxs("div",{style:{padding:16},children:[a.jsx("h4",{style:{margin:0},children:l.name}),a.jsxs("p",{style:{margin:"8px 0"},children:["Email: ",a.jsx("strong",{children:l.email})]}),a.jsxs("p",{style:{margin:0},children:["Score: ",a.jsx("strong",{children:l.nested.score})," — Statut:"," ",a.jsx("strong",{children:l.status})]})]}):null})}},U={args:{},render:e=>a.jsx(d,{...e,data:[...R]})},G={args:{pagination:{currentPage:1,pageCount:3,onPageClick:e=>{alert(`Go to page ${e}`)}}},render:e=>a.jsx(d,{...e,data:[...R]})};F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  render: args => <Table {...args} />
}`,...F.parameters?.docs?.source}}};P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    variant: TableVariant.SEPARATE
  }
}`,...P.parameters?.docs?.source}}};L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
  args: {
    isLoading: true
  }
}`,...L.parameters?.docs?.source}}};$.parameters={...$.parameters,docs:{...$.parameters?.docs,source:{originalSource:`{
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
}`,...$.parameters?.docs?.source}}};H.parameters={...H.parameters,docs:{...H.parameters?.docs,source:{originalSource:`{
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
}`,...H.parameters?.docs?.source}}};z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
  args: {
    selectable: true,
    selectedNumber: '0 sélectionnée'
  }
}`,...z.parameters?.docs?.source}}};W.parameters={...W.parameters,docs:{...W.parameters?.docs,source:{originalSource:`{
  render: args => {
    const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set([2, 4]));
    const selectedCount = selectedIds.size;
    return <Table {...args} selectable selectedIds={selectedIds} selectedNumber={\`\${selectedCount} sélectionnée\${selectedCount > 1 ? 's' : ''}\`} onSelectionChange={rows => {
      setSelectedIds(new Set(rows.map(r => r.id)));
    }} />;
  }
}`,...W.parameters?.docs?.source}}};M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
  render: args => <Table {...args} selectable isRowSelectable={row => row.status === 'active'} // disable inactive rows
  selectedNumber="—" />
}`,...M.parameters?.docs?.source}}};O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
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
}`,...O.parameters?.docs?.source}}};B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
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
}`,...B.parameters?.docs?.source}}};Z.parameters={...Z.parameters,docs:{...Z.parameters?.docs,source:{originalSource:`{
  args: {
    columns: [{
      ...baseColumns[0],
      headerColSpan: 2
    },
    // spans two header columns
    baseColumns[1], baseColumns[2], baseColumns[3]]
  }
}`,...Z.parameters?.docs?.source}}};j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
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
}`,...j.parameters?.docs?.source},description:{story:`Full-row (colspan) detail row
Your Table renders a second <tr> with a single <td colSpan=...>
whenever getFullRowContent(row) returns a ReactNode.`,...j.parameters?.docs?.description}}};w.parameters={...w.parameters,docs:{...w.parameters?.docs,source:{originalSource:`{
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
}`,...w.parameters?.docs?.source},description:{story:`Full-row (colspan) detail row
Your Table renders a second <tr> with a single <td colSpan=...>
whenever getFullRowContent(row) returns a ReactNode.`,...w.parameters?.docs?.description}}};U.parameters={...U.parameters,docs:{...U.parameters?.docs,source:{originalSource:`{
  args: {
    // keep default columns (sortable on name, age, created, score)
  },
  render: args => <Table {...args} data={[...sampleData]} />
}`,...U.parameters?.docs?.source}}};G.parameters={...G.parameters,docs:{...G.parameters?.docs,source:{originalSource:`{
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
}`,...G.parameters?.docs?.source}}};const la=["Basic","SeparateVariant","Loading","NoResults","NoDataState","SelectableUncontrolled","SelectableControlled","SelectableWithDisabledRows","StickyHeaderInScrollContainer","WithHiddenColumns","WithHeaderColSpan","WithFullRowAlwaysDisplayedDetail","WithFullRowDetail","SortingShowcase","WithPagination"];export{F as Basic,L as Loading,H as NoDataState,$ as NoResults,W as SelectableControlled,z as SelectableUncontrolled,M as SelectableWithDisabledRows,P as SeparateVariant,U as SortingShowcase,O as StickyHeaderInScrollContainer,j as WithFullRowAlwaysDisplayedDetail,w as WithFullRowDetail,Z as WithHeaderColSpan,B as WithHiddenColumns,G as WithPagination,la as __namedExportsOrder,na as default};
