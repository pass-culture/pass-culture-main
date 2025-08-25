import{j as a}from"./jsx-runtime-DF2Pcvd1.js";import{r as b,R as te}from"./index-B2-qRKKC.js";import{c as p}from"./index-DeARc5FM.js";import{C as se}from"./Checkbox-CT71AVYH.js";import{S as da}from"./Skeleton-BUJdKyl6.js";import{f as re}from"./full-down-Cmbtr9nI.js";import{f as ne}from"./full-up-D6TPt2ju.js";import{S as _}from"./SvgIcon-DfLnDDE5.js";import{f as ua}from"./full-refresh-BZh6W0mB.js";import{s as ma}from"./stroke-search-dgesjRZH.js";import{B as pa}from"./Button-3Je6mDU7.js";import{B as ba}from"./types-yVZEaApa.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./Tag-DoB-Hjk-.js";import"./full-thumb-up-Bb4kpRpM.js";import"./stroke-pass-CALgybTM.js";import"./Tooltip-C-mHJC8R.js";import"./Button.module-Md2doL54.js";var x=(e=>(e.ASC="asc",e.DESC="desc",e.NONE="none",e))(x||{});const ga=()=>{const[e,s]=b.useState(null),[r,l]=b.useState("none"),i=b.useCallback(u=>e!==u?(s(u),l("asc"),"asc"):r==="asc"?(l("desc"),"desc"):r==="desc"?(l("none"),"none"):(l("asc"),"asc"),[e,r]);return{currentSortingColumn:e,currentSortingMode:r,onColumnHeaderClick:i}},j={"sorting-icons":"_sorting-icons_1plp3_1","both-icons":"_both-icons_1plp3_17"},J=({sortingMode:e,onClick:s,children:r})=>a.jsxs("button",{type:"button",className:j["sorting-icons"],onClick:s,children:[r,e!==x.NONE?e===x.DESC?a.jsx(_,{className:j["sort-icon"],src:ne,alt:"Ne plus trier",width:"10"}):a.jsx(_,{className:j["sort-icon"],src:re,alt:"Trier par ordre décroissant",width:"10"}):a.jsxs("span",{className:p(j["sort-icon"],j["both-icons"]),children:[a.jsx(_,{src:ne,alt:"Trier par ordre croissant",width:"10"}),a.jsx(_,{src:re,alt:"",width:"10"})]})]});try{J.displayName="SortColumn",J.__docgenInfo={description:"",displayName:"SortColumn",props:{sortingMode:{defaultValue:null,description:"",name:"sortingMode",required:!0,type:{name:"enum",value:[{value:'"asc"'},{value:'"desc"'},{value:'"none"'}]}},onClick:{defaultValue:null,description:"",name:"onClick",required:!0,type:{name:"() => void"}}}}}catch{}const ha="_wrapper_cs7bj_1",fa="_table_cs7bj_5",n={wrapper:ha,table:fa,"table-separate":"_table-separate_cs7bj_14","table-separate-cell":"_table-separate-cell_cs7bj_18","table-collapse":"_table-collapse_cs7bj_35","table-collapse-cell":"_table-collapse-cell_cs7bj_42","table-row":"_table-row_cs7bj_47","table-header":"_table-header_cs7bj_51","table-header-sticky":"_table-header-sticky_cs7bj_57","table-header-th":"_table-header-th_cs7bj_62","table-header-sortable-th":"_table-header-sortable-th_cs7bj_75","table-select-all":"_table-select-all_cs7bj_80","table-checkbox-label":"_table-checkbox-label_cs7bj_86","visually-hidden":"_visually-hidden_cs7bj_98","table-caption-no-display":"_table-caption-no-display_cs7bj_110","table-fullrow-content":"_table-fullrow-content_cs7bj_154"},D={"no-data":"_no-data_1psx1_1","no-data-icon":"_no-data-icon_1psx1_7","no-data-title":"_no-data-title_1psx1_11","no-data-subtitle":"_no-data-subtitle_1psx1_18"},K=({noData:{icon:e,title:s,subtitle:r}})=>a.jsxs("div",{className:D["no-data"],children:[a.jsx(_,{src:e,alt:"",width:"100",className:D["no-data-icon"]}),a.jsx("p",{className:D["no-data-title"],children:s}),a.jsx("p",{className:D["no-data-subtitle"],children:r})]});try{K.displayName="TableNoData",K.__docgenInfo={description:"",displayName:"TableNoData",props:{noData:{defaultValue:null,description:"",name:"noData",required:!0,type:{name:"{ icon: string; title: string; subtitle: string; }"}}}}}catch{}const A={"search-no-results":"_search-no-results_2vpsi_1","search-no-results-icon":"_search-no-results-icon_2vpsi_4","search-no-results-title4":"_search-no-results-title4_2vpsi_8","search-no-results-text":"_search-no-results-text_2vpsi_14"},Q=({colSpan:e=1,message:s="Pas de résultat pour votre recherche",resetMessage:r="Réinitialiser les filtres",resetFilters:l})=>a.jsx("tr",{children:a.jsx("td",{colSpan:e,children:a.jsxs("div",{className:A["search-no-results"],children:[a.jsx(_,{src:ma,alt:"Illustration de recherche",className:A["search-no-results-icon"],width:"124"}),a.jsx("p",{className:A["search-no-results-title4"],children:s}),a.jsx("p",{className:A["search-no-results-text"],children:"Vous pouvez modifier votre recherche ou"}),a.jsx(pa,{variant:ba.TERNARYBRAND,icon:ua,onClick:l,children:r})]})})});try{Q.displayName="TableNoFilterResult",Q.__docgenInfo={description:"",displayName:"TableNoFilterResult",props:{colSpan:{defaultValue:{value:"1"},description:"",name:"colSpan",required:!1,type:{name:"number"}},message:{defaultValue:{value:"Pas de résultat pour votre recherche"},description:"",name:"message",required:!1,type:{name:"string"}},resetMessage:{defaultValue:{value:"Réinitialiser les filtres"},description:"",name:"resetMessage",required:!1,type:{name:"string"}},resetFilters:{defaultValue:null,description:"",name:"resetFilters",required:!0,type:{name:"() => void"}}}}}catch{}var y=(e=>(e.COLLAPSE="collapse",e.SEPARATE="separate",e))(y||{});function G(e,s){if(s)return typeof s=="function"?s(e):typeof s=="string"?s.split(".").reduce((r,l)=>r==null?void 0:r[l],e):e[s]}function d({title:e="Tableau de données",columns:s,data:r,selectable:l=!1,selectedNumber:i,selectedIds:u,className:z,isLoading:ea,isSticky:aa,variant:h,noResult:B,noData:X,onSelectionChange:Z,getFullRowContent:U,isRowSelectable:C}){const{currentSortingColumn:w,currentSortingMode:R,onColumnHeaderClick:ta}=ga(),[sa,ra]=b.useState(new Set),ee=u!==void 0,g=ee?u:sa,Y=t=>{ee||ra(t),Z==null||Z(r.filter(o=>t.has(o.id)))};function na(t){ta(t)}const f=b.useMemo(()=>C?r.filter(C):r,[r,C]),la=()=>{g.size===f.length?Y(new Set):Y(new Set(f.map(t=>t.id)))},oa=t=>{const o=new Set(g);o.has(t.id)?o.delete(t.id):o.add(t.id),Y(o)},ae=b.useMemo(()=>{if(!w)return r;const t=s.find(o=>o.id===w);return t?[...r].sort((o,S)=>{const T=G(o,t.ordererField),m=G(S,t.ordererField);return T===m?0:T<m?R===x.ASC?-1:1:R===x.ASC?1:-1}):r},[r,w,R,s]);return X.hasNoData?a.jsx(K,{noData:X.message}):a.jsxs("div",{className:p(n.wrapper,z),children:[l&&a.jsxs("div",{className:n["table-select-all"],children:[a.jsx(se,{label:g.size<f.length?"Tout sélectionner":"Tout désélectionner",checked:g.size===f.length&&f.length>0,onChange:la,indeterminate:g.size>0&&g.size<f.length}),a.jsx("span",{className:n["visually-hidden"],children:"Sélectionner toutes les lignes"}),a.jsx("div",{children:i})]}),a.jsxs("table",{className:p(n.table,{[n["table-separate"]]:h==="separate",[n["table-collapse"]]:h==="collapse"}),children:[a.jsx("caption",{className:n["table-caption-no-display"],children:e}),a.jsx("thead",{children:a.jsxs("tr",{className:p(n["table-header"],{[n["table-header-sticky"]]:aa}),children:[l&&a.jsx("th",{scope:"col",className:n["table-header-th"],children:a.jsx("span",{className:n["visually-hidden"],children:"Sélectionner"})}),s.map((t,o)=>t.headerHidden?null:a.jsx("th",{scope:"col",id:t.id,colSpan:t.headerColSpan||1,className:p(n.columnWidth,n["table-header-th"],{[n["table-header-sortable-th"]]:t.sortable}),children:t.sortable?a.jsx(J,{onClick:()=>na(t.id),sortingMode:w===t.id?R:x.NONE,children:t.label}):t.label},`col-${t.id}-${o}`))]})}),a.jsxs("tbody",{children:[ea&&Array.from({length:8}).map((t,o)=>a.jsx("tr",{children:a.jsx("td",{colSpan:s.length+1,children:a.jsx(da,{height:"7rem",width:"100%"})})},`loading-row-${s.length}-${o}`)),!ae.length&&a.jsx(Q,{colSpan:s.length+(l?1:0),message:B.message,resetMessage:B.resetMessage,resetFilters:B.onFilterReset}),ae.map(t=>{const o=g.has(t.id),S=U==null?void 0:U(t),T=te.isValidElement(S)&&S.key===t.id.toString();return a.jsxs(te.Fragment,{children:[a.jsxs("tr",{className:p({[n["table-row"]]:!T,[n.selected]:o}),children:[l&&a.jsxs("td",{className:p(n["table-checkbox-cell"],{[n["table-separate-cell"]]:h==="separate",[n["table-collapse-cell"]]:h==="collapse"}),children:[a.jsx(se,{label:t.hasOwnProperty.call(t,"name")?t.name:`ligne ${t.id}`,checked:o,onChange:()=>oa(t),className:n["table-checkbox-label"],disabled:C?!C(t):!1}),a.jsxs("span",{className:n["visually-hidden"],children:["Selectionner la ligne ",t.name||t.id]})]}),s.map((m,ia)=>{if(m.bodyHidden)return null;const ca=m.render?m.render(t):G(t,m.ordererField);return a.jsx("td",{className:p({[n["table-separate-cell"]]:h==="separate",[n["table-collapse-cell"]]:h==="collapse"}),"data-label":m.label,children:ca},`col-${m.id}-${ia}`)})]}),S&&a.jsx("tr",{className:p(n["table-row"]),children:a.jsx("td",{colSpan:s.length+(l?1:0),children:a.jsx("div",{className:n["table-fullrow-content"],children:S})})})]},t.id)})]})]})]})}try{d.displayName="Table",d.__docgenInfo={description:"",displayName:"Table",props:{title:{defaultValue:{value:"Tableau de données"},description:"",name:"title",required:!1,type:{name:"string"}},columns:{defaultValue:null,description:"",name:"columns",required:!0,type:{name:"Column<T>[]"}},data:{defaultValue:null,description:"",name:"data",required:!0,type:{name:"T[]"}},selectable:{defaultValue:{value:"false"},description:"",name:"selectable",required:!1,type:{name:"boolean"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},isLoading:{defaultValue:null,description:"",name:"isLoading",required:!0,type:{name:"boolean"}},isSticky:{defaultValue:null,description:"",name:"isSticky",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!0,type:{name:"enum",value:[{value:'"collapse"'},{value:'"separate"'}]}},selectedNumber:{defaultValue:null,description:"",name:"selectedNumber",required:!1,type:{name:"string"}},selectedIds:{defaultValue:null,description:"",name:"selectedIds",required:!1,type:{name:"Set<string | number>"}},onSelectionChange:{defaultValue:null,description:"",name:"onSelectionChange",required:!1,type:{name:"((rows: T[]) => void)"}},getFullRowContent:{defaultValue:null,description:"",name:"getFullRowContent",required:!1,type:{name:"((row: T) => ReactNode)"}},isRowSelectable:{defaultValue:null,description:"",name:"isRowSelectable",required:!1,type:{name:"((row: T) => boolean)"}},noResult:{defaultValue:null,description:"",name:"noResult",required:!0,type:{name:"NoResultProps"}},noData:{defaultValue:null,description:"",name:"noData",required:!0,type:{name:"EmptyStateProps"}}}}}catch{}const M=[{id:1,name:"Alice",email:"alice@example.com",age:27,status:"active",createdAt:"2024-01-05T10:00:00Z",nested:{score:77}},{id:2,name:"Bob",email:"bob@example.com",age:34,status:"inactive",createdAt:"2024-02-01T08:30:00Z",nested:{score:65}},{id:3,name:"Chloe",email:"chloe@example.com",age:22,status:"active",createdAt:"2024-03-12T12:45:00Z",nested:{score:92}},{id:4,name:"Diego",email:"diego@example.com",age:41,status:"active",createdAt:"2024-04-20T15:10:00Z",nested:{score:58}},{id:5,name:"Elise",email:"elise@example.com",age:29,status:"inactive",createdAt:"2024-05-11T09:00:00Z",nested:{score:80}},{id:6,name:"Fares",email:"fares@example.com",age:37,status:"active",createdAt:"2024-06-02T11:15:00Z",nested:{score:71}},{id:7,name:"Gina",email:"gina@example.com",age:31,status:"active",createdAt:"2024-06-18T16:20:00Z",nested:{score:88}},{id:8,name:"Hugo",email:"hugo@example.com",age:25,status:"inactive",createdAt:"2024-07-08T07:05:00Z",nested:{score:54}}],Sa=e=>new Date(e).toLocaleDateString("fr-FR",{year:"numeric",month:"short",day:"2-digit"}),c=[{id:"name",label:"Nom",sortable:!0,ordererField:e=>e.name,render:e=>a.jsx("strong",{children:e.name})},{id:"age",label:"Âge",sortable:!0,ordererField:e=>e.age,render:e=>e.age},{id:"created",label:"Créé le",sortable:!0,ordererField:e=>new Date(e.createdAt).getTime(),render:e=>Sa(e.createdAt)},{id:"status",label:"Statut",render:e=>a.jsx("span",{"aria-label":`status-${e.id}`,children:e.status==="active"?"Actif":"Inactif"})},{id:"score",label:"Score",sortable:!0,ordererField:e=>e.nested.score,render:e=>e.nested.score}],Qe={hasNoData:!1,message:{icon:"📄",title:"Aucune donnée",subtitle:"Commencez par créer un élément pour remplir ce tableau."}},Xe={message:"Aucun résultat pour ces filtres.",resetMessage:"Réinitialiser les filtres",onFilterReset:()=>alert("reset filters")},La={title:"Design System/Table",component:d,args:{title:"Tableau de données",columns:c,data:M,selectable:!1,isLoading:!1,isSticky:!1,variant:y.SEPARATE,noData:Qe,noResult:Xe},argTypes:{variant:{control:"inline-radio",options:[y.SEPARATE,y.COLLAPSE]},isLoading:{control:"boolean"},selectable:{control:"boolean"},isSticky:{control:"boolean"}},parameters:{layout:"padded"}},k={render:e=>a.jsx(d,{...e})},E={args:{variant:y.COLLAPSE}},I={args:{isLoading:!0}},V={args:{data:[],noData:{...Qe,hasNoData:!1},noResult:{...Xe,onFilterReset:()=>alert("Réinitialiser les filtres")}}},F={args:{data:[],noData:{hasNoData:!0,message:{icon:"📭",title:"Rien à afficher",subtitle:"Aucun élément n’a encore été créé."}}}},q={args:{selectable:!0,selectedNumber:"0 sélectionnée"}},L={render:e=>{const[s,r]=b.useState(new Set([2,4])),l=s.size;return a.jsx(d,{...e,selectable:!0,selectedIds:s,selectedNumber:`${l} sélectionnée${l>1?"s":""}`,onSelectionChange:i=>{r(new Set(i.map(u=>u.id)))}})}},P={render:e=>a.jsx(d,{...e,selectable:!0,isRowSelectable:s=>s.status==="active",selectedNumber:"—"})},H={args:{isSticky:!0},render:e=>a.jsx("div",{style:{height:260,overflow:"auto",border:"1px solid #eee"},children:a.jsx(d,{...e,data:[...M,...M]})})},$={args:{columns:[{...c[0],headerHidden:!0},c[1],{...c[2],bodyHidden:!0},c[3],c[4]]}},O={args:{columns:[{...c[0],headerColSpan:2},c[1],c[2],c[3]]}},N={render:e=>{const s=c;return a.jsx(d,{...e,variant:y.COLLAPSE,columns:s,getFullRowContent:r=>r.age>30?a.jsx("div",{style:{padding:"8px",margin:"8px",backgroundColor:"violet",borderRadius:"4px"},children:r.name},r.id):null})}},v={render:e=>{const[s,r]=b.useState(3),l=[...c.slice(0,4),{id:"actions",label:"Actions",render:i=>a.jsx("button",{onClick:u=>{u.stopPropagation(),r(z=>z===i.id?null:i.id)},children:s===i.id?"Fermer":"Voir détails"})}];return a.jsx(d,{...e,columns:l,getFullRowContent:i=>i.id===s?a.jsxs("div",{style:{padding:16},children:[a.jsx("h4",{style:{margin:0},children:i.name}),a.jsxs("p",{style:{margin:"8px 0"},children:["Email: ",a.jsx("strong",{children:i.email})]}),a.jsxs("p",{style:{margin:0},children:["Score: ",a.jsx("strong",{children:i.nested.score})," — Statut:"," ",a.jsx("strong",{children:i.status})]})]}):null})}},W={args:{},render:e=>a.jsx(d,{...e,data:[...M]})};var le,oe,ie;k.parameters={...k.parameters,docs:{...(le=k.parameters)==null?void 0:le.docs,source:{originalSource:`{
  render: args => <Table {...args} />
}`,...(ie=(oe=k.parameters)==null?void 0:oe.docs)==null?void 0:ie.source}}};var ce,de,ue;E.parameters={...E.parameters,docs:{...(ce=E.parameters)==null?void 0:ce.docs,source:{originalSource:`{
  args: {
    variant: TableVariant.COLLAPSE
  }
}`,...(ue=(de=E.parameters)==null?void 0:de.docs)==null?void 0:ue.source}}};var me,pe,be;I.parameters={...I.parameters,docs:{...(me=I.parameters)==null?void 0:me.docs,source:{originalSource:`{
  args: {
    isLoading: true
  }
}`,...(be=(pe=I.parameters)==null?void 0:pe.docs)==null?void 0:be.source}}};var ge,he,fe;V.parameters={...V.parameters,docs:{...(ge=V.parameters)==null?void 0:ge.docs,source:{originalSource:`{
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
}`,...(fe=(he=V.parameters)==null?void 0:he.docs)==null?void 0:fe.source}}};var Se,_e,xe;F.parameters={...F.parameters,docs:{...(Se=F.parameters)==null?void 0:Se.docs,source:{originalSource:`{
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
}`,...(xe=(_e=F.parameters)==null?void 0:_e.docs)==null?void 0:xe.source}}};var ye,Ce,je;q.parameters={...q.parameters,docs:{...(ye=q.parameters)==null?void 0:ye.docs,source:{originalSource:`{
  args: {
    selectable: true,
    selectedNumber: '0 sélectionnée'
  }
}`,...(je=(Ce=q.parameters)==null?void 0:Ce.docs)==null?void 0:je.source}}};var Ne,ve,we;L.parameters={...L.parameters,docs:{...(Ne=L.parameters)==null?void 0:Ne.docs,source:{originalSource:`{
  render: args => {
    const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set([2, 4]));
    const selectedCount = selectedIds.size;
    return <Table {...args} selectable selectedIds={selectedIds} selectedNumber={\`\${selectedCount} sélectionnée\${selectedCount > 1 ? 's' : ''}\`} onSelectionChange={rows => {
      setSelectedIds(new Set(rows.map(r => r.id)));
    }} />;
  }
}`,...(we=(ve=L.parameters)==null?void 0:ve.docs)==null?void 0:we.source}}};var Re,Te,De;P.parameters={...P.parameters,docs:{...(Re=P.parameters)==null?void 0:Re.docs,source:{originalSource:`{
  render: args => <Table {...args} selectable isRowSelectable={row => row.status === 'active'} // disable inactive rows
  selectedNumber="—" />
}`,...(De=(Te=P.parameters)==null?void 0:Te.docs)==null?void 0:De.source}}};var Ae,ke,Ee;H.parameters={...H.parameters,docs:{...(Ae=H.parameters)==null?void 0:Ae.docs,source:{originalSource:`{
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
}`,...(Ee=(ke=H.parameters)==null?void 0:ke.docs)==null?void 0:Ee.source}}};var Ie,Ve,Fe;$.parameters={...$.parameters,docs:{...(Ie=$.parameters)==null?void 0:Ie.docs,source:{originalSource:`{
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
}`,...(Fe=(Ve=$.parameters)==null?void 0:Ve.docs)==null?void 0:Fe.source}}};var qe,Le,Pe;O.parameters={...O.parameters,docs:{...(qe=O.parameters)==null?void 0:qe.docs,source:{originalSource:`{
  args: {
    columns: [{
      ...baseColumns[0],
      headerColSpan: 2
    },
    // spans two header columns
    baseColumns[1], baseColumns[2], baseColumns[3]]
  }
}`,...(Pe=(Le=O.parameters)==null?void 0:Le.docs)==null?void 0:Pe.source}}};var He,$e,Oe,We,Me;N.parameters={...N.parameters,docs:{...(He=N.parameters)==null?void 0:He.docs,source:{originalSource:`{
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
}`,...(Oe=($e=N.parameters)==null?void 0:$e.docs)==null?void 0:Oe.source},description:{story:`Full-row (colspan) detail row
Your Table renders a second <tr> with a single <td colSpan=...>
whenever getFullRowContent(row) returns a ReactNode.`,...(Me=(We=N.parameters)==null?void 0:We.docs)==null?void 0:Me.description}}};var ze,Be,Ze,Ue,Ye;v.parameters={...v.parameters,docs:{...(ze=v.parameters)==null?void 0:ze.docs,source:{originalSource:`{
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
}`,...(Ze=(Be=v.parameters)==null?void 0:Be.docs)==null?void 0:Ze.source},description:{story:`Full-row (colspan) detail row
Your Table renders a second <tr> with a single <td colSpan=...>
whenever getFullRowContent(row) returns a ReactNode.`,...(Ye=(Ue=v.parameters)==null?void 0:Ue.docs)==null?void 0:Ye.description}}};var Ge,Je,Ke;W.parameters={...W.parameters,docs:{...(Ge=W.parameters)==null?void 0:Ge.docs,source:{originalSource:`{
  args: {
    // keep default columns (sortable on name, age, created, score)
  },
  render: args => <Table {...args} data={[...sampleData]} />
}`,...(Ke=(Je=W.parameters)==null?void 0:Je.docs)==null?void 0:Ke.source}}};const Pa=["Basic","CollapseVariant","Loading","NoResults","NoDataState","SelectableUncontrolled","SelectableControlled","SelectableWithDisabledRows","StickyHeaderInScrollContainer","WithHiddenColumns","WithHeaderColSpan","WithFullRowAlwaysDisplayedDetail","WithFullRowDetail","SortingShowcase"];export{k as Basic,E as CollapseVariant,I as Loading,F as NoDataState,V as NoResults,L as SelectableControlled,q as SelectableUncontrolled,P as SelectableWithDisabledRows,W as SortingShowcase,H as StickyHeaderInScrollContainer,N as WithFullRowAlwaysDisplayedDetail,v as WithFullRowDetail,O as WithHeaderColSpan,$ as WithHiddenColumns,Pa as __namedExportsOrder,La as default};
