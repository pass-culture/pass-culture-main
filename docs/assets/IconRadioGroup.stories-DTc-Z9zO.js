import{i as e,s as t}from"./preload-helper-xPQekRTU.js";import{C as n}from"./iframe-CfylVhRV.js";import{t as r}from"./jsx-runtime-CaZkqeYb.js";import{n as i,t as a}from"./FieldFooter-DAfznmFE.js";import{i as o,o as s,t as c}from"./index.esm-BmKaeQeE.js";import{n as l,t as u}from"./IconRadio-D9DRqy83.js";var d,f=e((()=>{d={"icon-radio-group-legend":`_icon-radio-group-legend_16lqu_1`,"icon-radio-group-items":`_icon-radio-group-items_16lqu_4`,"icon-radio-group-items-container":`_icon-radio-group-items-container_16lqu_10`,"icon-radio-group-item":`_icon-radio-group-item_16lqu_4`,"icon-radio-group-scale":`_icon-radio-group-scale_16lqu_20`,"visually-hidden":`_visually-hidden_16lqu_31`}})),p,m,h,g=e((()=>{p=t(n(),1),i(),l(),f(),m=r(),h=({group:e,name:t,legend:n,required:r=!1,requiredIndicator:i=`symbol`,error:o,value:s,onChange:c})=>{let l=(0,p.useId)(),f=(0,p.useId)(),h=!!o,g=e.length>0?[e[0].label,e[e.length-1].label]:[],_=g.length>1;return(0,m.jsxs)(`fieldset`,{className:d[`icon-radio-group`],name:`icon-radio-group-${t}`,"aria-describedby":`${h?f:``} ${l}`,children:[(0,m.jsxs)(`legend`,{className:d[`icon-radio-group-legend`],children:[n,r&&i===`symbol`&&(0,m.jsx)(m.Fragment,{children:`\xA0*`})]}),_&&(0,m.jsxs)(`p`,{className:d[`visually-hidden`],id:l,children:[`L’échelle de sélection va de `,g[0],` à `,g[1]]}),(0,m.jsxs)(`div`,{className:d[`icon-radio-group-items-container`],children:[(0,m.jsx)(`div`,{className:d[`icon-radio-group-items`],children:e.map(e=>(0,m.jsx)(u,{name:t,className:d[`icon-radio-group-item`],icon:e.icon,label:e.label,checked:e.value===s,hasError:h,onChange:()=>{c(e.value)}},e.label))}),_&&(0,m.jsx)(`div`,{className:d[`icon-radio-group-scale`],"aria-hidden":`true`,children:g.map(e=>(0,m.jsx)(`span`,{children:e},e))}),(0,m.jsx)(a,{error:o,errorId:f})]})]})};try{h.displayName=`IconRadioGroup`,h.__docgenInfo={description:``,displayName:`IconRadioGroup`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,methods:[],props:{name:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`name`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!0,tags:{},type:{name:`string`}},legend:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`legend`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!0,tags:{},type:{name:`string`}},group:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`group`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!0,tags:{},type:{name:`IconRadioGroupValues[]`}},requiredIndicator:{defaultValue:{value:`symbol`},declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:`What type of required indicator is displayed`,name:`requiredIndicator`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!1,tags:{},type:{name:`enum`,raw:`RequiredIndicator`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}},error:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`error`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!1,tags:{},type:{name:`string`}},required:{defaultValue:{value:`false`},declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`required`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!1,tags:{},type:{name:`boolean`}},value:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`value`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!0,tags:{},type:{name:`string`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`}],description:``,name:`onChange`,parent:{fileName:`pro/src/ui-kit/form/IconRadioGroup/IconRadioGroup.tsx`,name:`IconRadioGroupProps`},required:!0,tags:{},type:{name:`(value: string) => void`}}},tags:{}}}catch{}})),_,v,y,b,x,S,C;e((()=>{o(),g(),_=r(),v={title:`@/ui-kit/forms/IconRadioGroup`,component:h},y=[{label:`Mécontent`,icon:`J`,value:`1`},{label:`Content`,icon:(0,_.jsx)(`span`,{children:`2`}),value:`2`},{label:`Très Content`,icon:(0,_.jsx)(`span`,{children:`3`}),value:`3`}],b={args:{name:`question`,legend:`What is the question?`,group:y,value:`1`,onChange:()=>{}}},x={args:{name:`question`,legend:`What is the question?`,error:`This is an error message`,group:y,value:`1`,onChange:()=>{}}},S={args:{name:`group`,legend:`Choisir une option`},render:e=>{let t=s({defaultValues:{question:`1`}});return(0,_.jsx)(c,{...t,children:(0,_.jsx)(`form`,{children:(0,_.jsx)(h,{...e,group:y,value:t.watch(`question`),onChange:e=>t.setValue(`question`,e)})})})}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'question',
    legend: 'What is the question?',
    group: group,
    value: '1',
    onChange: () => {}
  }
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'question',
    legend: 'What is the question?',
    error: 'This is an error message',
    group: group,
    value: '1',
    onChange: () => {}
  }
}`,...x.parameters?.docs?.source}}},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'group',
    legend: 'Choisir une option'
  },
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
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
}`,...S.parameters?.docs?.source}}},C=[`Default`,`WithError`,`WithinForm`]}))();export{b as Default,x as WithError,S as WithinForm,C as __namedExportsOrder,v as default};