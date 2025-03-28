import{j as e}from"./jsx-runtime-BYYWji4R.js";import{u as w,a as I,F as W}from"./index.esm-Z2NZos4s.js";import{c as M}from"./index-DeARc5FM.js";import{r as p}from"./index-ClcD9ViR.js";import{F as S}from"./FieldError-azuIsM2E.js";import{T as H}from"./Tooltip-BU5AxWXW.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./stroke-error-DSZD431a.js";import"./SvgIcon-CyWUmZpn.js";const R="_checkbox_ppwvf_1",T="_disabled_ppwvf_9",B="_error_ppwvf_14",n={checkbox:R,disabled:T,"checkbox-input":"_checkbox-input_ppwvf_9",error:B,"checkbox-label":"_checkbox-label_ppwvf_24"},o=p.forwardRef(({name:r,className:a,error:c,label:E,displayErrorMessage:j=!0,onChange:N,onBlur:V,checked:v,disabled:d,tooltipContent:q},D)=>{const u=p.useId();return e.jsxs("div",{className:M(n.checkbox,{[n.disabled]:d,[n.error]:!!c},a),children:[e.jsx("label",{className:n["checkbox-label"],"aria-hidden":!0,children:E}),e.jsx(H,{content:q,children:e.jsx("input",{type:"checkbox",className:n["checkbox-input"],name:r,ref:D,"aria-describedby":u,onChange:N,onBlur:V,checked:v,disabled:d})}),e.jsx("div",{role:"alert",id:u,children:c&&j&&e.jsx(S,{name:r,className:n.error,children:c})})]})});o.displayName="DayCheckbox";try{o.displayName="DayCheckbox",o.__docgenInfo={description:"",displayName:"DayCheckbox",props:{name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"Error text for the checkbox",name:"error",required:!1,type:{name:"string"}},displayErrorMessage:{defaultValue:{value:"true"},description:"Whether or not to display the error message. If false, the field has the error styles but no message",name:"displayErrorMessage",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLInputElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLInputElement>"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},checked:{defaultValue:null,description:"",name:"checked",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},tooltipContent:{defaultValue:null,description:"",name:"tooltipContent",required:!0,type:{name:"ReactNode"}}}}}catch{}const Y={title:"ui-kit/formsV2/DayCheckbox",component:o},A=({children:r})=>{const a=I({defaultValues:{myField:!0}});return e.jsx(W,{...a,children:e.jsx("form",{children:r})})},t={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!0,onChange:()=>{}}},s={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!1,disabled:!0,onChange:()=>{}}},l={args:{label:"L",tooltipContent:"Lundi",name:"myField",checked:!1,error:"error",displayErrorMessage:!1,onChange:()=>{}}},i={args:{label:"L",tooltipContent:"Lundi"},decorators:[r=>e.jsx(A,{children:e.jsx(r,{})})],render:r=>{const{register:a}=w();return e.jsx(o,{...r,...a("myField")})}};var m,h,f;t.parameters={...t.parameters,docs:{...(m=t.parameters)==null?void 0:m.docs,source:{originalSource:`{
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: true,
    onChange: () => {
      //  Control the result here with e.target.checked
    }
  }
}`,...(f=(h=t.parameters)==null?void 0:h.docs)==null?void 0:f.source}}};var b,y,g;s.parameters={...s.parameters,docs:{...(b=s.parameters)==null?void 0:b.docs,source:{originalSource:`{
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
}`,...(g=(y=s.parameters)==null?void 0:y.docs)==null?void 0:g.source}}};var x,k,C;l.parameters={...l.parameters,docs:{...(x=l.parameters)==null?void 0:x.docs,source:{originalSource:`{
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
}`,...(C=(k=l.parameters)==null?void 0:k.docs)==null?void 0:C.source}}};var _,F,L;i.parameters={...i.parameters,docs:{...(_=i.parameters)==null?void 0:_.docs,source:{originalSource:`{
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
}`,...(L=(F=i.parameters)==null?void 0:F.docs)==null?void 0:L.source}}};const Z=["Default","Disabled","WithinAGroupInError","WithinForm"];export{t as Default,s as Disabled,l as WithinAGroupInError,i as WithinForm,Z as __namedExportsOrder,Y as default};
