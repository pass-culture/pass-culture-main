import{j as e}from"./jsx-runtime-DF2Pcvd1.js";import{u as W,a as z,F as M}from"./index.esm-BBvhERNj.js";import{c as S}from"./index-DeARc5FM.js";import{r as c}from"./index-B2-qRKKC.js";import{F as w}from"./FieldError-B3RhE53I.js";import{T as H}from"./Tooltip-C-mHJC8R.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./stroke-error-DSZD431a.js";import"./SvgIcon-DfLnDDE5.js";const R="_checkbox_szfid_1",T="_disabled_szfid_9",B="_error_szfid_12",n={checkbox:R,disabled:T,"checkbox-input":"_checkbox-input_szfid_9",error:B,"checkbox-label":"_checkbox-label_szfid_22","visually-hidden":"_visually-hidden_szfid_64"},o=c.forwardRef(({name:r,className:a,error:d,label:N,displayErrorMessage:V=!0,onChange:q,onBlur:D,checked:I,disabled:u,tooltipContent:m},v)=>{const p=c.useId(),h=c.useId();return e.jsxs("div",{className:S(n.checkbox,{[n.disabled]:u,[n.error]:!!d},a),children:[e.jsxs("label",{className:n["checkbox-label"],htmlFor:h,children:[e.jsx("span",{"aria-hidden":"true",children:N}),e.jsx("span",{className:n["visually-hidden"],children:m})]}),e.jsx(H,{content:m,children:e.jsx("input",{type:"checkbox",className:n["checkbox-input"],"aria-labelledby":`${r}-label`,name:r,ref:v,"aria-describedby":p,onChange:q,onBlur:D,checked:I,disabled:u,id:h})}),e.jsx("div",{role:"alert",id:p,children:d&&V&&e.jsx(w,{name:r,className:n.error,children:d})})]})});o.displayName="DayCheckbox";try{o.displayName="DayCheckbox",o.__docgenInfo={description:"",displayName:"DayCheckbox",props:{name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error text for the checkbox",name:"error",required:!1,type:{name:"string"}},displayErrorMessage:{defaultValue:{value:"true"},description:"Whether or not to display the error message. If false, the field has the error styles but no message",name:"displayErrorMessage",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},checked:{defaultValue:null,description:"",name:"checked",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},tooltipContent:{defaultValue:null,description:"",name:"tooltipContent",required:!0,type:{name:"ReactNode"}}}}}catch{}const Y={title:"@/ui-kit/forms/DayCheckbox",component:o},A=({children:r})=>{const a=z({defaultValues:{myField:!0}});return e.jsx(M,{...a,children:e.jsx("form",{children:r})})},t={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!0,onChange:()=>{}}},s={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!1,disabled:!0,onChange:()=>{}}},l={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!1,error:"error",displayErrorMessage:!1,onChange:()=>{}}},i={args:{label:"L",tooltipContent:"Lundi"},decorators:[r=>e.jsx(A,{children:e.jsx(r,{})})],render:r=>{const{register:a}=W();return e.jsx(o,{...r,...a("myField")})}};var f,b,y;t.parameters={...t.parameters,docs:{...(f=t.parameters)==null?void 0:f.docs,source:{originalSource:`{
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: true,
    onChange: () => {
      //  Control the result here with e.target.checked
    }
  }
}`,...(y=(b=t.parameters)==null?void 0:b.docs)==null?void 0:y.source}}};var g,x,k;s.parameters={...s.parameters,docs:{...(g=s.parameters)==null?void 0:g.docs,source:{originalSource:`{
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
}`,...(k=(x=s.parameters)==null?void 0:x.docs)==null?void 0:k.source}}};var C,_,F;l.parameters={...l.parameters,docs:{...(C=l.parameters)==null?void 0:C.docs,source:{originalSource:`{
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
}`,...(F=(_=l.parameters)==null?void 0:_.docs)==null?void 0:F.source}}};var L,j,E;i.parameters={...i.parameters,docs:{...(L=i.parameters)==null?void 0:L.docs,source:{originalSource:`{
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
}`,...(E=(j=i.parameters)==null?void 0:j.docs)==null?void 0:E.source}}};const Z=["Default","Disabled","WithinAGroupInError","WithinForm"];export{t as Default,s as Disabled,l as WithinAGroupInError,i as WithinForm,Z as __namedExportsOrder,Y as default};
