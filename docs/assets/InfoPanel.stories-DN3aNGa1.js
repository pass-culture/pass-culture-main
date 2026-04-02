import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-BlIjmruf.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./classnames-MYlGWOUq.js";import{t as i}from"./SvgIcon-DK-x56iF.js";import{t as a}from"./dist-DsG-rlL9.js";import{a as o,i as s,r as c}from"./iconsList-DsXSjL2h.js";import{t as l}from"./stroke-user-D_V7MbVI.js";t();var u=e(r(),1),d={infopanel:`_infopanel_18993_1`,"infopanel-left-wrapper":`_infopanel-left-wrapper_18993_6`,"infopanel-left-wrapper-icon":`_infopanel-left-wrapper-icon_18993_13`,"infopanel-icon":`_infopanel-icon_18993_13`,"infopanel-left-wrapper-stepnumber":`_infopanel-left-wrapper-stepnumber_18993_16`,"infopanel-content-wrapper":`_infopanel-content-wrapper_18993_20`,"infopanel-small":`_infopanel-small_18993_24`,"infopanel-title":`_infopanel-title_18993_41`,"infopanel-content":`_infopanel-content_18993_20`,"infopanel-large":`_infopanel-large_18993_51`,"infopanel-flat":`_infopanel-flat_18993_111`,"infopanel-elevated":`_infopanel-elevated_18993_114`},f=function(e){return e.FLAT=`flat`,e.ELEVATED=`elevated`,e}({}),p=function(e){return e.LARGE=`large`,e.SMALL=`small`,e}({}),m=n(),h=({title:e,children:t,surface:n,size:r=p.LARGE,icon:a,iconAlt:o,stepNumber:s})=>{let c=s!==void 0;return(0,m.jsxs)(`section`,{className:(0,u.default)(d.infopanel,d[`infopanel-${n}`],d[`infopanel-${r}`]),children:[(0,m.jsxs)(`div`,{className:(0,u.default)(d[`infopanel-left-wrapper`],{[d[`infopanel-left-wrapper-icon`]]:a,[d[`infopanel-left-wrapper-stepnumber`]]:c}),children:[a&&(0,m.jsx)(i,{src:a,alt:o,className:d[`infopanel-icon`]}),c&&s]}),(0,m.jsxs)(`div`,{className:d[`infopanel-content-wrapper`],children:[(0,m.jsx)(`h3`,{className:d[`infopanel-title`],children:e}),(0,m.jsx)(`p`,{className:d[`infopanel-content`],children:t})]})]})};try{h.displayName=`InfoPanel`,h.__docgenInfo={description:``,displayName:`InfoPanel`,props:{title:{defaultValue:null,description:``,name:`title`,required:!0,type:{name:`string`}},surface:{defaultValue:null,description:``,name:`surface`,required:!0,type:{name:`enum`,value:[{value:`"flat"`},{value:`"elevated"`}]}},size:{defaultValue:{value:`InfoPanelSize.LARGE`},description:``,name:`size`,required:!1,type:{name:`enum`,value:[{value:`"large"`},{value:`"small"`}]}},icon:{defaultValue:null,description:``,name:`icon`,required:!1,type:{name:`string`}},iconAlt:{defaultValue:null,description:``,name:`iconAlt`,required:!1,type:{name:`string`}},stepNumber:{defaultValue:null,description:``,name:`stepNumber`,required:!1,type:{name:`number`}}}}}catch{}var g={none:null,...Object.fromEntries(c.map(e=>[e.src.split(`/`).pop()?.replace(`.svg`,``)||``,e.src]))},_={title:`@/ui-kit/InfoPanel`,component:h,decorators:[a],args:{title:`Panel title`,children:`Panel content description.`,size:p.LARGE},argTypes:{surface:{control:`select`,options:Object.values(f),description:"Variante visuelle. `flat` n'a pas de bordure, `elevated` a une bordure."},size:{control:`select`,options:Object.values(p),description:`Taille du panneau.`,table:{defaultValue:{summary:`large`}}},title:{control:`text`,description:`Titre affiché en haut du panneau.`},children:{control:`text`,description:`Contenu du panneau (chaîne de caractères ou JSX).`},stepNumber:{control:`number`,description:`Numéro d'étape affiché à gauche.`},icon:{control:`select`,options:Object.keys(g),mapping:g,description:"Source de l'icône SVG affichée à gauche (uniquement quand `stepNumber` est non-défini)",if:{arg:`stepNumber`,exists:!1}},iconAlt:{control:`text`,description:"Texte alternatif accessible pour l'icône (uniquement quand `stepNumber` est non-défini)",if:{arg:`stepNumber`,exists:!1}}},parameters:{docs:{description:{component:`\`InfoPanel\` affiche une information contextuelle avec un titre et un texte descriptif.

Il supporte deux variantes visuelles (surfaces) :
- **Flat** : affiche une icône ou un numéro d'étape à gauche sur un fond plat.
- **Elevated** : affiche une icône ou un numéro d'étape dans une carte avec bordure.

Chaque surface peut être rendue en deux tailles : \`large\` (par défaut) et \`small\`.`}}}},v={display:`flex`,flexDirection:`row`,gap:`24px`,alignItems:`flex-start`},y={display:`flex`,flexDirection:`column`,gap:`16px`,flex:1},b={args:{title:`4 millions de jeunes`,children:`Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles`,surface:f.FLAT,size:p.LARGE,icon:l,iconAlt:`Profil utilisateur`}},x={args:{title:`Nos équipes valident votre dossier — 48 heures`,children:`Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.`,surface:f.ELEVATED,size:p.LARGE,stepNumber:1}},S={args:{...b.args,size:p.SMALL}},C={args:{...x.args,size:p.SMALL}},w={render:()=>(0,m.jsxs)(`div`,{style:v,children:[(0,m.jsxs)(`div`,{style:y,children:[(0,m.jsx)(`h4`,{children:`Large`}),(0,m.jsx)(h,{title:`4 millions de jeunes`,surface:f.FLAT,size:p.LARGE,icon:l,iconAlt:`Profil utilisateur`,children:`Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles`})]}),(0,m.jsxs)(`div`,{style:y,children:[(0,m.jsx)(`h4`,{children:`Small`}),(0,m.jsx)(h,{title:`4 millions de jeunes`,surface:f.FLAT,size:p.SMALL,icon:l,iconAlt:`Profil utilisateur`,children:`Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles`})]})]})},T={render:()=>(0,m.jsxs)(`div`,{style:v,children:[(0,m.jsxs)(`div`,{style:y,children:[(0,m.jsx)(`h4`,{children:`Large`}),(0,m.jsx)(h,{title:`Nos équipes valident votre dossier — 48 heures`,surface:f.ELEVATED,size:p.LARGE,stepNumber:1,children:`Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.`})]}),(0,m.jsxs)(`div`,{style:y,children:[(0,m.jsx)(`h4`,{children:`Small`}),(0,m.jsx)(h,{title:`Nos équipes valident votre dossier — 48 heures`,surface:f.ELEVATED,size:p.SMALL,stepNumber:1,children:`Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.`})]})]})},E={render:()=>(0,m.jsxs)(`div`,{style:v,children:[(0,m.jsxs)(`div`,{style:y,children:[(0,m.jsx)(`h4`,{children:`Flat Small`}),(0,m.jsxs)(`div`,{style:{...y,gap:`32px`},children:[(0,m.jsx)(h,{title:`Décrivez votre structure et votre activité culturelle - 5 minutes`,surface:f.FLAT,size:p.SMALL,stepNumber:1,children:`Renseignez les informations administratives et les domaines dans lesquels vous intervenez`}),(0,m.jsx)(h,{title:`Nos équipes valident votre dossier — 48 heures`,surface:f.FLAT,size:p.SMALL,stepNumber:2,children:`Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.`}),(0,m.jsx)(h,{title:`Créez vos premières offres - 3 minutes`,surface:f.FLAT,size:p.SMALL,stepNumber:3,children:`Créez vos offres sur pass Culture Pro puis diffusez-les sur l'application pour les jeunes ou sur Adage.`})]})]}),(0,m.jsxs)(`div`,{style:y,children:[(0,m.jsx)(`h4`,{children:`Elevated Small`}),(0,m.jsx)(h,{title:`Décrivez votre structure et votre activité culturelle - 5 minutes`,surface:f.ELEVATED,size:p.SMALL,stepNumber:1,children:`Renseignez les informations administratives et les domaines dans lesquels vous intervenez`}),(0,m.jsx)(h,{title:`Nos équipes valident votre dossier — 48 heures`,surface:f.ELEVATED,size:p.SMALL,stepNumber:2,children:`Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.`}),(0,m.jsx)(h,{title:`Créez vos premières offres - 3 minutes`,surface:f.ELEVATED,size:p.SMALL,stepNumber:3,children:`Créez vos offres sur pass Culture Pro puis diffusez-les sur l'application pour les jeunes ou sur Adage.`})]})]})},D={render:()=>(0,m.jsxs)(`div`,{style:v,children:[(0,m.jsxs)(`div`,{style:y,children:[(0,m.jsx)(`h4`,{children:`Flat Small`}),(0,m.jsxs)(`div`,{style:{...y,gap:`32px`},children:[(0,m.jsx)(h,{title:`4 millions de jeunes`,surface:f.FLAT,size:p.SMALL,icon:l,iconAlt:`Profil utilisateur`,children:`Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles`}),(0,m.jsx)(h,{title:`Une inscription simple et rapide`,surface:f.FLAT,size:p.SMALL,icon:o,iconAlt:`Profil utilisateur`,children:`Contrairement aux appels à projet lourds et complexes, l'inscription à pass Culture Pro est simple et guidée`}),(0,m.jsx)(h,{title:`Publiez quand vous voulez`,surface:f.FLAT,size:p.SMALL,icon:s,iconAlt:`Profil utilisateur`,children:`Créez et modifiez vos offres, qu’elles soient gratuites ou payantes, à tout moment de l’année`})]})]}),(0,m.jsxs)(`div`,{style:y,children:[(0,m.jsx)(`h4`,{children:`Elevated Small`}),(0,m.jsx)(h,{title:`4 millions de jeunes`,surface:f.ELEVATED,size:p.SMALL,icon:o,iconAlt:`Profil utilisateur`,children:`Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles`}),(0,m.jsx)(h,{title:`Une inscription simple et rapide`,surface:f.ELEVATED,size:p.SMALL,icon:l,iconAlt:`Profil utilisateur`,children:`Contrairement aux appels à projet lourds et complexes, l'inscription à pass Culture Pro est simple et guidée`}),(0,m.jsx)(h,{title:`Publiez quand vous voulez`,surface:f.ELEVATED,size:p.SMALL,icon:s,iconAlt:`Profil utilisateur`,children:`Créez et modifiez vos offres, qu’elles soient gratuites ou payantes, à tout moment de l’année`})]})]})};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    title: '4 millions de jeunes',
    children: "Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles",
    surface: InfoPanelSurface.FLAT,
    size: InfoPanelSize.LARGE,
    icon: strokeUserProfile,
    iconAlt: 'Profil utilisateur'
  }
}`,...b.parameters?.docs?.source},description:{story:`Surface flat avec icône. L'icône et son texte alternatif sont requis.`,...b.parameters?.docs?.description}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    title: 'Nos équipes valident votre dossier — 48 heures',
    children: 'Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.',
    surface: InfoPanelSurface.ELEVATED,
    size: InfoPanelSize.LARGE,
    stepNumber: 1
  }
}`,...x.parameters?.docs?.source},description:{story:"Surface elevated avec numéro d'étape. La prop `stepNumber` est requise.",...x.parameters?.docs?.description}}},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  args: {
    ...Flat.args,
    size: InfoPanelSize.SMALL
  }
}`,...S.parameters?.docs?.source},description:{story:`Surface flat en taille small.`,...S.parameters?.docs?.description}}},C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`{
  args: {
    ...Elevated.args,
    size: InfoPanelSize.SMALL
  }
}`,...C.parameters?.docs?.source},description:{story:`Surface elevated en taille small.`,...C.parameters?.docs?.description}}},w.parameters={...w.parameters,docs:{...w.parameters?.docs,source:{originalSource:`{
  render: () => <div style={rowStyles}>
      <div style={columnStyles}>
        <h4>Large</h4>
        <InfoPanel title="4 millions de jeunes" surface={InfoPanelSurface.FLAT} size={InfoPanelSize.LARGE} icon={strokeUserProfile} iconAlt="Profil utilisateur">
          Touchez une audience de 15-21 ans partout en France, activement à la
          recherche d'expériences culturelles
        </InfoPanel>
      </div>
      <div style={columnStyles}>
        <h4>Small</h4>
        <InfoPanel title="4 millions de jeunes" surface={InfoPanelSurface.FLAT} size={InfoPanelSize.SMALL} icon={strokeUserProfile} iconAlt="Profil utilisateur">
          Touchez une audience de 15-21 ans partout en France, activement à la
          recherche d'expériences culturelles
        </InfoPanel>
      </div>
    </div>
}`,...w.parameters?.docs?.source},description:{story:`Comparaison côte à côte des panneaux **flat** dans les deux tailles.`,...w.parameters?.docs?.description}}},T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
  render: () => <div style={rowStyles}>
      <div style={columnStyles}>
        <h4>Large</h4>
        <InfoPanel title="Nos équipes valident votre dossier — 48 heures" surface={InfoPanelSurface.ELEVATED} size={InfoPanelSize.LARGE} stepNumber={1}>
          Elles peuvent demander des documents complémentaires. Les offres
          scolaires nécessitent aussi une validation des équipes externes
          rattachées à Adage.
        </InfoPanel>
      </div>
      <div style={columnStyles}>
        <h4>Small</h4>
        <InfoPanel title="Nos équipes valident votre dossier — 48 heures" surface={InfoPanelSurface.ELEVATED} size={InfoPanelSize.SMALL} stepNumber={1}>
          Elles peuvent demander des documents complémentaires. Les offres
          scolaires nécessitent aussi une validation des équipes externes
          rattachées à Adage.
        </InfoPanel>
      </div>
    </div>
}`,...T.parameters?.docs?.source},description:{story:`Comparaison côte à côte des panneaux **elevated** dans les deux tailles.`,...T.parameters?.docs?.description}}},E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
  render: () => <div style={rowStyles}>
      <div style={columnStyles}>
        <h4>Flat Small</h4>
        <div style={{
        ...columnStyles,
        gap: '32px'
      }}>
          <InfoPanel title="Décrivez votre structure et votre activité culturelle - 5 minutes" surface={InfoPanelSurface.FLAT} size={InfoPanelSize.SMALL} stepNumber={1}>
            Renseignez les informations administratives et les domaines dans lesquels vous intervenez
          </InfoPanel>
          <InfoPanel title="Nos équipes valident votre dossier — 48 heures" surface={InfoPanelSurface.FLAT} size={InfoPanelSize.SMALL} stepNumber={2}>
            Elles peuvent demander des documents complémentaires. Les offres
            scolaires nécessitent aussi une validation des équipes externes
            rattachées à Adage.
          </InfoPanel>
          <InfoPanel title="Créez vos premières offres - 3 minutes" surface={InfoPanelSurface.FLAT} size={InfoPanelSize.SMALL} stepNumber={3}>
            Créez vos offres sur pass Culture Pro puis diffusez-les sur l'application pour les jeunes ou sur Adage.
          </InfoPanel>
        </div>
      </div>
      <div style={columnStyles}>
        <h4>Elevated Small</h4>
        <InfoPanel title="Décrivez votre structure et votre activité culturelle - 5 minutes" surface={InfoPanelSurface.ELEVATED} size={InfoPanelSize.SMALL} stepNumber={1}>
          Renseignez les informations administratives et les domaines dans lesquels vous intervenez
        </InfoPanel>
        <InfoPanel title="Nos équipes valident votre dossier — 48 heures" surface={InfoPanelSurface.ELEVATED} size={InfoPanelSize.SMALL} stepNumber={2}>
          Elles peuvent demander des documents complémentaires. Les offres
          scolaires nécessitent aussi une validation des équipes externes
          rattachées à Adage.
        </InfoPanel>
        <InfoPanel title="Créez vos premières offres - 3 minutes" surface={InfoPanelSurface.ELEVATED} size={InfoPanelSize.SMALL} stepNumber={3}>
          Créez vos offres sur pass Culture Pro puis diffusez-les sur l'application pour les jeunes ou sur Adage.
        </InfoPanel>
      </div>
    </div>
}`,...E.parameters?.docs?.source},description:{story:`Plusieurs panneaux (flat ou elevated) utilisés comme liste d'étapes numérotées.`,...E.parameters?.docs?.description}}},D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  render: () => <div style={rowStyles}>
      <div style={columnStyles}>
        <h4>Flat Small</h4>
        <div style={{
        ...columnStyles,
        gap: '32px'
      }}>
          <InfoPanel title="4 millions de jeunes" surface={InfoPanelSurface.FLAT} size={InfoPanelSize.SMALL} icon={strokeUserProfile} iconAlt="Profil utilisateur">
            Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles
          </InfoPanel>
          <InfoPanel title="Une inscription simple et rapide" surface={InfoPanelSurface.FLAT} size={InfoPanelSize.SMALL} icon={strokeOffer} iconAlt="Profil utilisateur">
            Contrairement aux appels à projet lourds et complexes, l'inscription à pass Culture Pro est simple et guidée
          </InfoPanel>
          <InfoPanel title="Publiez quand vous voulez" surface={InfoPanelSurface.FLAT} size={InfoPanelSize.SMALL} icon={strokeParty} iconAlt="Profil utilisateur">
            Créez et modifiez vos offres, qu’elles soient gratuites ou payantes, à tout moment de l’année
          </InfoPanel>
        </div>
      </div>
      <div style={columnStyles}>
        <h4>Elevated Small</h4>
        <InfoPanel title="4 millions de jeunes" surface={InfoPanelSurface.ELEVATED} size={InfoPanelSize.SMALL} icon={strokeOffer} iconAlt="Profil utilisateur">
          Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles
        </InfoPanel>
        <InfoPanel title="Une inscription simple et rapide" surface={InfoPanelSurface.ELEVATED} size={InfoPanelSize.SMALL} icon={strokeUserProfile} iconAlt="Profil utilisateur">
          Contrairement aux appels à projet lourds et complexes, l'inscription à pass Culture Pro est simple et guidée
        </InfoPanel>
        <InfoPanel title="Publiez quand vous voulez" surface={InfoPanelSurface.ELEVATED} size={InfoPanelSize.SMALL} icon={strokeParty} iconAlt="Profil utilisateur">
          Créez et modifiez vos offres, qu’elles soient gratuites ou payantes, à tout moment de l’année
        </InfoPanel>
      </div>
    </div>
}`,...D.parameters?.docs?.source},description:{story:`Plusieurs panneaux (flat ou elevated) utilisés avec des icônes.`,...D.parameters?.docs?.description}}};var O=[`Flat`,`Elevated`,`FlatSmall`,`ElevatedSmall`,`FlatSizes`,`ElevatedSizes`,`StepList`,`IconsList`];export{x as Elevated,T as ElevatedSizes,C as ElevatedSmall,b as Flat,w as FlatSizes,S as FlatSmall,D as IconsList,E as StepList,O as __namedExportsOrder,_ as default};