import{j as e}from"./jsx-runtime-BYYWji4R.js";import{a as D,F as W}from"./index.esm-Z2NZos4s.js";import{C as p}from"./BaseCheckbox-BwQ6YW84.js";import{c as P}from"./index-DeARc5FM.js";import{r as R}from"./index-ClcD9ViR.js";import{F as $}from"./FieldError-azuIsM2E.js";import{C as M}from"./Checkbox-xcsJjzdZ.js";import"./SvgIcon-CyWUmZpn.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./stroke-error-DSZD431a.js";const w="_inline_1ayxx_7",z="_legend_1ayxx_13",H="_error_1ayxx_17",o={"checkbox-group":"_checkbox-group_1ayxx_1",inline:w,legend:z,error:H},d=({group:n,name:a,legend:h,describedBy:N,disabled:X,required:A,variant:E,inline:I=!1,asterisk:S=!0,error:m})=>{const b=R.useId();return e.jsxs("fieldset",{"aria-describedby":`${N||""} ${b}`,children:[h&&e.jsxs("legend",{className:o.legend,children:[h,A&&S?" *":""]}),e.jsx("div",{className:P(o["checkbox-group"],{[o.inline]:I}),children:n.map(r=>e.jsx("div",{className:o["checkbox-group-item"],children:e.jsx(M,{icon:r.icon,error:m,displayErrorMessage:!1,label:r.label,name:r.name,disabled:X,onChange:r.onChange,onBlur:r.onBlur,variant:E,checked:r.checked,childrenOnChecked:r.childrenOnChecked})},r.name))}),e.jsx("div",{role:"alert",id:b,children:m&&e.jsx($,{name:a,className:o.error,children:m})})]})};try{d.displayName="CheckboxGroup",d.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"box"'}]}},group:{defaultValue:null,description:"",name:"group",required:!0,type:{name:"GroupOption[]"}},inline:{defaultValue:{value:"false"},description:"",name:"inline",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},asterisk:{defaultValue:{value:"true"},description:"",name:"asterisk",required:!1,type:{name:"boolean"}},legend:{defaultValue:null,description:"",name:"legend",required:!1,type:{name:"ReactNode"}},describedBy:{defaultValue:null,description:"",name:"describedBy",required:!1,type:{name:"string"}}}}}catch{}const ae={title:"ui-kit/formsV2/CheckboxGroup",component:d},u={name:"group",legend:"Choisir une option",group:[{name:"checkbox1",label:"checkbox 1",onChange:()=>{},checked:!0},{name:"checkbox2",label:"checkbox 2",onChange:()=>{},checked:!1}]},s={args:u},c={args:{name:"group",legend:"Choisir une option"},render:n=>{const a=D({defaultValues:{checkbox1:!0,checkbox2:!1}});return e.jsx(W,{...a,children:e.jsx("form",{children:e.jsx(d,{...n,group:[{label:"checkbox 1",...a.register("checkbox1")},{label:"checkbox 2",...a.register("checkbox2")}]})})})}},l={args:{...u,variant:p.BOX,disabled:!0}},t={args:{...u,variant:p.BOX}},i={args:{...u,variant:p.BOX,inline:!0}};var x,g,k;s.parameters={...s.parameters,docs:{...(x=s.parameters)==null?void 0:x.docs,source:{originalSource:`{
  args: defaultArgs
}`,...(k=(g=s.parameters)==null?void 0:g.docs)==null?void 0:k.source}}};var f,y,C;c.parameters={...c.parameters,docs:{...(f=c.parameters)==null?void 0:f.docs,source:{originalSource:`{
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
}`,...(C=(y=c.parameters)==null?void 0:y.docs)==null?void 0:C.source}}};var _,v,V;l.parameters={...l.parameters,docs:{...(_=l.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: CheckboxVariant.BOX,
    disabled: true
  }
}`,...(V=(v=l.parameters)==null?void 0:v.docs)==null?void 0:V.source}}};var F,j,q;t.parameters={...t.parameters,docs:{...(F=t.parameters)==null?void 0:F.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: CheckboxVariant.BOX
  }
}`,...(q=(j=t.parameters)==null?void 0:j.docs)==null?void 0:q.source}}};var B,O,G;i.parameters={...i.parameters,docs:{...(B=i.parameters)==null?void 0:B.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: CheckboxVariant.BOX,
    inline: true
  }
}`,...(G=(O=i.parameters)==null?void 0:O.docs)==null?void 0:G.source}}};const oe=["Default","WithinForm","Disabled","WithBorder","Inline"];export{s as Default,l as Disabled,i as Inline,t as WithBorder,c as WithinForm,oe as __namedExportsOrder,ae as default};
