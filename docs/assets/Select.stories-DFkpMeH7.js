import{j as e}from"./jsx-runtime-DF2Pcvd1.js";import{u as E,a as C,F as O}from"./index.esm-BGRy545K.js";import{c as _}from"./index-DeARc5FM.js";import{r as h}from"./index-B2-qRKKC.js";import{f as W}from"./full-down-Cmbtr9nI.js";import{S as D}from"./SvgIcon-DfLnDDE5.js";import{F as H}from"./FieldError-B3RhE53I.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./stroke-error-DSZD431a.js";const r={"select-input":"_select-input_17wx0_1","filter-variant":"_filter-variant_17wx0_51","form-variant":"_form-variant_17wx0_57","has-value":"_has-value_17wx0_71","has-description":"_has-description_17wx0_79","has-error":"_has-error_17wx0_84","select-input-icon":"_select-input-icon_17wx0_88","select-input-wrapper":"_select-input-wrapper_17wx0_126","select-input-placeholder":"_select-input-placeholder_17wx0_133"},v=h.forwardRef(({hasError:a=!1,hasDescription:n=!1,defaultOption:l=null,name:t,disabled:d,options:y,className:b,variant:o,...i},s)=>e.jsxs("div",{className:_(r["select-input-wrapper"],{[r["has-description"]]:n}),children:[e.jsxs("select",{"aria-invalid":a,...a?{"aria-describedby":`error-${t}`}:{},className:_(r["select-input"],b,{[r["has-error"]]:a,[r["has-description"]]:n,[r["select-input-placeholder"]]:i.value==="",[r["filter-variant"]]:o==="filter",[r["form-variant"]]:o==="form",[r["has-value"]]:!!i.value}),disabled:d,id:t,name:t,...i,ref:s,children:[l&&e.jsx("option",{value:l.value,children:l.label}),y.map(u=>e.jsx("option",{value:u.value,children:u.label},u.value))]}),e.jsx("div",{className:_(r["select-input-icon"],{[r["filter-variant"]]:o==="filter"}),children:e.jsx(D,{src:W,alt:""})})]}));v.displayName="SelectInput";try{v.displayName="SelectInput",v.__docgenInfo={description:"",displayName:"SelectInput",props:{name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},hasError:{defaultValue:{value:"false"},description:"",name:"hasError",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"filter"'},{value:'"form"'}]}},options:{defaultValue:null,description:"",name:"options",required:!0,type:{name:"SelectOption[]"}},defaultOption:{defaultValue:{value:"null"},description:"",name:"defaultOption",required:!1,type:{name:"SelectOption | null"}},hasDescription:{defaultValue:{value:"false"},description:"",name:"hasDescription",required:!1,type:{name:"boolean"}}}}}catch{}const L="_label_1kw3x_1",R="_error_1kw3x_6",c={label:L,error:R},p=h.forwardRef(({name:a,defaultOption:n=null,options:l,className:t,required:d,disabled:y,label:b,onChange:o,onBlur:i,error:s,asterisk:u=!0,value:F,ariaLabel:I},k)=>{const x=h.useId(),g=h.useId();return e.jsxs("div",{className:_(c.select,t),children:[e.jsxs("div",{className:c["select-field"],children:[e.jsxs("label",{htmlFor:x,className:c.label,children:[b,d&&u?" *":""]}),e.jsx(v,{disabled:y,hasError:!!s,options:l,defaultOption:n,"aria-required":d,onBlur:i,onChange:o,name:a,value:F,"aria-describedby":g,ref:k,id:x,"aria-label":I})]}),e.jsx("div",{role:"alert",id:g,children:s&&e.jsx(H,{name:a,className:c.error,children:s})})]})});p.displayName="Select";try{p.displayName="Select",p.__docgenInfo={description:"",displayName:"Select",props:{name:{defaultValue:null,description:"Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error",name:"name",required:!0,type:{name:"string"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},required:{defaultValue:null,description:"",name:"required",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"ChangeEventHandler<HTMLSelectElement>"}},onBlur:{defaultValue:null,description:"",name:"onBlur",required:!1,type:{name:"FocusEventHandler<HTMLSelectElement>"}},defaultOption:{defaultValue:{value:"null"},description:"Option displayed if no option of the option list is selected",name:"defaultOption",required:!1,type:{name:"SelectOption | null"}},options:{defaultValue:null,description:"",name:"options",required:!0,type:{name:"SelectOption[]"}},asterisk:{defaultValue:{value:"true"},description:"Whether or not to display the asterisk in the label when the field is required",name:"asterisk",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},value:{defaultValue:null,description:"",name:"value",required:!1,type:{name:"string"}},ariaLabel:{defaultValue:null,description:"",name:"ariaLabel",required:!1,type:{name:"string"}}}}}catch{}const B=({children:a})=>{const n=C({defaultValues:{group:"option1"}});return e.jsx(O,{...n,children:e.jsx("form",{children:a})})},K={title:"ui-kit/formsV2/Select",component:p},m={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}],value:"option1",onChange:()=>{}}},f={args:{label:"Select an option",options:[{label:"option 1",value:"option1"},{label:"option 2",value:"option2"}]},decorators:[a=>e.jsx(B,{children:e.jsx(a,{})})],render:a=>{const{register:n}=E();return e.jsx(p,{...a,...n("option")})}};var S,q,V;m.parameters={...m.parameters,docs:{...(S=m.parameters)==null?void 0:S.docs,source:{originalSource:`{
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
}`,...(V=(q=m.parameters)==null?void 0:q.docs)==null?void 0:V.source}}};var j,w,N;f.parameters={...f.parameters,docs:{...(j=f.parameters)==null?void 0:j.docs,source:{originalSource:`{
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
}`,...(N=(w=f.parameters)==null?void 0:w.docs)==null?void 0:N.source}}};const Q=["Default","WithinForm"];export{m as Default,f as WithinForm,Q as __namedExportsOrder,K as default};
