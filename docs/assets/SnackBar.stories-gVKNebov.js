import{i as e,s as t}from"./preload-helper-xPQekRTU.js";import{C as n}from"./iframe-DZNoYant.js";import{t as r}from"./jsx-runtime-CaZkqeYb.js";import{n as i,r as a,t as o}from"./SnackBar-3ijw2QLx.js";var s,c=e((()=>{s={iphone5:{name:`iPhone 5`,styles:{height:`568px`,width:`320px`},type:`mobile`},iphone6:{name:`iPhone 6`,styles:{height:`667px`,width:`375px`},type:`mobile`},iphone6p:{name:`iPhone 6 Plus`,styles:{height:`736px`,width:`414px`},type:`mobile`},iphone8p:{name:`iPhone 8 Plus`,styles:{height:`736px`,width:`414px`},type:`mobile`},iphonex:{name:`iPhone X`,styles:{height:`812px`,width:`375px`},type:`mobile`},iphonexr:{name:`iPhone XR`,styles:{height:`896px`,width:`414px`},type:`mobile`},iphonexsmax:{name:`iPhone XS Max`,styles:{height:`896px`,width:`414px`},type:`mobile`},iphonese2:{name:`iPhone SE (2nd generation)`,styles:{height:`667px`,width:`375px`},type:`mobile`},iphone12mini:{name:`iPhone 12 mini`,styles:{height:`812px`,width:`375px`},type:`mobile`},iphone12:{name:`iPhone 12`,styles:{height:`844px`,width:`390px`},type:`mobile`},iphone12promax:{name:`iPhone 12 Pro Max`,styles:{height:`926px`,width:`428px`},type:`mobile`},iphoneSE3:{name:`iPhone SE 3rd generation`,styles:{height:`667px`,width:`375px`},type:`mobile`},iphone13:{name:`iPhone 13`,styles:{height:`844px`,width:`390px`},type:`mobile`},iphone13pro:{name:`iPhone 13 Pro`,styles:{height:`844px`,width:`390px`},type:`mobile`},iphone13promax:{name:`iPhone 13 Pro Max`,styles:{height:`926px`,width:`428px`},type:`mobile`},iphone14:{name:`iPhone 14`,styles:{height:`844px`,width:`390px`},type:`mobile`},iphone14pro:{name:`iPhone 14 Pro`,styles:{height:`852px`,width:`393px`},type:`mobile`},iphone14promax:{name:`iPhone 14 Pro Max`,styles:{height:`932px`,width:`430px`},type:`mobile`},ipad:{name:`iPad`,styles:{height:`1024px`,width:`768px`},type:`tablet`},ipad10p:{name:`iPad Pro 10.5-in`,styles:{height:`1112px`,width:`834px`},type:`tablet`},ipad11p:{name:`iPad Pro 11-in`,styles:{height:`1194px`,width:`834px`},type:`tablet`},ipad12p:{name:`iPad Pro 12.9-in`,styles:{height:`1366px`,width:`1024px`},type:`tablet`},galaxys5:{name:`Galaxy S5`,styles:{height:`640px`,width:`360px`},type:`mobile`},galaxys9:{name:`Galaxy S9`,styles:{height:`740px`,width:`360px`},type:`mobile`},nexus5x:{name:`Nexus 5X`,styles:{height:`660px`,width:`412px`},type:`mobile`},nexus6p:{name:`Nexus 6P`,styles:{height:`732px`,width:`412px`},type:`mobile`},pixel:{name:`Pixel`,styles:{height:`960px`,width:`540px`},type:`mobile`},pixelxl:{name:`Pixel XL`,styles:{height:`1280px`,width:`720px`},type:`mobile`}}})),l=e((()=>{c()})),u,d,f,p,m,h,g,_,v,y,b,x,S;e((()=>{u=t(n(),1),l(),a(),d=r(),f={title:`@/design-system/SnackBar`,component:o,parameters:{viewport:{options:s},docs:{description:{component:`Meta object for the SnackBar component.`}}}},p=e=>{let[t,n]=(0,u.useState)(!0);return(0,d.jsxs)(`div`,{children:[!t&&(0,d.jsx)(`button`,{onClick:()=>n(!0),children:`Afficher la notification`}),t&&(0,d.jsx)(o,{...e,onClose:()=>n(!1)})]})},m={parameters:{docs:{title:`Snack Bar - Default Success Variant`,description:{story:`Demonstration of a success snack bar.`}}},render:e=>(0,d.jsx)(p,{...e}),args:{variant:i.SUCCESS,description:`Snack Bar with a default success variant`,autoClose:!1,testId:`default-success-snack-bar`,forceMobile:!0}},h={render:e=>(0,d.jsx)(p,{...e}),args:{variant:i.ERROR,description:`Snack Bar with a default error variant`,autoClose:!1,testId:`default-error-snack-bar`,forceMobile:!0},parameters:{docs:{title:`Snack Bar - Default Error Variant`,description:{story:`Demonstration of an error snack bar.`}}}},g={render:e=>(0,d.jsx)(p,{...e}),args:{variant:i.SUCCESS,description:`SnackBar with a large success variant`,autoClose:!1,testId:`large-success-snack-bar`}},_={render:e=>(0,d.jsx)(p,{...e}),args:{variant:i.ERROR,description:`SnackBar with a large error variant`,autoClose:!1,testId:`large-error-snack-bar`}},v={render:e=>(0,d.jsx)(p,{...e}),args:{variant:i.SUCCESS,description:`Snack Bar Success with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)`,autoClose:!1,testId:`long-message-success-snack-bar`}},y={render:e=>(0,d.jsx)(p,{...e}),args:{variant:i.ERROR,description:`Snack Bar Error with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)`,autoClose:!1,testId:`long-message-error-snack-bar`}},b=()=>{let[e,t]=(0,u.useState)([]),[n,r]=(0,u.useState)(0),a=(e,i)=>{let a=n;r(e=>e+1),t(t=>[...t,{id:a,variant:e,description:i,date:new Date}])},s=e=>{t(t=>t.filter(t=>t.id!==e))},c=[...e];return(0,d.jsxs)(`div`,{style:{height:`500px`},children:[(0,d.jsxs)(`div`,{style:{display:`flex`,gap:`12px`,flexWrap:`wrap`,flexDirection:`column`,alignItems:`flex-start`},children:[(0,d.jsx)(`button`,{onClick:()=>a(i.SUCCESS,`Success snackBar`),children:`Add a success snackBar`}),(0,d.jsx)(`button`,{onClick:()=>a(i.ERROR,`Error snackBar`),children:`Add an error snackBar`}),(0,d.jsx)(`button`,{onClick:()=>a(i.SUCCESS,`Success snackBar with a long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)`),children:`Add a success snackBar with a long message.`}),(0,d.jsx)(`button`,{onClick:()=>a(i.ERROR,`Error snackBar with a long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)`),children:`Add an error snackBar with a long message.`}),(0,d.jsx)(`button`,{onClick:()=>t([]),children:`Clear all snackBars.`})]}),(0,d.jsx)(`div`,{style:{alignItems:`flex-end`,bottom:`24px`,display:`flex`,flexDirection:`column`,gap:`8px`,position:`fixed`,right:`24px`,zIndex:1e3},children:c.map(e=>(0,d.jsx)(o,{variant:e.variant,description:e.description,onClose:()=>s(e.id),autoClose:!0,testId:`snack-bar-${e.id}`},e.id))})]})},x={parameters:{docs:{description:{story:`Demonstration of stacking multiple snack bars. Click on the buttons to add snack bars that stack on the bottom right.`}}},render:()=>(0,d.jsx)(b,{})},m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  parameters: {
    docs: {
      title: 'Snack Bar - Default Success Variant',
      description: {
        story: 'Demonstration of a success snack bar.'
      }
    }
  },
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    description: 'Snack Bar with a default success variant',
    autoClose: false,
    testId: 'default-success-snack-bar',
    forceMobile: true
  }
}`,...m.parameters?.docs?.source},description:{story:`Story for the default SnackBar component.`,...m.parameters?.docs?.description}}},h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    description: 'Snack Bar with a default error variant',
    autoClose: false,
    testId: 'default-error-snack-bar',
    forceMobile: true
  },
  parameters: {
    docs: {
      title: 'Snack Bar - Default Error Variant',
      description: {
        story: 'Demonstration of an error snack bar.'
      }
    }
  }
}`,...h.parameters?.docs?.source},description:{story:`Story for the error SnackBar component.`,...h.parameters?.docs?.description}}},g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    description: 'SnackBar with a large success variant',
    autoClose: false,
    testId: 'large-success-snack-bar'
  }
}`,...g.parameters?.docs?.source},description:{story:`Story for the long message success SnackBar component.`,...g.parameters?.docs?.description}}},_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    description: 'SnackBar with a large error variant',
    autoClose: false,
    testId: 'large-error-snack-bar'
  }
}`,..._.parameters?.docs?.source},description:{story:`Story for the long message success SnackBar component.`,..._.parameters?.docs?.description}}},v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    description: 'Snack Bar Success with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)',
    autoClose: false,
    testId: 'long-message-success-snack-bar'
  }
}`,...v.parameters?.docs?.source},description:{story:`Story for the large message success SnackBar component.`,...v.parameters?.docs?.description}}},y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    description: 'Snack Bar Error with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)',
    autoClose: false,
    testId: 'long-message-error-snack-bar'
  }
}`,...y.parameters?.docs?.source},description:{story:`Story for the large message error SnackBar component.`,...y.parameters?.docs?.description}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  parameters: {
    docs: {
      description: {
        story: 'Demonstration of stacking multiple snack bars. Click on the buttons to add snack bars that stack on the bottom right.'
      }
    }
  },
  render: () => <PlaygroundComponent />
}`,...x.parameters?.docs?.source},description:{story:`Playground for the SnackBar component.`,...x.parameters?.docs?.description}}},S=[`DefaultSuccessVariant`,`DefaultErrorVariant`,`LargeSuccessVariant`,`LargeErrorVariant`,`LargeErrorVariantWithLongMessage`,`LargeSuccessVariantWithLongMessage`,`Playground`]}))();export{h as DefaultErrorVariant,m as DefaultSuccessVariant,_ as LargeErrorVariant,v as LargeErrorVariantWithLongMessage,g as LargeSuccessVariant,y as LargeSuccessVariantWithLongMessage,x as Playground,S as __namedExportsOrder,f as default};