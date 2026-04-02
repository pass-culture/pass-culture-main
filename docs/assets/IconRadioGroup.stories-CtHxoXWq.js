import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-COrE2XJm.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./FieldFooter-I0iRovCc.js";import{a as i,t as a}from"./index.esm--NUP_0Yy.js";import{t as o}from"./IconRadio-DSn8y1Vb.js";var s=e(t(),1),c={"icon-radio-group-legend":`_icon-radio-group-legend_16lqu_1`,"icon-radio-group-items":`_icon-radio-group-items_16lqu_4`,"icon-radio-group-items-container":`_icon-radio-group-items-container_16lqu_10`,"icon-radio-group-item":`_icon-radio-group-item_16lqu_4`,"icon-radio-group-scale":`_icon-radio-group-scale_16lqu_20`,"visually-hidden":`_visually-hidden_16lqu_31`},l=n(),u=({group:e,name:t,legend:n,required:i=!1,requiredIndicator:a=`symbol`,error:u,value:d,onChange:f})=>{let p=(0,s.useId)(),m=(0,s.useId)(),h=!!u,g=e.length>0?[e[0].label,e[e.length-1].label]:[],_=g.length>1;return(0,l.jsxs)(`fieldset`,{className:c[`icon-radio-group`],name:`icon-radio-group-${t}`,"aria-describedby":`${h?m:``} ${p}`,children:[(0,l.jsxs)(`legend`,{className:c[`icon-radio-group-legend`],children:[n,i&&a===`symbol`&&(0,l.jsx)(l.Fragment,{children:`\xA0*`})]}),_&&(0,l.jsxs)(`p`,{className:c[`visually-hidden`],id:p,children:[`L’échelle de sélection va de `,g[0],` à `,g[1]]}),(0,l.jsxs)(`div`,{className:c[`icon-radio-group-items-container`],children:[(0,l.jsx)(`div`,{className:c[`icon-radio-group-items`],children:e.map(e=>(0,l.jsx)(o,{name:t,className:c[`icon-radio-group-item`],icon:e.icon,label:e.label,checked:e.value===d,hasError:h,onChange:()=>{f(e.value)}},e.label))}),_&&(0,l.jsx)(`div`,{className:c[`icon-radio-group-scale`],"aria-hidden":`true`,children:g.map(e=>(0,l.jsx)(`span`,{children:e},e))}),(0,l.jsx)(r,{error:u,errorId:m})]})]})};try{u.displayName=`IconRadioGroup`,u.__docgenInfo={description:``,displayName:`IconRadioGroup`,props:{name:{defaultValue:null,description:``,name:`name`,required:!0,type:{name:`string`}},legend:{defaultValue:null,description:``,name:`legend`,required:!0,type:{name:`string`}},group:{defaultValue:null,description:``,name:`group`,required:!0,type:{name:`IconRadioGroupValues[]`}},requiredIndicator:{defaultValue:{value:`symbol`},description:`What type of required indicator is displayed`,name:`requiredIndicator`,required:!1,type:{name:`enum`,value:[{value:`"symbol"`},{value:`"explicit"`},{value:`"hidden"`}]}},error:{defaultValue:null,description:``,name:`error`,required:!1,type:{name:`string`}},required:{defaultValue:{value:`false`},description:``,name:`required`,required:!1,type:{name:`boolean`}},value:{defaultValue:null,description:``,name:`value`,required:!0,type:{name:`string`}},onChange:{defaultValue:null,description:``,name:`onChange`,required:!0,type:{name:`(value: string) => void`}}}}}catch{}var d={title:`@/ui-kit/forms/IconRadioGroup`,component:u},f=[{label:`Mécontent`,icon:`J`,value:`1`},{label:`Content`,icon:(0,l.jsx)(`span`,{children:`2`}),value:`2`},{label:`Très Content`,icon:(0,l.jsx)(`span`,{children:`3`}),value:`3`}],p={args:{name:`question`,legend:`What is the question?`,group:f,value:`1`,onChange:()=>{}}},m={args:{name:`question`,legend:`What is the question?`,error:`This is an error message`,group:f,value:`1`,onChange:()=>{}}},h={args:{name:`group`,legend:`Choisir une option`},render:e=>{let t=i({defaultValues:{question:`1`}});return(0,l.jsx)(a,{...t,children:(0,l.jsx)(`form`,{children:(0,l.jsx)(u,{...e,group:f,value:t.watch(`question`),onChange:e=>t.setValue(`question`,e)})})})}};p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'question',
    legend: 'What is the question?',
    group: group,
    value: '1',
    onChange: () => {}
  }
}`,...p.parameters?.docs?.source}}},m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'question',
    legend: 'What is the question?',
    error: 'This is an error message',
    group: group,
    value: '1',
    onChange: () => {}
  }
}`,...m.parameters?.docs?.source}}},h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
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
}`,...h.parameters?.docs?.source}}};var g=[`Default`,`WithError`,`WithinForm`];export{p as Default,m as WithError,h as WithinForm,g as __namedExportsOrder,d as default};