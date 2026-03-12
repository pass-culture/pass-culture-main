import{j as a}from"./jsx-runtime-u17CrQMm.js";import{r as g,R as ve}from"./iframe-CY64iaZD.js";import{c as p}from"./index-Cp6Xx17s.js";import{C as se}from"./Checkbox-C_RfCyDT.js";import{P as Ne}from"./Pagination-BJNdPBye.js";import{S as je}from"./Skeleton-BAKnPzGx.js";import{f as re}from"./full-down-Cmbtr9nI.js";import{f as ne}from"./full-up-D6TPt2ju.js";import{S}from"./SvgIcon-DuZPzNRk.js";import{B as we,b as Re,a as De}from"./Button-BGkSaDye.js";import{f as Te}from"./full-refresh-BZh6W0mB.js";import{s as Ae}from"./stroke-search-D6-mXEew.js";import"./preload-helper-PPVm8Dsz.js";import"./Asset-5z8k9i5S.js";import"./Tag-CmATaSNe.js";import"./full-thumb-up-B5qPZKde.js";import"./full-left-vjwAEs82.js";import"./full-right-Dd3YsyCq.js";import"./full-three-dots-C5Ey0HNi.js";import"./full-link-D8YFLOxw.js";import"./Tooltip-DG893zVB.js";import"./stroke-pass-CALgybTM.js";import"./chunk-LFPYN7LY-vffaCzQT.js";var y=(e=>(e.ASC="asc",e.DESC="desc",e.NONE="none",e))(y||{});const ke=()=>{const[e,s]=g.useState(null),[r,i]=g.useState("none"),l=g.useCallback(m=>e!==m?(s(m),i("asc"),"asc"):r==="asc"?(i("desc"),"desc"):r==="desc"?(i("none"),"none"):(i("asc"),"asc"),[e,r]);return{currentSortingColumn:e,currentSortingMode:r,onColumnHeaderClick:l}},le={"sorting-icons":"_sorting-icons_cbxcb_1","both-icons":"_both-icons_cbxcb_17"},J=({sortingMode:e,onClick:s,children:r})=>a.jsxs("button",{type:"button",className:le["sorting-icons"],onClick:s,children:[r,e!==y.NONE?e===y.DESC?a.jsx(S,{src:ne,alt:"Ne plus trier",width:"10"}):a.jsx(S,{src:re,alt:"Trier par ordre décroissant",width:"10"}):a.jsxs("span",{className:le["both-icons"],children:[a.jsx(S,{src:ne,alt:"Trier par ordre croissant",width:"10"}),a.jsx(S,{src:re,alt:"",width:"10"})]})]});try{J.displayName="SortColumn",J.__docgenInfo={description:"",displayName:"SortColumn",props:{sortingMode:{defaultValue:null,description:"",name:"sortingMode",required:!0,type:{name:"enum",value:[{value:'"asc"'},{value:'"desc"'},{value:'"none"'}]}},onClick:{defaultValue:null,description:"",name:"onClick",required:!0,type:{name:"() => void"}}}}}catch{}const Ve="_wrapper_my972_1",Ie="_table_my972_5",n={wrapper:Ve,table:Ie,"table-pagination":"_table-pagination_my972_13","table-separate":"_table-separate_my972_17","table-separate-cell":"_table-separate-cell_my972_21","table-collapse":"_table-collapse_my972_38","table-collapse-cell":"_table-collapse-cell_my972_45","table-row":"_table-row_my972_50","table-header":"_table-header_my972_54","table-header-sticky":"_table-header-sticky_my972_60","table-header-th":"_table-header-th_my972_65","table-header-sortable-th":"_table-header-sortable-th_my972_78","table-select-all":"_table-select-all_my972_83","table-checkbox-label":"_table-checkbox-label_my972_89","visually-hidden":"_visually-hidden_my972_104","table-caption-no-display":"_table-caption-no-display_my972_116","table-fullrow-content":"_table-fullrow-content_my972_120"},I={"no-data":"_no-data_10bkz_1","no-data-icon":"_no-data-icon_10bkz_7","no-data-title":"_no-data-title_10bkz_11","no-data-subtitle":"_no-data-subtitle_10bkz_19"},K=({noData:{icon:e,title:s,subtitle:r}})=>a.jsxs("div",{className:I["no-data"],children:[a.jsx(S,{src:e,alt:"",width:"100",className:I["no-data-icon"]}),a.jsx("p",{className:I["no-data-title"],children:s}),a.jsx("p",{className:I["no-data-subtitle"],children:r})]});try{K.displayName="TableNoData",K.__docgenInfo={description:"",displayName:"TableNoData",props:{noData:{defaultValue:null,description:"",name:"noData",required:!0,type:{name:"{ icon: string; title: string; subtitle: string; }"}}}}}catch{}const E={"search-no-results":"_search-no-results_yb0tv_1","search-no-results-icon":"_search-no-results-icon_yb0tv_4","search-no-results-title4":"_search-no-results-title4_yb0tv_8","search-no-results-text":"_search-no-results-text_yb0tv_14"},Q=({colSpan:e=1,message:s="Pas de résultat pour votre recherche",subtitle:r="Vous pouvez modifier votre recherche ou",resetMessage:i="Réinitialiser les filtres",resetFilters:l})=>a.jsx("tr",{children:a.jsx("td",{colSpan:e,children:a.jsxs("div",{className:E["search-no-results"],children:[a.jsx(S,{src:Ae,alt:"Illustration de recherche",className:E["search-no-results-icon"],width:"124"}),a.jsx("p",{className:E["search-no-results-title4"],children:s}),a.jsx("p",{className:E["search-no-results-text"],children:r}),a.jsx(we,{variant:De.SECONDARY,color:Re.BRAND,icon:Te,onClick:l,label:i})]})})});try{Q.displayName="TableNoFilterResult",Q.__docgenInfo={description:"",displayName:"TableNoFilterResult",props:{colSpan:{defaultValue:{value:"1"},description:"",name:"colSpan",required:!1,type:{name:"number"}},message:{defaultValue:{value:"Pas de résultat pour votre recherche"},description:"",name:"message",required:!1,type:{name:"string"}},subtitle:{defaultValue:{value:"Vous pouvez modifier votre recherche ou"},description:"",name:"subtitle",required:!1,type:{name:"string"}},resetMessage:{defaultValue:{value:"Réinitialiser les filtres"},description:"",name:"resetMessage",required:!1,type:{name:"string"}},resetFilters:{defaultValue:null,description:"",name:"resetFilters",required:!0,type:{name:"() => void"}}}}}catch{}var _=(e=>(e.COLLAPSE="collapse",e.SEPARATE="separate",e))(_||{});function Y(e,s){if(s)return typeof s=="function"?s(e):typeof s=="string"?s.split(".").reduce((r,i)=>r?.[i],e):e[s]}function d({title:e="Tableau de données",columns:s,data:r,allData:i,selectable:l=!1,selectedNumber:m,selectedIds:R,className:ce,isLoading:de,isSticky:ue,variant:b,noResult:D,noData:X,onSelectionChange:me,getFullRowContent:pe,isRowSelectable:x,pagination:T}){const h=i??r,{currentSortingColumn:A,currentSortingMode:k,onColumnHeaderClick:ge}=ke(),[be,he]=g.useState(new Set),ee=R!==void 0,f=ee?R:be,G=t=>{ee||he(t),me?.(h.filter(o=>t.has(o.id)))};function fe(t){ge(t)}const C=g.useMemo(()=>x?h.filter(x):h,[h,x]),Se=()=>{f.size===C.length?G(new Set):G(new Set(C.map(t=>t.id)))},ye=t=>{const o=new Set(f);o.has(t.id)?o.delete(t.id):o.add(t.id),G(o)},ae=g.useMemo(()=>{if(!A)return r;const t=s.find(o=>o.id===A);return t?[...h].sort((o,v)=>{const u=Y(o,t.ordererField),V=Y(v,t.ordererField);return u===V?0:u<V?k===y.ASC?-1:1:k===y.ASC?1:-1}):r},[r,A,k,s,h]),te=f.size===C.length&&C.length>0,_e=f.size>0&&f.size<C.length,xe=te?"Tout désélectionner":"Tout sélectionner";return X.hasNoData?a.jsx(K,{noData:X.message}):a.jsxs("div",{className:p(n.wrapper,ce),children:[l&&a.jsxs("div",{className:n["table-select-all"],children:[a.jsx(se,{label:xe,checked:te,indeterminate:_e,onChange:Se}),a.jsx("span",{className:n["visually-hidden"],children:"Sélectionner toutes les lignes"}),a.jsx("div",{children:m})]}),a.jsxs("table",{className:p(n.table,{[n["table-separate"]]:b==="separate",[n["table-collapse"]]:b==="collapse"}),children:[a.jsx("caption",{className:n["table-caption-no-display"],children:e}),a.jsx("thead",{children:a.jsxs("tr",{className:p(n["table-header"],{[n["table-header-sticky"]]:ue}),children:[l&&a.jsx("th",{scope:"col",className:n["table-header-th"],children:a.jsx("span",{className:n["visually-hidden"],children:"Sélectionner"})}),s.map(t=>{if(t.headerHidden)return null;const o=t.header??t.label??"";return a.jsx("th",{scope:"col",id:t.id,colSpan:t.headerColSpan||1,className:p(n["table-header-th"],{[n["table-header-sortable-th"]]:t.sortable}),children:t.sortable?a.jsx(J,{onClick:()=>fe(t.id),sortingMode:A===t.id?k:y.NONE,children:o}):o},`col-${t.id}`)})]})}),a.jsxs("tbody",{children:[de&&Array.from({length:8}).map((t,o)=>a.jsx("tr",{children:a.jsx("td",{colSpan:s.length+1,children:a.jsx(je,{height:"7rem",width:"100%"})})},`loading-row-${s.length}-${o}`)),!ae.length&&a.jsx(Q,{colSpan:s.length+(l?1:0),message:D.message,subtitle:D.subtitle,resetMessage:D.resetMessage,resetFilters:D.onFilterReset}),ae.map(t=>{const o=f.has(t.id),v=pe?.(t);return a.jsxs(ve.Fragment,{children:[a.jsxs("tr",{"data-testid":"table-row",className:p({[n["table-row"]]:!v}),children:[l&&a.jsxs("td",{className:p({[n["table-separate-cell"]]:b==="separate",[n["table-collapse-cell"]]:b==="collapse"}),children:[a.jsx(se,{label:t.name??`ligne ${t.id}`,checked:o,onChange:()=>ye(t),className:n["table-checkbox-label"],disabled:x?!x(t):!1}),a.jsxs("span",{className:n["visually-hidden"],children:["Selectionner la ligne ",t.name||t.id]})]}),s.map((u,V)=>{if(u.bodyHidden)return null;const Ce=u.render?u.render(t):Y(t,u.ordererField);return a.jsx("td",{className:p({[n["table-separate-cell"]]:b==="separate",[n["table-collapse-cell"]]:b==="collapse"}),"data-label":u.label,children:Ce},`col-${u.id}-${V}`)})]}),v&&a.jsx("tr",{className:p(n["table-row"]),children:a.jsx("td",{colSpan:s.length+(l?1:0),children:a.jsx("div",{className:n["table-fullrow-content"],children:v})})})]},t.id)})]})]}),T&&a.jsx("div",{className:n["table-pagination"],children:a.jsx(Ne,{currentPage:T.currentPage,pageCount:T.pageCount,onPageClick:T.onPageClick})})]})}try{d.displayName="Table",d.__docgenInfo={description:"",displayName:"Table",props:{title:{defaultValue:{value:"Tableau de données"},description:"",name:"title",required:!1,type:{name:"string"}},columns:{defaultValue:null,description:"",name:"columns",required:!0,type:{name:"Column<T>[]"}},data:{defaultValue:null,description:"",name:"data",required:!0,type:{name:"T[]"}},allData:{defaultValue:null,description:"",name:"allData",required:!1,type:{name:"T[]"}},selectable:{defaultValue:{value:"false"},description:"",name:"selectable",required:!1,type:{name:"boolean"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},isLoading:{defaultValue:null,description:"",name:"isLoading",required:!0,type:{name:"boolean"}},isSticky:{defaultValue:null,description:"",name:"isSticky",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!0,type:{name:"enum",value:[{value:'"collapse"'},{value:'"separate"'}]}},selectedNumber:{defaultValue:null,description:"",name:"selectedNumber",required:!1,type:{name:"string"}},selectedIds:{defaultValue:null,description:"",name:"selectedIds",required:!1,type:{name:"Set<string | number>"}},onSelectionChange:{defaultValue:null,description:"",name:"onSelectionChange",required:!1,type:{name:"((rows: T[]) => void)"}},getFullRowContent:{defaultValue:null,description:"",name:"getFullRowContent",required:!1,type:{name:"((row: T) => ReactNode)"}},isRowSelectable:{defaultValue:null,description:"",name:"isRowSelectable",required:!1,type:{name:"((row: T) => boolean)"}},noResult:{defaultValue:null,description:"",name:"noResult",required:!0,type:{name:"NoResultProps"}},noData:{defaultValue:null,description:"",name:"noData",required:!0,type:{name:"EmptyStateProps"}},pagination:{defaultValue:null,description:"",name:"pagination",required:!1,type:{name:"PaginationProps"}}}}}catch{}const w=[{id:1,name:"Alice",email:"alice@example.com",age:27,status:"active",createdAt:"2024-01-05T10:00:00Z",nested:{score:77}},{id:2,name:"Bob",email:"bob@example.com",age:34,status:"inactive",createdAt:"2024-02-01T08:30:00Z",nested:{score:65}},{id:3,name:"Chloe",email:"chloe@example.com",age:22,status:"active",createdAt:"2024-03-12T12:45:00Z",nested:{score:92}},{id:4,name:"Diego",email:"diego@example.com",age:41,status:"active",createdAt:"2024-04-20T15:10:00Z",nested:{score:58}},{id:5,name:"Elise",email:"elise@example.com",age:29,status:"inactive",createdAt:"2024-05-11T09:00:00Z",nested:{score:80}},{id:6,name:"Fares",email:"fares@example.com",age:37,status:"active",createdAt:"2024-06-02T11:15:00Z",nested:{score:71}},{id:7,name:"Gina",email:"gina@example.com",age:31,status:"active",createdAt:"2024-06-18T16:20:00Z",nested:{score:88}},{id:8,name:"Hugo",email:"hugo@example.com",age:25,status:"inactive",createdAt:"2024-07-08T07:05:00Z",nested:{score:54}}],Ee=e=>new Date(e).toLocaleDateString("fr-FR",{year:"numeric",month:"short",day:"2-digit"}),c=[{id:"name",label:"Nom",sortable:!0,ordererField:e=>e.name,render:e=>a.jsx("strong",{children:e.name})},{id:"age",label:"Âge",sortable:!0,ordererField:e=>e.age,render:e=>e.age},{id:"created",label:"Créé le",sortable:!0,ordererField:e=>new Date(e.createdAt).getTime(),render:e=>Ee(e.createdAt)},{id:"status",label:"Statut",render:e=>a.jsx("span",{"aria-label":`status-${e.id}`,children:e.status==="active"?"Actif":"Inactif"})},{id:"score",label:"Score",sortable:!0,ordererField:e=>e.nested.score,render:e=>e.nested.score}],oe={hasNoData:!1,message:{icon:"📄",title:"Aucune donnée",subtitle:"Commencez par créer un élément pour remplir ce tableau."}},ie={message:"Aucun résultat pour ces filtres.",resetMessage:"Réinitialiser les filtres",onFilterReset:()=>alert("reset filters")},ra={title:"Design System/Table",component:d,args:{title:"Tableau de données",columns:c,data:w,selectable:!1,isLoading:!1,isSticky:!1,variant:_.COLLAPSE,noData:oe,noResult:ie},argTypes:{variant:{control:"inline-radio",options:[_.SEPARATE,_.COLLAPSE]},isLoading:{control:"boolean"},selectable:{control:"boolean"},isSticky:{control:"boolean"}},parameters:{layout:"padded"}},F={render:e=>a.jsx(d,{...e})},P={args:{variant:_.SEPARATE}},q={args:{isLoading:!0}},L={args:{data:[],noData:{...oe,hasNoData:!1},noResult:{...ie,onFilterReset:()=>alert("Réinitialiser les filtres")}}},$={args:{data:[],noData:{hasNoData:!0,message:{icon:"📭",title:"Rien à afficher",subtitle:"Aucun élément n’a encore été créé."}}}},H={args:{selectable:!0,selectedNumber:"0 sélectionnée"}},z={render:e=>{const[s,r]=g.useState(new Set([2,4])),i=s.size;return a.jsx(d,{...e,selectable:!0,selectedIds:s,selectedNumber:`${i} sélectionnée${i>1?"s":""}`,onSelectionChange:l=>{r(new Set(l.map(m=>m.id)))}})}},W={render:e=>a.jsx(d,{...e,selectable:!0,isRowSelectable:s=>s.status==="active",selectedNumber:"—"})},M={args:{isSticky:!0},render:e=>a.jsx("div",{style:{height:260,overflow:"auto",border:"1px solid #eee"},children:a.jsx(d,{...e,data:[...w,...w]})})},O={args:{columns:[{...c[0],headerHidden:!0},c[1],{...c[2],bodyHidden:!0},c[3],c[4]]}},B={args:{columns:[{...c[0],headerColSpan:2},c[1],c[2],c[3]]}},N={render:e=>{const s=c;return a.jsx(d,{...e,variant:_.COLLAPSE,columns:s,getFullRowContent:r=>r.age>30?a.jsx("div",{style:{padding:"8px",margin:"8px",backgroundColor:"violet",borderRadius:"4px"},children:r.name},r.id):null})}},j={render:e=>{const[s,r]=g.useState(3),i=[...c.slice(0,4),{id:"actions",label:"Actions",render:l=>a.jsx("button",{onClick:m=>{m.stopPropagation(),r(R=>R===l.id?null:l.id)},children:s===l.id?"Fermer":"Voir détails"})}];return a.jsx(d,{...e,columns:i,getFullRowContent:l=>l.id===s?a.jsxs("div",{style:{padding:16},children:[a.jsx("h4",{style:{margin:0},children:l.name}),a.jsxs("p",{style:{margin:"8px 0"},children:["Email: ",a.jsx("strong",{children:l.email})]}),a.jsxs("p",{style:{margin:0},children:["Score: ",a.jsx("strong",{children:l.nested.score})," — Statut:"," ",a.jsx("strong",{children:l.status})]})]}):null})}},Z={args:{},render:e=>a.jsx(d,{...e,data:[...w]})},U={args:{pagination:{currentPage:1,pageCount:3,onPageClick:e=>{alert(`Go to page ${e}`)}}},render:e=>a.jsx(d,{...e,data:[...w]})};F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  render: args => <Table {...args} />
}`,...F.parameters?.docs?.source}}};P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    variant: TableVariant.SEPARATE
  }
}`,...P.parameters?.docs?.source}}};q.parameters={...q.parameters,docs:{...q.parameters?.docs,source:{originalSource:`{
  args: {
    isLoading: true
  }
}`,...q.parameters?.docs?.source}}};L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
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
}`,...L.parameters?.docs?.source}}};$.parameters={...$.parameters,docs:{...$.parameters?.docs,source:{originalSource:`{
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
}`,...$.parameters?.docs?.source}}};H.parameters={...H.parameters,docs:{...H.parameters?.docs,source:{originalSource:`{
  args: {
    selectable: true,
    selectedNumber: '0 sélectionnée'
  }
}`,...H.parameters?.docs?.source}}};z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
  render: args => {
    const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set([2, 4]));
    const selectedCount = selectedIds.size;
    return <Table {...args} selectable selectedIds={selectedIds} selectedNumber={\`\${selectedCount} sélectionnée\${selectedCount > 1 ? 's' : ''}\`} onSelectionChange={rows => {
      setSelectedIds(new Set(rows.map(r => r.id)));
    }} />;
  }
}`,...z.parameters?.docs?.source}}};W.parameters={...W.parameters,docs:{...W.parameters?.docs,source:{originalSource:`{
  render: args => <Table {...args} selectable isRowSelectable={row => row.status === 'active'} // disable inactive rows
  selectedNumber="—" />
}`,...W.parameters?.docs?.source}}};M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
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
}`,...M.parameters?.docs?.source}}};O.parameters={...O.parameters,docs:{...O.parameters?.docs,source:{originalSource:`{
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
}`,...O.parameters?.docs?.source}}};B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  args: {
    columns: [{
      ...baseColumns[0],
      headerColSpan: 2
    },
    // spans two header columns
    baseColumns[1], baseColumns[2], baseColumns[3]]
  }
}`,...B.parameters?.docs?.source}}};N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
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
}`,...N.parameters?.docs?.source},description:{story:`Full-row (colspan) detail row
Your Table renders a second <tr> with a single <td colSpan=...>
whenever getFullRowContent(row) returns a ReactNode.`,...N.parameters?.docs?.description}}};j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
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
}`,...j.parameters?.docs?.source},description:{story:`Full-row (colspan) detail row
Your Table renders a second <tr> with a single <td colSpan=...>
whenever getFullRowContent(row) returns a ReactNode.`,...j.parameters?.docs?.description}}};Z.parameters={...Z.parameters,docs:{...Z.parameters?.docs,source:{originalSource:`{
  args: {
    // keep default columns (sortable on name, age, created, score)
  },
  render: args => <Table {...args} data={[...sampleData]} />
}`,...Z.parameters?.docs?.source}}};U.parameters={...U.parameters,docs:{...U.parameters?.docs,source:{originalSource:`{
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
}`,...U.parameters?.docs?.source}}};const na=["Basic","SeparateVariant","Loading","NoResults","NoDataState","SelectableUncontrolled","SelectableControlled","SelectableWithDisabledRows","StickyHeaderInScrollContainer","WithHiddenColumns","WithHeaderColSpan","WithFullRowAlwaysDisplayedDetail","WithFullRowDetail","SortingShowcase","WithPagination"];export{F as Basic,q as Loading,$ as NoDataState,L as NoResults,z as SelectableControlled,H as SelectableUncontrolled,W as SelectableWithDisabledRows,P as SeparateVariant,Z as SortingShowcase,M as StickyHeaderInScrollContainer,N as WithFullRowAlwaysDisplayedDetail,j as WithFullRowDetail,B as WithHeaderColSpan,O as WithHiddenColumns,U as WithPagination,na as __namedExportsOrder,ra as default};
