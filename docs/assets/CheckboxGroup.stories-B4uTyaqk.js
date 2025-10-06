import{j as r}from"./jsx-runtime-IhBO-TUz.js";import{u as v,F as _}from"./index.esm-CiG9UK_C.js";import{c as y}from"./index-B14GwyKs.js";import{r as F}from"./iframe-CKreLz1g.js";import{C as V}from"./Checkbox-BzdPOFqu.js";import{F as j}from"./FieldError-fiVNChES.js";import"./preload-helper-PPVm8Dsz.js";import"./Tag-C7wNP0vl.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-Dn5J_L1j.js";import"./stroke-error-DSZD431a.js";const q="_inline_kny0n_7",G="_legend_kny0n_13",E="_error_kny0n_17",o={"checkbox-group":"_checkbox-group_kny0n_1",inline:q,legend:G,error:E},u=({group:s,legend:a,disabled:n,required:k,inline:b=!1,asterisk:f=!0,error:h,name:x,onChange:C})=>{const m=F.useId();return r.jsxs("fieldset",{"aria-describedby":m,children:[a&&r.jsxs("legend",{className:o.legend,children:[a,k&&f?" *":""]}),r.jsx("div",{className:y(o["checkbox-group"],{[o.inline]:b}),children:s.map(e=>r.jsx("div",{className:o["checkbox-group-item"],children:r.jsx(V,{asset:e.icon?{variant:"icon",src:e.icon}:void 0,hasError:!!h,label:e.label,disabled:n,onChange:g=>{e.onChange?.(g),C?.(g)},onBlur:e.onBlur,variant:"detailed",checked:!!e.checked,collapsed:e.collapsed,indeterminate:e.indeterminate,name:x,ref:e.ref,sizing:e.sizing})},e.label))}),r.jsx("div",{role:"alert",id:m,children:h&&r.jsx(j,{className:o.error,children:h})})]})};try{u.displayName="CheckboxGroup",u.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{legend:{defaultValue:null,description:"",name:"legend",required:!0,type:{name:"ReactNode"}},group:{defaultValue:null,description:"",name:"group",required:!0,type:{name:"GroupOption[]"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},inline:{defaultValue:{value:"false"},description:"",name:"inline",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"Callback function to handle changes in the radio group.",name:"onChange",required:!1,type:{name:"((e: ChangeEvent<HTMLInputElement>) => void)"}}}}}catch{}const R={title:"@/ui-kit/forms/CheckboxGroup",component:u},p={name:"group",legend:"Choisir une option",group:[{label:"checkbox 1",onChange:()=>{},checked:!0},{label:"checkbox 2",onChange:()=>{},checked:!1}]},c={args:p},t={args:{name:"group",legend:"Choisir une option"},render:s=>{const a=v({defaultValues:{checkbox1:!0,checkbox2:!1}});return r.jsx(_,{...a,children:r.jsx("form",{children:r.jsx(u,{...s,group:[{label:"checkbox 1",checked:a.watch("checkbox1"),onChange:n=>{a.setValue("checkbox1",n.target.checked)}},{label:"checkbox 2",checked:a.watch("checkbox2"),onChange:n=>{a.setValue("checkbox2",n.target.checked)}}]})})})}},l={args:{...p,variant:"detailed",disabled:!0}},i={args:{...p,variant:"detailed"}},d={args:{...p,variant:"detailed",inline:!0}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: defaultArgs
}`,...c.parameters?.docs?.source}}};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
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
}`,...t.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    disabled: true
  }
}`,...l.parameters?.docs?.source}}};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed'
  }
}`,...i.parameters?.docs?.source}}};d.parameters={...d.parameters,docs:{...d.parameters?.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    inline: true
  }
}`,...d.parameters?.docs?.source}}};const H=["Default","WithinForm","Disabled","WithBorder","Inline"];export{c as Default,l as Disabled,d as Inline,i as WithBorder,t as WithinForm,H as __namedExportsOrder,R as default};
