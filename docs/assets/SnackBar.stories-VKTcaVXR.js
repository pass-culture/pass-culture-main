import{j as e}from"./jsx-runtime-u17CrQMm.js";import{r as S}from"./iframe-Dgfvlk1z.js";import{S as t,a as k}from"./SnackBar-RBAfYVYW.js";import"./preload-helper-PPVm8Dsz.js";import"./index-BwaHwwHw.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-validate-CbMNulkZ.js";import"./SvgIcon-DuZPzNRk.js";var w={iphone5:{name:"iPhone 5",styles:{height:"568px",width:"320px"},type:"mobile"},iphone6:{name:"iPhone 6",styles:{height:"667px",width:"375px"},type:"mobile"},iphone6p:{name:"iPhone 6 Plus",styles:{height:"736px",width:"414px"},type:"mobile"},iphone8p:{name:"iPhone 8 Plus",styles:{height:"736px",width:"414px"},type:"mobile"},iphonex:{name:"iPhone X",styles:{height:"812px",width:"375px"},type:"mobile"},iphonexr:{name:"iPhone XR",styles:{height:"896px",width:"414px"},type:"mobile"},iphonexsmax:{name:"iPhone XS Max",styles:{height:"896px",width:"414px"},type:"mobile"},iphonese2:{name:"iPhone SE (2nd generation)",styles:{height:"667px",width:"375px"},type:"mobile"},iphone12mini:{name:"iPhone 12 mini",styles:{height:"812px",width:"375px"},type:"mobile"},iphone12:{name:"iPhone 12",styles:{height:"844px",width:"390px"},type:"mobile"},iphone12promax:{name:"iPhone 12 Pro Max",styles:{height:"926px",width:"428px"},type:"mobile"},iphoneSE3:{name:"iPhone SE 3rd generation",styles:{height:"667px",width:"375px"},type:"mobile"},iphone13:{name:"iPhone 13",styles:{height:"844px",width:"390px"},type:"mobile"},iphone13pro:{name:"iPhone 13 Pro",styles:{height:"844px",width:"390px"},type:"mobile"},iphone13promax:{name:"iPhone 13 Pro Max",styles:{height:"926px",width:"428px"},type:"mobile"},iphone14:{name:"iPhone 14",styles:{height:"844px",width:"390px"},type:"mobile"},iphone14pro:{name:"iPhone 14 Pro",styles:{height:"852px",width:"393px"},type:"mobile"},iphone14promax:{name:"iPhone 14 Pro Max",styles:{height:"932px",width:"430px"},type:"mobile"},ipad:{name:"iPad",styles:{height:"1024px",width:"768px"},type:"tablet"},ipad10p:{name:"iPad Pro 10.5-in",styles:{height:"1112px",width:"834px"},type:"tablet"},ipad11p:{name:"iPad Pro 11-in",styles:{height:"1194px",width:"834px"},type:"tablet"},ipad12p:{name:"iPad Pro 12.9-in",styles:{height:"1366px",width:"1024px"},type:"tablet"},galaxys5:{name:"Galaxy S5",styles:{height:"640px",width:"360px"},type:"mobile"},galaxys9:{name:"Galaxy S9",styles:{height:"740px",width:"360px"},type:"mobile"},nexus5x:{name:"Nexus 5X",styles:{height:"660px",width:"412px"},type:"mobile"},nexus6p:{name:"Nexus 6P",styles:{height:"732px",width:"412px"},type:"mobile"},pixel:{name:"Pixel",styles:{height:"960px",width:"540px"},type:"mobile"},pixelxl:{name:"Pixel XL",styles:{height:"1280px",width:"720px"},type:"mobile"}},C=w;const W={title:"@/design-system/SnackBar",component:k,parameters:{viewport:{options:C},docs:{description:{component:"Meta object for the SnackBar component."}}}},n=a=>{const[r,m]=S.useState(!0);return e.jsxs("div",{children:[!r&&e.jsx("button",{onClick:()=>m(!0),children:"Afficher la notification"}),r&&e.jsx(k,{...a,onClose:()=>m(!1)})]})},o={parameters:{docs:{title:"Snack Bar - Default Success Variant",description:{story:"Demonstration of a success snack bar."}}},render:a=>e.jsx(n,{...a}),args:{variant:t.SUCCESS,description:"Snack Bar with a default success variant",autoClose:!1,testId:"default-success-snack-bar",forceMobile:!0}},i={render:a=>e.jsx(n,{...a}),args:{variant:t.ERROR,description:"Snack Bar with a default error variant",autoClose:!1,testId:"default-error-snack-bar",forceMobile:!0},parameters:{docs:{title:"Snack Bar - Default Error Variant",description:{story:"Demonstration of an error snack bar."}}}},c={render:a=>e.jsx(n,{...a}),args:{variant:t.SUCCESS,description:"SnackBar with a large success variant",autoClose:!1,testId:"large-success-snack-bar"}},p={render:a=>e.jsx(n,{...a}),args:{variant:t.ERROR,description:"SnackBar with a large error variant",autoClose:!1,testId:"large-error-snack-bar"}},d={render:a=>e.jsx(n,{...a}),args:{variant:t.SUCCESS,description:"Snack Bar Success with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)",autoClose:!1,testId:"long-message-success-snack-bar"}},l={render:a=>e.jsx(n,{...a}),args:{variant:t.ERROR,description:"Snack Bar Error with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)",autoClose:!1,testId:"long-message-error-snack-bar"}},P=()=>{const[a,r]=S.useState([]),[m,b]=S.useState(0),u=(s,g)=>{const x=m;b(y=>y+1),r(y=>[...y,{id:x,variant:s,description:g,date:new Date}])},f=s=>{r(g=>g.filter(x=>x.id!==s))},B=[...a];return e.jsxs("div",{style:{height:"500px"},children:[e.jsxs("div",{style:{display:"flex",gap:"12px",flexWrap:"wrap",flexDirection:"column",alignItems:"flex-start"},children:[e.jsx("button",{onClick:()=>u(t.SUCCESS,"Success snackBar"),children:"Add a success snackBar"}),e.jsx("button",{onClick:()=>u(t.ERROR,"Error snackBar"),children:"Add an error snackBar"}),e.jsx("button",{onClick:()=>u(t.SUCCESS,"Success snackBar with a long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)"),children:"Add a success snackBar with a long message."}),e.jsx("button",{onClick:()=>u(t.ERROR,"Error snackBar with a long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)"),children:"Add an error snackBar with a long message."}),e.jsx("button",{onClick:()=>r([]),children:"Clear all snackBars."})]}),e.jsx("div",{style:{alignItems:"flex-end",bottom:"24px",display:"flex",flexDirection:"column",gap:"8px",position:"fixed",right:"24px",zIndex:1e3},children:B.map(s=>e.jsx(k,{variant:s.variant,description:s.description,onClose:()=>f(s.id),autoClose:!0,testId:`snack-bar-${s.id}`},s.id))})]})},h={parameters:{docs:{description:{story:"Demonstration of stacking multiple snack bars. Click on the buttons to add snack bars that stack on the bottom right."}}},render:()=>e.jsx(P,{})};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
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
}`,...o.parameters?.docs?.source},description:{story:"Story for the default SnackBar component.",...o.parameters?.docs?.description}}};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
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
}`,...i.parameters?.docs?.source},description:{story:"Story for the error SnackBar component.",...i.parameters?.docs?.description}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    description: 'SnackBar with a large success variant',
    autoClose: false,
    testId: 'large-success-snack-bar'
  }
}`,...c.parameters?.docs?.source},description:{story:"Story for the long message success SnackBar component.",...c.parameters?.docs?.description}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    description: 'SnackBar with a large error variant',
    autoClose: false,
    testId: 'large-error-snack-bar'
  }
}`,...p.parameters?.docs?.source},description:{story:"Story for the long message success SnackBar component.",...p.parameters?.docs?.description}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    description: 'Snack Bar Success with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)',
    autoClose: false,
    testId: 'long-message-success-snack-bar'
  }
}`,...d.parameters?.docs?.source},description:{story:"Story for the large message success SnackBar component.",...d.parameters?.docs?.description}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    description: 'Snack Bar Error with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)',
    autoClose: false,
    testId: 'long-message-error-snack-bar'
  }
}`,...l.parameters?.docs?.source},description:{story:"Story for the large message error SnackBar component.",...l.parameters?.docs?.description}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  parameters: {
    docs: {
      description: {
        story: 'Demonstration of stacking multiple snack bars. Click on the buttons to add snack bars that stack on the bottom right.'
      }
    }
  },
  render: () => <PlaygroundComponent />
}`,...h.parameters?.docs?.source},description:{story:"Playground for the SnackBar component.",...h.parameters?.docs?.description}}};const O=["DefaultSuccessVariant","DefaultErrorVariant","LargeSuccessVariant","LargeErrorVariant","LargeErrorVariantWithLongMessage","LargeSuccessVariantWithLongMessage","Playground"];export{i as DefaultErrorVariant,o as DefaultSuccessVariant,p as LargeErrorVariant,d as LargeErrorVariantWithLongMessage,c as LargeSuccessVariant,l as LargeSuccessVariantWithLongMessage,h as Playground,O as __namedExportsOrder,W as default};
