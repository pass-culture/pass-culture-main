import{i as e,s as t}from"./preload-helper-xPQekRTU.js";import{C as n}from"./iframe-CZ6K2i-D.js";import{t as r}from"./jsx-runtime-CaZkqeYb.js";import{t as i}from"./classnames-Dm_LJ4P4.js";import{n as a,t as o}from"./Tooltip-CSNV7CEb.js";import{i as s,o as c,s as l,t as u}from"./index.esm-BJtvp_MY.js";var d,f,p,m,h=e((()=>{d=`_checkbox_10b16_1`,f=`_disabled_10b16_9`,p=`_error_10b16_12`,m={checkbox:d,disabled:f,"checkbox-input":`_checkbox-input_10b16_9`,error:p,"checkbox-label":`_checkbox-label_10b16_22`,"visually-hidden":`_visually-hidden_10b16_64`}})),g,_,v,y,b=e((()=>{g=t(i(),1),_=t(n(),1),a(),h(),v=r(),y=(0,_.forwardRef)(({name:e,className:t,label:n,hasError:r,onChange:i,onBlur:a,checked:s,disabled:c,tooltipContent:l},u)=>{let d=(0,_.useId)();return(0,v.jsxs)(`div`,{className:(0,g.default)(m.checkbox,{[m.disabled]:c,[m.error]:!!r},t),children:[(0,v.jsxs)(`label`,{className:m[`checkbox-label`],htmlFor:d,children:[(0,v.jsx)(`span`,{"aria-hidden":`true`,children:n}),(0,v.jsx)(`span`,{className:m[`visually-hidden`],children:l})]}),(0,v.jsx)(o,{content:l,children:(0,v.jsx)(`input`,{type:`checkbox`,className:m[`checkbox-input`],"aria-labelledby":`${e}-label`,"aria-invalid":r,name:e,ref:u,onChange:i,onBlur:a,checked:s,disabled:c,id:d})})]})}),y.displayName=`DayCheckbox`;try{y.displayName=`DayCheckbox`,y.__docgenInfo={description:``,displayName:`DayCheckbox`,filePath:`/home/runner/work/pass-culture-main/pass-culture-main/pro/src/ui-kit/form/DayCheckbox/DayCheckbox.tsx`,methods:[],props:{name:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/DayCheckbox/DayCheckbox.tsx`,name:`TypeLiteral`}],description:`Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error`,name:`name`,required:!0,tags:{},type:{name:`string`}},className:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/DayCheckbox/DayCheckbox.tsx`,name:`TypeLiteral`}],description:``,name:`className`,required:!1,tags:{},type:{name:`string`}},hasError:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/DayCheckbox/DayCheckbox.tsx`,name:`TypeLiteral`}],description:`Error text for the checkbox`,name:`hasError`,required:!1,tags:{},type:{name:`boolean`}},displayErrorMessage:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/DayCheckbox/DayCheckbox.tsx`,name:`TypeLiteral`}],description:`Whether or not to display the error message. If false, the field has the error styles but no message`,name:`displayErrorMessage`,required:!1,tags:{},type:{name:`boolean`}},onChange:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/DayCheckbox/DayCheckbox.tsx`,name:`TypeLiteral`}],description:``,name:`onChange`,required:!1,tags:{},type:{name:`ChangeEventHandler<HTMLInputElement, HTMLInputElement>`}},onBlur:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/DayCheckbox/DayCheckbox.tsx`,name:`TypeLiteral`}],description:``,name:`onBlur`,required:!1,tags:{},type:{name:`FocusEventHandler<HTMLInputElement>`}},label:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/DayCheckbox/DayCheckbox.tsx`,name:`TypeLiteral`}],description:``,name:`label`,required:!0,tags:{},type:{name:`ReactNode`}},checked:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/DayCheckbox/DayCheckbox.tsx`,name:`TypeLiteral`}],description:``,name:`checked`,required:!1,tags:{},type:{name:`boolean`}},disabled:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/DayCheckbox/DayCheckbox.tsx`,name:`TypeLiteral`}],description:``,name:`disabled`,required:!1,tags:{},type:{name:`boolean`}},tooltipContent:{defaultValue:null,declarations:[{fileName:`pro/src/ui-kit/form/DayCheckbox/DayCheckbox.tsx`,name:`TypeLiteral`}],description:``,name:`tooltipContent`,required:!0,tags:{},type:{name:`ReactNode`}}},tags:{}}}catch{}})),x,S,C,w,T,E,D,O;e((()=>{s(),b(),x=r(),S={title:`@/ui-kit/forms/DayCheckbox`,component:y},C=({children:e})=>(0,x.jsx)(u,{...c({defaultValues:{myField:!0}}),children:(0,x.jsx)(`form`,{children:e})}),w={args:{label:`L`,tooltipContent:`Lundi`,name:`myField`,checked:!0,onChange:()=>{}}},T={args:{label:`L`,tooltipContent:`Lundi`,name:`myField`,checked:!1,disabled:!0,onChange:()=>{}}},E={args:{label:`L`,tooltipContent:`Lundi`,name:`myField`,checked:!1,hasError:!0,displayErrorMessage:!1,onChange:()=>{}}},D={args:{label:`L`,tooltipContent:`Lundi`},decorators:[e=>(0,x.jsx)(C,{children:(0,x.jsx)(e,{})})],render:e=>{let{register:t}=l();return(0,x.jsx)(y,{...e,...t(`myField`)})}},w.parameters={...w.parameters,docs:{...w.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: true,
    onChange: () => {
      //  Control the result here with e.target.checked
    }
  }
}`,...w.parameters?.docs?.source}}},T.parameters={...T.parameters,docs:{...T.parameters?.docs,source:{originalSource:`{
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
}`,...T.parameters?.docs?.source}}},E.parameters={...E.parameters,docs:{...E.parameters?.docs,source:{originalSource:`{
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
}`,...E.parameters?.docs?.source}}},D.parameters={...D.parameters,docs:{...D.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'L',
    tooltipContent: 'Lundi'
  },
  decorators: [Story => <Wrapper>
        <Story />
      </Wrapper>],
  render: args => {
    const {
      register
    } = useFormContext<{
      myField: boolean;
    }>();
    return <DayCheckbox {...args} {...register('myField')} />;
  }
}`,...D.parameters?.docs?.source}}},O=[`Default`,`Disabled`,`WithinAGroupInError`,`WithinForm`]}))();export{w as Default,T as Disabled,E as WithinAGroupInError,D as WithinForm,O as __namedExportsOrder,S as default};