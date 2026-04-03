import{i as e}from"./chunk-DseTPa7n.js";import{t}from"./jsx-runtime-BuabnPLX.js";import{t as n}from"./classnames-MYlGWOUq.js";import{i as r,n as i,r as a,t as o}from"./Button-BHr8DO29.js";var s=e(n(),1),c={card:`_card_1iz0g_1`,"card-info":`_card-info_1iz0g_10`,"card-image":`_card-image_1iz0g_14`,"card-header":`_card-header_1iz0g_20`,"card-title":`_card-title_1iz0g_24`,"card-subtitle":`_card-subtitle_1iz0g_30`,"card-content":`_card-content_1iz0g_37`,"card-footer":`_card-footer_1iz0g_48`},l=t(),u=({title:e,subtitle:t,className:n,titleTag:r=`h2`})=>(0,l.jsxs)(`div`,{className:(0,s.default)(c[`card-header`],n),children:[(0,l.jsx)(r,{className:c[`card-title`],children:e}),t&&(0,l.jsx)(`p`,{className:c[`card-subtitle`],children:t})]}),d=({children:e,className:t})=>(0,l.jsx)(`div`,{className:(0,s.default)(c[`card-content`],t),children:e}),f=({children:e,className:t})=>(0,l.jsx)(`div`,{className:(0,s.default)(c[`card-footer`],t),children:e}),p=({src:e,alt:t,className:n})=>(0,l.jsx)(`img`,{src:e,alt:t,className:(0,s.default)(c[`card-image`],n)}),m=({children:e,className:t,variant:n=`default`})=>(0,l.jsx)(`div`,{className:(0,s.default)(c.card,{[c[`card-info`]]:n===`info`},t),children:e});m.Header=u,m.Content=d,m.Footer=f,m.Image=p;try{m.displayName=`Card`,m.__docgenInfo={description:``,displayName:`Card`,props:{className:{defaultValue:null,description:``,name:`className`,required:!1,type:{name:`string`}},variant:{defaultValue:{value:`default`},description:``,name:`variant`,required:!1,type:{name:`enum`,value:[{value:`"default"`},{value:`"info"`}]}}}}}catch{}try{m.Header.displayName=`Card.Header`,m.Header.__docgenInfo={description:``,displayName:`Card.Header`,props:{title:{defaultValue:null,description:``,name:`title`,required:!0,type:{name:`string`}},subtitle:{defaultValue:null,description:``,name:`subtitle`,required:!1,type:{name:`string`}},className:{defaultValue:null,description:``,name:`className`,required:!1,type:{name:`string`}},titleTag:{defaultValue:null,description:``,name:`titleTag`,required:!1,type:{name:`enum`,value:[{value:`"h2"`},{value:`"h3"`},{value:`"h4"`}]}}}}}catch{}try{m.Content.displayName=`Card.Content`,m.Content.__docgenInfo={description:``,displayName:`Card.Content`,props:{className:{defaultValue:null,description:``,name:`className`,required:!1,type:{name:`string`}}}}}catch{}try{m.Footer.displayName=`Card.Footer`,m.Footer.__docgenInfo={description:``,displayName:`Card.Footer`,props:{className:{defaultValue:null,description:``,name:`className`,required:!1,type:{name:`string`}}}}}catch{}try{m.Image.displayName=`Card.Image`,m.Image.__docgenInfo={description:``,displayName:`Card.Image`,props:{src:{defaultValue:null,description:``,name:`src`,required:!0,type:{name:`string`}},alt:{defaultValue:null,description:``,name:`alt`,required:!0,type:{name:`string`}},className:{defaultValue:null,description:``,name:`className`,required:!1,type:{name:`string`}}}}}catch{}var h=``+new URL(`sample-image-landscape-B4GmPBHc.jpg`,import.meta.url).href,g={title:`@/ui-kit/Card`,component:m},_={render:()=>(0,l.jsxs)(m,{children:[(0,l.jsx)(m.Header,{title:`Titre de la carte`,subtitle:`Sous-titre de la carte`}),(0,l.jsx)(m.Content,{children:(0,l.jsx)(`p`,{children:`Contenu de la carte avec des informations utiles.`})}),(0,l.jsx)(m.Footer,{children:(0,l.jsx)(o,{label:`Action principale`})})]})},v={render:()=>(0,l.jsxs)(m,{children:[(0,l.jsx)(m.Image,{src:h,alt:`Image d'exemple`}),(0,l.jsx)(m.Header,{title:`Carte avec image`,subtitle:`L'image a des valeurs par défaut`}),(0,l.jsx)(m.Content,{children:(0,l.jsx)(`p`,{children:`Le composant Card.Image gère automatiquement les dimensions et le border-radius.`})}),(0,l.jsx)(m.Footer,{children:(0,l.jsx)(o,{label:`En savoir plus`})})]})},y={render:()=>(0,l.jsxs)(m,{variant:`info`,children:[(0,l.jsx)(m.Header,{title:`Carte avec variant info`}),(0,l.jsx)(m.Content,{children:(0,l.jsx)(`p`,{children:`Le variant "info" utilise un fond coloré et un bouton transparent pour mettre en avant du contenu important.`})}),(0,l.jsx)(m.Footer,{children:(0,l.jsx)(o,{as:`a`,to:`#`,isExternal:!0,opensInNewTab:!0,label:`En savoir plus`,size:a.SMALL,variant:r.SECONDARY,color:i.NEUTRAL,transparent:!0})})]})},b={render:()=>(0,l.jsxs)(m,{children:[(0,l.jsx)(m.Header,{title:`Carte sans sous-titre`}),(0,l.jsx)(m.Content,{children:(0,l.jsx)(`p`,{children:`Cette carte n'a pas de sous-titre.`})})]})},x={render:()=>(0,l.jsxs)(m,{children:[(0,l.jsx)(m.Header,{title:`Titre en h3`,titleTag:`h3`}),(0,l.jsx)(m.Content,{children:(0,l.jsx)(`p`,{children:`Le titre utilise une balise h3 au lieu du h2 par défaut.`})})]})},S={render:()=>(0,l.jsxs)(`div`,{style:{display:`flex`,gap:`24px`},children:[(0,l.jsxs)(m,{children:[(0,l.jsx)(m.Header,{title:`Carte 1`,subtitle:`Première carte`}),(0,l.jsx)(m.Content,{children:(0,l.jsx)(`p`,{children:`Contenu de la première carte.`})}),(0,l.jsx)(m.Footer,{children:(0,l.jsx)(o,{label:`Action 1`})})]}),(0,l.jsxs)(m,{children:[(0,l.jsx)(m.Header,{title:`Carte 2`,subtitle:`Deuxième carte`}),(0,l.jsx)(m.Content,{children:(0,l.jsx)(`p`,{children:`Contenu de la deuxième carte.`})}),(0,l.jsx)(m.Footer,{children:(0,l.jsx)(o,{label:`Action 2`,variant:r.SECONDARY})})]})]})};_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  render: () => <Card>
      <Card.Header title="Titre de la carte" subtitle="Sous-titre de la carte" />
      <Card.Content>
        <p>Contenu de la carte avec des informations utiles.</p>
      </Card.Content>
      <Card.Footer>
        <Button label="Action principale" />
      </Card.Footer>
    </Card>
}`,..._.parameters?.docs?.source}}},v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
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
}`,...v.parameters?.docs?.source}}},y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
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
}`,...y.parameters?.docs?.source}}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  render: () => <Card>
      <Card.Header title="Carte sans sous-titre" />
      <Card.Content>
        <p>Cette carte n'a pas de sous-titre.</p>
      </Card.Content>
    </Card>
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  render: () => <Card>
      <Card.Header title="Titre en h3" titleTag="h3" />
      <Card.Content>
        <p>Le titre utilise une balise h3 au lieu du h2 par défaut.</p>
      </Card.Content>
    </Card>
}`,...x.parameters?.docs?.source}}},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
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
}`,...S.parameters?.docs?.source}}};var C=[`Default`,`WithImage`,`InfoVariant`,`WithoutSubtitle`,`WithCustomTitleTag`,`SideBySide`];export{_ as Default,y as InfoVariant,S as SideBySide,x as WithCustomTitleTag,v as WithImage,b as WithoutSubtitle,C as __namedExportsOrder,g as default};