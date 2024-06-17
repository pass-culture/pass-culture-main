import{j as e}from"./jsx-runtime-X2b_N9AH.js";import{K as q}from"./index-D8J9PAlt.js";import{c as d}from"./index-BpvXyOxN.js";import{s as i,S as r,a}from"./SummarySubSection-BfOrrpta.js";import{f as x}from"./full-edit-DY97lsf2.js";import{B as L}from"./ButtonLink-Djmtr6Gs.js";import"./index-uCp2LrAq.js";import"./_commonjsHelpers-BosuxZz1.js";import"./index-CWNn-QuQ.js";import"./index-NGkXgOa-.js";import"./index-DoMt6nTV.js";import"./Divider-CReetM2C.js";import"./SvgIcon-DP_815J1.js";import"./Button.module-CvAyM0-b.js";import"./types-DjX_gQD6.js";const c=({className:t,children:m,fullWidth:u=!1})=>e.jsx("div",{className:d(i["summary-layout-content"],t,{[i["full-width"]]:u}),children:m});try{c.displayName="SummaryContent",c.__docgenInfo={description:"",displayName:"SummaryContent",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},fullWidth:{defaultValue:{value:"false"},description:"",name:"fullWidth",required:!1,type:{name:"boolean"}}}}}catch{}const s=({children:t,className:m})=>e.jsx("div",{className:d(i["summary-layout"],m),children:t});try{s.displayName="SummaryLayout",s.__docgenInfo={description:"",displayName:"SummaryLayout",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const n=({title:t,children:m,className:u,editLink:l,...S})=>e.jsxs("div",{className:d(i["summary-layout-section"],u),children:[e.jsxs("div",{className:i["summary-layout-section-header"],children:[e.jsx("h2",{className:i["section-title"],children:t}),typeof l=="string"?e.jsx(L,{link:{to:l,isExternal:!1,"aria-label":S["aria-label"]},className:i["summary-layout-section-header-edit-link"],icon:x,children:"Modifier"}):l]}),m]});try{n.displayName="SummarySection",n.__docgenInfo={description:"",displayName:"SummarySection",props:{title:{defaultValue:null,description:"",name:"title",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},editLink:{defaultValue:null,description:"",name:"editLink",required:!1,type:{name:"ReactNode"}},"aria-label":{defaultValue:null,description:"",name:"aria-label",required:!1,type:{name:"string"}}}}}catch{}const K={title:"components/SummaryLayout",component:s,decorators:[q]},b=()=>e.jsx("div",{style:{width:780},children:e.jsx(s,{children:e.jsxs(c,{children:[e.jsx(n,{title:"Lorem ipsum dolor sit amet",editLink:"/",children:e.jsx(r,{title:"Sub section title",children:e.jsx(a,{descriptions:[{title:"Lorem",text:"Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus."}]})})}),e.jsxs(n,{title:"Lorem ipsum dolor sit amet",editLink:"/",children:[e.jsx(r,{title:"Sub section title",children:e.jsx(a,{descriptions:[{title:"Lorem",text:"Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus."},{title:"Ipsum",text:"Lorem ipsum dolor sit amet"}]})}),e.jsx(r,{title:"Sub section title",children:e.jsx(a,{descriptions:[{text:"Pas de titre"}]})}),e.jsx(r,{title:"Sub section title",children:e.jsx(a,{descriptions:[{title:"Lorem",text:"Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus."},{title:"Ipsum",text:"Lorem ipsum dolor sit amet"}]})})]})]})})}),o=b.bind({});var p,f,y;o.parameters={...o.parameters,docs:{...(p=o.parameters)==null?void 0:p.docs,source:{originalSource:`() => <div style={{
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
  </div>`,...(y=(f=o.parameters)==null?void 0:f.docs)==null?void 0:y.source}}};const P=["Default"];export{o as Default,P as __namedExportsOrder,K as default};
