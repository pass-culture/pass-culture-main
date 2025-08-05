import{j as r}from"./jsx-runtime-DF2Pcvd1.js";import{a as P,F as z}from"./index.esm-BBvhERNj.js";import{c as O}from"./index-DeARc5FM.js";import{r as R}from"./index-B2-qRKKC.js";import{C as H}from"./Checkbox-DPzdcoeb.js";import{F as L}from"./FieldError-B3RhE53I.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./Tag-ClYlfzfP.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-DfLnDDE5.js";import"./stroke-error-DSZD431a.js";const M="_inline_1ayxx_7",T="_legend_1ayxx_13",w="_error_1ayxx_17",o={"checkbox-group":"_checkbox-group_1ayxx_1",inline:M,legend:T,error:w},d=({group:n,legend:a,disabled:I,required:A,inline:S=!1,asterisk:D=!0,error:p,name:W,onChange:m})=>{const h=R.useId();return r.jsxs("fieldset",{"aria-describedby":h,children:[a&&r.jsxs("legend",{className:o.legend,children:[a,A&&D?" *":""]}),r.jsx("div",{className:O(o["checkbox-group"],{[o.inline]:S}),children:n.map(e=>r.jsx("div",{className:o["checkbox-group-item"],children:r.jsx(H,{asset:e.icon?{variant:"icon",src:e.icon}:void 0,hasError:!!p,label:e.label,disabled:I,onChange:g=>{var b;(b=e.onChange)==null||b.call(e,g),m==null||m(g)},onBlur:e.onBlur,variant:"detailed",checked:!!e.checked,collapsed:e.collapsed,indeterminate:e.indeterminate,name:W,ref:e.ref,sizing:e.sizing})},e.label))}),r.jsx("div",{role:"alert",id:h,children:p&&r.jsx(L,{className:o.error,children:p})})]})};try{d.displayName="CheckboxGroup",d.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{legend:{defaultValue:null,description:"",name:"legend",required:!0,type:{name:"ReactNode"}},group:{defaultValue:null,description:"",name:"group",required:!0,type:{name:"GroupOption[]"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},inline:{defaultValue:{value:"false"},description:"",name:"inline",required:!1,type:{name:"boolean"}},asterisk:{defaultValue:{value:"true"},description:"",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!1,type:{name:"string"}},onChange:{defaultValue:null,description:"Callback function to handle changes in the radio group.",name:"onChange",required:!1,type:{name:"((e: ChangeEvent<HTMLInputElement>) => void)"}}}}}catch{}const oe={title:"ui-kit/formsV2/CheckboxGroup",component:d},u={name:"group",legend:"Choisir une option",group:[{label:"checkbox 1",onChange:()=>{},checked:!0},{label:"checkbox 2",onChange:()=>{},checked:!1}]},s={args:u},l={args:{name:"group",legend:"Choisir une option"},render:n=>{const a=P({defaultValues:{checkbox1:!0,checkbox2:!1}});return r.jsx(z,{...a,children:r.jsx("form",{children:r.jsx(d,{...n,group:[{label:"checkbox 1",...a.register("checkbox1")},{label:"checkbox 2",...a.register("checkbox2")}]})})})}},t={args:{...u,variant:"detailed",disabled:!0}},i={args:{...u,variant:"detailed"}},c={args:{...u,variant:"detailed",inline:!0}};var x,f,k;s.parameters={...s.parameters,docs:{...(x=s.parameters)==null?void 0:x.docs,source:{originalSource:`{
  args: defaultArgs
}`,...(k=(f=s.parameters)==null?void 0:f.docs)==null?void 0:k.source}}};var v,_,y;l.parameters={...l.parameters,docs:{...(v=l.parameters)==null?void 0:v.docs,source:{originalSource:`{
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
}`,...(y=(_=l.parameters)==null?void 0:_.docs)==null?void 0:y.source}}};var C,F,V;t.parameters={...t.parameters,docs:{...(C=t.parameters)==null?void 0:C.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    disabled: true
  }
}`,...(V=(F=t.parameters)==null?void 0:F.docs)==null?void 0:V.source}}};var j,q,G;i.parameters={...i.parameters,docs:{...(j=i.parameters)==null?void 0:j.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed'
  }
}`,...(G=(q=i.parameters)==null?void 0:q.docs)==null?void 0:G.source}}};var E,N,B;c.parameters={...c.parameters,docs:{...(E=c.parameters)==null?void 0:E.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    inline: true
  }
}`,...(B=(N=c.parameters)==null?void 0:N.docs)==null?void 0:B.source}}};const ne=["Default","WithinForm","Disabled","WithBorder","Inline"];export{s as Default,t as Disabled,c as Inline,i as WithBorder,l as WithinForm,ne as __namedExportsOrder,oe as default};
