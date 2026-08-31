import{n as e}from"./rolldown-runtime-DkW27tQK.js";import{d as t}from"./iframe-uFEEvKcX.js";import{t as n}from"./jsx-runtime-DeHZSEgm.js";import{n as r,t as i}from"./FieldFooter-BI4fC8Ei.js";import{i as a,o,t as s}from"./index.esm-DwnsBfV4.js";import{n as c,t as l}from"./IconRadio-rQoI-uk8.js";var u;function d(){return(d=e((()=>{u={"icon-radio-group-legend":`_icon-radio-group-legend_1na5l_1`,"icon-radio-group-items":`_icon-radio-group-items_1na5l_4`,"icon-radio-group-items-container":`_icon-radio-group-items-container_1na5l_10`,"icon-radio-group-scale":`_icon-radio-group-scale_1na5l_15`,"visually-hidden":`_visually-hidden_1na5l_26`}})))()}var f,p,m;function h(){return(h=e((()=>{f=t(),r(),c(),d(),p=n(),m=({group:e,name:t,legend:n,required:r=!1,requiredIndicator:a=`symbol`,error:o,value:s,onChange:c})=>{let d=(0,f.useId)(),m=(0,f.useId)(),h=!!o,g=e.length>0?[e[0].label,e[e.length-1].label]:[],_=g.length>1;return(0,p.jsxs)(`fieldset`,{className:u[`icon-radio-group`],name:`icon-radio-group-${t}`,"aria-describedby":`${h?m:``} ${d}`,"aria-invalid":h||void 0,children:[(0,p.jsxs)(`legend`,{className:u[`icon-radio-group-legend`],children:[n,r&&a===`symbol`&&(0,p.jsx)(p.Fragment,{children:`\xA0*`})]}),_&&(0,p.jsxs)(`p`,{className:u[`visually-hidden`],id:d,children:[`L’échelle de sélection va de `,g[0],` à `,g[1]]}),(0,p.jsxs)(`div`,{className:u[`icon-radio-group-items-container`],children:[(0,p.jsx)(`div`,{className:u[`icon-radio-group-items`],children:e.map(e=>(0,p.jsx)(l,{name:t,icon:e.icon,label:e.label,checked:e.value===s,onChange:()=>{c(e.value)}},e.label))}),_&&(0,p.jsx)(`div`,{className:u[`icon-radio-group-scale`],"aria-hidden":`true`,children:g.map(e=>(0,p.jsx)(`span`,{children:e},e))}),(0,p.jsx)(i,{error:o,errorId:m})]})]})};try{m.displayName=`IconRadioGroup`,m.__docgenInfo={description:``,displayName:`IconRadioGroup`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,methods:[],props:{name:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`name`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!0,tags:{},type:{name:`string`}},legend:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`legend`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!0,tags:{},type:{name:`string`}},group:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`group`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!0,tags:{},type:{name:`IconRadioGroupValues[]`}},requiredIndicator:{defaultValue:{value:`symbol`},declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:`What type of required indicator is displayed`,name:`requiredIndicator`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!1,tags:{},type:{name:`enum`,raw:`RequiredIndicator`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}},error:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`error`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!1,tags:{},type:{name:`string`}},required:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`required`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!1,tags:{},type:{name:`boolean`}},value:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`value`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!0,tags:{},type:{name:`string`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`onChange`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!0,tags:{},type:{name:`(value: string) => void`}}},tags:{}}}catch{}})))()}var g,_,v,y,b,x,S;function C(){return(C=e((()=>{a(),h(),g=n(),_={title:`@/ui-kit/forms/IconRadioGroup`,component:m},v=[{label:`Mécontent`,icon:`J`,value:`1`},{label:`Content`,icon:(0,g.jsx)(`span`,{children:`2`}),value:`2`},{label:`Très Content`,icon:(0,g.jsx)(`span`,{children:`3`}),value:`3`}],y={args:{name:`question`,legend:`What is the question?`,group:v,value:`1`,onChange:()=>{}}},b={args:{name:`question`,legend:`What is the question?`,error:`This is an error message`,group:v,value:`1`,onChange:()=>{}}},x={args:{name:`group`,legend:`Choisir une option`},render:e=>{let t=o({defaultValues:{question:`1`}});return(0,g.jsx)(s,{...t,children:(0,g.jsx)(`form`,{children:(0,g.jsx)(m,{...e,group:v,value:t.watch(`question`),onChange:e=>t.setValue(`question`,e)})})})}},y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'question',
    legend: 'What is the question?',
    group: group,
    value: '1',
    onChange: () => {}
  }
}`,...y.parameters?.docs?.source}}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'question',
    legend: 'What is the question?',
    error: 'This is an error message',
    group: group,
    value: '1',
    onChange: () => {}
  }
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'group',
    legend: 'Choisir une option'
  },
  render: (args: any) => {
    const hookForm = useForm<{
      question: string;
    }>({
      defaultValues: {
        question: '1'
      }
    });
    return <FormProvider {...hookForm}>
        <form>
          <IconRadioGroup {...args} group={group} value={hookForm.watch('question')} onChange={val => hookForm.setValue('question', val)}></IconRadioGroup>
        </form>
      </FormProvider>;
  }
}`,...x.parameters?.docs?.source}}},S=[`Default`,`WithError`,`WithinForm`]})))()}C();export{y as Default,b as WithError,x as WithinForm,S as __namedExportsOrder,_ as default};