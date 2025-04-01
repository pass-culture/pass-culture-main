import{j as n}from"./jsx-runtime-BYYWji4R.js";import{u as J,F as K}from"./formik.esm-DUQIEGuZ.js";import{B as P,C as s}from"./BaseCheckbox-D1eRSklh.js";import{c as Q}from"./index-DeARc5FM.js";import{F as U}from"./FieldSetLayout-Cs-MLWIC.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./SvgIcon-CyWUmZpn.js";import"./FieldError-azuIsM2E.js";import"./stroke-error-DSZD431a.js";const Y="_inline_1d5x2_7",v={"checkbox-group":"_checkbox-group_1d5x2_1",inline:Y},O=({setGroupTouched:e,label:a,name:g,hasError:f,icon:x,disabled:k,onChange:u,ariaDescribedBy:B,variant:C,childrenOnChecked:l,shouldShowChildren:y})=>{const[i]=J({name:g,type:"checkbox"}),o=V=>{e(),i.onChange(V),u&&u(V)};return n.jsx(P,{...i,icon:x,hasError:f,label:a,onChange:o,disabled:k,ariaDescribedBy:B,variant:C,childrenOnChecked:l,shouldShowChildren:y})};try{O.displayName="CheckboxGroupItem",O.__docgenInfo={description:"",displayName:"CheckboxGroupItem",props:{setGroupTouched:{defaultValue:null,description:"",name:"setGroupTouched",required:!0,type:{name:"() => void"}},name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"ReactNode"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},icon:{defaultValue:null,description:"",name:"icon",required:!1,type:{name:"string"}},hasError:{defaultValue:null,description:"",name:"hasError",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"((event: ChangeEvent<HTMLInputElement>) => void)"}},ariaDescribedBy:{defaultValue:null,description:"",name:"ariaDescribedBy",required:!1,type:{name:"string"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"box"'}]}},childrenOnChecked:{defaultValue:null,description:"",name:"childrenOnChecked",required:!1,type:{name:"Element"}},shouldShowChildren:{defaultValue:null,description:"",name:"shouldShowChildren",required:!1,type:{name:"boolean"}}}}}catch{}const t=({group:e,groupName:a,legend:g,describedBy:f,disabled:x,isOptional:k,variant:u,inline:B=!1,hideAsterisk:C})=>{const[,l,y]=J({name:a}),i=l.touched&&!!l.error;return n.jsx(U,{error:i?l.error:void 0,legend:g,name:a,ariaDescribedBy:f,isOptional:k,hideFooter:!0,hideAsterisk:C,children:n.jsx("div",{className:Q(v["checkbox-group"],{[v.inline]:B}),children:e.map(o=>n.jsx("div",{className:v["checkbox-group-item"],children:n.jsx(O,{icon:o.icon,hasError:i,label:o.label,name:o.name,setGroupTouched:()=>l.touched?null:y.setTouched(!0),disabled:x,onChange:o.onChange,...i?{ariaDescribedBy:`error-${a}`}:{},variant:u,childrenOnChecked:o.childrenOnChecked,shouldShowChildren:o.shouldShowChildren})},o.name))})})};try{t.displayName="CheckboxGroup",t.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"box"'}]}},group:{defaultValue:null,description:"",name:"group",required:!0,type:{name:"{ name: string; label: ReactNode; icon?: string | undefined; onChange?: ((event: ChangeEvent<HTMLInputElement>) => void) | undefined; childrenOnChecked?: Element | undefined; shouldShowChildren?: boolean | undefined; }[]"}},inline:{defaultValue:{value:"false"},description:"",name:"inline",required:!1,type:{name:"boolean"}},isOptional:{defaultValue:null,description:"",name:"isOptional",required:!1,type:{name:"boolean"}},hideAsterisk:{defaultValue:null,description:"",name:"hideAsterisk",required:!1,type:{name:"boolean"}},groupName:{defaultValue:null,description:"",name:"groupName",required:!0,type:{name:"string"}},legend:{defaultValue:null,description:"",name:"legend",required:!1,type:{name:"ReactNode"}},describedBy:{defaultValue:null,description:"",name:"describedBy",required:!1,type:{name:"string"}}}}}catch{}const ue={title:"ui-kit/forms/CheckboxGroup",component:t,decorators:[e=>n.jsx(K,{initialValues:{checkBoxes:{foo:!0,bar:!1,baz:!1,"sub-foo-0":!0,"sub-bar-0":!1,"sub-foo-1":!1,"sub-bar-1":!1,"sub-foo-2":!1,"sub-bar-2":!1}},onSubmit:()=>{},children:({getFieldProps:a})=>n.jsx(e,{...a("group")})})]},r={args:{group:["foo","bar","baz"].map(e=>({label:e,name:`checkBoxes.${e}`})),groupName:"checkBoxes",legend:"This is the legend",disabled:!1}},c={args:{...r.args,variant:s.BOX}},d={args:{...r.args,inline:!0,variant:s.BOX}},p={args:{...r.args,group:["foo","bar","baz"].map(e=>({label:e,name:`checkBoxes.${e}`,childrenOnChecked:n.jsxs("span",{children:["Child content for ",e]})})),variant:s.BOX}},m={args:{...r.args,group:["foo","bar","baz"].map((e,a)=>({label:e,name:`checkBoxes.${e}`,childrenOnChecked:n.jsx(t,{legend:"Sub group legend",groupName:"sub-name",group:[{label:"sub-foo",name:`checkBoxes.sub-foo-${a}`},{label:"sub-bar",name:`checkBoxes.sub-bar-${a}`}],variant:s.BOX})})),variant:s.BOX}},b={args:{...r.args,group:["foo","bar","baz"].map((e,a)=>({label:n.jsx("span",{children:e}),name:`checkBoxes.${e}`,childrenOnChecked:n.jsx(t,{describedBy:"parent-name-id",groupName:"sub-name",group:[{label:"sub-foo",name:`checkBoxes.sub-foo-${a}`},{label:"sub-bar",name:`checkBoxes.sub-bar-${a}`}],variant:s.BOX,inline:a===0})})),variant:s.BOX}},h={args:{...r.args,disabled:!0,group:["foo","bar","baz"].map((e,a)=>({label:n.jsx("span",{children:e}),name:`checkBoxes.${e}`,childrenOnChecked:n.jsx(t,{describedBy:"parent-name-id",groupName:"sub-name",group:[{label:"sub-foo",name:`checkBoxes.sub-foo-${a}`},{label:"sub-bar",name:`checkBoxes.sub-bar-${a}`}],variant:s.BOX,inline:a===0,disabled:!0})})),variant:s.BOX,groupName:"checkBoxes",legend:"This is the legend"}};var _,$,q;r.parameters={...r.parameters,docs:{...(_=r.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    group: ['foo', 'bar', 'baz'].map(item => ({
      label: item,
      name: \`checkBoxes.\${item}\`
    })),
    groupName: 'checkBoxes',
    legend: 'This is the legend',
    disabled: false
  }
}`,...(q=($=r.parameters)==null?void 0:$.docs)==null?void 0:q.source}}};var N,G,X;c.parameters={...c.parameters,docs:{...(N=c.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    variant: CheckboxVariant.BOX
  }
}`,...(X=(G=c.parameters)==null?void 0:G.docs)==null?void 0:X.source}}};var S,j,D;d.parameters={...d.parameters,docs:{...(S=d.parameters)==null?void 0:S.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    inline: true,
    variant: CheckboxVariant.BOX
  }
}`,...(D=(j=d.parameters)==null?void 0:j.docs)==null?void 0:D.source}}};var z,E,T;p.parameters={...p.parameters,docs:{...(z=p.parameters)==null?void 0:z.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    group: ['foo', 'bar', 'baz'].map(item => ({
      label: item,
      name: \`checkBoxes.\${item}\`,
      childrenOnChecked: <span>Child content for {item}</span>
    })),
    variant: CheckboxVariant.BOX
  }
}`,...(T=(E=p.parameters)==null?void 0:E.docs)==null?void 0:T.source}}};var I,W,F;m.parameters={...m.parameters,docs:{...(I=m.parameters)==null?void 0:I.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    group: ['foo', 'bar', 'baz'].map((item, i) => ({
      label: item,
      name: \`checkBoxes.\${item}\`,
      childrenOnChecked: <CheckboxGroup legend="Sub group legend" groupName="sub-name" group={[{
        label: 'sub-foo',
        name: \`checkBoxes.sub-foo-\${i}\`
      }, {
        label: 'sub-bar',
        name: \`checkBoxes.sub-bar-\${i}\`
      }]} variant={CheckboxVariant.BOX} />
    })),
    variant: CheckboxVariant.BOX
  }
}`,...(F=(W=m.parameters)==null?void 0:W.docs)==null?void 0:F.source}}};var w,L,R;b.parameters={...b.parameters,docs:{...(w=b.parameters)==null?void 0:w.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    group: ['foo', 'bar', 'baz'].map((item, i) => ({
      label: <span>{item}</span>,
      name: \`checkBoxes.\${item}\`,
      childrenOnChecked: <CheckboxGroup describedBy="parent-name-id" groupName="sub-name" group={[{
        label: 'sub-foo',
        name: \`checkBoxes.sub-foo-\${i}\`
      }, {
        label: 'sub-bar',
        name: \`checkBoxes.sub-bar-\${i}\`
      }]} variant={CheckboxVariant.BOX} inline={i === 0} />
    })),
    variant: CheckboxVariant.BOX
  }
}`,...(R=(L=b.parameters)==null?void 0:L.docs)==null?void 0:R.source}}};var A,H,M;h.parameters={...h.parameters,docs:{...(A=h.parameters)==null?void 0:A.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    disabled: true,
    group: ['foo', 'bar', 'baz'].map((item, i) => ({
      label: <span>{item}</span>,
      name: \`checkBoxes.\${item}\`,
      childrenOnChecked: <CheckboxGroup describedBy="parent-name-id" groupName="sub-name" group={[{
        label: 'sub-foo',
        name: \`checkBoxes.sub-foo-\${i}\`
      }, {
        label: 'sub-bar',
        name: \`checkBoxes.sub-bar-\${i}\`
      }]} variant={CheckboxVariant.BOX} inline={i === 0} disabled={true} />
    })),
    variant: CheckboxVariant.BOX,
    groupName: 'checkBoxes',
    legend: 'This is the legend'
  }
}`,...(M=(H=h.parameters)==null?void 0:H.docs)==null?void 0:M.source}}};const ce=["Default","Box","BoxInline","BoxWithChildren","BoxWithCheckboxGroupChildren","BoxWithCheckboxGroupChildrenNoLegend","BoxWithCheckboxGroupChildrenDisabled"];export{c as Box,d as BoxInline,m as BoxWithCheckboxGroupChildren,h as BoxWithCheckboxGroupChildrenDisabled,b as BoxWithCheckboxGroupChildrenNoLegend,p as BoxWithChildren,r as Default,ce as __namedExportsOrder,ue as default};
