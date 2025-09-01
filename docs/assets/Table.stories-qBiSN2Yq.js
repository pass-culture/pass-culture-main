import{j as a}from"./jsx-runtime-DF2Pcvd1.js";import{r as b,R as re}from"./index-B2-qRKKC.js";import{c as m}from"./index-DeARc5FM.js";import{C as ne}from"./Checkbox-DcgCepTx.js";import{S as ha}from"./Skeleton-BUJdKyl6.js";import{f as le}from"./full-down-Cmbtr9nI.js";import{f as oe}from"./full-up-D6TPt2ju.js";import{S}from"./SvgIcon-DfLnDDE5.js";import{f as ga}from"./full-refresh-BZh6W0mB.js";import{s as fa}from"./stroke-search-dgesjRZH.js";import{B as Sa}from"./Button-3Je6mDU7.js";import{B as _a}from"./types-yVZEaApa.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./Tag-DoB-Hjk-.js";import"./full-thumb-up-Bb4kpRpM.js";import"./stroke-pass-CALgybTM.js";import"./Tooltip-C-mHJC8R.js";import"./Button.module-Md2doL54.js";var _=(e=>(e.ASC="asc",e.DESC="desc",e.NONE="none",e))(_||{});const xa=()=>{const[e,s]=b.useState(null),[r,i]=b.useState("none"),l=b.useCallback(p=>e!==p?(s(p),i("asc"),"asc"):r==="asc"?(i("desc"),"desc"):r==="desc"?(i("none"),"none"):(i("asc"),"asc"),[e,r]);return{currentSortingColumn:e,currentSortingMode:r,onColumnHeaderClick:l}},j={"sorting-icons":"_sorting-icons_1plp3_1","both-icons":"_both-icons_1plp3_17"},K=({sortingMode:e,onClick:s,children:r})=>a.jsxs("button",{type:"button",className:j["sorting-icons"],onClick:s,children:[r,e!==_.NONE?e===_.DESC?a.jsx(S,{className:j["sort-icon"],src:oe,alt:"Ne plus trier",width:"10"}):a.jsx(S,{className:j["sort-icon"],src:le,alt:"Trier par ordre décroissant",width:"10"}):a.jsxs("span",{className:m(j["sort-icon"],j["both-icons"]),children:[a.jsx(S,{src:oe,alt:"Trier par ordre croissant",width:"10"}),a.jsx(S,{src:le,alt:"",width:"10"})]})]});try{K.displayName="SortColumn",K.__docgenInfo={description:"",displayName:"SortColumn",props:{sortingMode:{defaultValue:null,description:"",name:"sortingMode",required:!0,type:{name:"enum",value:[{value:'"asc"'},{value:'"desc"'},{value:'"none"'}]}},onClick:{defaultValue:null,description:"",name:"onClick",required:!0,type:{name:"() => void"}}}}}catch{}const ya="_wrapper_cs7bj_1",Ca="_table_cs7bj_5",n={wrapper:ya,table:Ca,"table-separate":"_table-separate_cs7bj_14","table-separate-cell":"_table-separate-cell_cs7bj_18","table-collapse":"_table-collapse_cs7bj_35","table-collapse-cell":"_table-collapse-cell_cs7bj_42","table-row":"_table-row_cs7bj_47","table-header":"_table-header_cs7bj_51","table-header-sticky":"_table-header-sticky_cs7bj_57","table-header-th":"_table-header-th_cs7bj_62","table-header-sortable-th":"_table-header-sortable-th_cs7bj_75","table-select-all":"_table-select-all_cs7bj_80","table-checkbox-label":"_table-checkbox-label_cs7bj_86","visually-hidden":"_visually-hidden_cs7bj_98","table-caption-no-display":"_table-caption-no-display_cs7bj_110","table-fullrow-content":"_table-fullrow-content_cs7bj_154"},k={"no-data":"_no-data_1psx1_1","no-data-icon":"_no-data-icon_1psx1_7","no-data-title":"_no-data-title_1psx1_11","no-data-subtitle":"_no-data-subtitle_1psx1_18"},Q=({noData:{icon:e,title:s,subtitle:r}})=>a.jsxs("div",{className:k["no-data"],children:[a.jsx(S,{src:e,alt:"",width:"100",className:k["no-data-icon"]}),a.jsx("p",{className:k["no-data-title"],children:s}),a.jsx("p",{className:k["no-data-subtitle"],children:r})]});try{Q.displayName="TableNoData",Q.__docgenInfo={description:"",displayName:"TableNoData",props:{noData:{defaultValue:null,description:"",name:"noData",required:!0,type:{name:"{ icon: string; title: string; subtitle: string; }"}}}}}catch{}const E={"search-no-results":"_search-no-results_2vpsi_1","search-no-results-icon":"_search-no-results-icon_2vpsi_4","search-no-results-title4":"_search-no-results-title4_2vpsi_8","search-no-results-text":"_search-no-results-text_2vpsi_14"},X=({colSpan:e=1,message:s="Pas de résultat pour votre recherche",resetMessage:r="Réinitialiser les filtres",resetFilters:i})=>a.jsx("tr",{children:a.jsx("td",{colSpan:e,children:a.jsxs("div",{className:E["search-no-results"],children:[a.jsx(S,{src:fa,alt:"Illustration de recherche",className:E["search-no-results-icon"],width:"124"}),a.jsx("p",{className:E["search-no-results-title4"],children:s}),a.jsx("p",{className:E["search-no-results-text"],children:"Vous pouvez modifier votre recherche ou"}),a.jsx(Sa,{variant:_a.TERNARYBRAND,icon:ga,onClick:i,children:r})]})})});try{X.displayName="TableNoFilterResult",X.__docgenInfo={description:"",displayName:"TableNoFilterResult",props:{colSpan:{defaultValue:{value:"1"},description:"",name:"colSpan",required:!1,type:{name:"number"}},message:{defaultValue:{value:"Pas de résultat pour votre recherche"},description:"",name:"message",required:!1,type:{name:"string"}},resetMessage:{defaultValue:{value:"Réinitialiser les filtres"},description:"",name:"resetMessage",required:!1,type:{name:"string"}},resetFilters:{defaultValue:null,description:"",name:"resetFilters",required:!0,type:{name:"() => void"}}}}}catch{}var x=(e=>(e.COLLAPSE="collapse",e.SEPARATE="separate",e))(x||{});function J(e,s){if(s)return typeof s=="function"?s(e):typeof s=="string"?s.split(".").reduce((r,i)=>r==null?void 0:r[i],e):e[s]}function d({title:e="Tableau de données",columns:s,data:r,allData:i,selectable:l=!1,selectedNumber:p,selectedIds:w,className:ta,isLoading:sa,isSticky:ra,variant:h,noResult:Z,noData:ee,onSelectionChange:U,getFullRowContent:Y,isRowSelectable:y}){const R=i??r,{currentSortingColumn:T,currentSortingMode:D,onColumnHeaderClick:na}=xa(),[la,oa]=b.useState(new Set),ae=w!==void 0,g=ae?w:la,G=t=>{ae||oa(t),U==null||U(R.filter(o=>t.has(o.id)))};function ia(t){na(t)}const C=b.useMemo(()=>y?R.filter(y):R,[R,y]),ca=()=>{g.size===C.length?G(new Set):G(new Set(C.map(t=>t.id)))},da=t=>{const o=new Set(g);o.has(t.id)?o.delete(t.id):o.add(t.id),G(o)},te=b.useMemo(()=>{if(!T)return r;const t=s.find(o=>o.id===T);return t?[...r].sort((o,f)=>{const A=J(o,t.ordererField),u=J(f,t.ordererField);return A===u?0:A<u?D===_.ASC?-1:1:D===_.ASC?1:-1}):r},[r,T,D,s]),se=g.size===C.length&&C.length>0,ua=g.size>0&&g.size<C.length,ma=se?"Tout désélectionner":"Tout sélectionner";return ee.hasNoData?a.jsx(Q,{noData:ee.message}):a.jsxs("div",{className:m(n.wrapper,ta),children:[l&&a.jsxs("div",{className:n["table-select-all"],children:[a.jsx(ne,{label:ma,checked:se,indeterminate:ua,onChange:ca}),a.jsx("span",{className:n["visually-hidden"],children:"Sélectionner toutes les lignes"}),a.jsx("div",{children:p})]}),a.jsxs("table",{className:m(n.table,{[n["table-separate"]]:h==="separate",[n["table-collapse"]]:h==="collapse"}),children:[a.jsx("caption",{className:n["table-caption-no-display"],children:e}),a.jsx("thead",{children:a.jsxs("tr",{className:m(n["table-header"],{[n["table-header-sticky"]]:ra}),children:[l&&a.jsx("th",{scope:"col",className:n["table-header-th"],children:a.jsx("span",{className:n["visually-hidden"],children:"Sélectionner"})}),s.map((t,o)=>t.headerHidden?null:a.jsx("th",{scope:"col",id:t.id,colSpan:t.headerColSpan||1,className:m(n.columnWidth,n["table-header-th"],{[n["table-header-sortable-th"]]:t.sortable}),children:t.sortable?a.jsx(K,{onClick:()=>ia(t.id),sortingMode:T===t.id?D:_.NONE,children:t.label}):t.label},`col-${t.id}-${o}`))]})}),a.jsxs("tbody",{children:[sa&&Array.from({length:8}).map((t,o)=>a.jsx("tr",{children:a.jsx("td",{colSpan:s.length+1,children:a.jsx(ha,{height:"7rem",width:"100%"})})},`loading-row-${s.length}-${o}`)),!te.length&&a.jsx(X,{colSpan:s.length+(l?1:0),message:Z.message,resetMessage:Z.resetMessage,resetFilters:Z.onFilterReset}),te.map(t=>{const o=g.has(t.id),f=Y==null?void 0:Y(t),A=re.isValidElement(f)&&f.key===t.id.toString();return a.jsxs(re.Fragment,{children:[a.jsxs("tr",{className:m({[n["table-row"]]:!A,[n.selected]:o}),children:[l&&a.jsxs("td",{className:m(n["table-checkbox-cell"],{[n["table-separate-cell"]]:h==="separate",[n["table-collapse-cell"]]:h==="collapse"}),children:[a.jsx(ne,{label:t.hasOwnProperty.call(t,"name")?t.name:`ligne ${t.id}`,checked:o,onChange:()=>da(t),className:n["table-checkbox-label"],disabled:y?!y(t):!1}),a.jsxs("span",{className:n["visually-hidden"],children:["Selectionner la ligne ",t.name||t.id]})]}),s.map((u,pa)=>{if(u.bodyHidden)return null;const ba=u.render?u.render(t):J(t,u.ordererField);return a.jsx("td",{className:m({[n["table-separate-cell"]]:h==="separate",[n["table-collapse-cell"]]:h==="collapse"}),"data-label":u.label,children:ba},`col-${u.id}-${pa}`)})]}),f&&a.jsx("tr",{className:m(n["table-row"]),children:a.jsx("td",{colSpan:s.length+(l?1:0),children:a.jsx("div",{className:n["table-fullrow-content"],children:f})})})]},t.id)})]})]})]})}try{d.displayName="Table",d.__docgenInfo={description:"",displayName:"Table",props:{title:{defaultValue:{value:"Tableau de données"},description:"",name:"title",required:!1,type:{name:"string"}},columns:{defaultValue:null,description:"",name:"columns",required:!0,type:{name:"Column<T>[]"}},data:{defaultValue:null,description:"",name:"data",required:!0,type:{name:"T[]"}},allData:{defaultValue:null,description:"",name:"allData",required:!1,type:{name:"T[]"}},selectable:{defaultValue:{value:"false"},description:"",name:"selectable",required:!1,type:{name:"boolean"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},isLoading:{defaultValue:null,description:"",name:"isLoading",required:!0,type:{name:"boolean"}},isSticky:{defaultValue:null,description:"",name:"isSticky",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!0,type:{name:"enum",value:[{value:'"collapse"'},{value:'"separate"'}]}},selectedNumber:{defaultValue:null,description:"",name:"selectedNumber",required:!1,type:{name:"string"}},selectedIds:{defaultValue:null,description:"",name:"selectedIds",required:!1,type:{name:"Set<string | number>"}},onSelectionChange:{defaultValue:null,description:"",name:"onSelectionChange",required:!1,type:{name:"((rows: T[]) => void)"}},getFullRowContent:{defaultValue:null,description:"",name:"getFullRowContent",required:!1,type:{name:"((row: T) => ReactNode)"}},isRowSelectable:{defaultValue:null,description:"",name:"isRowSelectable",required:!1,type:{name:"((row: T) => boolean)"}},noResult:{defaultValue:null,description:"",name:"noResult",required:!0,type:{name:"NoResultProps"}},noData:{defaultValue:null,description:"",name:"noData",required:!0,type:{name:"EmptyStateProps"}}}}}catch{}const z=[{id:1,name:"Alice",email:"alice@example.com",age:27,status:"active",createdAt:"2024-01-05T10:00:00Z",nested:{score:77}},{id:2,name:"Bob",email:"bob@example.com",age:34,status:"inactive",createdAt:"2024-02-01T08:30:00Z",nested:{score:65}},{id:3,name:"Chloe",email:"chloe@example.com",age:22,status:"active",createdAt:"2024-03-12T12:45:00Z",nested:{score:92}},{id:4,name:"Diego",email:"diego@example.com",age:41,status:"active",createdAt:"2024-04-20T15:10:00Z",nested:{score:58}},{id:5,name:"Elise",email:"elise@example.com",age:29,status:"inactive",createdAt:"2024-05-11T09:00:00Z",nested:{score:80}},{id:6,name:"Fares",email:"fares@example.com",age:37,status:"active",createdAt:"2024-06-02T11:15:00Z",nested:{score:71}},{id:7,name:"Gina",email:"gina@example.com",age:31,status:"active",createdAt:"2024-06-18T16:20:00Z",nested:{score:88}},{id:8,name:"Hugo",email:"hugo@example.com",age:25,status:"inactive",createdAt:"2024-07-08T07:05:00Z",nested:{score:54}}],ja=e=>new Date(e).toLocaleDateString("fr-FR",{year:"numeric",month:"short",day:"2-digit"}),c=[{id:"name",label:"Nom",sortable:!0,ordererField:e=>e.name,render:e=>a.jsx("strong",{children:e.name})},{id:"age",label:"Âge",sortable:!0,ordererField:e=>e.age,render:e=>e.age},{id:"created",label:"Créé le",sortable:!0,ordererField:e=>new Date(e.createdAt).getTime(),render:e=>ja(e.createdAt)},{id:"status",label:"Statut",render:e=>a.jsx("span",{"aria-label":`status-${e.id}`,children:e.status==="active"?"Actif":"Inactif"})},{id:"score",label:"Score",sortable:!0,ordererField:e=>e.nested.score,render:e=>e.nested.score}],ea={hasNoData:!1,message:{icon:"📄",title:"Aucune donnée",subtitle:"Commencez par créer un élément pour remplir ce tableau."}},aa={message:"Aucun résultat pour ces filtres.",resetMessage:"Réinitialiser les filtres",onFilterReset:()=>alert("reset filters")},Wa={title:"Design System/Table",component:d,args:{title:"Tableau de données",columns:c,data:z,selectable:!1,isLoading:!1,isSticky:!1,variant:x.SEPARATE,noData:ea,noResult:aa},argTypes:{variant:{control:"inline-radio",options:[x.SEPARATE,x.COLLAPSE]},isLoading:{control:"boolean"},selectable:{control:"boolean"},isSticky:{control:"boolean"}},parameters:{layout:"padded"}},I={render:e=>a.jsx(d,{...e})},V={args:{variant:x.COLLAPSE}},F={args:{isLoading:!0}},q={args:{data:[],noData:{...ea,hasNoData:!1},noResult:{...aa,onFilterReset:()=>alert("Réinitialiser les filtres")}}},L={args:{data:[],noData:{hasNoData:!0,message:{icon:"📭",title:"Rien à afficher",subtitle:"Aucun élément n’a encore été créé."}}}},P={args:{selectable:!0,selectedNumber:"0 sélectionnée"}},H={render:e=>{const[s,r]=b.useState(new Set([2,4])),i=s.size;return a.jsx(d,{...e,selectable:!0,selectedIds:s,selectedNumber:`${i} sélectionnée${i>1?"s":""}`,onSelectionChange:l=>{r(new Set(l.map(p=>p.id)))}})}},$={render:e=>a.jsx(d,{...e,selectable:!0,isRowSelectable:s=>s.status==="active",selectedNumber:"—"})},O={args:{isSticky:!0},render:e=>a.jsx("div",{style:{height:260,overflow:"auto",border:"1px solid #eee"},children:a.jsx(d,{...e,data:[...z,...z]})})},W={args:{columns:[{...c[0],headerHidden:!0},c[1],{...c[2],bodyHidden:!0},c[3],c[4]]}},M={args:{columns:[{...c[0],headerColSpan:2},c[1],c[2],c[3]]}},N={render:e=>{const s=c;return a.jsx(d,{...e,variant:x.COLLAPSE,columns:s,getFullRowContent:r=>r.age>30?a.jsx("div",{style:{padding:"8px",margin:"8px",backgroundColor:"violet",borderRadius:"4px"},children:r.name},r.id):null})}},v={render:e=>{const[s,r]=b.useState(3),i=[...c.slice(0,4),{id:"actions",label:"Actions",render:l=>a.jsx("button",{onClick:p=>{p.stopPropagation(),r(w=>w===l.id?null:l.id)},children:s===l.id?"Fermer":"Voir détails"})}];return a.jsx(d,{...e,columns:i,getFullRowContent:l=>l.id===s?a.jsxs("div",{style:{padding:16},children:[a.jsx("h4",{style:{margin:0},children:l.name}),a.jsxs("p",{style:{margin:"8px 0"},children:["Email: ",a.jsx("strong",{children:l.email})]}),a.jsxs("p",{style:{margin:0},children:["Score: ",a.jsx("strong",{children:l.nested.score})," — Statut:"," ",a.jsx("strong",{children:l.status})]})]}):null})}},B={args:{},render:e=>a.jsx(d,{...e,data:[...z]})};var ie,ce,de;I.parameters={...I.parameters,docs:{...(ie=I.parameters)==null?void 0:ie.docs,source:{originalSource:`{
  render: args => <Table {...args} />
}`,...(de=(ce=I.parameters)==null?void 0:ce.docs)==null?void 0:de.source}}};var ue,me,pe;V.parameters={...V.parameters,docs:{...(ue=V.parameters)==null?void 0:ue.docs,source:{originalSource:`{
  args: {
    variant: TableVariant.COLLAPSE
  }
}`,...(pe=(me=V.parameters)==null?void 0:me.docs)==null?void 0:pe.source}}};var be,he,ge;F.parameters={...F.parameters,docs:{...(be=F.parameters)==null?void 0:be.docs,source:{originalSource:`{
  args: {
    isLoading: true
  }
}`,...(ge=(he=F.parameters)==null?void 0:he.docs)==null?void 0:ge.source}}};var fe,Se,_e;q.parameters={...q.parameters,docs:{...(fe=q.parameters)==null?void 0:fe.docs,source:{originalSource:`{
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
}`,...(_e=(Se=q.parameters)==null?void 0:Se.docs)==null?void 0:_e.source}}};var xe,ye,Ce;L.parameters={...L.parameters,docs:{...(xe=L.parameters)==null?void 0:xe.docs,source:{originalSource:`{
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
}`,...(Ce=(ye=L.parameters)==null?void 0:ye.docs)==null?void 0:Ce.source}}};var je,Ne,ve;P.parameters={...P.parameters,docs:{...(je=P.parameters)==null?void 0:je.docs,source:{originalSource:`{
  args: {
    selectable: true,
    selectedNumber: '0 sélectionnée'
  }
}`,...(ve=(Ne=P.parameters)==null?void 0:Ne.docs)==null?void 0:ve.source}}};var we,Re,Te;H.parameters={...H.parameters,docs:{...(we=H.parameters)==null?void 0:we.docs,source:{originalSource:`{
  render: args => {
    const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set([2, 4]));
    const selectedCount = selectedIds.size;
    return <Table {...args} selectable selectedIds={selectedIds} selectedNumber={\`\${selectedCount} sélectionnée\${selectedCount > 1 ? 's' : ''}\`} onSelectionChange={rows => {
      setSelectedIds(new Set(rows.map(r => r.id)));
    }} />;
  }
}`,...(Te=(Re=H.parameters)==null?void 0:Re.docs)==null?void 0:Te.source}}};var De,Ae,ke;$.parameters={...$.parameters,docs:{...(De=$.parameters)==null?void 0:De.docs,source:{originalSource:`{
  render: args => <Table {...args} selectable isRowSelectable={row => row.status === 'active'} // disable inactive rows
  selectedNumber="—" />
}`,...(ke=(Ae=$.parameters)==null?void 0:Ae.docs)==null?void 0:ke.source}}};var Ee,Ie,Ve;O.parameters={...O.parameters,docs:{...(Ee=O.parameters)==null?void 0:Ee.docs,source:{originalSource:`{
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
}`,...(Ve=(Ie=O.parameters)==null?void 0:Ie.docs)==null?void 0:Ve.source}}};var Fe,qe,Le;W.parameters={...W.parameters,docs:{...(Fe=W.parameters)==null?void 0:Fe.docs,source:{originalSource:`{
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
}`,...(Le=(qe=W.parameters)==null?void 0:qe.docs)==null?void 0:Le.source}}};var Pe,He,$e;M.parameters={...M.parameters,docs:{...(Pe=M.parameters)==null?void 0:Pe.docs,source:{originalSource:`{
  args: {
    columns: [{
      ...baseColumns[0],
      headerColSpan: 2
    },
    // spans two header columns
    baseColumns[1], baseColumns[2], baseColumns[3]]
  }
}`,...($e=(He=M.parameters)==null?void 0:He.docs)==null?void 0:$e.source}}};var Oe,We,Me,Be,ze;N.parameters={...N.parameters,docs:{...(Oe=N.parameters)==null?void 0:Oe.docs,source:{originalSource:`{
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
}`,...(Me=(We=N.parameters)==null?void 0:We.docs)==null?void 0:Me.source},description:{story:`Full-row (colspan) detail row
Your Table renders a second <tr> with a single <td colSpan=...>
whenever getFullRowContent(row) returns a ReactNode.`,...(ze=(Be=N.parameters)==null?void 0:Be.docs)==null?void 0:ze.description}}};var Ze,Ue,Ye,Ge,Je;v.parameters={...v.parameters,docs:{...(Ze=v.parameters)==null?void 0:Ze.docs,source:{originalSource:`{
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
}`,...(Ye=(Ue=v.parameters)==null?void 0:Ue.docs)==null?void 0:Ye.source},description:{story:`Full-row (colspan) detail row
Your Table renders a second <tr> with a single <td colSpan=...>
whenever getFullRowContent(row) returns a ReactNode.`,...(Je=(Ge=v.parameters)==null?void 0:Ge.docs)==null?void 0:Je.description}}};var Ke,Qe,Xe;B.parameters={...B.parameters,docs:{...(Ke=B.parameters)==null?void 0:Ke.docs,source:{originalSource:`{
  args: {
    // keep default columns (sortable on name, age, created, score)
  },
  render: args => <Table {...args} data={[...sampleData]} />
}`,...(Xe=(Qe=B.parameters)==null?void 0:Qe.docs)==null?void 0:Xe.source}}};const Ma=["Basic","CollapseVariant","Loading","NoResults","NoDataState","SelectableUncontrolled","SelectableControlled","SelectableWithDisabledRows","StickyHeaderInScrollContainer","WithHiddenColumns","WithHeaderColSpan","WithFullRowAlwaysDisplayedDetail","WithFullRowDetail","SortingShowcase"];export{I as Basic,V as CollapseVariant,F as Loading,L as NoDataState,q as NoResults,H as SelectableControlled,P as SelectableUncontrolled,$ as SelectableWithDisabledRows,B as SortingShowcase,O as StickyHeaderInScrollContainer,N as WithFullRowAlwaysDisplayedDetail,v as WithFullRowDetail,M as WithHeaderColSpan,W as WithHiddenColumns,Ma as __namedExportsOrder,Wa as default};
