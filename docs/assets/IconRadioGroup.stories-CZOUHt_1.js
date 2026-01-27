import{j as e}from"./jsx-runtime-C_uOM0Gm.js";import{u as j,F}from"./index.esm-B74CwnGv.js";import{r as v}from"./iframe-CTnXOULQ.js";import{F as I}from"./FieldFooter-CL0tzobd.js";import{I as b}from"./IconRadio-Mz49gAaX.js";import"./preload-helper-PPVm8Dsz.js";import"./index-TscbDd2H.js";import"./full-error-BFAmjN4t.js";import"./index.module-DEHgy3-r.js";import"./SvgIcon-CJiY4LCz.js";import"./Tooltip-GJ5PEk5n.js";const n={"icon-radio-group-legend":"_icon-radio-group-legend_16lqu_1","icon-radio-group-items":"_icon-radio-group-items_16lqu_4","icon-radio-group-items-container":"_icon-radio-group-items-container_16lqu_10","icon-radio-group-item":"_icon-radio-group-item_16lqu_4","icon-radio-group-scale":"_icon-radio-group-scale_16lqu_20","visually-hidden":"_visually-hidden_16lqu_31"},u=({group:r,name:a,legend:d,required:f=!1,requiredIndicator:_="symbol",error:m,value:y,onChange:x})=>{const p=v.useId(),g=v.useId(),h=!!m,i=r.length>0?[r[0].label,r[r.length-1].label]:[],q=i.length>1;return e.jsxs("fieldset",{className:n["icon-radio-group"],name:`icon-radio-group-${a}`,"aria-describedby":`${h?g:""} ${p}`,children:[e.jsxs("legend",{className:n["icon-radio-group-legend"],children:[d,f&&_==="symbol"&&e.jsx(e.Fragment,{children:" *"})]}),q&&e.jsxs("p",{className:n["visually-hidden"],id:p,children:["L’échelle de sélection va de ",i[0]," à ",i[1]]}),e.jsxs("div",{className:n["icon-radio-group-items-container"],children:[e.jsx("div",{className:n["icon-radio-group-items"],children:r.map(o=>e.jsx(b,{name:a,className:n["icon-radio-group-item"],icon:o.icon,label:o.label,checked:o.value===y,hasError:h,onChange:()=>{x(o.value)}},o.label))}),q&&e.jsx("div",{className:n["icon-radio-group-scale"],"aria-hidden":"true",children:i.map(o=>e.jsx("span",{children:o},o))}),e.jsx(I,{error:m,errorId:g})]})]})};try{u.displayName="IconRadioGroup",u.__docgenInfo={description:"",displayName:"IconRadioGroup",props:{name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},legend:{defaultValue:null,description:"",name:"legend",required:!0,type:{name:"string"}},group:{defaultValue:null,description:"",name:"group",required:!0,type:{name:"IconRadioGroupValues[]"}},requiredIndicator:{defaultValue:{value:"symbol"},description:"What type of required indicator is displayed",name:"requiredIndicator",required:!1,type:{name:"enum",value:[{value:'"symbol"'},{value:'"hidden"'},{value:'"explicit"'}]}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},required:{defaultValue:{value:"false"},description:"",name:"required",required:!1,type:{name:"boolean"}},value:{defaultValue:null,description:"",name:"value",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!0,type:{name:"(value: string) => void"}}}}}catch{}const $={title:"@/ui-kit/forms/IconRadioGroup",component:u},c=[{label:"Mécontent",icon:"J",value:"1"},{label:"Content",icon:e.jsx("span",{children:"2"}),value:"2"},{label:"Très Content",icon:e.jsx("span",{children:"3"}),value:"3"}],s={args:{name:"question",legend:"What is the question?",group:c,value:"1",onChange:()=>{}}},t={args:{name:"question",legend:"What is the question?",error:"This is an error message",group:c,value:"1",onChange:()=>{}}},l={args:{name:"group",legend:"Choisir une option"},render:r=>{const a=j({defaultValues:{question:"1"}});return e.jsx(F,{...a,children:e.jsx("form",{children:e.jsx(u,{...r,group:c,value:a.watch("question"),onChange:d=>a.setValue("question",d)})})})}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'question',
    legend: 'What is the question?',
    group: group,
    value: '1',
    onChange: () => {}
  }
}`,...s.parameters?.docs?.source}}};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'question',
    legend: 'What is the question?',
    error: 'This is an error message',
    group: group,
    value: '1',
    onChange: () => {}
  }
}`,...t.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
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
}`,...l.parameters?.docs?.source}}};const w=["Default","WithError","WithinForm"];export{s as Default,t as WithError,l as WithinForm,w as __namedExportsOrder,$ as default};
