import{j as c}from"./jsx-runtime-DF2Pcvd1.js";import{V as G}from"./index-Bxip17NV.js";import{T as H}from"./Tag-BCb30wpn.js";import{s as J}from"./stroke-date-CWTXq8J4.js";import{i as K}from"./dog-C0QzEjl8.js";import{R as m}from"./RadioButton-CqbxNoHb.js";import"./index-B2-qRKKC.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./chunk-C37GKA54-DDhL6sEx.js";import"./index-DeARc5FM.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-DfLnDDE5.js";const re={title:"design-system/RadioButton",decorators:[G],argTypes:{checked:{control:"boolean"},disabled:{control:"boolean"}},component:m},e={args:{name:"default",label:"Label"}},a={args:{name:"disabled",label:"Désactivé",disabled:!0}},t={args:{name:"detailed",label:"Détaillé",variant:"detailed"}},i={args:{name:"detailed-with-description",label:"Avec description",variant:"detailed",description:"Description lorem ipsum"}},r={args:{name:"detailed-full-width",label:"Taille étendue",variant:"detailed",description:"Description lorem ipsum",sizing:"fill"}},s={args:{name:"detailed-with-tag",label:"Avec tag",variant:"detailed",description:"Description lorem ipsum",asset:{variant:"tag",tag:{label:"Tag",variant:H.SUCCESS}}}},n={args:{name:"detailed-with-icon",label:"Avec icône",variant:"detailed",description:"Description lorem ipsum",asset:{variant:"icon",src:J}}},o={args:{name:"detailed-with-text",label:"Avec texte",variant:"detailed",description:"Description lorem ipsum",asset:{variant:"text",text:"19€"}}},l={args:{name:"detailed-with-image",label:"Avec image",variant:"detailed",asset:{variant:"image",src:K,size:"s"}}},d={args:{name:"detailed-with-collapsed",label:"Avec enfants",variant:"detailed",description:"Description lorem ipsum",value:"today",checked:!0,onChange:()=>{},collapsed:c.jsxs("div",{style:{display:"flex",flexDirection:"row",gap:16},children:[c.jsx(m,{name:"subchoice",label:"Sous-label 1",value:"1"}),c.jsx(m,{name:"subchoice",label:"Sous-label 2",value:"2"})]})}};var p,u,g;e.parameters={...e.parameters,docs:{...(p=e.parameters)==null?void 0:p.docs,source:{originalSource:`{
  args: {
    name: 'default',
    label: 'Label'
  }
}`,...(g=(u=e.parameters)==null?void 0:u.docs)==null?void 0:g.source}}};var v,D,b;a.parameters={...a.parameters,docs:{...(v=a.parameters)==null?void 0:v.docs,source:{originalSource:`{
  args: {
    name: 'disabled',
    label: 'Désactivé',
    disabled: true
  }
}`,...(b=(D=a.parameters)==null?void 0:D.docs)==null?void 0:b.source}}};var h,f,x;t.parameters={...t.parameters,docs:{...(h=t.parameters)==null?void 0:h.docs,source:{originalSource:`{
  args: {
    name: 'detailed',
    label: 'Détaillé',
    variant: 'detailed'
  }
}`,...(x=(f=t.parameters)==null?void 0:f.docs)==null?void 0:x.source}}};var S,w,W;i.parameters={...i.parameters,docs:{...(S=i.parameters)==null?void 0:S.docs,source:{originalSource:`{
  args: {
    name: 'detailed-with-description',
    label: 'Avec description',
    variant: 'detailed',
    description: 'Description lorem ipsum'
  }
}`,...(W=(w=i.parameters)==null?void 0:w.docs)==null?void 0:W.source}}};var A,T,y;r.parameters={...r.parameters,docs:{...(A=r.parameters)==null?void 0:A.docs,source:{originalSource:`{
  args: {
    name: 'detailed-full-width',
    label: 'Taille étendue',
    variant: 'detailed',
    description: 'Description lorem ipsum',
    sizing: 'fill'
  }
}`,...(y=(T=r.parameters)==null?void 0:T.docs)==null?void 0:y.source}}};var C,R,I;s.parameters={...s.parameters,docs:{...(C=s.parameters)==null?void 0:C.docs,source:{originalSource:`{
  args: {
    name: 'detailed-with-tag',
    label: 'Avec tag',
    variant: 'detailed',
    description: 'Description lorem ipsum',
    asset: {
      variant: 'tag',
      tag: {
        label: 'Tag',
        variant: TagVariant.SUCCESS
      }
    }
  }
}`,...(I=(R=s.parameters)==null?void 0:R.docs)==null?void 0:I.source}}};var j,k,B;n.parameters={...n.parameters,docs:{...(j=n.parameters)==null?void 0:j.docs,source:{originalSource:`{
  args: {
    name: 'detailed-with-icon',
    label: 'Avec icône',
    variant: 'detailed',
    description: 'Description lorem ipsum',
    asset: {
      variant: 'icon',
      src: strokeDateIcon
    }
  }
}`,...(B=(k=n.parameters)==null?void 0:k.docs)==null?void 0:B.source}}};var z,E,V;o.parameters={...o.parameters,docs:{...(z=o.parameters)==null?void 0:z.docs,source:{originalSource:`{
  args: {
    name: 'detailed-with-text',
    label: 'Avec texte',
    variant: 'detailed',
    description: 'Description lorem ipsum',
    asset: {
      variant: 'text',
      text: '19€'
    }
  }
}`,...(V=(E=o.parameters)==null?void 0:E.docs)==null?void 0:V.source}}};var _,F,L;l.parameters={...l.parameters,docs:{...(_=l.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    name: 'detailed-with-image',
    label: 'Avec image',
    variant: 'detailed',
    asset: {
      variant: 'image',
      src: imageDemo,
      size: 's'
    }
  }
}`,...(L=(F=l.parameters)==null?void 0:F.docs)==null?void 0:L.source}}};var U,O,q;d.parameters={...d.parameters,docs:{...(U=d.parameters)==null?void 0:U.docs,source:{originalSource:`{
  args: {
    name: 'detailed-with-collapsed',
    label: 'Avec enfants',
    variant: 'detailed',
    description: 'Description lorem ipsum',
    value: 'today',
    checked: true,
    onChange: () => {},
    collapsed: <div style={{
      display: 'flex',
      flexDirection: 'row',
      gap: 16
    }}>
        <RadioButton name="subchoice" label="Sous-label 1" value="1" />
        <RadioButton name="subchoice" label="Sous-label 2" value="2" />
      </div>
  }
}`,...(q=(O=d.parameters)==null?void 0:O.docs)==null?void 0:q.source}}};const se=["Default","DefaultDisabled","Detailed","DetailedWithDescription","DetailedFullWidth","DetailedWithTag","DetailedWithIcon","DetailedWithText","DetailedWithImage","DetailedWithCollapsed"];export{e as Default,a as DefaultDisabled,t as Detailed,r as DetailedFullWidth,d as DetailedWithCollapsed,i as DetailedWithDescription,n as DetailedWithIcon,l as DetailedWithImage,s as DetailedWithTag,o as DetailedWithText,se as __namedExportsOrder,re as default};
