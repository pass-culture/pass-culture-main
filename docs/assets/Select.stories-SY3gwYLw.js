import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-BI_y8cM8.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./classnames-MYlGWOUq.js";import{t as i}from"./SvgIcon-DK-x56iF.js";import{t as a}from"./FieldFooter-BrfF0GUx.js";import{t as o}from"./FieldHeader-TlOH1AoV.js";import{t as s}from"./full-down-BRWJ0t1l.js";import{a as c,o as l,t as u}from"./index.esm-0X4ru14B.js";var d=e(r(),1),f=e(t(),1),p={"select-input":`_select-input_1q7x4_2`,"has-value":`_has-value_1q7x4_61`,"has-error":`_has-error_1q7x4_69`,"select-input-icon":`_select-input-icon_1q7x4_73`,"select-input-wrapper":`_select-input-wrapper_1q7x4_92`,"select-input-placeholder":`_select-input-placeholder_1q7x4_95`},m=n(),h=(0,f.forwardRef)(({name:e,label:t,options:n,defaultOption:r=null,required:c=!1,disabled:l,error:u,requiredIndicator:h=`symbol`,className:g,ariaLabel:_,value:v,onChange:y,onBlur:b},x)=>{let S=(0,f.useId)(),C=(0,f.useId)();return(0,m.jsxs)(`div`,{className:g,children:[(0,m.jsx)(o,{label:t,fieldId:S,required:c,requiredIndicator:h}),(0,m.jsxs)(`div`,{className:p[`select-input-wrapper`],children:[(0,m.jsxs)(`select`,{ref:x,id:S,name:e,disabled:l,value:v,"aria-label":_,"aria-required":c,"aria-invalid":!!u,"aria-describedby":u?C:void 0,className:(0,d.default)(p[`select-input`],{[p[`has-error`]]:!!u,[p[`select-input-placeholder`]]:v===``,[p[`has-value`]]:!!v}),onBlur:b,onChange:y,children:[r&&(0,m.jsx)(`option`,{value:r.value,children:r.label}),n.map(e=>(0,m.jsx)(`option`,{value:e.value,children:e.label},e.value))]}),(0,m.jsx)(`div`,{className:p[`select-input-icon`],children:(0,m.jsx)(i,{src:s,alt:``})})]}),(0,m.jsx)(a,{error:u,errorId:C})]})});h.displayName=`Select`;try{h.displayName=`Select`,h.__docgenInfo={description:``,displayName:`Select`,props:{name:{defaultValue:null,description:`Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error`,name:`name`,required:!0,type:{name:`string`}},className:{defaultValue:null,description:``,name:`className`,required:!1,type:{name:`string`}},required:{defaultValue:{value:`false`},description:``,name:`required`,required:!1,type:{name:`boolean`}},disabled:{defaultValue:null,description:``,name:`disabled`,required:!1,type:{name:`boolean`}},label:{defaultValue:null,description:``,name:`label`,required:!0,type:{name:`string`}},onChange:{defaultValue:null,description:``,name:`onChange`,required:!1,type:{name:`ChangeEventHandler<HTMLSelectElement, HTMLInputElement>`}},onBlur:{defaultValue:null,description:``,name:`onBlur`,required:!1,type:{name:`FocusEventHandler<HTMLSelectElement>`}},defaultOption:{defaultValue:{value:`null`},description:`Option displayed if no option of the option list is selected`,name:`defaultOption`,required:!1,type:{name:`SelectOption<string | number> | null`}},options:{defaultValue:null,description:``,name:`options`,required:!0,type:{name:`SelectOption<string | number>[]`}},requiredIndicator:{defaultValue:{value:`symbol`},description:`What type of required indicator is displayed`,name:`requiredIndicator`,required:!1,type:{name:`enum`,value:[{value:`"symbol"`},{value:`"explicit"`},{value:`"hidden"`}]}},error:{defaultValue:null,description:``,name:`error`,required:!1,type:{name:`string`}},value:{defaultValue:null,description:``,name:`value`,required:!1,type:{name:`string`}},ariaLabel:{defaultValue:null,description:``,name:`ariaLabel`,required:!1,type:{name:`string`}}}}}catch{}var g=({children:e})=>(0,m.jsx)(u,{...c({defaultValues:{group:`option1`}}),children:(0,m.jsx)(`form`,{children:e})}),_={title:`@/ui-kit/forms/Select`,component:h},v={args:{label:`Select an option`,options:[{label:`option 1`,value:`option1`},{label:`option 2`,value:`option2`}],value:`option1`,onChange:()=>{}}},y={args:{label:`Select an option`,options:[{label:`option 1`,value:`option1`},{label:`option 2`,value:`option2`}]},decorators:[e=>(0,m.jsx)(g,{children:(0,m.jsx)(e,{})})],render:e=>{let{register:t}=l();return(0,m.jsx)(h,{...e,...t(`option`)})}};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
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
}`,...v.parameters?.docs?.source}}},y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
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
}`,...y.parameters?.docs?.source}}};var b=[`Default`,`WithinForm`];export{v as Default,y as WithinForm,b as __namedExportsOrder,_ as default};