import{j as e}from"./jsx-runtime-BYYWji4R.js";import{u as k,a as E,F as C}from"./index.esm-ClDB96id.js";import{c as I}from"./index-DeARc5FM.js";import{r as s}from"./index-ClcD9ViR.js";import{S as O}from"./SelectInput-DrStvRQI.js";import{F as W}from"./FieldError-ky1_Lcaw.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./full-down-Cmbtr9nI.js";import"./SvgIcon-CyWUmZpn.js";import"./stroke-error-DSZD431a.js";const w="_label_1kw3x_1",H="_error_1kw3x_6",o={label:w,error:H},a=s.forwardRef(({name:n,defaultOption:r=null,options:y,className:x,required:u,disabled:v,label:S,onChange:q,onBlur:_,error:i,asterisk:V=!0,value:j,ariaLabel:F},N)=>{const p=s.useId(),d=s.useId();return e.jsxs("div",{className:I(o.select,x),children:[e.jsxs("div",{className:o["select-field"],children:[e.jsxs("label",{htmlFor:p,className:o.label,children:[S,u&&V?" *":""]}),e.jsx(O,{disabled:v,hasError:!!i,options:y,defaultOption:r,"aria-required":u,onBlur:_,onChange:q,name:n,value:j,"aria-describedby":d,ref:N,id:p,"aria-label":F})]}),e.jsx("div",{role:"alert",id:d,children:i&&e.jsx(W,{name:n,className:o.error,children:i})})]})});a.displayName="Select";try{a.displayName="Select",a.__docgenInfo={description:"",displayName:"Select",props:{name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLSelectElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLSelectElement>"}},defaultOption:{defaultValue:{value:"null"},description:"Option displayed if no option of the option list is selected",name:"defaultOption",required:!1,type:{name:"SelectOption | null"}},options:{defaultValue:null,description:"",name:"options",required:!0,type:{name:"SelectOption[]"}},asterisk:{defaultValue:{value:"true"},description:"Whether or not to display the asterisk in the label when the field is required",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},ariaLabel:{defaultValue:null,description:"",name:"ariaLabel",required:!1,type:{name:"string"}}}}}catch{}const L=({children:n})=>{const r=E({defaultValues:{group:"option1"}});return e.jsx(C,{...r,children:e.jsx("form",{children:n})})},J={title:"ui-kit/formsV2/Select",component:a},t={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}],value:"option1",onChange:()=>{}}},l={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}]},decorators:[n=>e.jsx(L,{children:e.jsx(n,{})})],render:n=>{const{register:r}=k();return e.jsx(a,{...n,...r("option")})}};var c,m,f;t.parameters={...t.parameters,docs:{...(c=t.parameters)==null?void 0:c.docs,source:{originalSource:`{
  args: {
    label: 'Select an option',
    options: [{
      label: 'option 1',
      value: 'option1'
    }, {
      label: 'option 2',
      value: 'option2'
    }],
    value: 'option1',
    onChange: () => {
      //    Control changes
    }
  }
}`,...(f=(m=t.parameters)==null?void 0:m.docs)==null?void 0:f.source}}};var b,h,g;l.parameters={...l.parameters,docs:{...(b=l.parameters)==null?void 0:b.docs,source:{originalSource:`{
  args: {
    label: 'Select an option',
    options: [{
      label: 'option 1',
      value: 'option1'
    }, {
      label: 'option 2',
      value: 'option2'
    }]
  },
  decorators: [(Story: any) => <Wrapper>
        <Story />
      </Wrapper>],
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const {
      register
    } = useFormContext<{
      option: string;
    }>();
    return <Select {...args} {...register('option')} />;
  }
}`,...(g=(h=l.parameters)==null?void 0:h.docs)==null?void 0:g.source}}};const K=["Default","WithinForm"];export{t as Default,l as WithinForm,K as __namedExportsOrder,J as default};
