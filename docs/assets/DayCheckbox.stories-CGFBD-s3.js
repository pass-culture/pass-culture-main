import{j as e}from"./jsx-runtime-DF2Pcvd1.js";import{u as I,a as W,F as M}from"./index.esm-BBvhERNj.js";import{c as S}from"./index-DeARc5FM.js";import{r as m}from"./index-B2-qRKKC.js";import{F as z}from"./FieldError-B3RhE53I.js";import{T as w}from"./Tooltip-C-mHJC8R.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./stroke-error-DSZD431a.js";import"./SvgIcon-DfLnDDE5.js";const H="_checkbox_t6kzv_1",R="_disabled_t6kzv_9",T="_error_t6kzv_12",n={checkbox:H,disabled:R,"checkbox-input":"_checkbox-input_t6kzv_9",error:T,"checkbox-label":"_checkbox-label_t6kzv_22"},a=m.forwardRef(({name:r,className:t,error:c,label:E,displayErrorMessage:j=!0,onChange:N,onBlur:V,checked:v,disabled:d,tooltipContent:q},D)=>{const u=m.useId();return e.jsxs("div",{className:S(n.checkbox,{[n.disabled]:d,[n.error]:!!c},t),children:[e.jsx("label",{className:n["checkbox-label"],"aria-hidden":!0,children:E}),e.jsx(w,{content:q,children:e.jsx("input",{type:"checkbox",className:n["checkbox-input"],name:r,ref:D,"aria-describedby":u,onChange:N,onBlur:V,checked:v,disabled:d})}),e.jsx("div",{role:"alert",id:u,children:c&&j&&e.jsx(z,{name:r,className:n.error,children:c})})]})});a.displayName="DayCheckbox";try{a.displayName="DayCheckbox",a.__docgenInfo={description:"",displayName:"DayCheckbox",props:{name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error text for the checkbox",name:"error",required:!1,type:{name:"string"}},displayErrorMessage:{defaultValue:{value:"true"},description:"Whether or not to display the error message. If false, the field has the error styles but no message",name:"displayErrorMessage",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},checked:{defaultValue:null,description:"",name:"checked",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},tooltipContent:{defaultValue:null,description:"",name:"tooltipContent",required:!0,type:{name:"ReactNode"}}}}}catch{}const Y={title:"@/ui-kit/formsV2/DayCheckbox",component:a},B=({children:r})=>{const t=W({defaultValues:{myField:!0}});return e.jsx(M,{...t,children:e.jsx("form",{children:r})})},o={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!0,onChange:()=>{}}},s={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!1,disabled:!0,onChange:()=>{}}},l={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!1,error:"error",displayErrorMessage:!1,onChange:()=>{}}},i={args:{label:"L",tooltipContent:"Lundi"},decorators:[r=>e.jsx(B,{children:e.jsx(r,{})})],render:r=>{const{register:t}=I();return e.jsx(a,{...r,...t("myField")})}};var p,h,b;o.parameters={...o.parameters,docs:{...(p=o.parameters)==null?void 0:p.docs,source:{originalSource:`{
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: true,
    onChange: () => {
      //  Control the result here with e.target.checked
    }
  }
}`,...(b=(h=o.parameters)==null?void 0:h.docs)==null?void 0:b.source}}};var f,y,g;s.parameters={...s.parameters,docs:{...(f=s.parameters)==null?void 0:f.docs,source:{originalSource:`{
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
}`,...(g=(y=s.parameters)==null?void 0:y.docs)==null?void 0:g.source}}};var k,x,C;l.parameters={...l.parameters,docs:{...(k=l.parameters)==null?void 0:k.docs,source:{originalSource:`{
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
}`,...(C=(x=l.parameters)==null?void 0:x.docs)==null?void 0:C.source}}};var _,F,L;i.parameters={...i.parameters,docs:{...(_=i.parameters)==null?void 0:_.docs,source:{originalSource:`{
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
}`,...(L=(F=i.parameters)==null?void 0:F.docs)==null?void 0:L.source}}};const Z=["Default","Disabled","WithinAGroupInError","WithinForm"];export{o as Default,s as Disabled,l as WithinAGroupInError,i as WithinForm,Z as __namedExportsOrder,Y as default};
