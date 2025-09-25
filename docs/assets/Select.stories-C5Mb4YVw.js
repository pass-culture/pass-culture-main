import{j as e}from"./jsx-runtime-Cf8x2fCZ.js";import{u as j,a as N,F}from"./index.esm-D1X9ZzX-.js";import{c as _}from"./index-B0pXE9zJ.js";import{r as h}from"./index-QQMyt9Ur.js";import{f as I}from"./full-down-Cmbtr9nI.js";import{S as k}from"./SvgIcon-B5V96DYN.js";import{F as w}from"./FieldError-2mFOl_uD.js";import"./index-yBjzXJbu.js";import"./_commonjsHelpers-CqkleIqs.js";import"./stroke-error-DSZD431a.js";const r={"select-input":"_select-input_1u0zs_1","filter-variant":"_filter-variant_1u0zs_49","form-variant":"_form-variant_1u0zs_55","has-value":"_has-value_1u0zs_69","has-description":"_has-description_1u0zs_77","has-error":"_has-error_1u0zs_82","select-input-icon":"_select-input-icon_1u0zs_86","select-input-wrapper":"_select-input-wrapper_1u0zs_124","select-input-placeholder":"_select-input-placeholder_1u0zs_131"},v=h.forwardRef(({hasError:a=!1,hasDescription:n=!1,defaultOption:l=null,name:t,disabled:d,options:b,className:y,variant:o,...i},s)=>e.jsxs("div",{className:_(r["select-input-wrapper"],{[r["has-description"]]:n}),children:[e.jsxs("select",{"aria-invalid":a,...a?{"aria-describedby":`error-${t}`}:{},className:_(r["select-input"],y,{[r["has-error"]]:a,[r["has-description"]]:n,[r["select-input-placeholder"]]:i.value==="",[r["filter-variant"]]:o==="filter",[r["form-variant"]]:o==="form",[r["has-value"]]:!!i.value}),disabled:d,id:t,name:t,...i,ref:s,children:[l&&e.jsx("option",{value:l.value,children:l.label}),b.map(u=>e.jsx("option",{value:u.value,children:u.label},u.value))]}),e.jsx("div",{className:_(r["select-input-icon"],{[r["filter-variant"]]:o==="filter"}),children:e.jsx(k,{src:I,alt:""})})]}));v.displayName="SelectInput";try{v.displayName="SelectInput",v.__docgenInfo={description:"",displayName:"SelectInput",props:{options:{defaultValue:null,description:"",name:"options",required:!0,type:{name:"SelectOption<string | number>[]"}},name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"filter"'},{value:'"form"'}]}},hasError:{defaultValue:{value:"false"},description:"",name:"hasError",required:!1,type:{name:"boolean"}},defaultOption:{defaultValue:{value:"null"},description:"",name:"defaultOption",required:!1,type:{name:"SelectOption<string | number> | null"}},hasDescription:{defaultValue:{value:"false"},description:"",name:"hasDescription",required:!1,type:{name:"boolean"}}}}}catch{}const z="_label_1kw3x_1",E="_error_1kw3x_6",c={label:z,error:E},p=h.forwardRef(({name:a,defaultOption:n=null,options:l,className:t,required:d,disabled:b,label:y,onChange:o,onBlur:i,error:s,asterisk:u=!0,value:S,ariaLabel:q},V)=>{const g=h.useId(),x=h.useId();return e.jsxs("div",{className:_(c.select,t),children:[e.jsxs("div",{className:c["select-field"],children:[e.jsxs("label",{htmlFor:g,className:c.label,children:[y,d&&u?" *":""]}),e.jsx(v,{disabled:b,hasError:!!s,options:l,defaultOption:n,"aria-required":d,onBlur:i,onChange:o,name:a,value:S,"aria-describedby":x,ref:V,id:g,"aria-label":q})]}),e.jsx("div",{role:"alert",id:x,children:s&&e.jsx(w,{name:a,className:c.error,children:s})})]})});p.displayName="Select";try{p.displayName="Select",p.__docgenInfo={description:"",displayName:"Select",props:{name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLSelectElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLSelectElement>"}},defaultOption:{defaultValue:{value:"null"},description:"Option displayed if no option of the option list is selected",name:"defaultOption",required:!1,type:{name:"SelectOption<string | number> | null"}},options:{defaultValue:null,description:"",name:"options",required:!0,type:{name:"SelectOption<string | number>[]"}},asterisk:{defaultValue:{value:"true"},description:"Whether or not to display the asterisk in the label when the field is required",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},ariaLabel:{defaultValue:null,description:"",name:"ariaLabel",required:!1,type:{name:"string"}}}}}catch{}const C=({children:a})=>{const n=N({defaultValues:{group:"option1"}});return e.jsx(F,{...n,children:e.jsx("form",{children:a})})},P={title:"@/ui-kit/forms/Select",component:p},m={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}],value:"option1",onChange:()=>{}}},f={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}]},decorators:[a=>e.jsx(C,{children:e.jsx(a,{})})],render:a=>{const{register:n}=j();return e.jsx(p,{...a,...n("option")})}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
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
}`,...m.parameters?.docs?.source}}};f.parameters={...f.parameters,docs:{...f.parameters?.docs,source:{originalSource:`{
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
}`,...f.parameters?.docs?.source}}};const U=["Default","WithinForm"];export{m as Default,f as WithinForm,U as __namedExportsOrder,P as default};
