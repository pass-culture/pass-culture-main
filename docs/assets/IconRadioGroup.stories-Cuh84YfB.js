import{j as e}from"./jsx-runtime-D6aF895J.js";import{u as y,F as j}from"./index.esm-Dx4jnakV.js";import{r as v}from"./iframe-DaXpIFWy.js";import{I}from"./IconRadio-DYmlIaFk.js";import{F}from"./FieldError-ByBBPH2U.js";import"./preload-helper-PPVm8Dsz.js";import"./index-HrlENxTc.js";import"./Tooltip-s9aVhEFj.js";import"./stroke-error-DSZD431a.js";import"./SvgIcon-Dpd7M0hP.js";const V="_error_r02xb_43",n={"icon-radio-group-legend":"_icon-radio-group-legend_r02xb_1","icon-radio-group-items":"_icon-radio-group-items_r02xb_4","icon-radio-group-items-container":"_icon-radio-group-items-container_r02xb_10","icon-radio-group-item":"_icon-radio-group-item_r02xb_4","icon-radio-group-scale":"_icon-radio-group-scale_r02xb_20","visually-hidden":"_visually-hidden_r02xb_31",error:V},u=({group:r,name:a,legend:d,required:_=!1,asterisk:x=!0,error:c,value:b,onChange:q})=>{const m=v.useId(),g=v.useId(),h=!!c,i=r.length>0?[r[0].label,r[r.length-1].label]:[],f=i.length>1;return e.jsxs("fieldset",{className:n["icon-radio-group"],name:`icon-radio-group-${a}`,"aria-describedby":`${h?g:""} ${m}`,children:[e.jsxs("legend",{className:n["icon-radio-group-legend"],children:[d,_&&x&&" *"]}),f&&e.jsxs("p",{className:n["visually-hidden"],id:m,children:["L’échelle de sélection va de ",i[0]," à ",i[1]]}),e.jsxs("div",{className:n["icon-radio-group-items-container"],children:[e.jsx("div",{className:n["icon-radio-group-items"],children:r.map(o=>e.jsx(I,{name:a,className:n["icon-radio-group-item"],icon:o.icon,label:o.label,checked:o.value===b,hasError:h,onChange:()=>{q(o.value)}},o.label))}),f&&e.jsx("div",{className:n["icon-radio-group-scale"],"aria-hidden":"true",children:i.map(o=>e.jsx("span",{children:o},o))}),e.jsx("div",{role:"alert",id:g,children:c&&e.jsx(F,{name:a,className:n.error,children:c})})]})]})};try{u.displayName="IconRadioGroup",u.__docgenInfo={description:"",displayName:"IconRadioGroup",props:{name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},legend:{defaultValue:null,description:"",name:"legend",required:!0,type:{name:"string"}},group:{defaultValue:null,description:"```\n{\n  label: Hidden label for the radio button shown as a tooltip on hover/focus\n  icon: Icon element displayed in the small round radio button\n  value: Value of the radio button\n}\n```",name:"group",required:!0,type:{name:"IconRadioGroupValues[]"}},isOptional:{defaultValue:null,description:"",name:"isOptional",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},required:{defaultValue:{value:"false"},description:"",name:"required",required:!1,type:{name:"boolean"}},value:{defaultValue:null,description:"",name:"value",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!0,type:{name:"(value: string) => void"}}}}}catch{}const P={title:"@/ui-kit/forms/IconRadioGroup",component:u},p=[{label:"Mécontent",icon:"J",value:"1"},{label:"Content",icon:e.jsx("span",{children:"2"}),value:"2"},{label:"Très Content",icon:e.jsx("span",{children:"3"}),value:"3"}],s={args:{name:"question",legend:"What is the question?",group:p,value:"1",onChange:()=>{}}},t={args:{name:"question",legend:"What is the question?",error:"This is an error message",group:p,value:"1",onChange:()=>{}}},l={args:{name:"group",legend:"Choisir une option"},render:r=>{const a=y({defaultValues:{question:"1"}});return e.jsx(j,{...a,children:e.jsx("form",{children:e.jsx(u,{...r,group:p,value:a.watch("question"),onChange:d=>a.setValue("question",d)})})})}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
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
