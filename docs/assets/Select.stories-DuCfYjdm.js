import{j as e}from"./jsx-runtime-BYYWji4R.js";import{u as N,a as k,F as E}from"./index.esm-Z2NZos4s.js";import{c as C}from"./index-DeARc5FM.js";import{r as s}from"./index-ClcD9ViR.js";import{S as I}from"./SelectInput-COYTHOTa.js";import{F as O}from"./FieldError-azuIsM2E.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./full-down-Cmbtr9nI.js";import"./SvgIcon-CyWUmZpn.js";import"./stroke-error-DSZD431a.js";const W="_label_1kw3x_1",w="_error_1kw3x_6",t={label:W,error:w},o=s.forwardRef(({name:n,defaultOption:r=null,options:y,className:x,required:p,disabled:v,label:S,onChange:_,onBlur:q,error:i,asterisk:V=!0,value:j},F)=>{const u=s.useId(),d=s.useId();return e.jsxs("div",{className:C(t.select,x),children:[e.jsxs("div",{className:t["select-field"],children:[e.jsxs("label",{htmlFor:u,className:t.label,children:[S,p&&V?" *":""]}),e.jsx(I,{disabled:v,hasError:!!i,options:y,defaultOption:r,"aria-required":p,onBlur:q,onChange:_,name:n,value:j,"aria-describedby":d,ref:F,id:u})]}),e.jsx("div",{role:"alert",id:d,children:i&&e.jsx(O,{name:n,className:t.error,children:i})})]})});o.displayName="Select";try{o.displayName="Select",o.__docgenInfo={description:"",displayName:"Select",props:{name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLSelectElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLSelectElement>"}},defaultOption:{defaultValue:{value:"null"},description:"Option displayed if no option of the option list is selected",name:"defaultOption",required:!1,type:{name:"SelectOption | null"}},options:{defaultValue:null,description:"",name:"options",required:!0,type:{name:"SelectOption[]"}},asterisk:{defaultValue:{value:"true"},description:"Whether or not to display the asterisk in the label when the field is required",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}}}}}catch{}const H=({children:n})=>{const r=k({defaultValues:{group:"option1"}});return e.jsx(E,{...r,children:e.jsx("form",{children:n})})},G={title:"ui-kit/formsV2/Select",component:o},a={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}],value:"option1",onChange:()=>{}}},l={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}]},decorators:[n=>e.jsx(H,{children:e.jsx(n,{})})],render:n=>{const{register:r}=N();return e.jsx(o,{...n,...r("option")})}};var c,m,f;a.parameters={...a.parameters,docs:{...(c=a.parameters)==null?void 0:c.docs,source:{originalSource:`{
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
}`,...(f=(m=a.parameters)==null?void 0:m.docs)==null?void 0:f.source}}};var h,b,g;l.parameters={...l.parameters,docs:{...(h=l.parameters)==null?void 0:h.docs,source:{originalSource:`{
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
}`,...(g=(b=l.parameters)==null?void 0:b.docs)==null?void 0:g.source}}};const J=["Default","WithinForm"];export{a as Default,l as WithinForm,J as __namedExportsOrder,G as default};
