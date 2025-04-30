import{j as a}from"./jsx-runtime-BYYWji4R.js";import{u as Q,F as U}from"./formik.esm-Dmsc_7od.js";import{R as n}from"./BaseRadio-DWuvXWmu.js";import{c as Y}from"./index-DeARc5FM.js";import{R as Z}from"./RadioButton-DyivfOGt.js";import{F as ee}from"./FieldSetLayout-Cs-MLWIC.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./SvgIcon-CyWUmZpn.js";import"./FieldError-azuIsM2E.js";import"./stroke-error-DSZD431a.js";const v={"radio-group-item":"_radio-group-item_1pthw_1","radio-group-display-inline":"_radio-group-display-inline_1pthw_4","radio-group-display-inline-grow":"_radio-group-display-inline-grow_1pthw_4"},t=({disabled:r,group:e,name:s,legend:T,describedBy:L,className:P,variant:H,onChange:z,isOptional:J=!0,displayMode:K})=>{const[,b]=Q({name:s}),f=b.touched&&!!b.error;return a.jsx(ee,{className:Y(v["radio-group"],P),dataTestId:`wrapper-${s}`,error:f?b.error:void 0,legend:T,name:`radio-group-${s}`,ariaDescribedBy:L,isOptional:J,hideFooter:!0,children:a.jsx("div",{className:v[`radio-group-display-${K}`],children:e.map(i=>a.jsx("div",{className:v["radio-group-item"],children:a.jsx(Z,{disabled:r,label:i.label,name:s,value:i.value,variant:H,hasError:f,onChange:z,icon:i.icon,iconPosition:i.iconPosition,description:i.description,...f?{ariaDescribedBy:`error-${s}`}:{},childrenOnChecked:i.childrenOnChecked})},i.value))})})};try{t.displayName="RadioGroup",t.__docgenInfo={description:"The RadioGroup component is a set of radio buttons grouped together under a common `fieldset`.\nIt integrates with Formik for form state management and provides customization options for layout and styling.",displayName:"RadioGroup",props:{className:{defaultValue:null,description:"Custom CSS class applied to the group's `fieldset` element.",name:"className",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"Whether the radio buttons are disabled.",name:"disabled",required:!1,type:{name:"boolean"}},name:{defaultValue:null,description:"The name of the radio group field.",name:"name",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"Callback function to handle changes in the radio group.",name:"onChange",required:!1,type:{name:"((e: ChangeEvent<HTMLInputElement>) => void)"}},variant:{defaultValue:null,description:"Variant of the radio inputs styles within the group.",name:"variant",required:!1,type:{name:"enum",value:[{value:'"BOX"'}]}},group:{defaultValue:null,description:`The group of radio button options.
Each item contains a label and a value.
The label is what's displayed while the value is used as an identifier.`,name:"group",required:!0,type:{name:'{ label: string | Element; value: string; icon?: string | undefined; iconPosition?: "center" | "right" | undefined; description?: string | undefined; childrenOnChecked?: Element | undefined; }[]'}},isOptional:{defaultValue:{value:"true"},description:"Whether or not the group is optional.",name:"isOptional",required:!1,type:{name:"boolean"}},displayMode:{defaultValue:null,description:`How the radio buttons are displayed within the group.
If "default", buttons are displayed in column.
If "inline", buttons are displayed in a row.
If "inline-grow", buttons are displayed in a row, and they share the available width.`,name:"displayMode",required:!1,type:{name:"enum",value:[{value:'"inline"'},{value:'"default"'},{value:'"inline-grow"'}]}},legend:{defaultValue:null,description:"The legend of the `fieldset`. If this prop is empty, the `describedBy` must be used.",name:"legend",required:!1,type:{name:"ReactNode"}},describedBy:{defaultValue:null,description:"A reference to the text element that describes the radio group. If this prop is empty, the `legend` must be used.",name:"describedBy",required:!1,type:{name:"string"}}}}}catch{}const me={title:"ui-kit/forms/RadioGroup",component:t,decorators:[r=>a.jsx(U,{initialValues:{name:"option1","name 3":"option1","name 4":"option02","name 5":"option3"},onSubmit:()=>{},children:({getFieldProps:e})=>a.jsx(r,{...e("group")})})]},o={name:"name",legend:"Choisir une option",group:[{label:"Option 1",value:"option1"},{label:"Option 2",value:"option2"},{label:"Option 3",value:"option3"}]},d={args:o},l={args:{...o,variant:n.BOX,disabled:!0}},u={args:{...o,variant:n.BOX,name:"name 2"}},p={args:{...o,variant:n.BOX,displayMode:"inline"}},m={args:{...o,variant:n.BOX,displayMode:"inline-grow"}},c={args:{...o,variant:n.BOX,group:o.group.map((r,e)=>({...r,childrenOnChecked:a.jsx(t,{legend:"Choisir une sous-option",name:"name 4",variant:n.BOX,group:[{label:`Sous-option ${e+1} 1`,value:`option${e}1`},{label:`Sous-option ${e+1} 2`,value:`option${e}2`}]})})),name:"name 3"}},g={args:{...o,variant:n.BOX,name:"name 5",group:[{label:a.jsx("span",{id:"my-id-1",children:"Option 1"}),value:"option1"},{label:a.jsx("span",{id:"my-id-2",children:"Option 2"}),value:"option2"},{label:a.jsx("span",{id:"my-id-3",children:"Option 3"}),value:"option3",childrenOnChecked:a.jsx(t,{name:"subgroup",describedBy:"my-id-3",variant:n.BOX,group:[{label:"Sous-option 1",value:"sub-option-1"},{label:"Sous-option 2",value:"sub-option-2"}]})}]}},h={args:{...o,disabled:!0,variant:n.BOX,group:o.group.map((r,e)=>({...r,childrenOnChecked:a.jsx(t,{legend:"Choisir une sous-option",name:"name 4",variant:n.BOX,group:[{label:`Sous-option ${e+1} 1`,value:`option${e}1`},{label:`Sous-option ${e+1} 2`,value:`option${e}2`}],disabled:!0})})),name:"name 3"}};var y,O,B;d.parameters={...d.parameters,docs:{...(y=d.parameters)==null?void 0:y.docs,source:{originalSource:`{
  args: defaultArgs
}`,...(B=(O=d.parameters)==null?void 0:O.docs)==null?void 0:B.source}}};var R,C,S;l.parameters={...l.parameters,docs:{...(R=l.parameters)==null?void 0:R.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    disabled: true
  }
}`,...(S=(C=l.parameters)==null?void 0:C.docs)==null?void 0:S.source}}};var V,X,_;u.parameters={...u.parameters,docs:{...(V=u.parameters)==null?void 0:V.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    name: 'name 2'
  }
}`,...(_=(X=u.parameters)==null?void 0:X.docs)==null?void 0:_.source}}};var $,w,x;p.parameters={...p.parameters,docs:{...($=p.parameters)==null?void 0:$.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    displayMode: 'inline'
  }
}`,...(x=(w=p.parameters)==null?void 0:w.docs)==null?void 0:x.source}}};var I,j,k;m.parameters={...m.parameters,docs:{...(I=m.parameters)==null?void 0:I.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    displayMode: 'inline-grow'
  }
}`,...(k=(j=m.parameters)==null?void 0:j.docs)==null?void 0:k.source}}};var A,W,G;c.parameters={...c.parameters,docs:{...(A=c.parameters)==null?void 0:A.docs,source:{originalSource:`{
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
}`,...(G=(W=c.parameters)==null?void 0:W.docs)==null?void 0:G.source}}};var q,N,F;g.parameters={...g.parameters,docs:{...(q=g.parameters)==null?void 0:q.docs,source:{originalSource:`{
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
}`,...(F=(N=g.parameters)==null?void 0:N.docs)==null?void 0:F.source}}};var D,E,M;h.parameters={...h.parameters,docs:{...(D=h.parameters)==null?void 0:D.docs,source:{originalSource:`{
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
}`,...(M=(E=h.parameters)==null?void 0:E.docs)==null?void 0:M.source}}};const ce=["Default","Disabled","WithBorder","Inline","InlineFullWidth","WithChildren","InnerRadioGroupWithNoLegend","WithChildrenDisabled"];export{d as Default,l as Disabled,p as Inline,m as InlineFullWidth,g as InnerRadioGroupWithNoLegend,u as WithBorder,c as WithChildren,h as WithChildrenDisabled,ce as __namedExportsOrder,me as default};
