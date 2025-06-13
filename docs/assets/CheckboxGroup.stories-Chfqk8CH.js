import{j as r}from"./jsx-runtime-BYYWji4R.js";import{a as S,F as D}from"./index.esm-nHDMj4MR.js";import{c as W}from"./index-DeARc5FM.js";import{r as P}from"./index-ClcD9ViR.js";import{C as z}from"./Checkbox-nM6ULP8N.js";import{F as O}from"./FieldError-ky1_Lcaw.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./Tag-CQO0EYV8.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-CyWUmZpn.js";import"./stroke-error-DSZD431a.js";const R="_inline_1ayxx_7",w="_legend_1ayxx_13",H="_error_1ayxx_17",o={"checkbox-group":"_checkbox-group_1ayxx_1",inline:R,legend:w,error:H},d=({group:n,legend:a,disabled:N,required:B,inline:A=!1,asterisk:E=!0,error:p,name:I})=>{const m=P.useId();return r.jsxs("fieldset",{"aria-describedby":m,children:[a&&r.jsxs("legend",{className:o.legend,children:[a,B&&E?" *":""]}),r.jsx("div",{className:W(o["checkbox-group"],{[o.inline]:A}),children:n.map(e=>r.jsx("div",{className:o["checkbox-group-item"],children:r.jsx(z,{asset:e.icon?{variant:"icon",src:e.icon}:void 0,hasError:!!p,label:e.label,disabled:N,onChange:e.onChange,onBlur:e.onBlur,variant:"detailed",checked:!!e.checked,collapsed:e.collapsed,indeterminate:e.indeterminate,name:I,ref:e.ref,sizing:e.sizing})},e.label))}),r.jsx("div",{role:"alert",id:m,children:p&&r.jsx(O,{className:o.error,children:p})})]})};try{d.displayName="CheckboxGroup",d.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{legend:{defaultValue:null,description:"",name:"legend",required:!0,type:{name:"ReactNode"}},group:{defaultValue:null,description:"",name:"group",required:!0,type:{name:"GroupOption[]"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},inline:{defaultValue:{value:"false"},description:"",name:"inline",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!1,type:{name:"string"}}}}}catch{}const ee={title:"ui-kit/formsV2/CheckboxGroup",component:d},u={name:"group",legend:"Choisir une option",group:[{label:"checkbox 1",onChange:()=>{},checked:!0},{label:"checkbox 2",onChange:()=>{},checked:!1}]},s={args:u},l={args:{name:"group",legend:"Choisir une option"},render:n=>{const a=S({defaultValues:{checkbox1:!0,checkbox2:!1}});return r.jsx(D,{...a,children:r.jsx("form",{children:r.jsx(d,{...n,group:[{label:"checkbox 1",...a.register("checkbox1")},{label:"checkbox 2",...a.register("checkbox2")}]})})})}},t={args:{...u,variant:"detailed",disabled:!0}},i={args:{...u,variant:"detailed"}},c={args:{...u,variant:"detailed",inline:!0}};var h,g,b;s.parameters={...s.parameters,docs:{...(h=s.parameters)==null?void 0:h.docs,source:{originalSource:`{
  args: defaultArgs
}`,...(b=(g=s.parameters)==null?void 0:g.docs)==null?void 0:b.source}}};var x,f,k;l.parameters={...l.parameters,docs:{...(x=l.parameters)==null?void 0:x.docs,source:{originalSource:`{
  args: {
    name: 'group',
    legend: 'Choisir une option'
  },
  render: (args: any) => {
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
          ...hookForm.register('checkbox1')
        }, {
          label: 'checkbox 2',
          ...hookForm.register('checkbox2')
        }]}></CheckboxGroup>
        </form>
      </FormProvider>;
  }
}`,...(k=(f=l.parameters)==null?void 0:f.docs)==null?void 0:k.source}}};var _,v,y;t.parameters={...t.parameters,docs:{...(_=t.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    disabled: true
  }
}`,...(y=(v=t.parameters)==null?void 0:v.docs)==null?void 0:y.source}}};var C,F,j;i.parameters={...i.parameters,docs:{...(C=i.parameters)==null?void 0:C.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed'
  }
}`,...(j=(F=i.parameters)==null?void 0:F.docs)==null?void 0:j.source}}};var V,q,G;c.parameters={...c.parameters,docs:{...(V=c.parameters)==null?void 0:V.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    inline: true
  }
}`,...(G=(q=c.parameters)==null?void 0:q.docs)==null?void 0:G.source}}};const re=["Default","WithinForm","Disabled","WithBorder","Inline"];export{s as Default,t as Disabled,c as Inline,i as WithBorder,l as WithinForm,re as __namedExportsOrder,ee as default};
