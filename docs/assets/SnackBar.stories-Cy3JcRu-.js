import{j as e}from"./jsx-runtime-CzLqzrAv.js";import{r as i}from"./iframe-BvfMKklh.js";import{c as o}from"./index-IKLFHI78.js";import{f as q}from"./full-clear-Q4kCtSRL.js";import{f as N}from"./full-close-5Oxr7nnd.js";import{f as T}from"./full-validate-CbMNulkZ.js";import{u as I}from"./useMediaQuery-BtIwXIpZ.js";import{S as P}from"./SvgIcon-5n9InJQx.js";import"./preload-helper-PPVm8Dsz.js";var D={iphone5:{name:"iPhone 5",styles:{height:"568px",width:"320px"},type:"mobile"},iphone6:{name:"iPhone 6",styles:{height:"667px",width:"375px"},type:"mobile"},iphone6p:{name:"iPhone 6 Plus",styles:{height:"736px",width:"414px"},type:"mobile"},iphone8p:{name:"iPhone 8 Plus",styles:{height:"736px",width:"414px"},type:"mobile"},iphonex:{name:"iPhone X",styles:{height:"812px",width:"375px"},type:"mobile"},iphonexr:{name:"iPhone XR",styles:{height:"896px",width:"414px"},type:"mobile"},iphonexsmax:{name:"iPhone XS Max",styles:{height:"896px",width:"414px"},type:"mobile"},iphonese2:{name:"iPhone SE (2nd generation)",styles:{height:"667px",width:"375px"},type:"mobile"},iphone12mini:{name:"iPhone 12 mini",styles:{height:"812px",width:"375px"},type:"mobile"},iphone12:{name:"iPhone 12",styles:{height:"844px",width:"390px"},type:"mobile"},iphone12promax:{name:"iPhone 12 Pro Max",styles:{height:"926px",width:"428px"},type:"mobile"},iphoneSE3:{name:"iPhone SE 3rd generation",styles:{height:"667px",width:"375px"},type:"mobile"},iphone13:{name:"iPhone 13",styles:{height:"844px",width:"390px"},type:"mobile"},iphone13pro:{name:"iPhone 13 Pro",styles:{height:"844px",width:"390px"},type:"mobile"},iphone13promax:{name:"iPhone 13 Pro Max",styles:{height:"926px",width:"428px"},type:"mobile"},iphone14:{name:"iPhone 14",styles:{height:"844px",width:"390px"},type:"mobile"},iphone14pro:{name:"iPhone 14 Pro",styles:{height:"852px",width:"393px"},type:"mobile"},iphone14promax:{name:"iPhone 14 Pro Max",styles:{height:"932px",width:"430px"},type:"mobile"},ipad:{name:"iPad",styles:{height:"1024px",width:"768px"},type:"tablet"},ipad10p:{name:"iPad Pro 10.5-in",styles:{height:"1112px",width:"834px"},type:"tablet"},ipad11p:{name:"iPad Pro 11-in",styles:{height:"1194px",width:"834px"},type:"tablet"},ipad12p:{name:"iPad Pro 12.9-in",styles:{height:"1366px",width:"1024px"},type:"tablet"},galaxys5:{name:"Galaxy S5",styles:{height:"640px",width:"360px"},type:"mobile"},galaxys9:{name:"Galaxy S9",styles:{height:"740px",width:"360px"},type:"mobile"},nexus5x:{name:"Nexus 5X",styles:{height:"660px",width:"412px"},type:"mobile"},nexus6p:{name:"Nexus 6P",styles:{height:"732px",width:"412px"},type:"mobile"},pixel:{name:"Pixel",styles:{height:"960px",width:"540px"},type:"mobile"},pixelxl:{name:"Pixel XL",styles:{height:"1280px",width:"720px"},type:"mobile"}},L=D;const M="_container_lffoq_1",O="_wrapper_lffoq_6",U="_content_lffoq_14",W="_show_lffoq_58",A="_hide_lffoq_61",X="_success_lffoq_64",G="_error_lffoq_73",H="_mobile_lffoq_83",t={container:M,wrapper:O,"wrapper-border-radius-desktop":"_wrapper-border-radius-desktop_lffoq_1",content:U,"content-icon":"_content-icon_lffoq_20","content-text":"_content-text_lffoq_26","close-button-container":"_close-button-container_lffoq_32","close-button":"_close-button_lffoq_32","progress-bar-container":"_progress-bar-container_lffoq_45","progress-bar":"_progress-bar_lffoq_45","progress-fill":"_progress-fill_lffoq_1",show:W,"slide-in-bottom":"_slide-in-bottom_lffoq_1",hide:A,"slide-out-bottom":"_slide-out-bottom_lffoq_1",success:X,"content-icon-svg":"_content-icon-svg_lffoq_67",error:G,mobile:H,"slide-in-top":"_slide-in-top_lffoq_1","slide-out-top":"_slide-out-top_lffoq_1","visually-hidden":"_visually-hidden_lffoq_110"},F=5e3,$=1e4,z=120;var r=(a=>(a.SUCCESS="success",a.ERROR="error",a))(r||{});const j=300,Q={success:{icon:T,ariaLabel:"Message de succès",role:"status",ariaLive:"polite"},error:{icon:q,ariaLabel:"Message d'erreur",role:"alert",ariaLive:"assertive"}},p=({variant:a="success",text:n,onClose:c,autoClose:_=!0,testId:w,forceMobile:d=!1})=>{const[C,B]=i.useState(!1),s=i.useRef(!1),l=i.useRef(c),u=I("(max-width: 38.125rem)"),m=d||u;i.useEffect(()=>{l.current=c},[c]);const R=n.length<=z?F:$,E=i.useCallback(()=>{s.current||(s.current=!0,B(!0),setTimeout(()=>{l.current?.()},j))},[]),v=Q[a];return i.useEffect(()=>{if(!_)return;const V=setTimeout(()=>{E()},R);return()=>clearTimeout(V)},[_,R,E]),e.jsxs("div",{className:o(t.container,t[a],C?t.hide:t.show,m?t.mobile:""),style:{"--snackbar-duration":`${R}ms`,"--snackbar-animation-duration":`${j}ms`},role:v.role,"aria-live":v.ariaLive,"aria-atomic":"true","data-testid":w,children:[e.jsxs("div",{className:o(t.wrapper),children:[e.jsxs("div",{className:o(t.content),children:[e.jsx("div",{className:o(t["content-icon"]),children:e.jsx(P,{src:v.icon,alt:"",width:"24",className:t["content-icon-svg"]})}),e.jsxs("p",{className:o(t["content-text"]),children:[e.jsxs("span",{className:t["visually-hidden"],children:[v.ariaLabel," :"," "]}),n]})]}),e.jsx("div",{className:o(t["close-button-container"]),children:e.jsx("button",{className:o(t["close-button"]),type:"button",onClick:E,"aria-label":"Fermer le message",children:e.jsx(P,{src:N,alt:"",width:"24",className:t["close-button-svg"]})})})]}),e.jsx("div",{className:o(t["progress-bar-container"]),children:e.jsx("div",{className:o(t["progress-bar"])})})]})};p.displayName="SnackBar";try{p.displayName="SnackBar",p.__docgenInfo={description:"",displayName:"SnackBar",props:{variant:{defaultValue:{value:"SnackBarVariant.SUCCESS"},description:"The variant of the snack bar",name:"variant",required:!1,type:{name:"enum",value:[{value:'"success"'},{value:'"error"'}]}},text:{defaultValue:null,description:"The text of the snack bar",name:"text",required:!0,type:{name:"string"}},onClose:{defaultValue:null,description:"The callback function to be called when the snack bar is closed",name:"onClose",required:!1,type:{name:"(() => void)"}},testId:{defaultValue:null,description:"The test id of the snack bar",name:"testId",required:!1,type:{name:"string"}},autoClose:{defaultValue:{value:"true"},description:"Whether the snack bar should automatically close or not",name:"autoClose",required:!1,type:{name:"boolean"}},forceMobile:{defaultValue:{value:"false"},description:"Force the mobile view mode.",name:"forceMobile",required:!1,type:{name:"boolean"}}}}}catch{}const oe={title:"@/design-system/SnackBar",component:p,parameters:{viewport:{options:L},docs:{description:{component:"Meta object for the SnackBar component."}}}},h=a=>{const[n,c]=i.useState(!0);return e.jsxs("div",{children:[!n&&e.jsx("button",{onClick:()=>c(!0),children:"Afficher la notification"}),n&&e.jsx(p,{...a,onClose:()=>c(!1)})]})},f={parameters:{docs:{title:"Snack Bar - Default Success Variant",description:{story:"Demonstration of a success snack bar."}}},render:a=>e.jsx(h,{...a}),args:{variant:r.SUCCESS,text:"Snack Bar with a default success variant",autoClose:!1,testId:"default-success-snack-bar",forceMobile:!0}},g={render:a=>e.jsx(h,{...a}),args:{variant:r.ERROR,text:"Snack Bar with a default error variant",autoClose:!1,testId:"default-error-snack-bar",forceMobile:!0},parameters:{docs:{title:"Snack Bar - Default Error Variant",description:{story:"Demonstration of an error snack bar."}}}},x={render:a=>e.jsx(h,{...a}),args:{variant:r.SUCCESS,text:"SnackBar with a large success variant",autoClose:!1,testId:"large-success-snack-bar"}},b={render:a=>e.jsx(h,{...a}),args:{variant:r.ERROR,text:"SnackBar with a large error variant",autoClose:!1,testId:"large-error-snack-bar"}},y={render:a=>e.jsx(h,{...a}),args:{variant:r.SUCCESS,text:"Snack Bar Success with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)",autoClose:!1,testId:"long-message-success-snack-bar"}},S={render:a=>e.jsx(h,{...a}),args:{variant:r.ERROR,text:"Snack Bar Error with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)",autoClose:!1,testId:"long-message-error-snack-bar"}},J=()=>{const[a,n]=i.useState([]),[c,_]=i.useState(0),w=I("(max-width: 600px)"),d=(s,l)=>{const u=c;_(m=>m+1),n(m=>[...m,{id:u,variant:s,text:l,date:new Date}])},C=s=>{n(l=>l.filter(u=>u.id!==s))},B=a.toSorted((s,l)=>(w?1:-1)*(s.date.getTime()-l.date.getTime()));return e.jsxs("div",{style:{height:"500px"},children:[e.jsxs("div",{style:{display:"flex",gap:"12px",flexWrap:"wrap",flexDirection:"column",alignItems:"flex-start"},children:[e.jsx("button",{onClick:()=>d(r.SUCCESS,"Success snackBar"),children:"Add a success snackBar"}),e.jsx("button",{onClick:()=>d(r.ERROR,"Error snackBar"),children:"Add an error snackBar"}),e.jsx("button",{onClick:()=>d(r.SUCCESS,"Success snackBar with a long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)"),children:"Add a success snackBar with a long message."}),e.jsx("button",{onClick:()=>d(r.ERROR,"Error snackBar with a long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)"),children:"Add an error snackBar with a long message."}),e.jsx("button",{onClick:()=>n([]),children:"Clear all snackBars."})]}),e.jsx("div",{style:{alignItems:"flex-end",bottom:"24px",display:"flex",flexDirection:"column",gap:"8px",position:"fixed",right:"24px",zIndex:1e3},children:B.map(s=>e.jsx(p,{variant:s.variant,text:s.text,onClose:()=>C(s.id),autoClose:!0,testId:`snack-bar-${s.id}`},s.id))})]})},k={parameters:{docs:{description:{story:"Demonstration of stacking multiple snack bars. Click on the buttons to add snack bars that stack on the bottom right."}}},render:()=>e.jsx(J,{})};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
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
    text: 'Snack Bar with a default success variant',
    autoClose: false,
    testId: 'default-success-snack-bar',
    forceMobile: true
  }
}`,...f.parameters?.docs?.source},description:{story:"Story for the default SnackBar component.",...f.parameters?.docs?.description}}};g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    text: 'Snack Bar with a default error variant',
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
}`,...g.parameters?.docs?.source},description:{story:"Story for the error SnackBar component.",...g.parameters?.docs?.description}}};x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    text: 'SnackBar with a large success variant',
    autoClose: false,
    testId: 'large-success-snack-bar'
  }
}`,...x.parameters?.docs?.source},description:{story:"Story for the long message success SnackBar component.",...x.parameters?.docs?.description}}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    text: 'SnackBar with a large error variant',
    autoClose: false,
    testId: 'large-error-snack-bar'
  }
}`,...b.parameters?.docs?.source},description:{story:"Story for the long message success SnackBar component.",...b.parameters?.docs?.description}}};y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    text: 'Snack Bar Success with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)',
    autoClose: false,
    testId: 'long-message-success-snack-bar'
  }
}`,...y.parameters?.docs?.source},description:{story:"Story for the large message success SnackBar component.",...y.parameters?.docs?.description}}};S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  render: args => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    text: 'Snack Bar Error with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)',
    autoClose: false,
    testId: 'long-message-error-snack-bar'
  }
}`,...S.parameters?.docs?.source},description:{story:"Story for the large message error SnackBar component.",...S.parameters?.docs?.description}}};k.parameters={...k.parameters,docs:{...k.parameters?.docs,source:{originalSource:`{
  parameters: {
    docs: {
      description: {
        story: 'Demonstration of stacking multiple snack bars. Click on the buttons to add snack bars that stack on the bottom right.'
      }
    }
  },
  render: () => <PlaygroundComponent />
}`,...k.parameters?.docs?.source},description:{story:"Playground for the SnackBar component.",...k.parameters?.docs?.description}}};const ie=["DefaultSuccessVariant","DefaultErrorVariant","LargeSuccessVariant","LargeErrorVariant","LargeErrorVariantWithLongMessage","LargeSuccessVariantWithLongMessage","Playground"];export{g as DefaultErrorVariant,f as DefaultSuccessVariant,b as LargeErrorVariant,y as LargeErrorVariantWithLongMessage,x as LargeSuccessVariant,S as LargeSuccessVariantWithLongMessage,k as Playground,ie as __namedExportsOrder,oe as default};
