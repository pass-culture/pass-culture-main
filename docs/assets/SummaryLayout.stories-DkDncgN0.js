import{j as e}from"./jsx-runtime-Nms4Y4qS.js";import{K as x}from"./index-BtHzObcb.js";import{c as u}from"./index-BpvXyOxN.js";import{f as h}from"./full-edit-DY97lsf2.js";import{B as q}from"./ButtonLink-D_PmXd41.js";import{D as j}from"./Divider-BT_HSdZX.js";import"./index-BwDkhjyp.js";import"./_commonjsHelpers-BosuxZz1.js";import"./index-DoFAhGZq.js";import"./index-CReuRBEY.js";import"./full-link-Ct7SQyQr.js";import"./SvgIcon-Cibea2Sc.js";import"./Button.module-DJTvdY49.js";import"./types-DjX_gQD6.js";const a={"summary-layout":"_summary-layout_wjvwo_2","summary-layout-content":"_summary-layout-content_wjvwo_8","full-width":"_full-width_wjvwo_11","summary-layout-side":"_summary-layout-side_wjvwo_14","summary-layout-section":"_summary-layout-section_wjvwo_20","summary-layout-section-header":"_summary-layout-section-header_wjvwo_24","summary-layout-section-header-edit-link":"_summary-layout-section-header-edit-link_wjvwo_30","summary-layout-sub-section":"_summary-layout-sub-section_wjvwo_39","summary-layout-sub-section-title":"_summary-layout-sub-section-title_wjvwo_42","summary-layout-row":"_summary-layout-row_wjvwo_49","summary-layout-row-title":"_summary-layout-row-title_wjvwo_53","summary-layout-row-description":"_summary-layout-row-description_wjvwo_57","section-title":"_section-title_wjvwo_75"},p=({className:t,children:i,fullWidth:r=!1})=>e.jsx("div",{className:u(a["summary-layout-content"],t,{[a["full-width"]]:r}),children:i});try{p.displayName="SummaryContent",p.__docgenInfo={description:"",displayName:"SummaryContent",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},fullWidth:{defaultValue:{value:"false"},description:"",name:"fullWidth",required:!1,type:{name:"boolean"}}}}}catch{}const y=({text:t,title:i})=>e.jsxs(e.Fragment,{children:[i&&e.jsxs("span",{className:a["summary-layout-row-title"],children:[i," : "]}),e.jsx("span",{className:a["summary-layout-row-description"],children:t})]}),o=({className:t,descriptions:i})=>{if(i.length===0)return null;if(i.length===1){const{text:r,title:s}=i[0];return e.jsx("div",{className:u(a["summary-layout-row"],t),children:e.jsx(y,{text:r,title:s})})}return e.jsx("ul",{children:i.map(({text:r,title:s},d)=>e.jsx("li",{className:u(a["summary-layout-row"],t),children:e.jsx(y,{text:r,title:s})},d))})};try{o.displayName="SummaryDescriptionList",o.__docgenInfo={description:"",displayName:"SummaryDescriptionList",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},descriptions:{defaultValue:null,description:"",name:"descriptions",required:!0,type:{name:"Description[]"}}}}}catch{}const n=({children:t,className:i})=>e.jsx("div",{className:u(a["summary-layout"],i),children:t});try{n.displayName="SummaryLayout",n.__docgenInfo={description:"",displayName:"SummaryLayout",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const c=({title:t,children:i,className:r,editLink:s,...d})=>e.jsxs("div",{className:u(a["summary-layout-section"],r),children:[e.jsxs("div",{className:a["summary-layout-section-header"],children:[e.jsx("h2",{className:a["section-title"],children:t}),typeof s=="string"?e.jsx(q,{to:s,"aria-label":d["aria-label"],className:a["summary-layout-section-header-edit-link"],icon:h,children:"Modifier"}):s]}),i]});try{c.displayName="SummarySection",c.__docgenInfo={description:"",displayName:"SummarySection",props:{title:{defaultValue:null,description:"",name:"title",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},editLink:{defaultValue:null,description:"",name:"editLink",required:!1,type:{name:"ReactNode"}},"aria-label":{defaultValue:null,description:"",name:"aria-label",required:!1,type:{name:"string"}}}}}catch{}const m=({title:t,children:i,className:r,shouldShowDivider:s=!0})=>e.jsxs("div",{className:u(a["summary-layout-sub-section"],r),children:[e.jsx("h3",{className:a["summary-layout-sub-section-title"],children:t}),i,s&&e.jsx(j,{size:"large"})]});try{m.displayName="SummarySubSection",m.__docgenInfo={description:"",displayName:"SummarySubSection",props:{title:{defaultValue:null,description:"",name:"title",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},shouldShowDivider:{defaultValue:{value:"true"},description:"",name:"shouldShowDivider",required:!1,type:{name:"boolean"}}}}}catch{}const P={title:"components/SummaryLayout",component:n,decorators:[x]},b=()=>e.jsx("div",{style:{width:780},children:e.jsx(n,{children:e.jsxs(p,{children:[e.jsx(c,{title:"Lorem ipsum dolor sit amet",editLink:"/",children:e.jsx(m,{title:"Sub section title",children:e.jsx(o,{descriptions:[{title:"Lorem",text:"Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus."}]})})}),e.jsxs(c,{title:"Lorem ipsum dolor sit amet",editLink:"/",children:[e.jsx(m,{title:"Sub section title",children:e.jsx(o,{descriptions:[{title:"Lorem",text:"Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus."},{title:"Ipsum",text:"Lorem ipsum dolor sit amet"}]})}),e.jsx(m,{title:"Sub section title",children:e.jsx(o,{descriptions:[{text:"Pas de titre"}]})}),e.jsx(m,{title:"Sub section title",children:e.jsx(o,{descriptions:[{title:"Lorem",text:"Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus."},{title:"Ipsum",text:"Lorem ipsum dolor sit amet"}]})})]})]})})}),l=b.bind({});var f,_,S;l.parameters={...l.parameters,docs:{...(f=l.parameters)==null?void 0:f.docs,source:{originalSource:`() => <div style={{
  width: 780
}}>
    <SummaryLayout>
      <SummaryContent>
        <SummarySection title="Lorem ipsum dolor sit amet" editLink="/">
          <SummarySubSection title="Sub section title">
            <SummaryDescriptionList descriptions={[{
            title: 'Lorem',
            text: 'Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus.'
          }]} />
          </SummarySubSection>
        </SummarySection>
        <SummarySection title="Lorem ipsum dolor sit amet" editLink="/">
          <SummarySubSection title="Sub section title">
            <SummaryDescriptionList descriptions={[{
            title: 'Lorem',
            text: 'Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus.'
          }, {
            title: 'Ipsum',
            text: 'Lorem ipsum dolor sit amet'
          }]} />
          </SummarySubSection>

          <SummarySubSection title="Sub section title">
            <SummaryDescriptionList descriptions={[{
            text: 'Pas de titre'
          }]} />
          </SummarySubSection>

          <SummarySubSection title="Sub section title">
            <SummaryDescriptionList descriptions={[{
            title: 'Lorem',
            text: 'Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus.'
          }, {
            title: 'Ipsum',
            text: 'Lorem ipsum dolor sit amet'
          }]} />
          </SummarySubSection>
        </SummarySection>
      </SummaryContent>
    </SummaryLayout>
  </div>`,...(S=(_=l.parameters)==null?void 0:_.docs)==null?void 0:S.source}}};const R=["Default"];export{l as Default,R as __namedExportsOrder,P as default};
