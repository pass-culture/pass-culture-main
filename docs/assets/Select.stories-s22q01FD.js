import{j as e}from"./jsx-runtime-BUYBQRMB.js";import{a as j,u as F,F as N}from"./index.esm-CtTQ8M53.js";import{c as f}from"./index-DOgqEbsk.js";import{r as v}from"./iframe-BmP2TQXG.js";import{F as I}from"./FieldFooter-CFoNjvBF.js";import{F as C}from"./FieldHeader-y8wn0Jf-.js";import{f as E}from"./full-down-Cmbtr9nI.js";import{S as O}from"./SvgIcon-B5MJ00Mq.js";import"./preload-helper-PPVm8Dsz.js";import"./full-error-BFAmjN4t.js";import"./index.module-CEkOFNPs.js";const n={"select-input":"_select-input_126qm_1","filter-variant":"_filter-variant_126qm_49","form-variant":"_form-variant_126qm_55","has-value":"_has-value_126qm_69","has-description":"_has-description_126qm_77","has-error":"_has-error_126qm_82","select-input-icon":"_select-input-icon_126qm_86","select-input-wrapper":"_select-input-wrapper_126qm_124","select-input-placeholder":"_select-input-placeholder_126qm_131"},h=v.forwardRef(({hasError:a=!1,hasDescription:r=!1,defaultOption:t=null,name:l,disabled:d,options:_,className:y,variant:o,...i},s)=>e.jsxs("div",{className:f(n["select-input-wrapper"],{[n["has-description"]]:r}),children:[e.jsxs("select",{"aria-invalid":a,...a?{"aria-describedby":`error-${l}`}:{},className:f(n["select-input"],y,{[n["has-error"]]:a,[n["has-description"]]:r,[n["select-input-placeholder"]]:i.value==="",[n["filter-variant"]]:o==="filter",[n["form-variant"]]:o==="form",[n["has-value"]]:!!i.value}),disabled:d,id:l,name:l,...i,ref:s,children:[t&&e.jsx("option",{value:t.value,children:t.label}),_.map(u=>e.jsx("option",{value:u.value,children:u.label},u.value))]}),e.jsx("div",{className:f(n["select-input-icon"],{[n["filter-variant"]]:o==="filter"}),children:e.jsx(O,{src:E,alt:""})})]}));h.displayName="SelectInput";try{h.displayName="SelectInput",h.__docgenInfo={description:"",displayName:"SelectInput",props:{name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"filter"'},{value:'"form"'}]}},options:{defaultValue:null,description:"",name:"options",required:!0,type:{name:"SelectOption<string | number>[]"}},hasError:{defaultValue:{value:"false"},description:"",name:"hasError",required:!1,type:{name:"boolean"}},defaultOption:{defaultValue:{value:"null"},description:"",name:"defaultOption",required:!1,type:{name:"SelectOption<string | number> | null"}},hasDescription:{defaultValue:{value:"false"},description:"",name:"hasDescription",required:!1,type:{name:"boolean"}}}}}catch{}const q={},p=v.forwardRef(({name:a,defaultOption:r=null,options:t,className:l,required:d=!1,disabled:_,label:y,onChange:o,onBlur:i,error:s,asterisk:u=!0,value:S,ariaLabel:x},V)=>{const g=v.useId(),b=v.useId();return e.jsxs("div",{className:f(q.select,l),children:[e.jsxs("div",{className:q["select-field"],children:[e.jsx(C,{label:y,fieldId:g,required:d,asterisk:u}),e.jsx(h,{disabled:_,hasError:!!s,options:t,defaultOption:r,"aria-required":d,onBlur:i,onChange:o,name:a,value:S,"aria-describedby":s?b:void 0,ref:V,id:g,"aria-label":x})]}),e.jsx(I,{error:s,errorId:b})]})});p.displayName="Select";try{p.displayName="Select",p.__docgenInfo={description:"",displayName:"Select",props:{name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},required:{defaultValue:{value:"false"},description:"",name:"required",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLSelectElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLSelectElement>"}},defaultOption:{defaultValue:{value:"null"},description:"Option displayed if no option of the option list is selected",name:"defaultOption",required:!1,type:{name:"SelectOption<string | number> | null"}},options:{defaultValue:null,description:"",name:"options",required:!0,type:{name:"SelectOption<string | number>[]"}},asterisk:{defaultValue:{value:"true"},description:"Whether or not to display the asterisk in the label when the field is required",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},ariaLabel:{defaultValue:null,description:"",name:"ariaLabel",required:!1,type:{name:"string"}}}}}catch{}const k=({children:a})=>{const r=F({defaultValues:{group:"option1"}});return e.jsx(N,{...r,children:e.jsx("form",{children:a})})},U={title:"@/ui-kit/forms/Select",component:p},c={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}],value:"option1",onChange:()=>{}}},m={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}]},decorators:[a=>e.jsx(k,{children:e.jsx(a,{})})],render:a=>{const{register:r}=j();return e.jsx(p,{...a,...r("option")})}};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
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
}`,...c.parameters?.docs?.source}}};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`{
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
}`,...m.parameters?.docs?.source}}};const z=["Default","WithinForm"];export{c as Default,m as WithinForm,z as __namedExportsOrder,U as default};
