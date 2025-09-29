import{j as e}from"./jsx-runtime-BM-03y9p.js";import{a as C,u as _,F}from"./index.esm-D9af2D0Q.js";import{c as L}from"./index-k1Krptel.js";import{r as c}from"./iframe-NGzEZkYW.js";import{F as j}from"./FieldError-DmzTvgrd.js";import{T as E}from"./Tooltip-RH70y-x7.js";import"./preload-helper-PPVm8Dsz.js";import"./stroke-error-DSZD431a.js";import"./SvgIcon-DkRG759-.js";const N="_checkbox_10b16_1",V="_disabled_10b16_9",q="_error_10b16_12",n={checkbox:N,disabled:V,"checkbox-input":"_checkbox-input_10b16_9",error:q,"checkbox-label":"_checkbox-label_10b16_22","visually-hidden":"_visually-hidden_10b16_64"},o=c.forwardRef(({name:r,className:a,error:d,label:b,displayErrorMessage:f=!0,onChange:y,onBlur:g,checked:x,disabled:u,tooltipContent:m},k)=>{const p=c.useId(),h=c.useId();return e.jsxs("div",{className:L(n.checkbox,{[n.disabled]:u,[n.error]:!!d},a),children:[e.jsxs("label",{className:n["checkbox-label"],htmlFor:h,children:[e.jsx("span",{"aria-hidden":"true",children:b}),e.jsx("span",{className:n["visually-hidden"],children:m})]}),e.jsx(E,{content:m,children:e.jsx("input",{type:"checkbox",className:n["checkbox-input"],"aria-labelledby":`${r}-label`,name:r,ref:k,"aria-describedby":p,onChange:y,onBlur:g,checked:x,disabled:u,id:h})}),e.jsx("div",{role:"alert",id:p,children:d&&f&&e.jsx(j,{name:r,className:n.error,children:d})})]})});o.displayName="DayCheckbox";try{o.displayName="DayCheckbox",o.__docgenInfo={description:"",displayName:"DayCheckbox",props:{name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error text for the checkbox",name:"error",required:!1,type:{name:"string"}},displayErrorMessage:{defaultValue:{value:"true"},description:"Whether or not to display the error message. If false, the field has the error styles but no message",name:"displayErrorMessage",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},checked:{defaultValue:null,description:"",name:"checked",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},tooltipContent:{defaultValue:null,description:"",name:"tooltipContent",required:!0,type:{name:"ReactNode"}}}}}catch{}const B={title:"@/ui-kit/forms/DayCheckbox",component:o},D=({children:r})=>{const a=_({defaultValues:{myField:!0}});return e.jsx(F,{...a,children:e.jsx("form",{children:r})})},t={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!0,onChange:()=>{}}},s={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!1,disabled:!0,onChange:()=>{}}},l={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!1,error:"error",displayErrorMessage:!1,onChange:()=>{}}},i={args:{label:"L",tooltipContent:"Lundi"},decorators:[r=>e.jsx(D,{children:e.jsx(r,{})})],render:r=>{const{register:a}=C();return e.jsx(o,{...r,...a("myField")})}};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: true,
    onChange: () => {
      //  Control the result here with e.target.checked
    }
  }
}`,...t.parameters?.docs?.source}}};s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
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
}`,...s.parameters?.docs?.source}}};l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: false,
    error: 'error',
    displayErrorMessage: false,
    onChange: () => {
      //  Control the result here with e.target.checked
    }
  }
}`,...l.parameters?.docs?.source}}};i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{
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
}`,...i.parameters?.docs?.source}}};const A=["Default","Disabled","WithinAGroupInError","WithinForm"];export{t as Default,s as Disabled,l as WithinAGroupInError,i as WithinForm,A as __namedExportsOrder,B as default};
