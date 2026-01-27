import{j as e}from"./jsx-runtime-C_uOM0Gm.js";import{a as j,u as F,F as V}from"./index.esm-B74CwnGv.js";import{c as y}from"./index-TscbDd2H.js";import{r as d}from"./iframe-CTnXOULQ.js";import{F as N}from"./FieldFooter-CL0tzobd.js";import{F as I}from"./FieldHeader-DxZ9joXq.js";import{f as C}from"./full-down-Cmbtr9nI.js";import{S as E}from"./SvgIcon-CJiY4LCz.js";import"./preload-helper-PPVm8Dsz.js";import"./full-error-BFAmjN4t.js";import"./index.module-DEHgy3-r.js";const a={"select-input":"_select-input_1y370_1","has-value":"_has-value_1y370_60","has-error":"_has-error_1y370_73","select-input-icon":"_select-input-icon_1y370_77","select-input-wrapper":"_select-input-wrapper_1y370_96","select-input-placeholder":"_select-input-placeholder_1y370_103"},l=d.forwardRef(({name:n,label:r,options:h,defaultOption:s=null,required:c=!1,disabled:v,error:t,requiredIndicator:g="symbol",className:b,ariaLabel:_,value:u,onChange:x,onBlur:S},q)=>{const m=d.useId(),f=d.useId();return e.jsxs("div",{className:y(a.select,b),children:[e.jsxs("div",{className:a["select-field"],children:[e.jsx(I,{label:r,fieldId:m,required:c,requiredIndicator:g}),e.jsxs("div",{className:a["select-input-wrapper"],children:[e.jsxs("select",{ref:q,id:m,name:n,disabled:v,value:u,"aria-label":_,"aria-required":c,"aria-invalid":!!t,"aria-describedby":t?f:void 0,className:y(a["select-input"],{[a["has-error"]]:!!t,[a["select-input-placeholder"]]:u==="",[a["has-value"]]:!!u}),onBlur:S,onChange:x,children:[s&&e.jsx("option",{value:s.value,children:s.label}),h.map(p=>e.jsx("option",{value:p.value,children:p.label},p.value))]}),e.jsx("div",{className:a["select-input-icon"],children:e.jsx(E,{src:C,alt:""})})]})]}),e.jsx(N,{error:t,errorId:f})]})});l.displayName="Select";try{l.displayName="Select",l.__docgenInfo={description:"",displayName:"Select",props:{name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},required:{defaultValue:{value:"false"},description:"",name:"required",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLSelectElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLSelectElement>"}},defaultOption:{defaultValue:{value:"null"},description:"Option displayed if no option of the option list is selected",name:"defaultOption",required:!1,type:{name:"SelectOption<string | number> | null"}},options:{defaultValue:null,description:"",name:"options",required:!0,type:{name:"SelectOption<string | number>[]"}},requiredIndicator:{defaultValue:{value:"symbol"},description:"What type of required indicator is displayed",name:"requiredIndicator",required:!1,type:{name:"enum",value:[{value:'"symbol"'},{value:'"hidden"'},{value:'"explicit"'}]}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},ariaLabel:{defaultValue:null,description:"",name:"ariaLabel",required:!1,type:{name:"string"}}}}}catch{}const W=({children:n})=>{const r=F({defaultValues:{group:"option1"}});return e.jsx(V,{...r,children:e.jsx("form",{children:n})})},U={title:"@/ui-kit/forms/Select",component:l},o={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}],value:"option1",onChange:()=>{}}},i={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}]},decorators:[n=>e.jsx(W,{children:e.jsx(n,{})})],render:n=>{const{register:r}=j();return e.jsx(l,{...n,...r("option")})}};o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
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
