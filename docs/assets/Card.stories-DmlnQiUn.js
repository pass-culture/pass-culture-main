import{j as e}from"./jsx-runtime-u17CrQMm.js";import{c as o}from"./index-DgmQ1ES7.js";import{B as i,b as _,a as C,c as x}from"./Button-CswxsKAs.js";import"./iframe-CwnXUavg.js";import"./preload-helper-PPVm8Dsz.js";import"./full-link-D8YFLOxw.js";import"./Tooltip-DfdHuYk7.js";import"./SvgIcon-DuZPzNRk.js";import"./stroke-pass-CALgybTM.js";import"./chunk-LFPYN7LY-qMf7m9Ai.js";const f="_card_1iz0g_1",n={card:f,"card-info":"_card-info_1iz0g_10","card-image":"_card-image_1iz0g_14","card-header":"_card-header_1iz0g_20","card-title":"_card-title_1iz0g_24","card-subtitle":"_card-subtitle_1iz0g_30","card-content":"_card-content_1iz0g_37","card-footer":"_card-footer_1iz0g_48"},h=({title:r,subtitle:t,className:s,titleTag:g="h2"})=>e.jsxs("div",{className:o(n["card-header"],s),children:[e.jsx(g,{className:n["card-title"],children:r}),t&&e.jsx("p",{className:n["card-subtitle"],children:t})]}),j=({children:r,className:t})=>e.jsx("div",{className:o(n["card-content"],t),children:r}),v=({children:r,className:t})=>e.jsx("div",{className:o(n["card-footer"],t),children:r}),y=({src:r,alt:t,className:s})=>e.jsx("img",{src:r,alt:t,className:o(n["card-image"],s)}),a=({children:r,className:t,variant:s="default"})=>e.jsx("div",{className:o(n.card,{[n["card-info"]]:s==="info"},t),children:r});a.Header=h;a.Content=j;a.Footer=v;a.Image=y;try{a.displayName="Card",a.__docgenInfo={description:"",displayName:"Card",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},variant:{defaultValue:{value:"default"},description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"info"'}]}}}}}catch{}try{a.Header.displayName="Card.Header",a.Header.__docgenInfo={description:"",displayName:"Card.Header",props:{title:{defaultValue:null,description:"",name:"title",required:!0,type:{name:"string"}},subtitle:{defaultValue:null,description:"",name:"subtitle",required:!1,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},titleTag:{defaultValue:null,description:"",name:"titleTag",required:!1,type:{name:"enum",value:[{value:'"h2"'},{value:'"h3"'},{value:'"h4"'}]}}}}}catch{}try{a.Content.displayName="Card.Content",a.Content.__docgenInfo={description:"",displayName:"Card.Content",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}try{a.Footer.displayName="Card.Footer",a.Footer.__docgenInfo={description:"",displayName:"Card.Footer",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}try{a.Image.displayName="Card.Image",a.Image.__docgenInfo={description:"",displayName:"Card.Image",props:{src:{defaultValue:null,description:"",name:"src",required:!0,type:{name:"string"}},alt:{defaultValue:null,description:"",name:"alt",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const N=""+new URL("sample-image-landscape-B4GmPBHc.jpg",import.meta.url).href,E={title:"@/ui-kit/Card",component:a},d={render:()=>e.jsxs(a,{children:[e.jsx(a.Header,{title:"Titre de la carte",subtitle:"Sous-titre de la carte"}),e.jsx(a.Content,{children:e.jsx("p",{children:"Contenu de la carte avec des informations utiles."})}),e.jsx(a.Footer,{children:e.jsx(i,{label:"Action principale"})})]})},l={render:()=>e.jsxs(a,{children:[e.jsx(a.Image,{src:N,alt:"Image d'exemple"}),e.jsx(a.Header,{title:"Carte avec image",subtitle:"L'image a des valeurs par défaut"}),e.jsx(a.Content,{children:e.jsx("p",{children:"Le composant Card.Image gère automatiquement les dimensions et le border-radius."})}),e.jsx(a.Footer,{children:e.jsx(i,{label:"En savoir plus"})})]})},c={render:()=>e.jsxs(a,{variant:"info",children:[e.jsx(a.Header,{title:"Carte avec variant info"}),e.jsx(a.Content,{children:e.jsx("p",{children:'Le variant "info" utilise un fond coloré et un bouton transparent pour mettre en avant du contenu important.'})}),e.jsx(a.Footer,{children:e.jsx(i,{as:"a",to:"#",isExternal:!0,opensInNewTab:!0,label:"En savoir plus",size:x.SMALL,variant:C.SECONDARY,color:_.NEUTRAL,transparent:!0})})]})},u={render:()=>e.jsxs(a,{children:[e.jsx(a.Header,{title:"Carte sans sous-titre"}),e.jsx(a.Content,{children:e.jsx("p",{children:"Cette carte n'a pas de sous-titre."})})]})},p={render:()=>e.jsxs(a,{children:[e.jsx(a.Header,{title:"Titre en h3",titleTag:"h3"}),e.jsx(a.Content,{children:e.jsx("p",{children:"Le titre utilise une balise h3 au lieu du h2 par défaut."})})]})},m={render:()=>e.jsxs("div",{style:{display:"flex",gap:"24px"},children:[e.jsxs(a,{children:[e.jsx(a.Header,{title:"Carte 1",subtitle:"Première carte"}),e.jsx(a.Content,{children:e.jsx("p",{children:"Contenu de la première carte."})}),e.jsx(a.Footer,{children:e.jsx(i,{label:"Action 1"})})]}),e.jsxs(a,{children:[e.jsx(a.Header,{title:"Carte 2",subtitle:"Deuxième carte"}),e.jsx(a.Content,{children:e.jsx("p",{children:"Contenu de la deuxième carte."})}),e.jsx(a.Footer,{children:e.jsx(i,{label:"Action 2",variant:C.SECONDARY})})]})]})};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  render: () => <Card>
      <Card.Header title="Titre de la carte" subtitle="Sous-titre de la carte" />
      <Card.Content>
        <p>Contenu de la carte avec des informations utiles.</p>
      </Card.Content>
      <Card.Footer>
        <Button label="Action principale" />
      </Card.Footer>
    </Card>
}`,...d.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  render: () => <Card>
      <Card.Image src={sampleImage} alt="Image d'exemple" />
      <Card.Header title="Carte avec image" subtitle="L'image a des valeurs par défaut" />
      <Card.Content>
        <p>Le composant Card.Image gère automatiquement les dimensions et le border-radius.</p>
      </Card.Content>
      <Card.Footer>
        <Button label="En savoir plus" />
      </Card.Footer>
    </Card>
}`,...l.parameters?.docs?.source}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  render: () => <Card variant="info">
      <Card.Header title="Carte avec variant info" />
      <Card.Content>
        <p>
          Le variant "info" utilise un fond coloré et un bouton transparent
          pour mettre en avant du contenu important.
        </p>
      </Card.Content>
      <Card.Footer>
        <Button as="a" to="#" isExternal opensInNewTab label="En savoir plus" size={ButtonSize.SMALL} variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} transparent />
      </Card.Footer>
    </Card>
}`,...c.parameters?.docs?.source}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  render: () => <Card>
      <Card.Header title="Carte sans sous-titre" />
      <Card.Content>
        <p>Cette carte n'a pas de sous-titre.</p>
      </Card.Content>
    </Card>
}`,...u.parameters?.docs?.source}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  render: () => <Card>
      <Card.Header title="Titre en h3" titleTag="h3" />
      <Card.Content>
        <p>Le titre utilise une balise h3 au lieu du h2 par défaut.</p>
      </Card.Content>
    </Card>
}`,...p.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  render: () => <div style={{
    display: 'flex',
    gap: '24px'
  }}>
      <Card>
        <Card.Header title="Carte 1" subtitle="Première carte" />
        <Card.Content>
          <p>Contenu de la première carte.</p>
        </Card.Content>
        <Card.Footer>
          <Button label="Action 1" />
        </Card.Footer>
      </Card>
      <Card>
        <Card.Header title="Carte 2" subtitle="Deuxième carte" />
        <Card.Content>
          <p>Contenu de la deuxième carte.</p>
        </Card.Content>
        <Card.Footer>
          <Button label="Action 2" variant={ButtonVariant.SECONDARY} />
        </Card.Footer>
      </Card>
    </div>
}`,...m.parameters?.docs?.source}}};const q=["Default","WithImage","InfoVariant","WithoutSubtitle","WithCustomTitleTag","SideBySide"];export{d as Default,c as InfoVariant,m as SideBySide,p as WithCustomTitleTag,l as WithImage,u as WithoutSubtitle,q as __namedExportsOrder,E as default};
