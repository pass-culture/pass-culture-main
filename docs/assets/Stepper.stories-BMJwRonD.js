import{a as e,n as t}from"./rolldown-runtime-DkW27tQK.js";import{f as n}from"./iframe-Mz7TzPKX.js";import{t as r}from"./jsx-runtime-DeHZSEgm.js";import{t as i}from"./classnames-D09xBJOL.js";import{n as a,t as o}from"./lib-B3eP8kW1.js";import{n as s,t as c}from"./dist-yCR3Px6t.js";import{n as l,t as u}from"./noop-C6_kCKXi.js";import{n as d,t as f}from"./useFocus-Yo6vgLFx.js";var p,m,h,g,_,v,y,b,x,S,C,w,T,E,D,O,k;function A(){return(A=t((()=>{p=`_stepper_i0asc_1`,m=`_button_i0asc_9`,h=`_link_i0asc_10`,g=`_wrapper_i0asc_11`,_=`_indicator_i0asc_61`,v=`_number_i0asc_74`,y=`_label_i0asc_84`,b=`_sublabel_i0asc_90`,x=`_connector_i0asc_97`,S=`_horizontal_i0asc_102`,C=`_vertical_i0asc_123`,w=`_disabled_i0asc_144`,T=`_current_i0asc_156`,E=`_done_i0asc_174`,D=`_active_i0asc_179`,O=`_clickable_i0asc_182`,k={stepper:p,button:m,link:h,wrapper:g,"visually-hidden":`_visually-hidden_i0asc_41`,"step-item":`_step-item_i0asc_52`,"step-content":`_step-content_i0asc_56`,indicator:_,number:v,"text-container":`_text-container_i0asc_78`,label:y,sublabel:b,connector:x,horizontal:S,vertical:C,disabled:w,current:T,done:E,active:D,clickable:O}})))()}function j({linkUrl:e,hasButton:t,onClick:n,voiceOverText:r,isActive:i,children:a,ref:s}){return e?(0,P.jsx)(o,{to:e,onClick:n,className:k.link,"aria-label":r,children:a}):t?(0,P.jsx)(`button`,{type:`button`,onClick:n,className:k.button,"aria-label":r,children:a}):(0,P.jsxs)(`div`,{ref:s,className:k.wrapper,tabIndex:-1,children:[(0,P.jsx)(`div`,{role:`log`,className:k[`visually-hidden`],children:i?r:(0,P.jsx)(`span`,{children:`\xA0`})}),(0,P.jsx)(`span`,{className:k[`visually-hidden`],children:r}),a]})}var M,N,P,F;function I(){return(I=t((()=>{M=e(i(),1),N=n(),a(),d(),u(),A(),P=r(),F=({steps:e,activeStep:t,orientation:n=`auto`,ref:r})=>{let i=(0,N.useRef)(null),a=r||i,[o,s]=(0,N.useState)(n===`vertical`),c=(0,N.useRef)(null),u=e.findIndex(e=>e.id===t);return(0,N.useEffect)(()=>{f(c.current)},[t]),(0,N.useLayoutEffect)(()=>{if(n!==`auto`)return s(n===`vertical`),l;let t=a.current;if(!t)return l;let r=t=>{let n=e.length*80;s(t<n)},i=t.getBoundingClientRect();if(i.width>0&&r(i.width),typeof window<`u`&&`ResizeObserver`in window){let e=new window.ResizeObserver(e=>{for(let t of e){let e=t.contentRect.width;e>0&&r(e)}});return e.observe(t),()=>{e.disconnect()}}return l},[e.length,n,a]),(0,P.jsx)(`ol`,{ref:a,className:(0,M.default)(k.stepper,o?k.vertical:k.horizontal),children:e.map((t,n)=>{let r=`disabled`;n<u?r=`done`:n===u&&(r=`current`);let i=r===`done`,a=i?t.url:void 0,o=i&&!t.url&&!!t.onClick,s=!!a||o,l={done:`terminée`,current:`active`,disabled:`à venir`}[r],d=`Étape ${n+1} sur ${e.length}, ${l}, ${t.label}`,f=(0,P.jsxs)(`div`,{className:k[`step-content`],"aria-hidden":`true`,children:[(0,P.jsxs)(`div`,{className:k.indicator,children:[(0,P.jsx)(`span`,{className:k.number,children:(n+1).toString()}),(0,P.jsx)(`div`,{className:(0,M.default)(k.connector,{[k.active]:r===`done`})})]}),(0,P.jsxs)(`div`,{className:k[`text-container`],children:[(0,P.jsx)(`span`,{className:k.label,children:t.label}),t.sublabel&&(0,P.jsx)(`span`,{className:k.sublabel,children:t.sublabel})]})]});return(0,P.jsx)(`li`,{"aria-current":r===`current`?`step`:void 0,className:(0,M.default)(k[`step-item`],k[r],{[k.clickable]:s}),children:(0,P.jsx)(j,{ref:r===`current`?c:void 0,linkUrl:a,hasButton:o,onClick:t.onClick,voiceOverText:d,isActive:r===`current`,children:f})},t.id)})})},F.displayName=`Stepper`;try{F.displayName=`Stepper`,F.__docgenInfo={description:``,displayName:`Stepper`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/design-system/Stepper/Stepper.tsx`,methods:[],props:{steps:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`}],description:``,name:`steps`,parent:{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`},required:!0,tags:{},type:{name:`StepItem[]`}},activeStep:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`}],description:``,name:`activeStep`,parent:{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`},required:!0,tags:{},type:{name:`string`}},orientation:{defaultValue:{value:`auto`},declarations:[{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`}],description:`Layout direction of the stepper.
- 'auto': horizontal on desktop (if space permits, >= 80px per step), vertical on mobile.
- 'horizontal': forced horizontal layout.
- 'vertical': forced vertical layout.`,name:`orientation`,parent:{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`},required:!1,tags:{},type:{name:`enum`,raw:`"auto" | "horizontal" | "vertical"`,value:[{value:`"auto"`},{value:`"horizontal"`},{value:`"vertical"`}]}},ref:{defaultValue:null,declarations:[{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`}],description:``,name:`ref`,parent:{fileName:`pro/src/design-system/Stepper/Stepper.tsx`,name:`StepperProps`},required:!1,tags:{},type:{name:`RefObject<HTMLOListElement>`}}},tags:{}}}catch{}})))()}var L,R,z,B,V,H,U,W,G,K,q,J;function Y(){return(Y=t((()=>{s(),I(),u(),L=r(),R={title:`@/design-system/Stepper`,component:F,decorators:[c]},z=[{id:`category`,label:`Choisissez votre catégorie`,onClick:l},{id:`pricing`,label:`Définissez un tarif`,onClick:l},{id:`validation`,label:`Validez votre offre`,onClick:l}],B=[{id:`category`,label:`Choisissez votre catégorie`,sublabel:`Sélectionnez le type d’offre`,onClick:l},{id:`pricing`,label:`Définissez un tarif`,sublabel:`Saisissez les informations de prix`,onClick:l},{id:`validation`,label:`Validez votre offre`,sublabel:`Confirmez et publiez`,onClick:l}],V={args:{steps:z,activeStep:`pricing`,orientation:`horizontal`}},H={args:{steps:B,activeStep:`pricing`,orientation:`horizontal`}},U={args:{steps:z,activeStep:`pricing`,orientation:`vertical`}},W={args:{steps:B,activeStep:`pricing`,orientation:`vertical`}},G={args:{steps:[{id:`category`,label:`Choisissez votre catégorie`,sublabel:`Lien vers /category`,url:`/category`,onClick:l},{id:`pricing`,label:`Définissez un tarif`,sublabel:`Lien vers /pricing`,url:`/pricing`,onClick:l},{id:`summary`,label:`Relisez votre offre`,sublabel:`Étape en cours : pas de lien vers soi-même`,url:`/summary`},{id:`validation`,label:`Validez votre offre`,sublabel:`À venir : lien inactif`,url:`/validation`}],activeStep:`summary`,orientation:`horizontal`}},K={render:e=>(0,L.jsxs)(`div`,{style:{width:`100%`,resize:`horizontal`,overflow:`auto`,border:`1px dashed #ccc`,padding:`1rem`},children:[(0,L.jsx)(`p`,{style:{margin:`0 0 1rem 0`,fontSize:`0.875rem`,color:`#666`},children:`Redimensionnez ce bloc pour voir le composant basculer d’horizontal à vertical (seuil : 80px par étape).`}),(0,L.jsx)(F,{...e})]}),args:{steps:B,activeStep:`pricing`,orientation:`auto`}},q={args:{steps:[{id:`done`,label:`Étape 1 terminée`,sublabel:`Cliquable et validée`,onClick:()=>alert(`Clic Étape 1`)},{id:`current`,label:`Étape 2 active`,sublabel:`C’est l’étape en cours (non cliquable)`,onClick:()=>alert(`Clic Étape 2`)},{id:`upcoming`,label:`Étape 3 à venir`,sublabel:`Pas encore atteignable`,onClick:l},{id:`last`,label:`Étape 4 dernière`,sublabel:`Dernière étape`,onClick:l}],activeStep:`current`}},J=[`HorizontalSimple`,`HorizontalDetailed`,`VerticalSimple`,`VerticalDetailed`,`WithNavigationLinks`,`AutoResponsive`,`AllStatesShowcase`],V.parameters={...V.parameters,docs:{...V.parameters?.docs,source:{originalSource:`{
  args: {
    steps: mockStepsSimple,
    activeStep: 'pricing',
    orientation: 'horizontal'
  }
}`,...V.parameters?.docs?.source}}},H.parameters={...H.parameters,docs:{...H.parameters?.docs,source:{originalSource:`{
  args: {
    steps: mockStepsDetailed,
    activeStep: 'pricing',
    orientation: 'horizontal'
  }
}`,...H.parameters?.docs?.source}}},U.parameters={...U.parameters,docs:{...U.parameters?.docs,source:{originalSource:`{
  args: {
    steps: mockStepsSimple,
    activeStep: 'pricing',
    orientation: 'vertical'
  }
}`,...U.parameters?.docs?.source}}},W.parameters={...W.parameters,docs:{...W.parameters?.docs,source:{originalSource:`{
  args: {
    steps: mockStepsDetailed,
    activeStep: 'pricing',
    orientation: 'vertical'
  }
}`,...W.parameters?.docs?.source}}},G.parameters={...G.parameters,docs:{...G.parameters?.docs,source:{originalSource:`{
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
}`,...G.parameters?.docs?.source}}},K.parameters={...K.parameters,docs:{...K.parameters?.docs,source:{originalSource:`{
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
}`,...K.parameters?.docs?.source}}},q.parameters={...q.parameters,docs:{...q.parameters?.docs,source:{originalSource:`{
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
}`,...q.parameters?.docs?.source}}}})))()}Y();export{q as AllStatesShowcase,K as AutoResponsive,H as HorizontalDetailed,V as HorizontalSimple,W as VerticalDetailed,U as VerticalSimple,G as WithNavigationLinks,J as __namedExportsOrder,R as default};