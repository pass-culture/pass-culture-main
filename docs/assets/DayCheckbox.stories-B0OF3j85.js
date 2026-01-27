import{j as e}from"./jsx-runtime-C_uOM0Gm.js";import{a as x,u as k,F as C}from"./index.esm-B74CwnGv.js";import{c as _}from"./index-TscbDd2H.js";import{r as p}from"./iframe-CTnXOULQ.js";import{T as F}from"./Tooltip-GJ5PEk5n.js";import"./preload-helper-PPVm8Dsz.js";const L="_checkbox_10b16_1",E="_disabled_10b16_9",j="_error_10b16_12",n={checkbox:L,disabled:E,"checkbox-input":"_checkbox-input_10b16_9",error:j,"checkbox-label":"_checkbox-label_10b16_22","visually-hidden":"_visually-hidden_10b16_64"},o=p.forwardRef(({name:r,className:a,label:h,hasError:d,onChange:b,onBlur:f,checked:y,disabled:c,tooltipContent:u},g)=>{const m=p.useId();return e.jsxs("div",{className:_(n.checkbox,{[n.disabled]:c,[n.error]:!!d},a),children:[e.jsxs("label",{className:n["checkbox-label"],htmlFor:m,children:[e.jsx("span",{"aria-hidden":"true",children:h}),e.jsx("span",{className:n["visually-hidden"],children:u})]}),e.jsx(F,{content:u,children:e.jsx("input",{type:"checkbox",className:n["checkbox-input"],"aria-labelledby":`${r}-label`,"aria-invalid":d,name:r,ref:g,onChange:b,onBlur:f,checked:y,disabled:c,id:m})})]})});o.displayName="DayCheckbox";try{o.displayName="DayCheckbox",o.__docgenInfo={description:"",displayName:"DayCheckbox",props:{name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},hasError:{defaultValue:null,description:"Error text for the checkbox",name:"hasError",required:!1,type:{name:"boolean"}},displayErrorMessage:{defaultValue:null,description:"Whether or not to display the error message. If false, the field has the error styles but no message",name:"displayErrorMessage",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},checked:{defaultValue:null,description:"",name:"checked",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},tooltipContent:{defaultValue:null,description:"",name:"tooltipContent",required:!0,type:{name:"ReactNode"}}}}}catch{}const M={title:"@/ui-kit/forms/DayCheckbox",component:o},N=({children:r})=>{const a=k({defaultValues:{myField:!0}});return e.jsx(C,{...a,children:e.jsx("form",{children:r})})},t={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!0,onChange:()=>{}}},s={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!1,disabled:!0,onChange:()=>{}}},l={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!1,hasError:!0,displayErrorMessage:!1,onChange:()=>{}}},i={args:{label:"L",tooltipContent:"Lundi"},decorators:[r=>e.jsx(N,{children:e.jsx(r,{})})],render:r=>{const{register:a}=x();return e.jsx(o,{...r,...a("myField")})}};t.parameters={...t.parameters,docs:{...t.parameters?.docs,source:{originalSource:`{
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
    hasError: true,
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
}`,...i.parameters?.docs?.source}}};const S=["Default","Disabled","WithinAGroupInError","WithinForm"];export{t as Default,s as Disabled,l as WithinAGroupInError,i as WithinForm,S as __namedExportsOrder,M as default};
