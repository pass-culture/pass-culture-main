import{j as e}from"./jsx-runtime-u17CrQMm.js";import{V as T}from"./index-fOp-Lm1j.js";import{s as v}from"./stroke-user-u-f9pznf.js";import{a as P,b as x,s as _}from"./iconsList-D62-xbC4.js";import{c as E}from"./index-DDxytC1g.js";import{S as b}from"./SvgIcon-DuZPzNRk.js";import"./iframe-bFIKgCwh.js";import"./preload-helper-PPVm8Dsz.js";import"./chunk-LFPYN7LY-DZyVkyWz.js";import"./full-thumb-up-B5qPZKde.js";import"./full-bulb-PM9lEXbZ.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-down-Cmbtr9nI.js";import"./full-download-XQM5pv74.js";import"./full-duplicate-DkJBC6en.js";import"./full-edit-CxAaM2Fv.js";import"./full-error-BFAmjN4t.js";import"./full-show-C6WS4j9u.js";import"./full-info-D24AtBVt.js";import"./full-left-vjwAEs82.js";import"./full-link-D8YFLOxw.js";import"./full-location-BXQqoJrQ.js";import"./full-more-CW05xvvr.js";import"./full-next-B_76kGmE.js";import"./full-refresh-BZh6W0mB.js";import"./full-right-Dd3YsyCq.js";import"./full-three-dots-C5Ey0HNi.js";import"./full-up-D6TPt2ju.js";import"./full-validate-CbMNulkZ.js";import"./stroke-close-DnlFsd1c.js";import"./stroke-date-CWTXq8J4.js";import"./stroke-price-CbFScctA.js";import"./stroke-error-DSZD431a.js";import"./stroke-pass-CALgybTM.js";import"./stroke-picture-CuOPiYLi.js";import"./stroke-search-D6-mXEew.js";import"./stroke-thing-DUCGOIkU.js";import"./stroke-trash-Cc_5v2lW.js";import"./stroke-video-Ci8i7Kz7.js";import"./stroke-wrong-BAouvvNg.js";const q="_infopanel_18993_1",i={infopanel:q,"infopanel-left-wrapper":"_infopanel-left-wrapper_18993_6","infopanel-left-wrapper-icon":"_infopanel-left-wrapper-icon_18993_13","infopanel-icon":"_infopanel-icon_18993_13","infopanel-left-wrapper-stepnumber":"_infopanel-left-wrapper-stepnumber_18993_16","infopanel-content-wrapper":"_infopanel-content-wrapper_18993_20","infopanel-small":"_infopanel-small_18993_24","infopanel-title":"_infopanel-title_18993_41","infopanel-content":"_infopanel-content_18993_20","infopanel-large":"_infopanel-large_18993_51","infopanel-flat":"_infopanel-flat_18993_111","infopanel-elevated":"_infopanel-elevated_18993_114"};var n=(r=>(r.FLAT="flat",r.ELEVATED="elevated",r))(n||{}),s=(r=>(r.LARGE="large",r.SMALL="small",r))(s||{});const t=({title:r,children:S,surface:g,size:y=s.LARGE,icon:L,iconAlt:j,stepNumber:z})=>{const A=z!==void 0;return e.jsxs("section",{className:E(i.infopanel,i[`infopanel-${g}`],i[`infopanel-${y}`]),children:[e.jsxs("div",{className:E(i["infopanel-left-wrapper"],{[i["infopanel-left-wrapper-icon"]]:L,[i["infopanel-left-wrapper-stepnumber"]]:A}),children:[L&&e.jsx(b,{src:L,alt:j,className:i["infopanel-icon"]}),A&&z]}),e.jsxs("div",{className:i["infopanel-content-wrapper"],children:[e.jsx("h3",{className:i["infopanel-title"],children:r}),e.jsx("p",{className:i["infopanel-content"],children:S})]})]})};try{t.displayName="InfoPanel",t.__docgenInfo={description:"",displayName:"InfoPanel",props:{title:{defaultValue:null,description:"",name:"title",required:!0,type:{name:"string"}},surface:{defaultValue:null,description:"",name:"surface",required:!0,type:{name:"enum",value:[{value:'"flat"'},{value:'"elevated"'}]}},size:{defaultValue:{value:"InfoPanelSize.LARGE"},description:"",name:"size",required:!1,type:{name:"enum",value:[{value:'"large"'},{value:'"small"'}]}},icon:{defaultValue:null,description:"",name:"icon",required:!1,type:{name:"string"}},iconAlt:{defaultValue:null,description:"",name:"iconAlt",required:!1,type:{name:"string"}},stepNumber:{defaultValue:null,description:"",name:"stepNumber",required:!1,type:{name:"number"}}}}}catch{}const I={none:null,...Object.fromEntries(_.map(r=>[r.src.split("/").pop()?.replace(".svg","")||"",r.src]))},ze={title:"@/ui-kit/InfoPanel",component:t,decorators:[T],args:{title:"Panel title",children:"Panel content description.",size:s.LARGE},argTypes:{surface:{control:"select",options:Object.values(n),description:"Variante visuelle. `flat` n'a pas de bordure, `elevated` a une bordure."},size:{control:"select",options:Object.values(s),description:"Taille du panneau.",table:{defaultValue:{summary:"large"}}},title:{control:"text",description:"Titre affiché en haut du panneau."},children:{control:"text",description:"Contenu du panneau (chaîne de caractères ou JSX)."},stepNumber:{control:"number",description:"Numéro d'étape affiché à gauche."},icon:{control:"select",options:Object.keys(I),mapping:I,description:"Source de l'icône SVG affichée à gauche (uniquement quand `stepNumber` est non-défini)",if:{arg:"stepNumber",exists:!1}},iconAlt:{control:"text",description:"Texte alternatif accessible pour l'icône (uniquement quand `stepNumber` est non-défini)",if:{arg:"stepNumber",exists:!1}}},parameters:{docs:{description:{component:"`InfoPanel` affiche une information contextuelle avec un titre et un texte descriptif.\n\nIl supporte deux variantes visuelles (surfaces) :\n- **Flat** : affiche une icône ou un numéro d'étape à gauche sur un fond plat.\n- **Elevated** : affiche une icône ou un numéro d'étape dans une carte avec bordure.\n\nChaque surface peut être rendue en deux tailles : `large` (par défaut) et `small`."}}}},h={display:"flex",flexDirection:"row",gap:"24px",alignItems:"flex-start"},a={display:"flex",flexDirection:"column",gap:"16px",flex:1},l={args:{title:"4 millions de jeunes",children:"Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles",surface:n.FLAT,size:s.LARGE,icon:v,iconAlt:"Profil utilisateur"}},o={args:{title:"Nos équipes valident votre dossier — 48 heures",children:"Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.",surface:n.ELEVATED,size:s.LARGE,stepNumber:1}},u={args:{...l.args,size:s.SMALL}},c={args:{...o.args,size:s.SMALL}},d={render:()=>e.jsxs("div",{style:h,children:[e.jsxs("div",{style:a,children:[e.jsx("h4",{children:"Large"}),e.jsx(t,{title:"4 millions de jeunes",surface:n.FLAT,size:s.LARGE,icon:v,iconAlt:"Profil utilisateur",children:"Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles"})]}),e.jsxs("div",{style:a,children:[e.jsx("h4",{children:"Small"}),e.jsx(t,{title:"4 millions de jeunes",surface:n.FLAT,size:s.SMALL,icon:v,iconAlt:"Profil utilisateur",children:"Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles"})]})]})},p={render:()=>e.jsxs("div",{style:h,children:[e.jsxs("div",{style:a,children:[e.jsx("h4",{children:"Large"}),e.jsx(t,{title:"Nos équipes valident votre dossier — 48 heures",surface:n.ELEVATED,size:s.LARGE,stepNumber:1,children:"Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage."})]}),e.jsxs("div",{style:a,children:[e.jsx("h4",{children:"Small"}),e.jsx(t,{title:"Nos équipes valident votre dossier — 48 heures",surface:n.ELEVATED,size:s.SMALL,stepNumber:1,children:"Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage."})]})]})},f={render:()=>e.jsxs("div",{style:h,children:[e.jsxs("div",{style:a,children:[e.jsx("h4",{children:"Flat Small"}),e.jsxs("div",{style:{...a,gap:"32px"},children:[e.jsx(t,{title:"Décrivez votre structure et votre activité culturelle - 5 minutes",surface:n.FLAT,size:s.SMALL,stepNumber:1,children:"Renseignez les informations administratives et les domaines dans lesquels vous intervenez"}),e.jsx(t,{title:"Nos équipes valident votre dossier — 48 heures",surface:n.FLAT,size:s.SMALL,stepNumber:2,children:"Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage."}),e.jsx(t,{title:"Créez vos premières offres - 3 minutes",surface:n.FLAT,size:s.SMALL,stepNumber:3,children:"Créez vos offres sur pass Culture Pro puis diffusez-les sur l'application pour les jeunes ou sur Adage."})]})]}),e.jsxs("div",{style:a,children:[e.jsx("h4",{children:"Elevated Small"}),e.jsx(t,{title:"Décrivez votre structure et votre activité culturelle - 5 minutes",surface:n.ELEVATED,size:s.SMALL,stepNumber:1,children:"Renseignez les informations administratives et les domaines dans lesquels vous intervenez"}),e.jsx(t,{title:"Nos équipes valident votre dossier — 48 heures",surface:n.ELEVATED,size:s.SMALL,stepNumber:2,children:"Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage."}),e.jsx(t,{title:"Créez vos premières offres - 3 minutes",surface:n.ELEVATED,size:s.SMALL,stepNumber:3,children:"Créez vos offres sur pass Culture Pro puis diffusez-les sur l'application pour les jeunes ou sur Adage."})]})]})},m={render:()=>e.jsxs("div",{style:h,children:[e.jsxs("div",{style:a,children:[e.jsx("h4",{children:"Flat Small"}),e.jsxs("div",{style:{...a,gap:"32px"},children:[e.jsx(t,{title:"4 millions de jeunes",surface:n.FLAT,size:s.SMALL,icon:v,iconAlt:"Profil utilisateur",children:"Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles"}),e.jsx(t,{title:"Une inscription simple et rapide",surface:n.FLAT,size:s.SMALL,icon:P,iconAlt:"Profil utilisateur",children:"Contrairement aux appels à projet lourds et complexes, l'inscription à pass Culture Pro est simple et guidée"}),e.jsx(t,{title:"Publiez quand vous voulez",surface:n.FLAT,size:s.SMALL,icon:x,iconAlt:"Profil utilisateur",children:"Créez et modifiez vos offres, qu’elles soient gratuites ou payantes, à tout moment de l’année"})]})]}),e.jsxs("div",{style:a,children:[e.jsx("h4",{children:"Elevated Small"}),e.jsx(t,{title:"4 millions de jeunes",surface:n.ELEVATED,size:s.SMALL,icon:P,iconAlt:"Profil utilisateur",children:"Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles"}),e.jsx(t,{title:"Une inscription simple et rapide",surface:n.ELEVATED,size:s.SMALL,icon:v,iconAlt:"Profil utilisateur",children:"Contrairement aux appels à projet lourds et complexes, l'inscription à pass Culture Pro est simple et guidée"}),e.jsx(t,{title:"Publiez quand vous voulez",surface:n.ELEVATED,size:s.SMALL,icon:x,iconAlt:"Profil utilisateur",children:"Créez et modifiez vos offres, qu’elles soient gratuites ou payantes, à tout moment de l’année"})]})]})};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    title: '4 millions de jeunes',
    children: "Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles",
    surface: InfoPanelSurface.FLAT,
    size: InfoPanelSize.LARGE,
    icon: strokeUserProfile,
    iconAlt: 'Profil utilisateur'
  }
}`,...l.parameters?.docs?.source},description:{story:"Surface flat avec icône. L'icône et son texte alternatif sont requis.",...l.parameters?.docs?.description}}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  args: {
    title: 'Nos équipes valident votre dossier — 48 heures',
    children: 'Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.',
    surface: InfoPanelSurface.ELEVATED,
    size: InfoPanelSize.LARGE,
    stepNumber: 1
  }
}`,...o.parameters?.docs?.source},description:{story:"Surface elevated avec numéro d'étape. La prop `stepNumber` est requise.",...o.parameters?.docs?.description}}};u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  args: {
    ...Flat.args,
    size: InfoPanelSize.SMALL
  }
}`,...u.parameters?.docs?.source},description:{story:"Surface flat en taille small.",...u.parameters?.docs?.description}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    ...Elevated.args,
    size: InfoPanelSize.SMALL
  }
}`,...c.parameters?.docs?.source},description:{story:"Surface elevated en taille small.",...c.parameters?.docs?.description}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
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
}`,...d.parameters?.docs?.source},description:{story:"Comparaison côte à côte des panneaux **flat** dans les deux tailles.",...d.parameters?.docs?.description}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
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
}`,...p.parameters?.docs?.source},description:{story:"Comparaison côte à côte des panneaux **elevated** dans les deux tailles.",...p.parameters?.docs?.description}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
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
}`,...f.parameters?.docs?.source},description:{story:"Plusieurs panneaux (flat ou elevated) utilisés comme liste d'étapes numérotées.",...f.parameters?.docs?.description}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
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
}`,...m.parameters?.docs?.source},description:{story:"Plusieurs panneaux (flat ou elevated) utilisés avec des icônes.",...m.parameters?.docs?.description}}};const Ae=["Flat","Elevated","FlatSmall","ElevatedSmall","FlatSizes","ElevatedSizes","StepList","IconsList"];export{o as Elevated,p as ElevatedSizes,c as ElevatedSmall,l as Flat,d as FlatSizes,u as FlatSmall,m as IconsList,f as StepList,Ae as __namedExportsOrder,ze as default};
