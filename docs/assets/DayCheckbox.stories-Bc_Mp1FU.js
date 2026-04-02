import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-BQ2D5nxH.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./classnames-MYlGWOUq.js";import{t as i}from"./Tooltip-Cg7qlRsB.js";import{a,o,t as s}from"./index.esm-C_aINoPJ.js";var c=e(t(),1),l=e(r(),1),u=`_checkbox_10b16_1`,d=`_disabled_10b16_9`,f=`_error_10b16_12`,p={checkbox:u,disabled:d,"checkbox-input":`_checkbox-input_10b16_9`,error:f,"checkbox-label":`_checkbox-label_10b16_22`,"visually-hidden":`_visually-hidden_10b16_64`},m=n(),h=(0,c.forwardRef)(({name:e,className:t,label:n,hasError:r,onChange:a,onBlur:o,checked:s,disabled:u,tooltipContent:d},f)=>{let h=(0,c.useId)();return(0,m.jsxs)(`div`,{className:(0,l.default)(p.checkbox,{[p.disabled]:u,[p.error]:!!r},t),children:[(0,m.jsxs)(`label`,{className:p[`checkbox-label`],htmlFor:h,children:[(0,m.jsx)(`span`,{"aria-hidden":`true`,children:n}),(0,m.jsx)(`span`,{className:p[`visually-hidden`],children:d})]}),(0,m.jsx)(i,{content:d,children:(0,m.jsx)(`input`,{type:`checkbox`,className:p[`checkbox-input`],"aria-labelledby":`${e}-label`,"aria-invalid":r,name:e,ref:f,onChange:a,onBlur:o,checked:s,disabled:u,id:h})})]})});h.displayName=`DayCheckbox`;try{h.displayName=`DayCheckbox`,h.__docgenInfo={description:``,displayName:`DayCheckbox`,props:{name:{defaultValue:null,description:`Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error`,name:`name`,required:!0,type:{name:`string`}},className:{defaultValue:null,description:``,name:`className`,required:!1,type:{name:`string`}},hasError:{defaultValue:null,description:`Error text for the checkbox`,name:`hasError`,required:!1,type:{name:`boolean`}},displayErrorMessage:{defaultValue:null,description:`Whether or not to display the error message. If false, the field has the error styles but no message`,name:`displayErrorMessage`,required:!1,type:{name:`boolean`}},onChange:{defaultValue:null,description:``,name:`onChange`,required:!1,type:{name:`ChangeEventHandler<HTMLInputElement, HTMLInputElement>`}},onBlur:{defaultValue:null,description:``,name:`onBlur`,required:!1,type:{name:`FocusEventHandler<HTMLInputElement>`}},label:{defaultValue:null,description:``,name:`label`,required:!0,type:{name:`ReactNode`}},checked:{defaultValue:null,description:``,name:`checked`,required:!1,type:{name:`boolean`}},disabled:{defaultValue:null,description:``,name:`disabled`,required:!1,type:{name:`boolean`}},tooltipContent:{defaultValue:null,description:``,name:`tooltipContent`,required:!0,type:{name:`ReactNode`}}}}}catch{}var g={title:`@/ui-kit/forms/DayCheckbox`,component:h},_=({children:e})=>(0,m.jsx)(s,{...a({defaultValues:{myField:!0}}),children:(0,m.jsx)(`form`,{children:e})}),v={args:{label:`L`,tooltipContent:`Lundi`,name:`myField`,checked:!0,onChange:()=>{}}},y={args:{label:`L`,tooltipContent:`Lundi`,name:`myField`,checked:!1,disabled:!0,onChange:()=>{}}},b={args:{label:`L`,tooltipContent:`Lundi`,name:`myField`,checked:!1,hasError:!0,displayErrorMessage:!1,onChange:()=>{}}},x={args:{label:`L`,tooltipContent:`Lundi`},decorators:[e=>(0,m.jsx)(_,{children:(0,m.jsx)(e,{})})],render:e=>{let{register:t}=o();return(0,m.jsx)(h,{...e,...t(`myField`)})}};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: true,
    onChange: () => {
      //  Control the result here with e.target.checked
    }
  }
}`,...v.parameters?.docs?.source}}},y.parameters={...y.parameters,docs:{...y.parameters?.docs,source:{originalSource:`{
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
}`,...y.parameters?.docs?.source}}},b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
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
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
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
}`,...x.parameters?.docs?.source}}};var S=[`Default`,`Disabled`,`WithinAGroupInError`,`WithinForm`];export{v as Default,y as Disabled,b as WithinAGroupInError,x as WithinForm,S as __namedExportsOrder,g as default};