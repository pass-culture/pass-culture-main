import{j as e}from"./jsx-runtime-B98n_Yrv.js";import{u as b,F as j}from"./index.esm-DaNEenLE.js";import{r as q}from"./iframe-BB2Vf2Ik.js";import{F}from"./FieldFooter-BBWjKfFR.js";import{I}from"./IconRadio-CMJ1kLbm.js";import"./preload-helper-PPVm8Dsz.js";import"./index-COnx5CMC.js";import"./full-error-BFAmjN4t.js";import"./index.module-D4WhIeQf.js";import"./SvgIcon-CC0dx-C-.js";import"./Tooltip-B-ZJQF1-.js";const n={"icon-radio-group-legend":"_icon-radio-group-legend_16lqu_1","icon-radio-group-items":"_icon-radio-group-items_16lqu_4","icon-radio-group-items-container":"_icon-radio-group-items-container_16lqu_10","icon-radio-group-item":"_icon-radio-group-item_16lqu_4","icon-radio-group-scale":"_icon-radio-group-scale_16lqu_20","visually-hidden":"_visually-hidden_16lqu_31"},u=({group:o,name:a,legend:d,required:v=!1,asterisk:_=!0,error:p,value:y,onChange:x})=>{const m=q.useId(),g=q.useId(),h=!!p,i=o.length>0?[o[0].label,o[o.length-1].label]:[],f=i.length>1;return e.jsxs("fieldset",{className:n["icon-radio-group"],name:`icon-radio-group-${a}`,"aria-describedby":`${h?g:""} ${m}`,children:[e.jsxs("legend",{className:n["icon-radio-group-legend"],children:[d,v&&_&&" *"]}),f&&e.jsxs("p",{className:n["visually-hidden"],id:m,children:["L’échelle de sélection va de ",i[0]," à ",i[1]]}),e.jsxs("div",{className:n["icon-radio-group-items-container"],children:[e.jsx("div",{className:n["icon-radio-group-items"],children:o.map(r=>e.jsx(I,{name:a,className:n["icon-radio-group-item"],icon:r.icon,label:r.label,checked:r.value===y,hasError:h,onChange:()=>{x(r.value)}},r.label))}),f&&e.jsx("div",{className:n["icon-radio-group-scale"],"aria-hidden":"true",children:i.map(r=>e.jsx("span",{children:r},r))}),e.jsx(F,{error:p,errorId:g})]})]})};try{u.displayName="IconRadioGroup",u.__docgenInfo={description:"",displayName:"IconRadioGroup",props:{name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},legend:{defaultValue:null,description:"",name:"legend",required:!0,type:{name:"string"}},group:{defaultValue:null,description:"```\n{\n  label: Hidden label for the radio button shown as a tooltip on hover/focus\n  icon: Icon element displayed in the small round radio button\n  value: Value of the radio button\n}\n```",name:"group",required:!0,type:{name:"IconRadioGroupValues[]"}},isOptional:{defaultValue:null,description:"",name:"isOptional",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},required:{defaultValue:{value:"false"},description:"",name:"required",required:!1,type:{name:"boolean"}},value:{defaultValue:null,description:"",name:"value",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!0,type:{name:"(value: string) => void"}}}}}catch{}const P={title:"@/ui-kit/forms/IconRadioGroup",component:u},c=[{label:"Mécontent",icon:"J",value:"1"},{label:"Content",icon:e.jsx("span",{children:"2"}),value:"2"},{label:"Très Content",icon:e.jsx("span",{children:"3"}),value:"3"}],s={args:{name:"question",legend:"What is the question?",group:c,value:"1",onChange:()=>{}}},t={args:{name:"question",legend:"What is the question?",error:"This is an error message",group:c,value:"1",onChange:()=>{}}},l={args:{name:"group",legend:"Choisir une option"},render:o=>{const a=b({defaultValues:{question:"1"}});return e.jsx(j,{...a,children:e.jsx("form",{children:e.jsx(u,{...o,group:c,value:a.watch("question"),onChange:d=>a.setValue("question",d)})})})}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
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
}`,...l.parameters?.docs?.source}}};const T=["Default","WithError","WithinForm"];export{s as Default,t as WithError,l as WithinForm,T as __namedExportsOrder,P as default};
