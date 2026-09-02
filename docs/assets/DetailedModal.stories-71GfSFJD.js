import{n as e}from"./rolldown-runtime-DkW27tQK.js";import{d as t}from"./iframe-BOncW1wH.js";import{t as n}from"./jsx-runtime-DeHZSEgm.js";import{a as r,n as i,r as a,s as o,t as s}from"./Button-AlPK9t0e.js";import{n as c,t as l}from"./TextInput-BM-D_7Ze.js";import{n as u,t as d}from"./dist-D1ZaROZW.js";import{n as f,t as p}from"./DetailedModal-B6W1T7HK.js";import{n as m,t as h}from"./full-back-tyjMQbd0.js";var g,_,v,y,b,x,S,C,w,T,E,D,O,k,A,j;function M(){return(M=e((()=>{g=t(),u(),i(),o(),m(),f(),c(),_=n(),v=e=>{let[t,n]=(0,g.useState)(!1);return(0,_.jsxs)(`div`,{style:{minHeight:`240px`},children:[(0,_.jsx)(s,{variant:r.PRIMARY,label:`Ouvrir la modal`,onClick:()=>n(!0)}),(0,_.jsx)(p,{...e,isOpen:t,onClose:()=>n(!1)})]})},y={title:`@/design-system/DetailedModal`,component:p,args:{isOpen:!0,onClose:()=>{},title:`Titre très très très loong Titre très très très loongTitre très très très loong`,description:`Ceci est une description qui peut être assez longue en fonction du contenu de la page. Il n’y a pas de limites en termes de nombre de lignes…`,onGoBack:()=>{},primaryAction:(0,_.jsx)(s,{variant:r.PRIMARY,label:`Primary`}),secondaryAction:(0,_.jsx)(s,{variant:r.SECONDARY,color:a.NEUTRAL,label:`Secondary`}),tertiaryAction:(0,_.jsx)(s,{variant:r.TERTIARY,color:a.NEUTRAL,label:`Tertiary`}),footerMessage:`Message précisant le bouton`,children:(0,_.jsx)(`form`,{onSubmit:e=>e.preventDefault(),children:(0,_.jsxs)(`div`,{style:{display:`grid`,gap:`12px`},children:[(0,_.jsx)(l,{label:`Nom de l’offre`,name:`name`}),(0,_.jsx)(`span`,{children:`Lorem ipsum dolor sit amet consectetur adipisicing elit. Repellendus ut quo velit soluta esse est omnis, laudantium sapiente sint molestiae illum, autem magni! Reiciendis exercitationem inventore praesentium sunt ut recusandae? Lorem ipsum dolor sit amet consectetur adipisicing elit. Repellendus ut quo velit soluta esse est omnis, laudantium sapiente sint molestiae illum, autem magni! Reiciendis exercitationem inventore praesentium sunt ut recusandae? Lorem ipsum dolor sit amet consectetur adipisicing elit. Repellendus ut quo velit soluta esse est omnis, laudantium sapiente sint molestiae illum, autem magni! Reiciendis exercitationem inventore praesentium sunt ut recusandae?`})]})})}},b={args:{goBackButtonAriaLabel:``,isFooterFixed:!1},render:e=>(0,_.jsx)(v,{...e})},x={args:{onGoBack:void 0}},S={args:{description:`Ceci est une description qui peut être assez longue en fonction du contenu de la page. Il n’y a pas de limites en termes de nombre de lignes. Ceci est une description qui peut être assez longue en fonction du contenu de la page. Il n’y a pas de limites en termes de nombre de lignes. Ceci est une description qui peut être assez longue en fonction du contenu de la page. Il n’y a pas de limites en termes de nombre de lignes. mottresssssloooooongsansespacespourtesterlewrappingresponsivemottresssssloooooongsansespacespourtesterlewrappingresponsive.`,isFooterFixed:!1}},C={args:{primaryAction:(0,_.jsx)(s,{variant:r.PRIMARY,label:`Primary`,isLoading:!0}),secondaryAction:(0,_.jsx)(s,{variant:r.SECONDARY,color:a.NEUTRAL,label:`Secondary`,disabled:!0})}},w={args:{isFooterFixed:!0,children:(0,_.jsx)(`div`,{style:{display:`grid`,gap:`12px`},children:Array.from({length:20}).map((e,t)=>{let n=t+1;return(0,_.jsxs)(`p`,{children:[`Ligne de contenu `,n]},`content-line-${n}`)})})}},T={decorators:[d],args:{tertiaryAction:(0,_.jsx)(s,{as:`router-link`,to:`/offres`,variant:r.TERTIARY,color:a.NEUTRAL,label:`Voir les offres`,icon:h}),secondaryAction:(0,_.jsx)(s,{variant:r.SECONDARY,color:a.NEUTRAL,label:`Secondary`,icon:h}),primaryAction:(0,_.jsx)(s,{variant:r.PRIMARY,label:`Primary`})}},E={args:{loadingState:{label:`Chargement en cours…`},children:(0,_.jsx)(`div`,{})},render:e=>(0,_.jsx)(v,{...e})},D={args:{primaryAction:(0,_.jsx)(s,{variant:r.PRIMARY,label:`Primary`}),secondaryAction:void 0,tertiaryAction:void 0,footerMessage:void 0}},O=[{title:`Étape 1 - Informations générales`,description:`Renseignez les informations de base de votre offre.`,content:(0,_.jsx)(l,{label:`Nom de l'offre`,name:`name`})},{title:`Étape 2 - Détails`,description:`Ajoutez les détails complémentaires.`,content:(0,_.jsx)(l,{label:`Description`,name:`description`})},{title:`Étape 3 - Confirmation`,description:`Vérifiez et confirmez les informations saisies.`,content:(0,_.jsx)(`p`,{children:`Tout est correct ? Cliquez sur "Terminer" pour valider.`})}],k=()=>{let[e,t]=(0,g.useState)(!1),[n,i]=(0,g.useState)(0),o=n===O.length-1,c=n===0,l=O[n],u=()=>{t(!1),i(0)};return(0,_.jsxs)(`div`,{style:{minHeight:`240px`},children:[(0,_.jsx)(s,{variant:r.PRIMARY,label:`Ouvrir la modal`,onClick:()=>t(!0)}),(0,_.jsx)(p,{isOpen:e,onClose:u,title:l.title,description:l.description,onGoBack:c?void 0:()=>i(e=>e-1),primaryAction:(0,_.jsx)(s,{variant:r.PRIMARY,label:o?`Terminer`:`Suivant`,onClick:o?u:()=>i(e=>e+1)}),secondaryAction:(0,_.jsx)(s,{variant:r.SECONDARY,color:a.NEUTRAL,label:`Annuler`,onClick:u}),footerMessage:`Étape ${n+1} sur ${O.length}`,children:(0,_.jsx)(`form`,{onSubmit:e=>e.preventDefault(),children:(0,_.jsx)(`div`,{style:{display:`grid`,gap:`12px`},children:l.content})})})]})},A={render:()=>(0,_.jsx)(k,{})},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    goBackButtonAriaLabel: '',
    isFooterFixed: false
  },
  render: args => <DetailedModalWithOpenButton {...args} />
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    onGoBack: undefined
  }
}`,...x.parameters?.docs?.source}}},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  args: {
    description: 'Ceci est une description qui peut être assez longue en fonction du contenu de la page. Il n’y a pas de limites en termes de nombre de lignes. Ceci est une description qui peut être assez longue en fonction du contenu de la page. Il n’y a pas de limites en termes de nombre de lignes. Ceci est une description qui peut être assez longue en fonction du contenu de la page. Il n’y a pas de limites en termes de nombre de lignes. mottresssssloooooongsansespacespourtesterlewrappingresponsivemottresssssloooooongsansespacespourtesterlewrappingresponsive.',
    isFooterFixed: false
  }
}`,...S.parameters?.docs?.source}}},C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`{
  args: {
    primaryAction: <Button variant={ButtonVariant.PRIMARY} label="Primary" isLoading />,
    secondaryAction: <Button variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} label="Secondary" disabled />
  }
}`,...C.parameters?.docs?.source}}},w.parameters={...w.parameters,docs:{...w.parameters?.docs,source:{originalSource:`{
  args: {
    isFooterFixed: true,
    children: <div style={{
      display: 'grid',
      gap: '12px'
    }}>
        {Array.from({
        length: 20
      }).map((_, index) => {
        const lineNumber = index + 1;
        return <p key={\`content-line-\${lineNumber}\`}>
              Ligne de contenu {lineNumber}
            </p>;
      })}
      </div>
  }
}`,...w.parameters?.docs?.source}}},T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
  decorators: [withRouter],
  args: {
    tertiaryAction: <Button as="router-link" to="/offres" variant={ButtonVariant.TERTIARY} color={ButtonColor.NEUTRAL} label="Voir les offres" icon={fullBackIcon} />,
    secondaryAction: <Button variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} label="Secondary" icon={fullBackIcon} />,
    primaryAction: <Button variant={ButtonVariant.PRIMARY} label="Primary" />
  }
}`,...T.parameters?.docs?.source}}},E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
  args: {
    loadingState: {
      label: 'Chargement en cours…'
    },
    children: <div />
  },
  render: args => <DetailedModalWithOpenButton {...args} />
}`,...E.parameters?.docs?.source}}},D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  args: {
    primaryAction: <Button variant={ButtonVariant.PRIMARY} label="Primary" />,
    secondaryAction: undefined,
    tertiaryAction: undefined,
    footerMessage: undefined
  }
}`,...D.parameters?.docs?.source}}},A.parameters={...A.parameters,docs:{...A.parameters?.docs,source:{originalSource:`{
  render: () => <DetailedModalWithSteps />
}`,...A.parameters?.docs?.source}}},j=[`Default`,`WithoutGoBack`,`WithLongDescription`,`WithLoadingActions`,`WithFixedFooter`,`WithLinkAndIconActions`,`LoadingVariant`,`WithSingleAction`,`WithStepNavigation`]})))()}M();export{b as Default,E as LoadingVariant,w as WithFixedFooter,T as WithLinkAndIconActions,C as WithLoadingActions,S as WithLongDescription,D as WithSingleAction,A as WithStepNavigation,x as WithoutGoBack,j as __namedExportsOrder,y as default};