import{j as e}from"./jsx-runtime-DF2Pcvd1.js";import{u as oe,a as te,F as ie}from"./index.esm-8K3KKJpn.js";import{c as re}from"./index-DeARc5FM.js";import{R as j}from"./RadioButton-cKQWA5sp.js";import{r as se}from"./index-B2-qRKKC.js";import{F as le}from"./FieldError-B3RhE53I.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./Tag-T67fX36U.js";import"./full-thumb-up-Bb4kpRpM.js";import"./SvgIcon-DfLnDDE5.js";import"./stroke-error-DSZD431a.js";const V={"fieldset-layout":"_fieldset-layout_14lq3_1","fieldset-layout-legend":"_fieldset-layout-legend_14lq3_4","fieldset-layout-error":"_fieldset-layout-error_14lq3_7"},O=({children:r,legend:a,className:o,error:t,name:y,hideFooter:b=!1,dataTestId:v,isOptional:_=!1,ariaDescribedBy:x,hideAsterisk:S=!1})=>{const C=!!t||!b;return e.jsxs("fieldset",{className:re(V["fieldset-layout"],o),"data-testid":v,"aria-labelledby":"fieldsetlayout-legend","aria-describedby":`fieldsetlayout-error ${x??""}`.trim(),children:[a&&e.jsxs("legend",{id:"fieldsetlayout-legend",className:se.isValidElement(a)?void 0:V["fieldset-layout-legend"],children:[a,!_&&!S&&" *"]}),r,C&&e.jsx("div",{id:"fieldsetlayout-error",className:V["fieldset-layout-error"],"aria-live":"assertive",children:!!t&&e.jsx(le,{name:y,children:t})})]})};try{O.displayName="FieldSetLayout",O.__docgenInfo={description:"",displayName:"FieldSetLayout",props:{legend:{defaultValue:null,description:"",name:"legend",required:!1,type:{name:"ReactNode"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},error:{defaultValue:null,description:"",name:"error",required:!1,type:{name:"string"}},name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},hideFooter:{defaultValue:{value:"false"},description:"",name:"hideFooter",required:!1,type:{name:"boolean"}},dataTestId:{defaultValue:null,description:"",name:"dataTestId",required:!1,type:{name:"string"}},isOptional:{defaultValue:{value:"false"},description:"",name:"isOptional",required:!1,type:{name:"boolean"}},ariaDescribedBy:{defaultValue:null,description:"",name:"ariaDescribedBy",required:!1,type:{name:"string"}},hideAsterisk:{defaultValue:{value:"false"},description:`Can be false only when it's the only field in a form and it's mandatory,
or when all fields are mandatory and the form indicates that all fields are mandatory
or when the legend itself handles the asterisk`,name:"hideAsterisk",required:!1,type:{name:"boolean"}}}}}catch{}const w={"radio-group-item":"_radio-group-item_1pthw_1","radio-group-display-inline":"_radio-group-display-inline_1pthw_4","radio-group-display-inline-grow":"_radio-group-display-inline-grow_1pthw_4"},i=({disabled:r,group:a,name:o,legend:t,describedBy:y,className:b,onChange:v,isOptional:_=!0,displayMode:x,checkedOption:S,variant:C})=>e.jsx(O,{className:re(w["radio-group"],b),dataTestId:`wrapper-${o}`,legend:t,name:`radio-group-${o}`,ariaDescribedBy:y,isOptional:_,hideFooter:!0,children:e.jsx("div",{className:w[`radio-group-display-${x}`],children:a.map(s=>{const ne=C||s.variant,q={disabled:r,name:o,onChange:v,checked:S===s.value};return e.jsx("div",{className:w["radio-group-item"],children:ne==="default"?e.jsx(j,{...s,...q,variant:"default",description:void 0,asset:void 0,collapsed:void 0}):e.jsx(j,{...s,...q,variant:"detailed"})},s.value)})})});try{i.displayName="RadioGroup",i.__docgenInfo={description:"The RadioGroup component is a set of radio buttons grouped together under a common `fieldset`.",displayName:"RadioGroup",props:{className:{defaultValue:null,description:"Custom CSS class applied to the group's `fieldset` element.",name:"className",required:!1,type:{name:"string"}},disabled:{defaultValue:null,description:"Whether the radio buttons are disabled.",name:"disabled",required:!1,type:{name:"boolean"}},name:{defaultValue:null,description:"The name of the radio group field.",name:"name",required:!0,type:{name:"string"}},onChange:{defaultValue:null,description:"Callback function to handle changes in the radio group.",name:"onChange",required:!1,type:{name:"((e: ChangeEvent<HTMLInputElement>) => void)"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},group:{defaultValue:null,description:`The group of radio button options.
Each item contains a label and a value.
The label is what's displayed while the value is used as an identifier.`,name:"group",required:!0,type:{name:'Omit<RadioButtonProps, "disabled" | "name" | "onChange" | "checked">[]'}},isOptional:{defaultValue:{value:"true"},description:"Whether or not the group is optional.",name:"isOptional",required:!1,type:{name:"boolean"}},checkedOption:{defaultValue:null,description:"Selected option, required if the group is non-controlled",name:"checkedOption",required:!1,type:{name:"string"}},displayMode:{defaultValue:null,description:`How the radio buttons are displayed within the group.
If "default", buttons are displayed in column.
If "inline", buttons are displayed in a row.
If "inline-grow", buttons are displayed in a row, and they share the available width.`,name:"displayMode",required:!1,type:{name:"enum",value:[{value:'"inline"'},{value:'"default"'},{value:'"inline-grow"'}]}},legend:{defaultValue:null,description:"The legend of the `fieldset`. If this prop is empty, the `describedBy` must be used.",name:"legend",required:!1,type:{name:"ReactNode"}},describedBy:{defaultValue:null,description:"A reference to the text element that describes the radio group. If this prop is empty, the `legend` must be used.",name:"describedBy",required:!1,type:{name:"string"}}}}}catch{}const xe={title:"ui-kit/formsV2/RadioGroup",component:i},de=({children:r})=>{const a=te({defaultValues:{group:"option1"}});return e.jsx(ie,{...a,children:e.jsx("form",{children:r})})},n={name:"group",legend:"Choisir une option",group:[{label:"Option 1",value:"option1"},{label:"Option 2",value:"option2"},{label:"Option 3",value:"option3"}],onChange:()=>{}},l={args:n},d={args:n,decorators:[r=>e.jsx(de,{children:e.jsx(r,{})})],render:r=>{const{setValue:a,watch:o}=oe();return e.jsx(i,{...r,checkedOption:o("group"),onChange:t=>{a("group",t.target.value)}})}},u={args:{...n,variant:"detailed",disabled:!0}},p={args:{...n,variant:"detailed",name:"name 2"}},c={args:{...n,variant:"detailed",displayMode:"inline"}},m={args:{...n,variant:"detailed",displayMode:"inline-grow"}},g={args:{...n,variant:"detailed",group:n.group.map((r,a)=>({...r,childrenOnChecked:e.jsx(i,{legend:"Choisir une sous-option",name:"name 4",group:[{label:`Sous-option ${a+1} 1`,value:`option${a}1`},{label:`Sous-option ${a+1} 2`,value:`option${a}2`}]})})),name:"name 3"}},h={args:{...n,variant:"detailed",name:"name 5",group:[{label:e.jsx("span",{id:"my-id-1",children:"Option 1"}),value:"option1"},{label:e.jsx("span",{id:"my-id-2",children:"Option 2"}),value:"option2"},{label:e.jsx("span",{id:"my-id-3",children:"Option 3"}),value:"option3",childrenOnChecked:e.jsx(i,{name:"subgroup",describedBy:"my-id-3",group:[{label:"Sous-option 1",value:"sub-option-1"},{label:"Sous-option 2",value:"sub-option-2"}]})}]}},f={args:{...n,disabled:!0,variant:"detailed",group:n.group.map((r,a)=>({...r,childrenOnChecked:e.jsx(i,{legend:"Choisir une sous-option",name:"name 4",group:[{label:`Sous-option ${a+1} 1`,value:`option${a}1`},{label:`Sous-option ${a+1} 2`,value:`option${a}2`}],disabled:!0})})),name:"name 3"}};var $,k,R;l.parameters={...l.parameters,docs:{...($=l.parameters)==null?void 0:$.docs,source:{originalSource:`{
  args: defaultArgs
}`,...(R=(k=l.parameters)==null?void 0:k.docs)==null?void 0:R.source}}};var N,I,F;d.parameters={...d.parameters,docs:{...(N=d.parameters)==null?void 0:N.docs,source:{originalSource:`{
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
}`,...(F=(I=d.parameters)==null?void 0:I.docs)==null?void 0:F.source}}};var A,G,W;u.parameters={...u.parameters,docs:{...(A=u.parameters)==null?void 0:A.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    disabled: true
  }
}`,...(W=(G=u.parameters)==null?void 0:G.docs)==null?void 0:W.source}}};var B,D,E;p.parameters={...p.parameters,docs:{...(B=p.parameters)==null?void 0:B.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    name: 'name 2'
  }
}`,...(E=(D=p.parameters)==null?void 0:D.docs)==null?void 0:E.source}}};var T,M,L;c.parameters={...c.parameters,docs:{...(T=c.parameters)==null?void 0:T.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    displayMode: 'inline'
  }
}`,...(L=(M=c.parameters)==null?void 0:M.docs)==null?void 0:L.source}}};var P,H,z;m.parameters={...m.parameters,docs:{...(P=m.parameters)==null?void 0:P.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    displayMode: 'inline-grow'
  }
}`,...(z=(H=m.parameters)==null?void 0:H.docs)==null?void 0:z.source}}};var J,K,Q;g.parameters={...g.parameters,docs:{...(J=g.parameters)==null?void 0:J.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
    group: defaultArgs.group.map((g, i) => ({
      ...g,
      childrenOnChecked: <RadioGroup legend="Choisir une sous-option" name="name 4" group={[{
        label: \`Sous-option \${i + 1} 1\`,
        value: \`option\${i}1\`
      }, {
        label: \`Sous-option \${i + 1} 2\`,
        value: \`option\${i}2\`
      }]} />
    })),
    name: 'name 3'
  }
}`,...(Q=(K=g.parameters)==null?void 0:K.docs)==null?void 0:Q.source}}};var U,X,Y;h.parameters={...h.parameters,docs:{...(U=h.parameters)==null?void 0:U.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    variant: 'detailed',
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
      childrenOnChecked: <RadioGroup name="subgroup" describedBy="my-id-3" group={[{
        label: 'Sous-option 1',
        value: 'sub-option-1'
      }, {
        label: 'Sous-option 2',
        value: 'sub-option-2'
      }]} />
    }]
  }
}`,...(Y=(X=h.parameters)==null?void 0:X.docs)==null?void 0:Y.source}}};var Z,ee,ae;f.parameters={...f.parameters,docs:{...(Z=f.parameters)==null?void 0:Z.docs,source:{originalSource:`{
  args: {
    ...defaultArgs,
    disabled: true,
    variant: 'detailed',
    group: defaultArgs.group.map((g, i) => ({
      ...g,
      childrenOnChecked: <RadioGroup legend="Choisir une sous-option" name="name 4" group={[{
        label: \`Sous-option \${i + 1} 1\`,
        value: \`option\${i}1\`
      }, {
        label: \`Sous-option \${i + 1} 2\`,
        value: \`option\${i}2\`
      }]} disabled={true} />
    })),
    name: 'name 3'
  }
}`,...(ae=(ee=f.parameters)==null?void 0:ee.docs)==null?void 0:ae.source}}};const Se=["Default","WithinForm","Disabled","WithBorder","Inline","InlineGrow","WithChildren","InnerRadioGroupWithNoLegend","WithChildrenDisabled"];export{l as Default,u as Disabled,c as Inline,m as InlineGrow,h as InnerRadioGroupWithNoLegend,p as WithBorder,g as WithChildren,f as WithChildrenDisabled,d as WithinForm,Se as __namedExportsOrder,xe as default};
