import{a as e,n as t}from"./chunk-DnJy8xQt.js";import{S as n}from"./iframe-XvC5t-WH.js";import{t as r}from"./jsx-runtime-BGU0mfus.js";import{t as i}from"./classnames-6GGtIhaA.js";import{n as a,t as o}from"./SvgIcon-81PoVxLd.js";import{n as s,t as c}from"./dist-07MscONQ.js";import{a as l,c as u,i as d,n as f,o as p,s as m}from"./iconsList-C9yGTkY9.js";import{n as h,t as g}from"./stroke-user-CwPft_Ws.js";var _,v,y=t((()=>{_=`_infopanel_18993_1`,v={infopanel:_,"infopanel-left-wrapper":`_infopanel-left-wrapper_18993_6`,"infopanel-left-wrapper-icon":`_infopanel-left-wrapper-icon_18993_13`,"infopanel-icon":`_infopanel-icon_18993_13`,"infopanel-left-wrapper-stepnumber":`_infopanel-left-wrapper-stepnumber_18993_16`,"infopanel-content-wrapper":`_infopanel-content-wrapper_18993_20`,"infopanel-small":`_infopanel-small_18993_24`,"infopanel-title":`_infopanel-title_18993_41`,"infopanel-content":`_infopanel-content_18993_20`,"infopanel-large":`_infopanel-large_18993_51`,"infopanel-flat":`_infopanel-flat_18993_111`,"infopanel-elevated":`_infopanel-elevated_18993_114`}})),b,x,S=t((()=>{b=function(e){return e.FLAT=`flat`,e.ELEVATED=`elevated`,e}({}),x=function(e){return e.LARGE=`large`,e.SMALL=`small`,e}({})})),C,w,T,E=t((()=>{C=e(i(),1),a(),y(),S(),w=r(),T=({title:e,children:t,surface:n,size:r=x.LARGE,icon:i,iconAlt:a,stepNumber:s})=>{let c=s!==void 0;return(0,w.jsxs)(`section`,{className:(0,C.default)(v.infopanel,v[`infopanel-${n}`],v[`infopanel-${r}`]),children:[(0,w.jsxs)(`div`,{className:(0,C.default)(v[`infopanel-left-wrapper`],{[v[`infopanel-left-wrapper-icon`]]:i,[v[`infopanel-left-wrapper-stepnumber`]]:c}),children:[i&&(0,w.jsx)(o,{src:i,alt:a,className:v[`infopanel-icon`]}),c&&s]}),(0,w.jsxs)(`div`,{className:v[`infopanel-content-wrapper`],children:[(0,w.jsx)(`h3`,{className:v[`infopanel-title`],children:e}),(0,w.jsx)(`p`,{className:v[`infopanel-content`],children:t})]})]})};try{T.displayName=`InfoPanel`,T.__docgenInfo={description:``,displayName:`InfoPanel`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/InfoPanel/InfoPanel.tsx`,methods:[],props:{title:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/InfoPanel/types.ts`,name:`TypeLiteral`}],description:``,name:`title`,required:!0,tags:{},type:{name:`string`}},surface:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/InfoPanel/types.ts`,name:`TypeLiteral`}],description:``,name:`surface`,required:!0,tags:{},type:{name:`enum`,raw:`InfoPanelSurface`,value:[{value:`"flat"`,description:``,fullComment:``,tags:{}},{value:`"elevated"`,description:``,fullComment:``,tags:{}}]}},size:{defaultValue:{value:`InfoPanelSize.LARGE`},declarations:[{fileName:`pro/src/ui-kit/InfoPanel/types.ts`,name:`TypeLiteral`}],description:``,name:`size`,required:!1,tags:{},type:{name:`enum`,raw:`InfoPanelSize`,value:[{value:`"large"`,description:``,fullComment:``,tags:{}},{value:`"small"`,description:``,fullComment:``,tags:{}}]}},icon:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/InfoPanel/types.ts`,name:`TypeLiteral`},{fileName:`pro/src/ui-kit/InfoPanel/types.ts`,name:`TypeLiteral`}],description:``,name:`icon`,required:!1,tags:{},type:{name:`string`}},iconAlt:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/InfoPanel/types.ts`,name:`TypeLiteral`},{fileName:`pro/src/ui-kit/InfoPanel/types.ts`,name:`TypeLiteral`}],description:``,name:`iconAlt`,required:!1,tags:{},type:{name:`string`}},stepNumber:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/InfoPanel/types.ts`,name:`TypeLiteral`},{fileName:`pro/src/ui-kit/InfoPanel/types.ts`,name:`TypeLiteral`}],description:``,name:`stepNumber`,required:!1,tags:{},type:{name:`number`}}},tags:{}}}catch{}})),D,O,k,A,j,M,N,P,F,I,L,R,z,B;t((()=>{n(),s(),g(),m(),l(),f(),E(),S(),D=r(),O={none:null,...Object.fromEntries(d.map(e=>[e.src.split(`/`).pop()?.replace(`.svg`,``)||``,e.src]))},k={title:`@/ui-kit/InfoPanel`,component:T,decorators:[c],args:{title:`Panel title`,children:`Panel content description.`,size:x.LARGE},argTypes:{surface:{control:`select`,options:Object.values(b),description:"Variante visuelle. `flat` n'a pas de bordure, `elevated` a une bordure."},size:{control:`select`,options:Object.values(x),description:`Taille du panneau.`,table:{defaultValue:{summary:`large`}}},title:{control:`text`,description:`Titre affiché en haut du panneau.`},children:{control:`text`,description:`Contenu du panneau (chaîne de caractères ou JSX).`},stepNumber:{control:`number`,description:`Numéro d'étape affiché à gauche.`},icon:{control:`select`,options:Object.keys(O),mapping:O,description:"Source de l'icône SVG affichée à gauche (uniquement quand `stepNumber` est non-défini)",if:{arg:`stepNumber`,exists:!1}},iconAlt:{control:`text`,description:"Texte alternatif accessible pour l'icône (uniquement quand `stepNumber` est non-défini)",if:{arg:`stepNumber`,exists:!1}}},parameters:{docs:{description:{component:`\`InfoPanel\` affiche une information contextuelle avec un titre et un texte descriptif.

Il supporte deux variantes visuelles (surfaces) :
- **Flat** : affiche une icône ou un numéro d'étape à gauche sur un fond plat.
- **Elevated** : affiche une icône ou un numéro d'étape dans une carte avec bordure.

Chaque surface peut être rendue en deux tailles : \`large\` (par défaut) et \`small\`.`}}}},A={display:`flex`,flexDirection:`row`,gap:`24px`,alignItems:`flex-start`},j={display:`flex`,flexDirection:`column`,gap:`16px`,flex:1},M={args:{title:`4 millions de jeunes`,children:`Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles`,surface:b.FLAT,size:x.LARGE,icon:h,iconAlt:`Profil utilisateur`}},N={args:{title:`Nos équipes valident votre dossier — 48 heures`,children:`Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.`,surface:b.ELEVATED,size:x.LARGE,stepNumber:1}},P={args:{...M.args,size:x.SMALL}},F={args:{...N.args,size:x.SMALL}},I={render:()=>(0,D.jsxs)(`div`,{style:A,children:[(0,D.jsxs)(`div`,{style:j,children:[(0,D.jsx)(`h4`,{children:`Large`}),(0,D.jsx)(T,{title:`4 millions de jeunes`,surface:b.FLAT,size:x.LARGE,icon:h,iconAlt:`Profil utilisateur`,children:`Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles`})]}),(0,D.jsxs)(`div`,{style:j,children:[(0,D.jsx)(`h4`,{children:`Small`}),(0,D.jsx)(T,{title:`4 millions de jeunes`,surface:b.FLAT,size:x.SMALL,icon:h,iconAlt:`Profil utilisateur`,children:`Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles`})]})]})},L={render:()=>(0,D.jsxs)(`div`,{style:A,children:[(0,D.jsxs)(`div`,{style:j,children:[(0,D.jsx)(`h4`,{children:`Large`}),(0,D.jsx)(T,{title:`Nos équipes valident votre dossier — 48 heures`,surface:b.ELEVATED,size:x.LARGE,stepNumber:1,children:`Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.`})]}),(0,D.jsxs)(`div`,{style:j,children:[(0,D.jsx)(`h4`,{children:`Small`}),(0,D.jsx)(T,{title:`Nos équipes valident votre dossier — 48 heures`,surface:b.ELEVATED,size:x.SMALL,stepNumber:1,children:`Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.`})]})]})},R={render:()=>(0,D.jsxs)(`div`,{style:A,children:[(0,D.jsxs)(`div`,{style:j,children:[(0,D.jsx)(`h4`,{children:`Flat Small`}),(0,D.jsxs)(`div`,{style:{...j,gap:`32px`},children:[(0,D.jsx)(T,{title:`Décrivez votre structure et votre activité culturelle - 5 minutes`,surface:b.FLAT,size:x.SMALL,stepNumber:1,children:`Renseignez les informations administratives et les domaines dans lesquels vous intervenez`}),(0,D.jsx)(T,{title:`Nos équipes valident votre dossier — 48 heures`,surface:b.FLAT,size:x.SMALL,stepNumber:2,children:`Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.`}),(0,D.jsx)(T,{title:`Créez vos premières offres - 3 minutes`,surface:b.FLAT,size:x.SMALL,stepNumber:3,children:`Créez vos offres sur pass Culture Pro puis diffusez-les sur l'application pour les jeunes ou sur Adage.`})]})]}),(0,D.jsxs)(`div`,{style:j,children:[(0,D.jsx)(`h4`,{children:`Elevated Small`}),(0,D.jsx)(T,{title:`Décrivez votre structure et votre activité culturelle - 5 minutes`,surface:b.ELEVATED,size:x.SMALL,stepNumber:1,children:`Renseignez les informations administratives et les domaines dans lesquels vous intervenez`}),(0,D.jsx)(T,{title:`Nos équipes valident votre dossier — 48 heures`,surface:b.ELEVATED,size:x.SMALL,stepNumber:2,children:`Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.`}),(0,D.jsx)(T,{title:`Créez vos premières offres - 3 minutes`,surface:b.ELEVATED,size:x.SMALL,stepNumber:3,children:`Créez vos offres sur pass Culture Pro puis diffusez-les sur l'application pour les jeunes ou sur Adage.`})]})]})},z={render:()=>(0,D.jsxs)(`div`,{style:A,children:[(0,D.jsxs)(`div`,{style:j,children:[(0,D.jsx)(`h4`,{children:`Flat Small`}),(0,D.jsxs)(`div`,{style:{...j,gap:`32px`},children:[(0,D.jsx)(T,{title:`4 millions de jeunes`,surface:b.FLAT,size:x.SMALL,icon:h,iconAlt:`Profil utilisateur`,children:`Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles`}),(0,D.jsx)(T,{title:`Une inscription simple et rapide`,surface:b.FLAT,size:x.SMALL,icon:u,iconAlt:`Profil utilisateur`,children:`Contrairement aux appels à projet lourds et complexes, l'inscription à pass Culture Pro est simple et guidée`}),(0,D.jsx)(T,{title:`Publiez quand vous voulez`,surface:b.FLAT,size:x.SMALL,icon:p,iconAlt:`Profil utilisateur`,children:`Créez et modifiez vos offres, qu’elles soient gratuites ou payantes, à tout moment de l’année`})]})]}),(0,D.jsxs)(`div`,{style:j,children:[(0,D.jsx)(`h4`,{children:`Elevated Small`}),(0,D.jsx)(T,{title:`4 millions de jeunes`,surface:b.ELEVATED,size:x.SMALL,icon:u,iconAlt:`Profil utilisateur`,children:`Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles`}),(0,D.jsx)(T,{title:`Une inscription simple et rapide`,surface:b.ELEVATED,size:x.SMALL,icon:h,iconAlt:`Profil utilisateur`,children:`Contrairement aux appels à projet lourds et complexes, l'inscription à pass Culture Pro est simple et guidée`}),(0,D.jsx)(T,{title:`Publiez quand vous voulez`,surface:b.ELEVATED,size:x.SMALL,icon:p,iconAlt:`Profil utilisateur`,children:`Créez et modifiez vos offres, qu’elles soient gratuites ou payantes, à tout moment de l’année`})]})]})},M.parameters={...M.parameters,docs:{...M.parameters?.docs,source:{originalSource:`{
  args: {
    title: '4 millions de jeunes',
    children: "Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles",
    surface: InfoPanelSurface.FLAT,
    size: InfoPanelSize.LARGE,
    icon: strokeUserProfile,
    iconAlt: 'Profil utilisateur'
  }
}`,...M.parameters?.docs?.source},description:{story:`Surface flat avec icône. L'icône et son texte alternatif sont requis.`,...M.parameters?.docs?.description}}},N.parameters={...N.parameters,docs:{...N.parameters?.docs,source:{originalSource:`{
  args: {
    title: 'Nos équipes valident votre dossier — 48 heures',
    children: 'Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.',
    surface: InfoPanelSurface.ELEVATED,
    size: InfoPanelSize.LARGE,
    stepNumber: 1
  }
}`,...N.parameters?.docs?.source},description:{story:"Surface elevated avec numéro d'étape. La prop `stepNumber` est requise.",...N.parameters?.docs?.description}}},P.parameters={...P.parameters,docs:{...P.parameters?.docs,source:{originalSource:`{
  args: {
    ...Flat.args,
    size: InfoPanelSize.SMALL
  }
}`,...P.parameters?.docs?.source},description:{story:`Surface flat en taille small.`,...P.parameters?.docs?.description}}},F.parameters={...F.parameters,docs:{...F.parameters?.docs,source:{originalSource:`{
  args: {
    ...Elevated.args,
    size: InfoPanelSize.SMALL
  }
}`,...F.parameters?.docs?.source},description:{story:`Surface elevated en taille small.`,...F.parameters?.docs?.description}}},I.parameters={...I.parameters,docs:{...I.parameters?.docs,source:{originalSource:`{
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
}`,...I.parameters?.docs?.source},description:{story:`Comparaison côte à côte des panneaux **flat** dans les deux tailles.`,...I.parameters?.docs?.description}}},L.parameters={...L.parameters,docs:{...L.parameters?.docs,source:{originalSource:`{
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
}`,...L.parameters?.docs?.source},description:{story:`Comparaison côte à côte des panneaux **elevated** dans les deux tailles.`,...L.parameters?.docs?.description}}},R.parameters={...R.parameters,docs:{...R.parameters?.docs,source:{originalSource:`{
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
}`,...R.parameters?.docs?.source},description:{story:`Plusieurs panneaux (flat ou elevated) utilisés comme liste d'étapes numérotées.`,...R.parameters?.docs?.description}}},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
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
}`,...z.parameters?.docs?.source},description:{story:`Plusieurs panneaux (flat ou elevated) utilisés avec des icônes.`,...z.parameters?.docs?.description}}},B=[`Flat`,`Elevated`,`FlatSmall`,`ElevatedSmall`,`FlatSizes`,`ElevatedSizes`,`StepList`,`IconsList`]}))();export{N as Elevated,L as ElevatedSizes,F as ElevatedSmall,M as Flat,I as FlatSizes,P as FlatSmall,z as IconsList,R as StepList,B as __namedExportsOrder,k as default};