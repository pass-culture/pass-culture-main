import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-C_rXmNQI.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{n as r,t as i}from"./SnackBar-KrksVE99.js";var a=e(t(),1),o=`storybook/viewport`;`${o}`,`${o}`;var s={iphone5:{name:`iPhone 5`,styles:{height:`568px`,width:`320px`},type:`mobile`},iphone6:{name:`iPhone 6`,styles:{height:`667px`,width:`375px`},type:`mobile`},iphone6p:{name:`iPhone 6 Plus`,styles:{height:`736px`,width:`414px`},type:`mobile`},iphone8p:{name:`iPhone 8 Plus`,styles:{height:`736px`,width:`414px`},type:`mobile`},iphonex:{name:`iPhone X`,styles:{height:`812px`,width:`375px`},type:`mobile`},iphonexr:{name:`iPhone XR`,styles:{height:`896px`,width:`414px`},type:`mobile`},iphonexsmax:{name:`iPhone XS Max`,styles:{height:`896px`,width:`414px`},type:`mobile`},iphonese2:{name:`iPhone SE (2nd generation)`,styles:{height:`667px`,width:`375px`},type:`mobile`},iphone12mini:{name:`iPhone 12 mini`,styles:{height:`812px`,width:`375px`},type:`mobile`},iphone12:{name:`iPhone 12`,styles:{height:`844px`,width:`390px`},type:`mobile`},iphone12promax:{name:`iPhone 12 Pro Max`,styles:{height:`926px`,width:`428px`},type:`mobile`},iphoneSE3:{name:`iPhone SE 3rd generation`,styles:{height:`667px`,width:`375px`},type:`mobile`},iphone13:{name:`iPhone 13`,styles:{height:`844px`,width:`390px`},type:`mobile`},iphone13pro:{name:`iPhone 13 Pro`,styles:{height:`844px`,width:`390px`},type:`mobile`},iphone13promax:{name:`iPhone 13 Pro Max`,styles:{height:`926px`,width:`428px`},type:`mobile`},iphone14:{name:`iPhone 14`,styles:{height:`844px`,width:`390px`},type:`mobile`},iphone14pro:{name:`iPhone 14 Pro`,styles:{height:`852px`,width:`393px`},type:`mobile`},iphone14promax:{name:`iPhone 14 Pro Max`,styles:{height:`932px`,width:`430px`},type:`mobile`},ipad:{name:`iPad`,styles:{height:`1024px`,width:`768px`},type:`tablet`},ipad10p:{name:`iPad Pro 10.5-in`,styles:{height:`1112px`,width:`834px`},type:`tablet`},ipad11p:{name:`iPad Pro 11-in`,styles:{height:`1194px`,width:`834px`},type:`tablet`},ipad12p:{name:`iPad Pro 12.9-in`,styles:{height:`1366px`,width:`1024px`},type:`tablet`},galaxys5:{name:`Galaxy S5`,styles:{height:`640px`,width:`360px`},type:`mobile`},galaxys9:{name:`Galaxy S9`,styles:{height:`740px`,width:`360px`},type:`mobile`},nexus5x:{name:`Nexus 5X`,styles:{height:`660px`,width:`412px`},type:`mobile`},nexus6p:{name:`Nexus 6P`,styles:{height:`732px`,width:`412px`},type:`mobile`},pixel:{name:`Pixel`,styles:{height:`960px`,width:`540px`},type:`mobile`},pixelxl:{name:`Pixel XL`,styles:{height:`1280px`,width:`720px`},type:`mobile`}},c=n(),l={title:`@/design-system/SnackBar`,component:i,parameters:{viewport:{options:s},docs:{description:{component:`Meta object for the SnackBar component.`}}}},u=e=>{let[t,n]=(0,a.useState)(!0);return(0,c.jsxs)(`div`,{children:[!t&&(0,c.jsx)(`button`,{onClick:()=>n(!0),children:`Afficher la notification`}),t&&(0,c.jsx)(i,{...e,onClose:()=>n(!1)})]})},d={parameters:{docs:{title:`Snack Bar - Default Success Variant`,description:{story:`Demonstration of a success snack bar.`}}},render:e=>(0,c.jsx)(u,{...e}),args:{variant:r.SUCCESS,description:`Snack Bar with a default success variant`,autoClose:!1,testId:`default-success-snack-bar`,forceMobile:!0}},f={render:e=>(0,c.jsx)(u,{...e}),args:{variant:r.ERROR,description:`Snack Bar with a default error variant`,autoClose:!1,testId:`default-error-snack-bar`,forceMobile:!0},parameters:{docs:{title:`Snack Bar - Default Error Variant`,description:{story:`Demonstration of an error snack bar.`}}}},p={render:e=>(0,c.jsx)(u,{...e}),args:{variant:r.SUCCESS,description:`SnackBar with a large success variant`,autoClose:!1,testId:`large-success-snack-bar`}},m={render:e=>(0,c.jsx)(u,{...e}),args:{variant:r.ERROR,description:`SnackBar with a large error variant`,autoClose:!1,testId:`large-error-snack-bar`}},h={render:e=>(0,c.jsx)(u,{...e}),args:{variant:r.SUCCESS,description:`Snack Bar Success with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)`,autoClose:!1,testId:`long-message-success-snack-bar`}},g={render:e=>(0,c.jsx)(u,{...e}),args:{variant:r.ERROR,description:`Snack Bar Error with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)`,autoClose:!1,testId:`long-message-error-snack-bar`}},_=()=>{let[e,t]=(0,a.useState)([]),[n,o]=(0,a.useState)(0),s=(e,r)=>{let i=n;o(e=>e+1),t(t=>[...t,{id:i,variant:e,description:r,date:new Date}])},l=e=>{t(t=>t.filter(t=>t.id!==e))},u=[...e];return(0,c.jsxs)(`div`,{style:{height:`500px`},children:[(0,c.jsxs)(`div`,{style:{display:`flex`,gap:`12px`,flexWrap:`wrap`,flexDirection:`column`,alignItems:`flex-start`},children:[(0,c.jsx)(`button`,{onClick:()=>s(r.SUCCESS,`Success snackBar`),children:`Add a success snackBar`}),(0,c.jsx)(`button`,{onClick:()=>s(r.ERROR,`Error snackBar`),children:`Add an error snackBar`}),(0,c.jsx)(`button`,{onClick:()=>s(r.SUCCESS,`Success snackBar with a long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)`),children:`Add a success snackBar with a long message.`}),(0,c.jsx)(`button`,{onClick:()=>s(r.ERROR,`Error snackBar with a long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)`),children:`Add an error snackBar with a long message.`}),(0,c.jsx)(`button`,{onClick:()=>t([]),children:`Clear all snackBars.`})]}),(0,c.jsx)(`div`,{style:{alignItems:`flex-end`,bottom:`24px`,display:`flex`,flexDirection:`column`,gap:`8px`,position:`fixed`,right:`24px`,zIndex:1e3},children:u.map(e=>(0,c.jsx)(i,{variant:e.variant,description:e.description,onClose:()=>l(e.id),autoClose:!0,testId:`snack-bar-${e.id}`},e.id))})]})},v={parameters:{docs:{description:{story:`Demonstration of stacking multiple snack bars. Click on the buttons to add snack bars that stack on the bottom right.`}}},render:()=>(0,c.jsx)(_,{})};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
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
}`,...d.parameters?.docs?.source},description:{story:`Story for the default SnackBar component.`,...d.parameters?.docs?.description}}},f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
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
}`,...f.parameters?.docs?.source},description:{story:`Story for the error SnackBar component.`,...f.parameters?.docs?.description}}},p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    description: 'SnackBar with a large success variant',
    autoClose: false,
    testId: 'large-success-snack-bar'
  }
}`,...p.parameters?.docs?.source},description:{story:`Story for the long message success SnackBar component.`,...p.parameters?.docs?.description}}},m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    description: 'SnackBar with a large error variant',
    autoClose: false,
    testId: 'large-error-snack-bar'
  }
}`,...m.parameters?.docs?.source},description:{story:`Story for the long message success SnackBar component.`,...m.parameters?.docs?.description}}},h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    description: 'Snack Bar Success with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)',
    autoClose: false,
    testId: 'long-message-success-snack-bar'
  }
}`,...h.parameters?.docs?.source},description:{story:`Story for the large message success SnackBar component.`,...h.parameters?.docs?.description}}},g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    description: 'Snack Bar Error with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)',
    autoClose: false,
    testId: 'long-message-error-snack-bar'
  }
}`,...g.parameters?.docs?.source},description:{story:`Story for the large message error SnackBar component.`,...g.parameters?.docs?.description}}},v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  parameters: {
    docs: {
      description: {
        story: 'Demonstration of stacking multiple snack bars. Click on the buttons to add snack bars that stack on the bottom right.'
      }
    }
  },
  render: () => <PlaygroundComponent />
}`,...v.parameters?.docs?.source},description:{story:`Playground for the SnackBar component.`,...v.parameters?.docs?.description}}};var y=[`DefaultSuccessVariant`,`DefaultErrorVariant`,`LargeSuccessVariant`,`LargeErrorVariant`,`LargeErrorVariantWithLongMessage`,`LargeSuccessVariantWithLongMessage`,`Playground`];export{f as DefaultErrorVariant,d as DefaultSuccessVariant,m as LargeErrorVariant,h as LargeErrorVariantWithLongMessage,p as LargeSuccessVariant,g as LargeSuccessVariantWithLongMessage,v as Playground,y as __namedExportsOrder,l as default};