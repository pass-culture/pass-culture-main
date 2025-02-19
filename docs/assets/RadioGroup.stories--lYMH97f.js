import{j as a}from"./jsx-runtime-CfatFE5O.js";import{u as F,F as T}from"./formik.esm-DyanDbCL.js";import{R as n}from"./BaseRadio-By6x2KuI.js";import{c as w}from"./index-DeARc5FM.js";import{R as L}from"./RadioButton-viGFXuZe.js";import{F as z}from"./FieldSetLayout-DzzARNTO.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./FieldError-DblMbt5C.js";import"./stroke-error-DSZD431a.js";import"./SvgIcon-CUWb-Ez8.js";const b={"radio-group-item":"_radio-group-item_1eofs_1"},i=({disabled:o,group:e,name:t,legend:q,describedBy:D,className:E,variant:I,onChange:N})=>{const[,g]=F({name:t}),h=g.touched&&!!g.error;return a.jsx(z,{className:w(b["radio-group"],E),dataTestId:`wrapper-${t}`,error:h?g.error:void 0,legend:q,name:`radio-group-${t}`,ariaDescribedBy:D,isOptional:!0,hideFooter:!0,children:e.map(s=>a.jsx("div",{className:b["radio-group-item"],children:a.jsx(L,{disabled:o,label:s.label,name:t,value:s.value,variant:I,hasError:h,onChange:N,...h?{ariaDescribedBy:`error-${t}`}:{},childrenOnChecked:s.childrenOnChecked})},s.value))})};try{i.displayName="RadioGroup",i.__docgenInfo={description:"The RadioGroup component is a set of radio buttons grouped together under a common `fieldset`.\nIt integrates with Formik for form state management and provides customization options for layout and styling.",displayName:"RadioGroup",props:{className:{defaultValue:null,description:"Custom CSS class applied to the group's `fieldset` element.",name:"className",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"Whether the radio buttons are disabled.",name:"disabled",required:!1,type:{name:"boolean"}},name:{defaultValue:null,description:"The name of the radio group field.",name:"name",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"Callback function to handle changes in the radio group.",name:"onChange",required:!1,type:{name:"((e: ChangeEvent<HTMLInputElement>) => void)"}},variant:{defaultValue:null,description:"Variant of the radio inputs styles within the group.",name:"variant",required:!1,type:{name:"enum",value:[{value:'"BOX"'}]}},group:{defaultValue:null,description:`The group of radio button options.
Each item contains a label and a value.
The label is what's displayed while the value is used as an identifier.`,name:"group",required:!0,type:{name:"{ label: string | Element; value: string; childrenOnChecked?: Element | undefined; }[]"}},legend:{defaultValue:null,description:"The legend of the `fieldset`. If this prop is empty, the `describedBy` must be used.",name:"legend",required:!1,type:{name:"string"}},describedBy:{defaultValue:null,description:"A reference to the text element that describes the radio group. If this prop is empty, the `legend` must be used.",name:"describedBy",required:!1,type:{name:"string"}}}}}catch{}const oe={title:"ui-kit/forms/RadioGroup",component:i,decorators:[o=>a.jsx(T,{initialValues:{name:"option1","name 3":"option1","name 4":"option02","name 5":"option3"},onSubmit:()=>{},children:({getFieldProps:e})=>a.jsx(o,{...e("group")})})]},r={name:"name",legend:"Choisir une option",group:[{label:"Option 1",value:"option1"},{label:"Option 2",value:"option2"}]},d={args:r},l={args:{...r,variant:n.BOX,disabled:!0}},u={args:{...r,variant:n.BOX,name:"name 2"}},p={args:{...r,variant:n.BOX,group:r.group.map((o,e)=>({...o,childrenOnChecked:a.jsx(i,{legend:"Choisir une sous-option",name:"name 4",variant:n.BOX,group:[{label:`Sous-option ${e+1} 1`,value:`option${e}1`},{label:`Sous-option ${e+1} 2`,value:`option${e}2`}]})})),name:"name 3"}},m={args:{...r,variant:n.BOX,name:"name 5",group:[{label:a.jsx("span",{id:"my-id-1",children:"Option 1"}),value:"option1"},{label:a.jsx("span",{id:"my-id-2",children:"Option 2"}),value:"option2"},{label:a.jsx("span",{id:"my-id-3",children:"Option 3"}),value:"option3",childrenOnChecked:a.jsx(i,{name:"subgroup",describedBy:"my-id-3",variant:n.BOX,group:[{label:"Sous-option 1",value:"sub-option-1"},{label:"Sous-option 2",value:"sub-option-2"}]})}]}},c={args:{...r,disabled:!0,variant:n.BOX,group:r.group.map((o,e)=>({...o,childrenOnChecked:a.jsx(i,{legend:"Choisir une sous-option",name:"name 4",variant:n.BOX,group:[{label:`Sous-option ${e+1} 1`,value:`option${e}1`},{label:`Sous-option ${e+1} 2`,value:`option${e}2`}],disabled:!0})})),name:"name 3"}};var f,v,O;d.parameters={...d.parameters,docs:{...(f=d.parameters)==null?void 0:f.docs,source:{originalSource:`{
  args: defaultArgs
}`,...(O=(v=d.parameters)==null?void 0:v.docs)==null?void 0:O.source}}};var y,B,C;l.parameters={...l.parameters,docs:{...(y=l.parameters)==null?void 0:y.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    disabled: true
  }
}`,...(C=(B=l.parameters)==null?void 0:B.docs)==null?void 0:C.source}}};var R,S,V;u.parameters={...u.parameters,docs:{...(R=u.parameters)==null?void 0:R.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    name: 'name 2'
  }
}`,...(V=(S=u.parameters)==null?void 0:S.docs)==null?void 0:V.source}}};var $,X,x;p.parameters={...p.parameters,docs:{...($=p.parameters)==null?void 0:$.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    group: defaultArgs.group.map((g, i) => ({
      ...g,
      childrenOnChecked: <RadioGroup legend="Choisir une sous-option" name="name 4" variant={RadioVariant.BOX} group={[{
        label: \`Sous-option \${i + 1} 1\`,
        value: \`option\${i}1\`
      }, {
        label: \`Sous-option \${i + 1} 2\`,
        value: \`option\${i}2\`
      }]} />
    })),
    name: 'name 3'
  }
}`,...(x=(X=p.parameters)==null?void 0:X.docs)==null?void 0:x.source}}};var _,j,k;m.parameters={...m.parameters,docs:{...(_=m.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    name: 'name 5',
    group: [{
      label: <span id="my-id-1">Option 1</span>,
      value: 'option1'
    }, {
      label: <span id="my-id-2">Option 2</span>,
      value: 'option2'
    }, {
      label: <span id="my-id-3">Option 3</span>,
      value: 'option3',
      childrenOnChecked: <RadioGroup name="subgroup" describedBy="my-id-3" variant={RadioVariant.BOX} group={[{
        label: 'Sous-option 1',
        value: 'sub-option-1'
      }, {
        label: 'Sous-option 2',
        value: 'sub-option-2'
      }]} />
    }]
  }
}`,...(k=(j=m.parameters)==null?void 0:j.docs)==null?void 0:k.source}}};var G,A,W;c.parameters={...c.parameters,docs:{...(G=c.parameters)==null?void 0:G.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    disabled: true,
    variant: RadioVariant.BOX,
    group: defaultArgs.group.map((g, i) => ({
      ...g,
      childrenOnChecked: <RadioGroup legend="Choisir une sous-option" name="name 4" variant={RadioVariant.BOX} group={[{
        label: \`Sous-option \${i + 1} 1\`,
        value: \`option\${i}1\`
      }, {
        label: \`Sous-option \${i + 1} 2\`,
        value: \`option\${i}2\`
      }]} disabled={true} />
    })),
    name: 'name 3'
  }
}`,...(W=(A=c.parameters)==null?void 0:A.docs)==null?void 0:W.source}}};const ne=["Default","Disabled","WithBorder","WithChildren","InnerRadioGroupWithNoLegend","WithChildrenDisabled"];export{d as Default,l as Disabled,m as InnerRadioGroupWithNoLegend,u as WithBorder,p as WithChildren,c as WithChildrenDisabled,ne as __namedExportsOrder,oe as default};
