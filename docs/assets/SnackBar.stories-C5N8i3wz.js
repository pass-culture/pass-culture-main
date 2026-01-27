import{j as e}from"./jsx-runtime-C_uOM0Gm.js";import{r as S}from"./iframe-CTnXOULQ.js";import{a as k,S as s}from"./SnackBar-DSFSWWuB.js";import{u as C}from"./useMediaQuery-DeNVqfPX.js";import"./preload-helper-PPVm8Dsz.js";import"./index-TscbDd2H.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-validate-CbMNulkZ.js";import"./SvgIcon-CJiY4LCz.js";var P={iphone5:{name:"iPhone 5",styles:{height:"568px",width:"320px"},type:"mobile"},iphone6:{name:"iPhone 6",styles:{height:"667px",width:"375px"},type:"mobile"},iphone6p:{name:"iPhone 6 Plus",styles:{height:"736px",width:"414px"},type:"mobile"},iphone8p:{name:"iPhone 8 Plus",styles:{height:"736px",width:"414px"},type:"mobile"},iphonex:{name:"iPhone X",styles:{height:"812px",width:"375px"},type:"mobile"},iphonexr:{name:"iPhone XR",styles:{height:"896px",width:"414px"},type:"mobile"},iphonexsmax:{name:"iPhone XS Max",styles:{height:"896px",width:"414px"},type:"mobile"},iphonese2:{name:"iPhone SE (2nd generation)",styles:{height:"667px",width:"375px"},type:"mobile"},iphone12mini:{name:"iPhone 12 mini",styles:{height:"812px",width:"375px"},type:"mobile"},iphone12:{name:"iPhone 12",styles:{height:"844px",width:"390px"},type:"mobile"},iphone12promax:{name:"iPhone 12 Pro Max",styles:{height:"926px",width:"428px"},type:"mobile"},iphoneSE3:{name:"iPhone SE 3rd generation",styles:{height:"667px",width:"375px"},type:"mobile"},iphone13:{name:"iPhone 13",styles:{height:"844px",width:"390px"},type:"mobile"},iphone13pro:{name:"iPhone 13 Pro",styles:{height:"844px",width:"390px"},type:"mobile"},iphone13promax:{name:"iPhone 13 Pro Max",styles:{height:"926px",width:"428px"},type:"mobile"},iphone14:{name:"iPhone 14",styles:{height:"844px",width:"390px"},type:"mobile"},iphone14pro:{name:"iPhone 14 Pro",styles:{height:"852px",width:"393px"},type:"mobile"},iphone14promax:{name:"iPhone 14 Pro Max",styles:{height:"932px",width:"430px"},type:"mobile"},ipad:{name:"iPad",styles:{height:"1024px",width:"768px"},type:"tablet"},ipad10p:{name:"iPad Pro 10.5-in",styles:{height:"1112px",width:"834px"},type:"tablet"},ipad11p:{name:"iPad Pro 11-in",styles:{height:"1194px",width:"834px"},type:"tablet"},ipad12p:{name:"iPad Pro 12.9-in",styles:{height:"1366px",width:"1024px"},type:"tablet"},galaxys5:{name:"Galaxy S5",styles:{height:"640px",width:"360px"},type:"mobile"},galaxys9:{name:"Galaxy S9",styles:{height:"740px",width:"360px"},type:"mobile"},nexus5x:{name:"Nexus 5X",styles:{height:"660px",width:"412px"},type:"mobile"},nexus6p:{name:"Nexus 6P",styles:{height:"732px",width:"412px"},type:"mobile"},pixel:{name:"Pixel",styles:{height:"960px",width:"540px"},type:"mobile"},pixelxl:{name:"Pixel XL",styles:{height:"1280px",width:"720px"},type:"mobile"}},E=P;const A={title:"@/design-system/SnackBar",component:k,parameters:{viewport:{options:E},docs:{description:{component:"Meta object for the SnackBar component."}}}},n=a=>{const[r,u]=S.useState(!0);return e.jsxs("div",{children:[!r&&e.jsx("button",{onClick:()=>u(!0),children:"Afficher la notification"}),r&&e.jsx(k,{...a,onClose:()=>u(!1)})]})},i={parameters:{docs:{title:"Snack Bar - Default Success Variant",description:{story:"Demonstration of a success snack bar."}}},render:a=>e.jsx(n,{...a}),args:{variant:s.SUCCESS,description:"Snack Bar with a default success variant",autoClose:!1,testId:"default-success-snack-bar",forceMobile:!0}},c={render:a=>e.jsx(n,{...a}),args:{variant:s.ERROR,description:"Snack Bar with a default error variant",autoClose:!1,testId:"default-error-snack-bar",forceMobile:!0},parameters:{docs:{title:"Snack Bar - Default Error Variant",description:{story:"Demonstration of an error snack bar."}}}},p={render:a=>e.jsx(n,{...a}),args:{variant:s.SUCCESS,description:"SnackBar with a large success variant",autoClose:!1,testId:"large-success-snack-bar"}},d={render:a=>e.jsx(n,{...a}),args:{variant:s.ERROR,description:"SnackBar with a large error variant",autoClose:!1,testId:"large-error-snack-bar"}},l={render:a=>e.jsx(n,{...a}),args:{variant:s.SUCCESS,description:"Snack Bar Success with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)",autoClose:!1,testId:"long-message-success-snack-bar"}},h={render:a=>e.jsx(n,{...a}),args:{variant:s.ERROR,description:"Snack Bar Error with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)",autoClose:!1,testId:"long-message-error-snack-bar"}},v=()=>{const[a,r]=S.useState([]),[u,b]=S.useState(0),f=C("(max-width: 38.125rem)"),g=(t,o)=>{const x=u;b(y=>y+1),r(y=>[...y,{id:x,variant:t,description:o,date:new Date}])},B=t=>{r(o=>o.filter(x=>x.id!==t))},w=a.sort((t,o)=>(f?1:-1)*(t.date.getTime()-o.date.getTime()));return e.jsxs("div",{style:{height:"500px"},children:[e.jsxs("div",{style:{display:"flex",gap:"12px",flexWrap:"wrap",flexDirection:"column",alignItems:"flex-start"},children:[e.jsx("button",{onClick:()=>g(s.SUCCESS,"Success snackBar"),children:"Add a success snackBar"}),e.jsx("button",{onClick:()=>g(s.ERROR,"Error snackBar"),children:"Add an error snackBar"}),e.jsx("button",{onClick:()=>g(s.SUCCESS,"Success snackBar with a long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)"),children:"Add a success snackBar with a long message."}),e.jsx("button",{onClick:()=>g(s.ERROR,"Error snackBar with a long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)"),children:"Add an error snackBar with a long message."}),e.jsx("button",{onClick:()=>r([]),children:"Clear all snackBars."})]}),e.jsx("div",{style:{alignItems:"flex-end",bottom:"24px",display:"flex",flexDirection:"column",gap:"8px",position:"fixed",right:"24px",zIndex:1e3},children:w.map(t=>e.jsx(k,{variant:t.variant,description:t.description,onClose:()=>B(t.id),autoClose:!0,testId:`snack-bar-${t.id}`},t.id))})]})},m={parameters:{docs:{description:{story:"Demonstration of stacking multiple snack bars. Click on the buttons to add snack bars that stack on the bottom right."}}},render:()=>e.jsx(v,{})};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
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
}`,...i.parameters?.docs?.source},description:{story:"Story for the default SnackBar component.",...i.parameters?.docs?.description}}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
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
}`,...c.parameters?.docs?.source},description:{story:"Story for the error SnackBar component.",...c.parameters?.docs?.description}}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    description: 'SnackBar with a large success variant',
    autoClose: false,
    testId: 'large-success-snack-bar'
  }
}`,...p.parameters?.docs?.source},description:{story:"Story for the long message success SnackBar component.",...p.parameters?.docs?.description}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    description: 'SnackBar with a large error variant',
    autoClose: false,
    testId: 'large-error-snack-bar'
  }
}`,...d.parameters?.docs?.source},description:{story:"Story for the long message success SnackBar component.",...d.parameters?.docs?.description}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    description: 'Snack Bar Success with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)',
    autoClose: false,
    testId: 'long-message-success-snack-bar'
  }
}`,...l.parameters?.docs?.source},description:{story:"Story for the large message success SnackBar component.",...l.parameters?.docs?.description}}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    description: 'Snack Bar Error with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)',
    autoClose: false,
    testId: 'long-message-error-snack-bar'
  }
}`,...h.parameters?.docs?.source},description:{story:"Story for the large message error SnackBar component.",...h.parameters?.docs?.description}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  parameters: {
    docs: {
      description: {
        story: 'Demonstration of stacking multiple snack bars. Click on the buttons to add snack bars that stack on the bottom right.'
      }
    }
  },
  render: () => <PlaygroundComponent />
}`,...m.parameters?.docs?.source},description:{story:"Playground for the SnackBar component.",...m.parameters?.docs?.description}}};const N=["DefaultSuccessVariant","DefaultErrorVariant","LargeSuccessVariant","LargeErrorVariant","LargeErrorVariantWithLongMessage","LargeSuccessVariantWithLongMessage","Playground"];export{c as DefaultErrorVariant,i as DefaultSuccessVariant,d as LargeErrorVariant,l as LargeErrorVariantWithLongMessage,p as LargeSuccessVariant,h as LargeSuccessVariantWithLongMessage,m as Playground,N as __namedExportsOrder,A as default};
