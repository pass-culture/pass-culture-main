import{i as e}from"./chunk-DseTPa7n.js";import{t}from"./react-DCnNfEIY.js";import{t as n}from"./jsx-runtime-BUC2lftT.js";import{t as r}from"./classnames-BHgbbynn.js";import{t as i}from"./Tooltip-BT9GAY5L.js";import{a,o,t as s}from"./index.esm-DCH0oH1a.js";var c=e(t(),1),l=e(r(),1),u={checkbox:`_checkbox_10b16_1`,disabled:`_disabled_10b16_9`,"checkbox-input":`_checkbox-input_10b16_9`,error:`_error_10b16_12`,"checkbox-label":`_checkbox-label_10b16_22`,"visually-hidden":`_visually-hidden_10b16_64`},d=n(),f=(0,c.forwardRef)(({name:e,className:t,label:n,hasError:r,onChange:a,onBlur:o,checked:s,disabled:f,tooltipContent:p},m)=>{let h=(0,c.useId)();return(0,d.jsxs)(`div`,{className:(0,l.default)(u.checkbox,{[u.disabled]:f,[u.error]:!!r},t),children:[(0,d.jsxs)(`label`,{className:u[`checkbox-label`],htmlFor:h,children:[(0,d.jsx)(`span`,{"aria-hidden":`true`,children:n}),(0,d.jsx)(`span`,{className:u[`visually-hidden`],children:p})]}),(0,d.jsx)(i,{content:p,children:(0,d.jsx)(`input`,{type:`checkbox`,className:u[`checkbox-input`],"aria-labelledby":`${e}-label`,"aria-invalid":r,name:e,ref:m,onChange:a,onBlur:o,checked:s,disabled:f,id:h})})]})});f.displayName=`DayCheckbox`;try{f.displayName=`DayCheckbox`,f.__docgenInfo={description:``,displayName:`DayCheckbox`,props:{name:{defaultValue:null,description:`Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error`,name:`name`,required:!0,type:{name:`string`}},className:{defaultValue:null,description:``,name:`className`,required:!1,type:{name:`string`}},hasError:{defaultValue:null,description:`Error text for the checkbox`,name:`hasError`,required:!1,type:{name:`boolean`}},displayErrorMessage:{defaultValue:null,description:`Whether or not to display the error message. If false, the field has the error styles but no message`,name:`displayErrorMessage`,required:!1,type:{name:`boolean`}},onChange:{defaultValue:null,description:``,name:`onChange`,required:!1,type:{name:`ChangeEventHandler<HTMLInputElement, HTMLInputElement>`}},onBlur:{defaultValue:null,description:``,name:`onBlur`,required:!1,type:{name:`FocusEventHandler<HTMLInputElement>`}},label:{defaultValue:null,description:``,name:`label`,required:!0,type:{name:`ReactNode`}},checked:{defaultValue:null,description:``,name:`checked`,required:!1,type:{name:`boolean`}},disabled:{defaultValue:null,description:``,name:`disabled`,required:!1,type:{name:`boolean`}},tooltipContent:{defaultValue:null,description:``,name:`tooltipContent`,required:!0,type:{name:`ReactNode`}}}}}catch{}var p={title:`@/ui-kit/forms/DayCheckbox`,component:f},m=({children:e})=>(0,d.jsx)(s,{...a({defaultValues:{myField:!0}}),children:(0,d.jsx)(`form`,{children:e})}),h={args:{label:`L`,tooltipContent:`Lundi`,name:`myField`,checked:!0,onChange:()=>{}}},g={args:{label:`L`,tooltipContent:`Lundi`,name:`myField`,checked:!1,disabled:!0,onChange:()=>{}}},_={args:{label:`L`,tooltipContent:`Lundi`,name:`myField`,checked:!1,hasError:!0,displayErrorMessage:!1,onChange:()=>{}}},v={args:{label:`L`,tooltipContent:`Lundi`},decorators:[e=>(0,d.jsx)(m,{children:(0,d.jsx)(e,{})})],render:e=>{let{register:t}=o();return(0,d.jsx)(f,{...e,...t(`myField`)})}};h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: true,
    onChange: () => {
      //  Control the result here with e.target.checked
    }
  }
}`,...h.parameters?.docs?.source}}},g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: false,
    disabled: true,
    onChange: () => {
      //  Control the result here with e.target.checked
    }
  }
}`,...g.parameters?.docs?.source}}},_.parameters={..._.parameters,docs:{..._.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: false,
    hasError: true,
    displayErrorMessage: false,
    onChange: () => {
      //  Control the result here with e.target.checked
    }
  }
}`,..._.parameters?.docs?.source}}},v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'L',
    tooltipContent: 'Lundi'
  },
  decorators: [Story => <Wrapper>
        <Story />
      </Wrapper>],
  render: args => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const {
      register
    } = useFormContext<{
      myField: boolean;
    }>();
    return <DayCheckbox {...args} {...register('myField')} />;
  }
}`,...v.parameters?.docs?.source}}};var y=[`Default`,`Disabled`,`WithinAGroupInError`,`WithinForm`];export{h as Default,g as Disabled,_ as WithinAGroupInError,v as WithinForm,y as __namedExportsOrder,p as default};