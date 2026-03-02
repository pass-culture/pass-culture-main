import{j as e}from"./jsx-runtime-u17CrQMm.js";import{a as j,u as F,F as V}from"./index.esm-CZnaqMrI.js";import{c as g}from"./index-BiHGfcXp.js";import{r as d}from"./iframe-C-BmCXuN.js";import{F as N}from"./FieldFooter-bEO4MnCi.js";import{F as I}from"./FieldHeader-Dvnity9I.js";import{f as C}from"./full-down-Cmbtr9nI.js";import{S as E}from"./SvgIcon-DuZPzNRk.js";import"./preload-helper-PPVm8Dsz.js";import"./full-error-BFAmjN4t.js";import"./index.module-BZPftzAv.js";const a={"select-input":"_select-input_6g3ap_2","has-value":"_has-value_6g3ap_61","has-error":"_has-error_6g3ap_74","select-input-icon":"_select-input-icon_6g3ap_78","select-input-wrapper":"_select-input-wrapper_6g3ap_97","select-input-placeholder":"_select-input-placeholder_6g3ap_104"},t=d.forwardRef(({name:n,label:r,options:h,defaultOption:s=null,required:c=!1,disabled:v,error:l,requiredIndicator:b="symbol",className:y,ariaLabel:_,value:p,onChange:x,onBlur:S},q)=>{const m=d.useId(),f=d.useId();return e.jsxs("div",{className:g(a.select,y),children:[e.jsxs("div",{className:a["select-field"],children:[e.jsx(I,{label:r,fieldId:m,required:c,requiredIndicator:b}),e.jsxs("div",{className:a["select-input-wrapper"],children:[e.jsxs("select",{ref:q,id:m,name:n,disabled:v,value:p,"aria-label":_,"aria-required":c,"aria-invalid":!!l,"aria-describedby":l?f:void 0,className:g(a["select-input"],{[a["has-error"]]:!!l,[a["select-input-placeholder"]]:p==="",[a["has-value"]]:!!p}),onBlur:S,onChange:x,children:[s&&e.jsx("option",{value:s.value,children:s.label}),h.map(u=>e.jsx("option",{value:u.value,children:u.label},u.value))]}),e.jsx("div",{className:a["select-input-icon"],children:e.jsx(E,{src:C,alt:""})})]})]}),e.jsx(N,{error:l,errorId:f})]})});t.displayName="Select";try{t.displayName="Select",t.__docgenInfo={description:"",displayName:"Select",props:{name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},required:{defaultValue:{value:"false"},description:"",name:"required",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLSelectElement, HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLSelectElement>"}},defaultOption:{defaultValue:{value:"null"},description:"Option displayed if no option of the option list is selected",name:"defaultOption",required:!1,type:{name:"SelectOption<string | number> | null"}},options:{defaultValue:null,description:"",name:"options",required:!0,type:{name:"SelectOption<string | number>[]"}},requiredIndicator:{defaultValue:{value:"symbol"},description:"What type of required indicator is displayed",name:"requiredIndicator",required:!1,type:{name:"enum",value:[{value:'"symbol"'},{value:'"hidden"'},{value:'"explicit"'}]}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},ariaLabel:{defaultValue:null,description:"",name:"ariaLabel",required:!1,type:{name:"string"}}}}}catch{}const H=({children:n})=>{const r=F({defaultValues:{group:"option1"}});return e.jsx(V,{...r,children:e.jsx("form",{children:n})})},U={title:"@/ui-kit/forms/Select",component:t},o={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}],value:"option1",onChange:()=>{}}},i={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}]},decorators:[n=>e.jsx(H,{children:e.jsx(n,{})})],render:n=>{const{register:r}=j();return e.jsx(t,{...n,...r("option")})}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
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
}`,...o.parameters?.docs?.source}}};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
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
}`,...i.parameters?.docs?.source}}};const z=["Default","WithinForm"];export{o as Default,i as WithinForm,z as __namedExportsOrder,U as default};
