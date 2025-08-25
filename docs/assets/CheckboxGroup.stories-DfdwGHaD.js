import{j as r}from"./jsx-runtime-DF2Pcvd1.js";import{a as P,F as W}from"./index.esm-BBvhERNj.js";import{c as z}from"./index-DeARc5FM.js";import{r as O}from"./index-B2-qRKKC.js";import{C as R}from"./Checkbox-CT71AVYH.js";import{F as H}from"./FieldError-B3RhE53I.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./Tag-DoB-Hjk-.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-DfLnDDE5.js";import"./stroke-error-DSZD431a.js";const L="_inline_1ayxx_7",M="_legend_1ayxx_13",T="_error_1ayxx_17",n={"checkbox-group":"_checkbox-group_1ayxx_1",inline:L,legend:M,error:T},u=({group:s,legend:a,disabled:o,required:A,inline:S=!1,asterisk:w=!0,error:h,name:D,onChange:m})=>{const g=O.useId();return r.jsxs("fieldset",{"aria-describedby":g,children:[a&&r.jsxs("legend",{className:n.legend,children:[a,A&&w?" *":""]}),r.jsx("div",{className:z(n["checkbox-group"],{[n.inline]:S}),children:s.map(e=>r.jsx("div",{className:n["checkbox-group-item"],children:r.jsx(R,{asset:e.icon?{variant:"icon",src:e.icon}:void 0,hasError:!!h,label:e.label,disabled:o,onChange:b=>{var k;(k=e.onChange)==null||k.call(e,b),m==null||m(b)},onBlur:e.onBlur,variant:"detailed",checked:!!e.checked,collapsed:e.collapsed,indeterminate:e.indeterminate,name:D,ref:e.ref,sizing:e.sizing})},e.label))}),r.jsx("div",{role:"alert",id:g,children:h&&r.jsx(H,{className:n.error,children:h})})]})};try{u.displayName="CheckboxGroup",u.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{legend:{defaultValue:null,description:"",name:"legend",required:!0,type:{name:"ReactNode"}},group:{defaultValue:null,description:"",name:"group",required:!0,type:{name:"GroupOption[]"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},inline:{defaultValue:{value:"false"},description:"",name:"inline",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"Callback function to handle changes in the radio group.",name:"onChange",required:!1,type:{name:"((e: ChangeEvent<HTMLInputElement>) => void)"}}}}}catch{}const oe={title:"@/ui-kit/forms/CheckboxGroup",component:u},p={name:"group",legend:"Choisir une option",group:[{label:"checkbox 1",onChange:()=>{},checked:!0},{label:"checkbox 2",onChange:()=>{},checked:!1}]},c={args:p},l={args:{name:"group",legend:"Choisir une option"},render:s=>{const a=P({defaultValues:{checkbox1:!0,checkbox2:!1}});return r.jsx(W,{...a,children:r.jsx("form",{children:r.jsx(u,{...s,group:[{label:"checkbox 1",checked:a.watch("checkbox1"),onChange:o=>{a.setValue("checkbox1",o.target.checked)}},{label:"checkbox 2",checked:a.watch("checkbox2"),onChange:o=>{a.setValue("checkbox2",o.target.checked)}}]})})})}},t={args:{...p,variant:"detailed",disabled:!0}},i={args:{...p,variant:"detailed"}},d={args:{...p,variant:"detailed",inline:!0}};var x,f,v;c.parameters={...c.parameters,docs:{...(x=c.parameters)==null?void 0:x.docs,source:{originalSource:`{
  args: defaultArgs
}`,...(v=(f=c.parameters)==null?void 0:f.docs)==null?void 0:v.source}}};var _,C,y;l.parameters={...l.parameters,docs:{...(_=l.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    name: 'group',
    legend: 'Choisir une option'
  },
  render: (args: CheckboxGroupProps) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const hookForm = useForm<{
      checkbox1: boolean;
      checkbox2: boolean;
    }>({
      defaultValues: {
        checkbox1: true,
        checkbox2: false
      }
    });
    return <FormProvider {...hookForm}>
        <form>
          <CheckboxGroup {...args} group={[{
          label: 'checkbox 1',
          checked: hookForm.watch('checkbox1'),
          onChange: e => {
            hookForm.setValue('checkbox1', e.target.checked);
          }
        }, {
          label: 'checkbox 2',
          checked: hookForm.watch('checkbox2'),
          onChange: e => {
            hookForm.setValue('checkbox2', e.target.checked);
          }
        }]}></CheckboxGroup>
        </form>
      </FormProvider>;
  }
}`,...(y=(C=l.parameters)==null?void 0:C.docs)==null?void 0:y.source}}};var F,V,j;t.parameters={...t.parameters,docs:{...(F=t.parameters)==null?void 0:F.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    disabled: true
  }
}`,...(j=(V=t.parameters)==null?void 0:V.docs)==null?void 0:j.source}}};var q,G,E;i.parameters={...i.parameters,docs:{...(q=i.parameters)==null?void 0:q.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed'
  }
}`,...(E=(G=i.parameters)==null?void 0:G.docs)==null?void 0:E.source}}};var N,B,I;d.parameters={...d.parameters,docs:{...(N=d.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    inline: true
  }
}`,...(I=(B=d.parameters)==null?void 0:B.docs)==null?void 0:I.source}}};const ne=["Default","WithinForm","Disabled","WithBorder","Inline"];export{c as Default,t as Disabled,d as Inline,i as WithBorder,l as WithinForm,ne as __namedExportsOrder,oe as default};
