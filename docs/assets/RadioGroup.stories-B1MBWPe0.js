import{j as e}from"./jsx-runtime-CfatFE5O.js";import{u as I,F as N}from"./formik.esm-DyanDbCL.js";import{R as r}from"./BaseRadio-D4qL5j88.js";import{c as F}from"./index-DeARc5FM.js";import{R as T}from"./RadioButton-C32EmsW5.js";import{F as W}from"./FieldSetLayout-DBZofOUU.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./FieldError-Bb6I73np.js";import"./stroke-error-DSZD431a.js";import"./SvgIcon-B6esR8Vf.js";const h={"radio-group-item":"_radio-group-item_1eofs_1"},t=({disabled:o,group:a,name:i,legend:$,describedBy:G,className:q,variant:A,onChange:E})=>{const[,c]=I({name:i}),g=c.touched&&!!c.error;return e.jsx(W,{className:F(h["radio-group"],q),dataTestId:`wrapper-${i}`,error:g?c.error:void 0,legend:$,name:`radio-group-${i}`,ariaDescribedBy:G,isOptional:!0,hideFooter:!0,children:a.map(s=>e.jsx("div",{className:h["radio-group-item"],children:e.jsx(T,{disabled:o,label:s.label,name:i,value:s.value,variant:A,hasError:g,onChange:E,...g?{ariaDescribedBy:`error-${i}`}:{},childrenOnChecked:s.childrenOnChecked})},s.value))})};try{t.displayName="RadioGroup",t.__docgenInfo={description:"The RadioGroup component is a set of radio buttons grouped together under a common `fieldset`.\nIt integrates with Formik for form state management and provides customization options for layout and styling.",displayName:"RadioGroup",props:{className:{defaultValue:null,description:"Custom CSS class applied to the group's `fieldset` element.",name:"className",required:!1,type:{name:"string"}},variant:{defaultValue:null,description:"Variant of the radio inputs styles within the group.",name:"variant",required:!1,type:{name:"enum",value:[{value:'"BOX"'}]}},disabled:{defaultValue:null,description:"Whether the radio buttons are disabled.",name:"disabled",required:!1,type:{name:"boolean"}},name:{defaultValue:null,description:"The name of the radio group field.",name:"name",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"Callback function to handle changes in the radio group.",name:"onChange",required:!1,type:{name:"((e: ChangeEvent<HTMLInputElement>) => void)"}},group:{defaultValue:null,description:`The group of radio button options.
Each item contains a label and a value.
The label is what's displayed while the value is used as an identifier.`,name:"group",required:!0,type:{name:"{ label: string | Element; value: string; childrenOnChecked?: Element | undefined; }[]"}},legend:{defaultValue:null,description:"The legend of the `fieldset`. If this prop is empty, the `describedBy` must be used.",name:"legend",required:!1,type:{name:"string"}},describedBy:{defaultValue:null,description:"A reference to the text element that describes the radio group. If this prop is empty, the `legend` must be used.",name:"describedBy",required:!1,type:{name:"string"}}}}}catch{}const Y={title:"ui-kit/forms/RadioGroup",component:t,decorators:[o=>e.jsx(N,{initialValues:{name:"option1","name 3":"option1","name 4":"option02","name 5":"option3"},onSubmit:()=>{},children:({getFieldProps:a})=>e.jsx(o,{...a("group")})})]},n={name:"name",legend:"Choisir une option",group:[{label:"Option 1",value:"option1"},{label:"Option 2",value:"option2"}]},d={args:n},l={args:{...n,variant:r.BOX,disabled:!0}},u={args:{...n,variant:r.BOX,name:"name 2"}},p={args:{...n,variant:r.BOX,group:n.group.map((o,a)=>({...o,childrenOnChecked:e.jsx(t,{legend:"Choisir une sous-option",name:"name 4",variant:r.BOX,group:[{label:`Sous-option ${a+1} 1`,value:`option${a}1`},{label:`Sous-option ${a+1} 2`,value:`option${a}2`}]})})),name:"name 3"}},m={args:{...n,variant:r.BOX,name:"name 5",group:[{label:e.jsx("span",{id:"my-id-1",children:"Option 1"}),value:"option1"},{label:e.jsx("span",{id:"my-id-2",children:"Option 2"}),value:"option2"},{label:e.jsx("span",{id:"my-id-3",children:"Option 3"}),value:"option3",childrenOnChecked:e.jsx(t,{name:"subgroup",describedBy:"my-id-3",variant:r.BOX,group:[{label:"Sous-option 1",value:"sub-option-1"},{label:"Sous-option 2",value:"sub-option-2"}]})}]}};var f,b,v;d.parameters={...d.parameters,docs:{...(f=d.parameters)==null?void 0:f.docs,source:{originalSource:`{
  args: defaultArgs
}`,...(v=(b=d.parameters)==null?void 0:b.docs)==null?void 0:v.source}}};var y,O,B;l.parameters={...l.parameters,docs:{...(y=l.parameters)==null?void 0:y.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    disabled: true
  }
}`,...(B=(O=l.parameters)==null?void 0:O.docs)==null?void 0:B.source}}};var R,C,S;u.parameters={...u.parameters,docs:{...(R=u.parameters)==null?void 0:R.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    name: 'name 2'
  }
}`,...(S=(C=u.parameters)==null?void 0:C.docs)==null?void 0:S.source}}};var V,x,_;p.parameters={...p.parameters,docs:{...(V=p.parameters)==null?void 0:V.docs,source:{originalSource:`{
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
}`,...(_=(x=p.parameters)==null?void 0:x.docs)==null?void 0:_.source}}};var X,j,k;m.parameters={...m.parameters,docs:{...(X=m.parameters)==null?void 0:X.docs,source:{originalSource:`{
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
}`,...(k=(j=m.parameters)==null?void 0:j.docs)==null?void 0:k.source}}};const Z=["Default","Disabled","WithBorder","WithChildren","InnerRadioGroupWithNoLegend"];export{d as Default,l as Disabled,m as InnerRadioGroupWithNoLegend,u as WithBorder,p as WithChildren,Z as __namedExportsOrder,Y as default};
