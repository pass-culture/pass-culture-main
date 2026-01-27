import{j as a}from"./jsx-runtime-C_uOM0Gm.js";import{r as g,R as ye}from"./iframe-CTnXOULQ.js";import{c as m}from"./index-TscbDd2H.js";import{C as te}from"./Checkbox-BYovAbr0.js";import{S as Ce}from"./Skeleton-cjoPGwI3.js";import{f as se}from"./full-down-Cmbtr9nI.js";import{f as re}from"./full-up-D6TPt2ju.js";import{S}from"./SvgIcon-CJiY4LCz.js";import{f as ve}from"./full-refresh-BZh6W0mB.js";import{s as Ne}from"./stroke-search-Bph5aoaJ.js";import{B as je}from"./Button-D-MtOkGK.js";import{B as we}from"./types-yVZEaApa.js";import"./preload-helper-PPVm8Dsz.js";import"./Asset-DEO5YOFe.js";import"./Tag-CZrfY-rG.js";import"./full-thumb-up-Bb4kpRpM.js";import"./stroke-pass-CALgybTM.js";import"./Tooltip-GJ5PEk5n.js";import"./Button.module-BE-jPv6M.js";var _=(e=>(e.ASC="asc",e.DESC="desc",e.NONE="none",e))(_||{});const Re=()=>{const[e,s]=g.useState(null),[r,i]=g.useState("none"),l=g.useCallback(p=>e!==p?(s(p),i("asc"),"asc"):r==="asc"?(i("desc"),"desc"):r==="desc"?(i("none"),"none"):(i("asc"),"asc"),[e,r]);return{currentSortingColumn:e,currentSortingMode:r,onColumnHeaderClick:l}},N={"sorting-icons":"_sorting-icons_cbxcb_1","both-icons":"_both-icons_cbxcb_17"},G=({sortingMode:e,onClick:s,children:r})=>a.jsxs("button",{type:"button",className:N["sorting-icons"],onClick:s,children:[r,e!==_.NONE?e===_.DESC?a.jsx(S,{className:N["sort-icon"],src:re,alt:"Ne plus trier",width:"10"}):a.jsx(S,{className:N["sort-icon"],src:se,alt:"Trier par ordre décroissant",width:"10"}):a.jsxs("span",{className:m(N["sort-icon"],N["both-icons"]),children:[a.jsx(S,{src:re,alt:"Trier par ordre croissant",width:"10"}),a.jsx(S,{src:se,alt:"",width:"10"})]})]});try{G.displayName="SortColumn",G.__docgenInfo={description:"",displayName:"SortColumn",props:{sortingMode:{defaultValue:null,description:"",name:"sortingMode",required:!0,type:{name:"enum",value:[{value:'"asc"'},{value:'"desc"'},{value:'"none"'}]}},onClick:{defaultValue:null,description:"",name:"onClick",required:!0,type:{name:"() => void"}}}}}catch{}const Te="_wrapper_4is3g_1",De="_table_4is3g_5",n={wrapper:Te,table:De,"table-separate":"_table-separate_4is3g_14","table-separate-cell":"_table-separate-cell_4is3g_18","table-collapse":"_table-collapse_4is3g_35","table-collapse-cell":"_table-collapse-cell_4is3g_42","table-row":"_table-row_4is3g_47","table-header":"_table-header_4is3g_51","table-header-sticky":"_table-header-sticky_4is3g_57","table-header-th":"_table-header-th_4is3g_62","table-header-sortable-th":"_table-header-sortable-th_4is3g_75","table-select-all":"_table-select-all_4is3g_80","table-checkbox-label":"_table-checkbox-label_4is3g_86","visually-hidden":"_visually-hidden_4is3g_98","table-caption-no-display":"_table-caption-no-display_4is3g_110","table-fullrow-content":"_table-fullrow-content_4is3g_154"},I={"no-data":"_no-data_jhwou_1","no-data-icon":"_no-data-icon_jhwou_7","no-data-title":"_no-data-title_jhwou_11","no-data-subtitle":"_no-data-subtitle_jhwou_18"},J=({noData:{icon:e,title:s,subtitle:r}})=>a.jsxs("div",{className:I["no-data"],children:[a.jsx(S,{src:e,alt:"",width:"100",className:I["no-data-icon"]}),a.jsx("p",{className:I["no-data-title"],children:s}),a.jsx("p",{className:I["no-data-subtitle"],children:r})]});try{J.displayName="TableNoData",J.__docgenInfo={description:"",displayName:"TableNoData",props:{noData:{defaultValue:null,description:"",name:"noData",required:!0,type:{name:"{ icon: string; title: string; subtitle: string; }"}}}}}catch{}const V={"search-no-results":"_search-no-results_yb0tv_1","search-no-results-icon":"_search-no-results-icon_yb0tv_4","search-no-results-title4":"_search-no-results-title4_yb0tv_8","search-no-results-text":"_search-no-results-text_yb0tv_14"},K=({colSpan:e=1,message:s="Pas de résultat pour votre recherche",subtitle:r="Vous pouvez modifier votre recherche ou",resetMessage:i="Réinitialiser les filtres",resetFilters:l})=>a.jsx("tr",{children:a.jsx("td",{colSpan:e,children:a.jsxs("div",{className:V["search-no-results"],children:[a.jsx(S,{src:Ne,alt:"Illustration de recherche",className:V["search-no-results-icon"],width:"124"}),a.jsx("p",{className:V["search-no-results-title4"],children:s}),a.jsx("p",{className:V["search-no-results-text"],children:r}),a.jsx(je,{variant:we.TERNARYBRAND,icon:ve,onClick:l,children:i})]})})});try{K.displayName="TableNoFilterResult",K.__docgenInfo={description:"",displayName:"TableNoFilterResult",props:{colSpan:{defaultValue:{value:"1"},description:"",name:"colSpan",required:!1,type:{name:"number"}},message:{defaultValue:{value:"Pas de résultat pour votre recherche"},description:"",name:"message",required:!1,type:{name:"string"}},subtitle:{defaultValue:{value:"Vous pouvez modifier votre recherche ou"},description:"",name:"subtitle",required:!1,type:{name:"string"}},resetMessage:{defaultValue:{value:"Réinitialiser les filtres"},description:"",name:"resetMessage",required:!1,type:{name:"string"}},resetFilters:{defaultValue:null,description:"",name:"resetFilters",required:!0,type:{name:"() => void"}}}}}catch{}var x=(e=>(e.COLLAPSE="collapse",e.SEPARATE="separate",e))(x||{});function Y(e,s){if(s)return typeof s=="function"?s(e):typeof s=="string"?s.split(".").reduce((r,i)=>r?.[i],e):e[s]}function d({title:e="Tableau de données",columns:s,data:r,allData:i,selectable:l=!1,selectedNumber:p,selectedIds:R,className:oe,isLoading:ie,isSticky:ce,variant:b,noResult:T,noData:Q,onSelectionChange:de,getFullRowContent:ue,isRowSelectable:y}){const h=i??r,{currentSortingColumn:D,currentSortingMode:A,onColumnHeaderClick:me}=Re(),[pe,ge]=g.useState(new Set),X=R!==void 0,f=X?R:pe,U=t=>{X||ge(t),de?.(h.filter(o=>t.has(o.id)))};function be(t){me(t)}const C=g.useMemo(()=>y?h.filter(y):h,[h,y]),he=()=>{f.size===C.length?U(new Set):U(new Set(C.map(t=>t.id)))},fe=t=>{const o=new Set(f);o.has(t.id)?o.delete(t.id):o.add(t.id),U(o)},ee=g.useMemo(()=>{if(!D)return r;const t=s.find(o=>o.id===D);return t?[...h].sort((o,v)=>{const u=Y(o,t.ordererField),k=Y(v,t.ordererField);return u===k?0:u<k?A===_.ASC?-1:1:A===_.ASC?1:-1}):r},[r,D,A,s,h]),ae=f.size===C.length&&C.length>0,Se=f.size>0&&f.size<C.length,_e=ae?"Tout désélectionner":"Tout sélectionner";return Q.hasNoData?a.jsx(J,{noData:Q.message}):a.jsxs("div",{className:m(n.wrapper,oe),children:[l&&a.jsxs("div",{className:n["table-select-all"],children:[a.jsx(te,{label:_e,checked:ae,indeterminate:Se,onChange:he}),a.jsx("span",{className:n["visually-hidden"],children:"Sélectionner toutes les lignes"}),a.jsx("div",{children:p})]}),a.jsxs("table",{className:m(n.table,{[n["table-separate"]]:b==="separate",[n["table-collapse"]]:b==="collapse"}),children:[a.jsx("caption",{className:n["table-caption-no-display"],children:e}),a.jsx("thead",{children:a.jsxs("tr",{className:m(n["table-header"],{[n["table-header-sticky"]]:ce}),children:[l&&a.jsx("th",{scope:"col",className:n["table-header-th"],children:a.jsx("span",{className:n["visually-hidden"],children:"Sélectionner"})}),s.map(t=>{if(t.headerHidden)return null;const o=t.header??t.label??"";return a.jsx("th",{scope:"col",id:t.id,colSpan:t.headerColSpan||1,className:m(n.columnWidth,n["table-header-th"],{[n["table-header-sortable-th"]]:t.sortable}),children:t.sortable?a.jsx(G,{onClick:()=>be(t.id),sortingMode:D===t.id?A:_.NONE,children:o}):o},`col-${t.id}`)})]})}),a.jsxs("tbody",{children:[ie&&Array.from({length:8}).map((t,o)=>a.jsx("tr",{children:a.jsx("td",{colSpan:s.length+1,children:a.jsx(Ce,{height:"7rem",width:"100%"})})},`loading-row-${s.length}-${o}`)),!ee.length&&a.jsx(K,{colSpan:s.length+(l?1:0),message:T.message,subtitle:T.subtitle,resetMessage:T.resetMessage,resetFilters:T.onFilterReset}),ee.map(t=>{const o=f.has(t.id),v=ue?.(t);return a.jsxs(ye.Fragment,{children:[a.jsxs("tr",{"data-testid":"table-row",className:m({[n["table-row"]]:!v,[n.selected]:o}),children:[l&&a.jsxs("td",{className:m(n["table-checkbox-cell"],{[n["table-separate-cell"]]:b==="separate",[n["table-collapse-cell"]]:b==="collapse"}),children:[a.jsx(te,{label:t.name??`ligne ${t.id}`,checked:o,onChange:()=>fe(t),className:n["table-checkbox-label"],disabled:y?!y(t):!1}),a.jsxs("span",{className:n["visually-hidden"],children:["Selectionner la ligne ",t.name||t.id]})]}),s.map((u,k)=>{if(u.bodyHidden)return null;const xe=u.render?u.render(t):Y(t,u.ordererField);return a.jsx("td",{className:m({[n["table-separate-cell"]]:b==="separate",[n["table-collapse-cell"]]:b==="collapse"}),"data-label":u.label,children:xe},`col-${u.id}-${k}`)})]}),v&&a.jsx("tr",{className:m(n["table-row"]),children:a.jsx("td",{colSpan:s.length+(l?1:0),children:a.jsx("div",{className:n["table-fullrow-content"],children:v})})})]},t.id)})]})]})]})}try{d.displayName="Table",d.__docgenInfo={description:"",displayName:"Table",props:{title:{defaultValue:{value:"Tableau de données"},description:"",name:"title",required:!1,type:{name:"string"}},columns:{defaultValue:null,description:"",name:"columns",required:!0,type:{name:"Column<T>[]"}},data:{defaultValue:null,description:"",name:"data",required:!0,type:{name:"T[]"}},allData:{defaultValue:null,description:"",name:"allData",required:!1,type:{name:"T[]"}},selectable:{defaultValue:{value:"false"},description:"",name:"selectable",required:!1,type:{name:"boolean"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},isLoading:{defaultValue:null,description:"",name:"isLoading",required:!0,type:{name:"boolean"}},isSticky:{defaultValue:null,description:"",name:"isSticky",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!0,type:{name:"enum",value:[{value:'"collapse"'},{value:'"separate"'}]}},selectedNumber:{defaultValue:null,description:"",name:"selectedNumber",required:!1,type:{name:"string"}},selectedIds:{defaultValue:null,description:"",name:"selectedIds",required:!1,type:{name:"Set<string | number>"}},onSelectionChange:{defaultValue:null,description:"",name:"onSelectionChange",required:!1,type:{name:"((rows: T[]) => void)"}},getFullRowContent:{defaultValue:null,description:"",name:"getFullRowContent",required:!1,type:{name:"((row: T) => ReactNode)"}},isRowSelectable:{defaultValue:null,description:"",name:"isRowSelectable",required:!1,type:{name:"((row: T) => boolean)"}},noResult:{defaultValue:null,description:"",name:"noResult",required:!0,type:{name:"NoResultProps"}},noData:{defaultValue:null,description:"",name:"noData",required:!0,type:{name:"EmptyStateProps"}}}}}catch{}const Z=[{id:1,name:"Alice",email:"alice@example.com",age:27,status:"active",createdAt:"2024-01-05T10:00:00Z",nested:{score:77}},{id:2,name:"Bob",email:"bob@example.com",age:34,status:"inactive",createdAt:"2024-02-01T08:30:00Z",nested:{score:65}},{id:3,name:"Chloe",email:"chloe@example.com",age:22,status:"active",createdAt:"2024-03-12T12:45:00Z",nested:{score:92}},{id:4,name:"Diego",email:"diego@example.com",age:41,status:"active",createdAt:"2024-04-20T15:10:00Z",nested:{score:58}},{id:5,name:"Elise",email:"elise@example.com",age:29,status:"inactive",createdAt:"2024-05-11T09:00:00Z",nested:{score:80}},{id:6,name:"Fares",email:"fares@example.com",age:37,status:"active",createdAt:"2024-06-02T11:15:00Z",nested:{score:71}},{id:7,name:"Gina",email:"gina@example.com",age:31,status:"active",createdAt:"2024-06-18T16:20:00Z",nested:{score:88}},{id:8,name:"Hugo",email:"hugo@example.com",age:25,status:"inactive",createdAt:"2024-07-08T07:05:00Z",nested:{score:54}}],Ae=e=>new Date(e).toLocaleDateString("fr-FR",{year:"numeric",month:"short",day:"2-digit"}),c=[{id:"name",label:"Nom",sortable:!0,ordererField:e=>e.name,render:e=>a.jsx("strong",{children:e.name})},{id:"age",label:"Âge",sortable:!0,ordererField:e=>e.age,render:e=>e.age},{id:"created",label:"Créé le",sortable:!0,ordererField:e=>new Date(e.createdAt).getTime(),render:e=>Ae(e.createdAt)},{id:"status",label:"Statut",render:e=>a.jsx("span",{"aria-label":`status-${e.id}`,children:e.status==="active"?"Actif":"Inactif"})},{id:"score",label:"Score",sortable:!0,ordererField:e=>e.nested.score,render:e=>e.nested.score}],ne={hasNoData:!1,message:{icon:"📄",title:"Aucune donnée",subtitle:"Commencez par créer un élément pour remplir ce tableau."}},le={message:"Aucun résultat pour ces filtres.",resetMessage:"Réinitialiser les filtres",onFilterReset:()=>alert("reset filters")},Je={title:"Design System/Table",component:d,args:{title:"Tableau de données",columns:c,data:Z,selectable:!1,isLoading:!1,isSticky:!1,variant:x.SEPARATE,noData:ne,noResult:le},argTypes:{variant:{control:"inline-radio",options:[x.SEPARATE,x.COLLAPSE]},isLoading:{control:"boolean"},selectable:{control:"boolean"},isSticky:{control:"boolean"}},parameters:{layout:"padded"}},F={render:e=>a.jsx(d,{...e})},E={args:{variant:x.COLLAPSE}},q={args:{isLoading:!0}},L={args:{data:[],noData:{...ne,hasNoData:!1},noResult:{...le,onFilterReset:()=>alert("Réinitialiser les filtres")}}},H={args:{data:[],noData:{hasNoData:!0,message:{icon:"📭",title:"Rien à afficher",subtitle:"Aucun élément n’a encore été créé."}}}},P={args:{selectable:!0,selectedNumber:"0 sélectionnée"}},$={render:e=>{const[s,r]=g.useState(new Set([2,4])),i=s.size;return a.jsx(d,{...e,selectable:!0,selectedIds:s,selectedNumber:`${i} sélectionnée${i>1?"s":""}`,onSelectionChange:l=>{r(new Set(l.map(p=>p.id)))}})}},W={render:e=>a.jsx(d,{...e,selectable:!0,isRowSelectable:s=>s.status==="active",selectedNumber:"—"})},M={args:{isSticky:!0},render:e=>a.jsx("div",{style:{height:260,overflow:"auto",border:"1px solid #eee"},children:a.jsx(d,{...e,data:[...Z,...Z]})})},O={args:{columns:[{...c[0],headerHidden:!0},c[1],{...c[2],bodyHidden:!0},c[3],c[4]]}},z={args:{columns:[{...c[0],headerColSpan:2},c[1],c[2],c[3]]}},j={render:e=>{const s=c;return a.jsx(d,{...e,variant:x.COLLAPSE,columns:s,getFullRowContent:r=>r.age>30?a.jsx("div",{style:{padding:"8px",margin:"8px",backgroundColor:"violet",borderRadius:"4px"},children:r.name},r.id):null})}},w={render:e=>{const[s,r]=g.useState(3),i=[...c.slice(0,4),{id:"actions",label:"Actions",render:l=>a.jsx("button",{onClick:p=>{p.stopPropagation(),r(R=>R===l.id?null:l.id)},children:s===l.id?"Fermer":"Voir détails"})}];return a.jsx(d,{...e,columns:i,getFullRowContent:l=>l.id===s?a.jsxs("div",{style:{padding:16},children:[a.jsx("h4",{style:{margin:0},children:l.name}),a.jsxs("p",{style:{margin:"8px 0"},children:["Email: ",a.jsx("strong",{children:l.email})]}),a.jsxs("p",{style:{margin:0},children:["Score: ",a.jsx("strong",{children:l.nested.score})," — Statut:"," ",a.jsx("strong",{children:l.status})]})]}):null})}},B={args:{},render:e=>a.jsx(d,{...e,data:[...Z]})};F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  render: args => <Table {...args} />
}`,...F.parameters?.docs?.source}}};E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
  args: {
    variant: TableVariant.COLLAPSE
  }
}`,...E.parameters?.docs?.source}}};q.parameters={...q.parameters,docs:{...q.parameters?.docs,source:{originalSource:`{
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
}`,...L.parameters?.docs?.source}}};H.parameters={...H.parameters,docs:{...H.parameters?.docs,source:{originalSource:`{
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
}`,...H.parameters?.docs?.source}}};P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    selectable: true,
    selectedNumber: '0 sélectionnée'
  }
}`,...P.parameters?.docs?.source}}};$.parameters={...$.parameters,docs:{...$.parameters?.docs,source:{originalSource:`{
  render: args => {
    const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set([2, 4]));
    const selectedCount = selectedIds.size;
    return <Table {...args} selectable selectedIds={selectedIds} selectedNumber={\`\${selectedCount} sélectionnée\${selectedCount > 1 ? 's' : ''}\`} onSelectionChange={rows => {
      setSelectedIds(new Set(rows.map(r => r.id)));
    }} />;
  }
}`,...$.parameters?.docs?.source}}};W.parameters={...W.parameters,docs:{...W.parameters?.docs,source:{originalSource:`{
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
}`,...O.parameters?.docs?.source}}};z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
  args: {
    columns: [{
      ...baseColumns[0],
      headerColSpan: 2
    },
    // spans two header columns
    baseColumns[1], baseColumns[2], baseColumns[3]]
  }
}`,...z.parameters?.docs?.source}}};j.parameters={...j.parameters,docs:{...j.parameters?.docs,source:{originalSource:`{
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
whenever getFullRowContent(row) returns a ReactNode.`,...w.parameters?.docs?.description}}};B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  args: {
    // keep default columns (sortable on name, age, created, score)
  },
  render: args => <Table {...args} data={[...sampleData]} />
}`,...B.parameters?.docs?.source}}};const Ke=["Basic","CollapseVariant","Loading","NoResults","NoDataState","SelectableUncontrolled","SelectableControlled","SelectableWithDisabledRows","StickyHeaderInScrollContainer","WithHiddenColumns","WithHeaderColSpan","WithFullRowAlwaysDisplayedDetail","WithFullRowDetail","SortingShowcase"];export{F as Basic,E as CollapseVariant,q as Loading,H as NoDataState,L as NoResults,$ as SelectableControlled,P as SelectableUncontrolled,W as SelectableWithDisabledRows,B as SortingShowcase,M as StickyHeaderInScrollContainer,j as WithFullRowAlwaysDisplayedDetail,w as WithFullRowDetail,z as WithHeaderColSpan,O as WithHiddenColumns,Ke as __namedExportsOrder,Je as default};
