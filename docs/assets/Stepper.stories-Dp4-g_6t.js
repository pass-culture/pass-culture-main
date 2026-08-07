import{a as e,n as t}from"./rolldown-runtime-DaJ6WEGw.js";import{d as n}from"./iframe-3ZjrBVuT.js";import{t as r}from"./jsx-runtime-cM__dR4X.js";import{t as i}from"./classnames-Bkdxq3RN.js";import{n as a,t as o}from"./development-Dx3QM2QX.js";import{n as s,r as c}from"./dist-C5MHBVLx.js";import{n as l,t as u}from"./noop-69r-7vnb.js";var d,f,p,m,h,g,_,v,y,b,x,S,C,w,T,E,D,O=t((()=>{d=`_stepper_12gim_1`,f=`_button_12gim_9`,p=`_link_12gim_10`,m=`_wrapper_12gim_11`,h=`_indicator_12gim_57`,g=`_number_12gim_70`,_=`_label_12gim_80`,v=`_sublabel_12gim_86`,y=`_connector_12gim_93`,b=`_horizontal_12gim_98`,x=`_vertical_12gim_119`,S=`_disabled_12gim_143`,C=`_current_12gim_155`,w=`_done_12gim_173`,T=`_active_12gim_178`,E=`_clickable_12gim_181`,D={stepper:d,button:f,link:p,wrapper:m,"visually-hidden":`_visually-hidden_12gim_37`,"step-item":`_step-item_12gim_48`,"step-content":`_step-content_12gim_52`,indicator:h,number:g,"text-container":`_text-container_12gim_74`,label:_,sublabel:v,connector:y,horizontal:b,vertical:x,disabled:S,current:C,done:w,active:T,clickable:E}}));function k({linkUrl:e,hasButton:t,onClick:n,voiceOverText:r,children:i}){return e?(0,M.jsx)(a,{to:e,onClick:n,className:D.link,"aria-label":r,children:i}):t?(0,M.jsx)(`button`,{type:`button`,onClick:n,className:D.button,"aria-label":r,children:i}):(0,M.jsxs)(`div`,{className:D.wrapper,children:[(0,M.jsx)(`span`,{className:D[`visually-hidden`],children:r}),i]})}var A,j,M,N,P=t((()=>{A=e(i(),1),j=e(n(),1),o(),u(),O(),M=r(),N=({steps:e,activeStep:t,orientation:n=`auto`,ref:r})=>{let i=(0,j.useRef)(null),a=r||i,[o,s]=(0,j.useState)(n===`vertical`),c=e.findIndex(e=>e.id===t);return(0,j.useLayoutEffect)(()=>{if(n!==`auto`)return s(n===`vertical`),l;let t=a.current;if(!t)return l;let r=t=>{let n=e.length*80;s(t<n)},i=t.getBoundingClientRect();if(i.width>0&&r(i.width),typeof window<`u`&&`ResizeObserver`in window){let e=new window.ResizeObserver(e=>{for(let t of e){let e=t.contentRect.width;e>0&&r(e)}});return e.observe(t),()=>{e.disconnect()}}return l},[e.length,n,a]),(0,M.jsx)(`ol`,{ref:a,className:(0,A.default)(D.stepper,o?D.vertical:D.horizontal),children:e.map((t,n)=>{let r=`disabled`;n<c?r=`done`:n===c&&(r=`current`);let i=r===`done`,a=i?t.url:void 0,o=i&&!t.url&&!!t.onClick,s=!!a||o,l={done:`terminée`,current:`active`,disabled:`à venir`}[r],u=`Étape ${n+1} sur ${e.length}, ${l}, ${t.label}`,d=(0,M.jsxs)(`div`,{className:D[`step-content`],"aria-hidden":`true`,children:[(0,M.jsxs)(`div`,{className:D.indicator,children:[(0,M.jsx)(`span`,{className:D.number,children:(n+1).toString().padStart(2,`0`)}),(0,M.jsx)(`div`,{className:(0,A.default)(D.connector,{[D.active]:r===`done`})})]}),(0,M.jsxs)(`div`,{className:D[`text-container`],children:[(0,M.jsx)(`span`,{className:D.label,children:t.label}),t.sublabel&&(0,M.jsx)(`span`,{className:D.sublabel,children:t.sublabel})]})]});return(0,M.jsx)(`li`,{"aria-current":r===`current`?`step`:void 0,className:(0,A.default)(D[`step-item`],D[r],{[D.clickable]:s}),children:(0,M.jsx)(k,{linkUrl:a,hasButton:o,onClick:t.onClick,voiceOverText:u,children:d})},t.id)})})},N.displayName=`Stepper`;try{N.displayName=`Stepper`,N.__docgenInfo={description:``,displayName:`Stepper`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/design-system/Stepper/Stepper.tsx`,methods:[],props:{steps:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`}],description:``,name:`steps`,parent:{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`},required:!0,tags:{},type:{name:`StepItem[]`}},activeStep:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`}],description:``,name:`activeStep`,parent:{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`},required:!0,tags:{},type:{name:`string`}},orientation:{defaultValue:{value:`auto`},declarations:[{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`}],description:`Layout direction of the stepper.
- 'auto': horizontal on desktop (if space permits, >= 80px per step), vertical on mobile.
- 'horizontal': forced horizontal layout.
- 'vertical': forced vertical layout.`,name:`orientation`,parent:{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`},required:!1,tags:{},type:{name:`enum`,raw:`"auto" | "horizontal" | "vertical"`,value:[{value:`"auto"`},{value:`"horizontal"`},{value:`"vertical"`}]}},ref:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`}],description:``,name:`ref`,parent:{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`},required:!1,tags:{},type:{name:`RefObject<HTMLOListElement>`}}},tags:{}}}catch{}})),F,I,L,R,z,B,V,H,U,W,G,K;t((()=>{c(),P(),u(),F=r(),I={title:`@/design-system/Stepper`,component:N,decorators:[s]},L=[{id:`category`,label:`Choisissez votre catégorie`,onClick:l},{id:`pricing`,label:`Définissez un tarif`,onClick:l},{id:`validation`,label:`Validez votre offre`,onClick:l}],R=[{id:`category`,label:`Choisissez votre catégorie`,sublabel:`Sélectionnez le type d’offre`,onClick:l},{id:`pricing`,label:`Définissez un tarif`,sublabel:`Saisissez les informations de prix`,onClick:l},{id:`validation`,label:`Validez votre offre`,sublabel:`Confirmez et publiez`,onClick:l}],z={args:{steps:L,activeStep:`pricing`,orientation:`horizontal`}},B={args:{steps:R,activeStep:`pricing`,orientation:`horizontal`}},V={args:{steps:L,activeStep:`pricing`,orientation:`vertical`}},H={args:{steps:R,activeStep:`pricing`,orientation:`vertical`}},U={args:{steps:[{id:`category`,label:`Choisissez votre catégorie`,sublabel:`Lien vers /category`,url:`/category`,onClick:l},{id:`pricing`,label:`Définissez un tarif`,sublabel:`Lien vers /pricing`,url:`/pricing`,onClick:l},{id:`summary`,label:`Relisez votre offre`,sublabel:`Étape en cours : pas de lien vers soi-même`,url:`/summary`},{id:`validation`,label:`Validez votre offre`,sublabel:`À venir : lien inactif`,url:`/validation`}],activeStep:`summary`,orientation:`horizontal`}},W={render:e=>(0,F.jsxs)(`div`,{style:{width:`100%`,resize:`horizontal`,overflow:`auto`,border:`1px dashed #ccc`,padding:`1rem`},children:[(0,F.jsx)(`p`,{style:{margin:`0 0 1rem 0`,fontSize:`0.875rem`,color:`#666`},children:`Redimensionnez ce bloc pour voir le composant basculer d’horizontal à vertical (seuil : 80px par étape).`}),(0,F.jsx)(N,{...e})]}),args:{steps:R,activeStep:`pricing`,orientation:`auto`}},G={args:{steps:[{id:`done`,label:`Étape 1 terminée`,sublabel:`Cliquable et validée`,onClick:()=>alert(`Clic Étape 1`)},{id:`current`,label:`Étape 2 active`,sublabel:`C’est l’étape en cours (non cliquable)`,onClick:()=>alert(`Clic Étape 2`)},{id:`upcoming`,label:`Étape 3 à venir`,sublabel:`Pas encore atteignable`,onClick:l},{id:`last`,label:`Étape 4 dernière`,sublabel:`Dernière étape`,onClick:l}],activeStep:`current`}},z.parameters={...z.parameters,docs:{...z.parameters?.docs,source:{originalSource:`{
  args: {
    steps: mockStepsSimple,
    activeStep: 'pricing',
    orientation: 'horizontal'
  }
}`,...z.parameters?.docs?.source}}},B.parameters={...B.parameters,docs:{...B.parameters?.docs,source:{originalSource:`{
  args: {
    steps: mockStepsDetailed,
    activeStep: 'pricing',
    orientation: 'horizontal'
  }
}`,...B.parameters?.docs?.source}}},V.parameters={...V.parameters,docs:{...V.parameters?.docs,source:{originalSource:`{
  args: {
    steps: mockStepsSimple,
    activeStep: 'pricing',
    orientation: 'vertical'
  }
}`,...V.parameters?.docs?.source}}},H.parameters={...H.parameters,docs:{...H.parameters?.docs,source:{originalSource:`{
  args: {
    steps: mockStepsDetailed,
    activeStep: 'pricing',
    orientation: 'vertical'
  }
}`,...H.parameters?.docs?.source}}},U.parameters={...U.parameters,docs:{...U.parameters?.docs,source:{originalSource:`{
  args: {
    steps: [{
      id: 'category',
      label: 'Choisissez votre catégorie',
      sublabel: 'Lien vers /category',
      url: '/category',
      onClick: noop
    }, {
      id: 'pricing',
      label: 'Définissez un tarif',
      sublabel: 'Lien vers /pricing',
      url: '/pricing',
      onClick: noop
    }, {
      id: 'summary',
      label: 'Relisez votre offre',
      sublabel: 'Étape en cours : pas de lien vers soi-même',
      url: '/summary'
    }, {
      id: 'validation',
      label: 'Validez votre offre',
      sublabel: 'À venir : lien inactif',
      url: '/validation'
    }],
    activeStep: 'summary',
    orientation: 'horizontal'
  }
}`,...U.parameters?.docs?.source}}},W.parameters={...W.parameters,docs:{...W.parameters?.docs,source:{originalSource:`{
  render: args => <div style={{
    width: '100%',
    resize: 'horizontal',
    overflow: 'auto',
    border: '1px dashed #ccc',
    padding: '1rem'
  }}>
      <p style={{
      margin: '0 0 1rem 0',
      fontSize: '0.875rem',
      color: '#666'
    }}>
        Redimensionnez ce bloc pour voir le composant basculer d’horizontal à
        vertical (seuil : 80px par étape).
      </p>
      <Stepper {...args} />
    </div>,
  args: {
    steps: mockStepsDetailed,
    activeStep: 'pricing',
    orientation: 'auto'
  }
}`,...W.parameters?.docs?.source}}},G.parameters={...G.parameters,docs:{...G.parameters?.docs,source:{originalSource:`{
  args: {
    steps: [{
      id: 'done',
      label: 'Étape 1 terminée',
      sublabel: 'Cliquable et validée',
      onClick: () => alert('Clic Étape 1')
    }, {
      id: 'current',
      label: 'Étape 2 active',
      sublabel: 'C’est l’étape en cours (non cliquable)',
      onClick: () => alert('Clic Étape 2')
    }, {
      id: 'upcoming',
      label: 'Étape 3 à venir',
      sublabel: 'Pas encore atteignable',
      onClick: noop
    }, {
      id: 'last',
      label: 'Étape 4 dernière',
      sublabel: 'Dernière étape',
      onClick: noop
    }],
    activeStep: 'current'
  }
}`,...G.parameters?.docs?.source}}},K=[`HorizontalSimple`,`HorizontalDetailed`,`VerticalSimple`,`VerticalDetailed`,`WithNavigationLinks`,`AutoResponsive`,`AllStatesShowcase`]}))();export{G as AllStatesShowcase,W as AutoResponsive,B as HorizontalDetailed,z as HorizontalSimple,H as VerticalDetailed,V as VerticalSimple,U as WithNavigationLinks,K as __namedExportsOrder,I as default};