import{j as a}from"./jsx-runtime-BYYWji4R.js";import{u as ee,a as ae,F as re}from"./index.esm-BuPb1Mi7.js";import{B as ne,R as o}from"./BaseRadio-DWuvXWmu.js";import{c as oe}from"./index-DeARc5FM.js";import{F as ie}from"./FieldSetLayout-Cs-MLWIC.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./SvgIcon-CyWUmZpn.js";import"./FieldError-azuIsM2E.js";import"./stroke-error-DSZD431a.js";const y={"radio-group-item":"_radio-group-item_1pthw_1","radio-group-display-inline":"_radio-group-display-inline_1pthw_4","radio-group-display-inline-grow":"_radio-group-display-inline-grow_1pthw_4"},t=({disabled:r,group:e,name:s,legend:b,describedBy:z,className:J,variant:K,onChange:Q,isOptional:U=!0,displayMode:Y,error:v,checkedOption:Z})=>a.jsx(ie,{className:oe(y["radio-group"],J),dataTestId:`wrapper-${s}`,error:v,legend:b,name:`radio-group-${s}`,ariaDescribedBy:z,isOptional:U,hideFooter:!0,children:a.jsx("div",{className:y[`radio-group-display-${Y}`],children:e.map(i=>a.jsx("div",{className:y["radio-group-item"],children:a.jsx(ne,{disabled:r,label:i.label,name:s,value:i.value,variant:K,hasError:!!v,onChange:Q,icon:i.icon,iconPosition:i.iconPosition,description:i.description,checked:Z===i.value,...v?{ariaDescribedBy:`error-${s}`}:{},childrenOnChecked:i.childrenOnChecked})},i.value))})});try{t.displayName="RadioGroup",t.__docgenInfo={description:"The RadioGroup component is a set of radio buttons grouped together under a common `fieldset`.",displayName:"RadioGroup",props:{className:{defaultValue:null,description:"Custom CSS class applied to the group's `fieldset` element.",name:"className",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"Whether the radio buttons are disabled.",name:"disabled",required:!1,type:{name:"boolean"}},name:{defaultValue:null,description:"The name of the radio group field.",name:"name",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"Callback function to handle changes in the radio group.",name:"onChange",required:!1,type:{name:"((e: ChangeEvent<HTMLInputElement>) => void)"}},variant:{defaultValue:null,description:"Variant of the radio inputs styles within the group.",name:"variant",required:!1,type:{name:"enum",value:[{value:'"BOX"'}]}},group:{defaultValue:null,description:`The group of radio button options.
Each item contains a label and a value.
The label is what's displayed while the value is used as an identifier.`,name:"group",required:!0,type:{name:"GroupOption[]"}},isOptional:{defaultValue:{value:"true"},description:"Whether or not the group is optional.",name:"isOptional",required:!1,type:{name:"boolean"}},error:{defaultValue:null,description:"Error message",name:"error",required:!1,type:{name:"string"}},displayMode:{defaultValue:null,description:`How the radio buttons are displayed within the group.
If "default", buttons are displayed in column.
If "inline", buttons are displayed in a row.
If "inline-grow", buttons are displayed in a row, and they share the available width.`,name:"displayMode",required:!1,type:{name:"enum",value:[{value:'"inline"'},{value:'"default"'},{value:'"inline-grow"'}]}},checkedOption:{defaultValue:null,description:"Selected option, required if the group is non-controlled",name:"checkedOption",required:!1,type:{name:"string"}},legend:{defaultValue:null,description:"The legend of the `fieldset`. If this prop is empty, the `describedBy` must be used.",name:"legend",required:!1,type:{name:"ReactNode"}},describedBy:{defaultValue:null,description:"A reference to the text element that describes the radio group. If this prop is empty, the `legend` must be used.",name:"describedBy",required:!1,type:{name:"string"}}}}}catch{}const be={title:"ui-kit/formsV2/RadioGroup",component:t},te=({children:r})=>{const e=ae({defaultValues:{group:"option1"}});return a.jsx(re,{...e,children:a.jsx("form",{children:r})})},n={name:"group",legend:"Choisir une option",group:[{label:"Option 1",value:"option1"},{label:"Option 2",value:"option2"},{label:"Option 3",value:"option3"}],onChange:()=>{}},l={args:n},d={args:n,decorators:[r=>a.jsx(te,{children:a.jsx(r,{})})],render:r=>{const{setValue:e,watch:s}=ee();return a.jsx(t,{...r,checkedOption:s("group"),onChange:b=>{e("group",b.target.value)}})}},u={args:{...n,variant:o.BOX,disabled:!0}},p={args:{...n,variant:o.BOX,name:"name 2"}},c={args:{...n,variant:o.BOX,displayMode:"inline"}},m={args:{...n,variant:o.BOX,displayMode:"inline-grow"}},g={args:{...n,variant:o.BOX,group:n.group.map((r,e)=>({...r,childrenOnChecked:a.jsx(t,{legend:"Choisir une sous-option",name:"name 4",variant:o.BOX,group:[{label:`Sous-option ${e+1} 1`,value:`option${e}1`},{label:`Sous-option ${e+1} 2`,value:`option${e}2`}]})})),name:"name 3"}},h={args:{...n,variant:o.BOX,name:"name 5",group:[{label:a.jsx("span",{id:"my-id-1",children:"Option 1"}),value:"option1"},{label:a.jsx("span",{id:"my-id-2",children:"Option 2"}),value:"option2"},{label:a.jsx("span",{id:"my-id-3",children:"Option 3"}),value:"option3",childrenOnChecked:a.jsx(t,{name:"subgroup",describedBy:"my-id-3",variant:o.BOX,group:[{label:"Sous-option 1",value:"sub-option-1"},{label:"Sous-option 2",value:"sub-option-2"}]})}]}},f={args:{...n,disabled:!0,variant:o.BOX,group:n.group.map((r,e)=>({...r,childrenOnChecked:a.jsx(t,{legend:"Choisir une sous-option",name:"name 4",variant:o.BOX,group:[{label:`Sous-option ${e+1} 1`,value:`option${e}1`},{label:`Sous-option ${e+1} 2`,value:`option${e}2`}],disabled:!0})})),name:"name 3"}};var O,B,V;l.parameters={...l.parameters,docs:{...(O=l.parameters)==null?void 0:O.docs,source:{originalSource:`{
  args: defaultArgs
}`,...(V=(B=l.parameters)==null?void 0:B.docs)==null?void 0:V.source}}};var C,R,S;d.parameters={...d.parameters,docs:{...(C=d.parameters)==null?void 0:C.docs,source:{originalSource:`{
  args: defaultArgs,
  decorators: [(Story: any) => <Wrapper>
        <Story />
      </Wrapper>],
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const {
      setValue,
      watch
    } = useFormContext<{
      group: string;
    }>();
    return <RadioGroup {...args} checkedOption={watch('group')} onChange={e => {
      setValue('group', e.target.value);
    }}></RadioGroup>;
  }
}`,...(S=(R=d.parameters)==null?void 0:R.docs)==null?void 0:S.source}}};var w,x,X;u.parameters={...u.parameters,docs:{...(w=u.parameters)==null?void 0:w.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    disabled: true
  }
}`,...(X=(x=u.parameters)==null?void 0:x.docs)==null?void 0:X.source}}};var _,$,k;p.parameters={...p.parameters,docs:{...(_=p.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    name: 'name 2'
  }
}`,...(k=($=p.parameters)==null?void 0:$.docs)==null?void 0:k.source}}};var j,G,W;c.parameters={...c.parameters,docs:{...(j=c.parameters)==null?void 0:j.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    displayMode: 'inline'
  }
}`,...(W=(G=c.parameters)==null?void 0:G.docs)==null?void 0:W.source}}};var I,q,A;m.parameters={...m.parameters,docs:{...(I=m.parameters)==null?void 0:I.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    displayMode: 'inline-grow'
  }
}`,...(A=(q=m.parameters)==null?void 0:q.docs)==null?void 0:A.source}}};var F,N,D;g.parameters={...g.parameters,docs:{...(F=g.parameters)==null?void 0:F.docs,source:{originalSource:`{
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
}`,...(D=(N=g.parameters)==null?void 0:N.docs)==null?void 0:D.source}}};var E,M,T;h.parameters={...h.parameters,docs:{...(E=h.parameters)==null?void 0:E.docs,source:{originalSource:`{
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
}`,...(T=(M=h.parameters)==null?void 0:M.docs)==null?void 0:T.source}}};var L,P,H;f.parameters={...f.parameters,docs:{...(L=f.parameters)==null?void 0:L.docs,source:{originalSource:`{
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
}`,...(H=(P=f.parameters)==null?void 0:P.docs)==null?void 0:H.source}}};const ve=["Default","WithinForm","Disabled","WithBorder","Inline","InlineGrow","WithChildren","InnerRadioGroupWithNoLegend","WithChildrenDisabled"];export{l as Default,u as Disabled,c as Inline,m as InlineGrow,h as InnerRadioGroupWithNoLegend,p as WithBorder,g as WithChildren,f as WithChildrenDisabled,d as WithinForm,ve as __namedExportsOrder,be as default};
