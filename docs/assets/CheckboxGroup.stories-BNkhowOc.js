import{j as n}from"./jsx-runtime-CfatFE5O.js";import{u as w,F as J}from"./formik.esm-DyanDbCL.js";import{B as K,C as s}from"./BaseCheckbox-CAknIdKI.js";import{c as P}from"./index-DeARc5FM.js";import{F as Q}from"./FieldSetLayout-DvEJSbWD.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./SvgIcon-CUWb-Ez8.js";import"./FieldError-DblMbt5C.js";import"./stroke-error-DSZD431a.js";const U="_inline_1nmte_7",v={"checkbox-group":"_checkbox-group_1nmte_1",inline:U},O=({setGroupTouched:e,label:a,name:f,hasError:x,icon:k,disabled:B,onChange:u,ariaDescribedBy:C,variant:y,childrenOnChecked:i})=>{const[c]=w({name:f,type:"checkbox"}),t=o=>{e(),c.onChange(o),u&&u(o)};return n.jsx(K,{...c,icon:k,hasError:x,label:a,onChange:t,disabled:B,ariaDescribedBy:C,variant:y,childrenOnChecked:i})};try{O.displayName="CheckboxGroupItem",O.__docgenInfo={description:"",displayName:"CheckboxGroupItem",props:{setGroupTouched:{defaultValue:null,description:"",name:"setGroupTouched",required:!0,type:{name:"() => void"}},name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},icon:{defaultValue:null,description:"",name:"icon",required:!1,type:{name:"string"}},hasError:{defaultValue:null,description:"",name:"hasError",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"((event: ChangeEvent<HTMLInputElement>) => void)"}},ariaDescribedBy:{defaultValue:null,description:"",name:"ariaDescribedBy",required:!1,type:{name:"string"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"box"'}]}},childrenOnChecked:{defaultValue:null,description:"",name:"childrenOnChecked",required:!1,type:{name:"Element"}}}}}catch{}const l=({group:e,groupName:a,legend:f,describedBy:x,disabled:k,isOptional:B,variant:u,inline:C=!1,hideAsterisk:y})=>{const[,i,c]=w({name:a}),t=i.touched&&!!i.error;return n.jsx(Q,{error:t?i.error:void 0,legend:f,name:a,ariaDescribedBy:x,isOptional:B,hideFooter:!0,hideAsterisk:y,children:n.jsx("div",{className:P(v["checkbox-group"],{[v.inline]:C}),children:e.map(o=>n.jsx("div",{className:v["checkbox-group-item"],children:n.jsx(O,{icon:o.icon,hasError:t,label:o.label,name:o.name,setGroupTouched:()=>i.touched?null:c.setTouched(!0),disabled:k,onChange:o.onChange,...t?{ariaDescribedBy:`error-${a}`}:{},variant:u,childrenOnChecked:o.childrenOnChecked})},o.name))})})};try{l.displayName="CheckboxGroup",l.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"box"'}]}},group:{defaultValue:null,description:"",name:"group",required:!0,type:{name:"{ name: string; label: string; icon?: string | undefined; onChange?: ((event: ChangeEvent<HTMLInputElement>) => void) | undefined; childrenOnChecked?: Element | undefined; }[]"}},inline:{defaultValue:{value:"false"},description:"",name:"inline",required:!1,type:{name:"boolean"}},isOptional:{defaultValue:null,description:"",name:"isOptional",required:!1,type:{name:"boolean"}},hideAsterisk:{defaultValue:null,description:"",name:"hideAsterisk",required:!1,type:{name:"boolean"}},groupName:{defaultValue:null,description:"",name:"groupName",required:!0,type:{name:"string"}},legend:{defaultValue:null,description:"",name:"legend",required:!1,type:{name:"ReactNode"}},describedBy:{defaultValue:null,description:"",name:"describedBy",required:!1,type:{name:"string"}}}}}catch{}const te={title:"ui-kit/forms/CheckboxGroup",component:l,decorators:[e=>n.jsx(J,{initialValues:{checkBoxes:{foo:!0,bar:!1,baz:!1,"sub-foo-0":!0,"sub-bar-0":!1,"sub-foo-1":!1,"sub-bar-1":!1,"sub-foo-2":!1,"sub-bar-2":!1}},onSubmit:()=>{},children:({getFieldProps:a})=>n.jsx(e,{...a("group")})})]},r={args:{group:["foo","bar","baz"].map(e=>({label:e,name:`checkBoxes.${e}`})),groupName:"checkBoxes",legend:"This is the legend",disabled:!1}},d={args:{...r.args,variant:s.BOX}},p={args:{...r.args,inline:!0,variant:s.BOX}},m={args:{...r.args,group:["foo","bar","baz"].map(e=>({label:e,name:`checkBoxes.${e}`,childrenOnChecked:n.jsxs("span",{children:["Child content for ",e]})})),variant:s.BOX}},b={args:{...r.args,group:["foo","bar","baz"].map((e,a)=>({label:e,name:`checkBoxes.${e}`,childrenOnChecked:n.jsx(l,{legend:"Sub group legend",groupName:"sub-name",group:[{label:"sub-foo",name:`checkBoxes.sub-foo-${a}`},{label:"sub-bar",name:`checkBoxes.sub-bar-${a}`}],variant:s.BOX})})),variant:s.BOX}},h={args:{...r.args,group:["foo","bar","baz"].map((e,a)=>({label:n.jsx("span",{children:e}),name:`checkBoxes.${e}`,childrenOnChecked:n.jsx(l,{describedBy:"parent-name-id",groupName:"sub-name",group:[{label:"sub-foo",name:`checkBoxes.sub-foo-${a}`},{label:"sub-bar",name:`checkBoxes.sub-bar-${a}`}],variant:s.BOX,inline:a===0})})),variant:s.BOX}},g={args:{...r.args,disabled:!0,group:["foo","bar","baz"].map((e,a)=>({label:n.jsx("span",{children:e}),name:`checkBoxes.${e}`,childrenOnChecked:n.jsx(l,{describedBy:"parent-name-id",groupName:"sub-name",group:[{label:"sub-foo",name:`checkBoxes.sub-foo-${a}`},{label:"sub-bar",name:`checkBoxes.sub-bar-${a}`}],variant:s.BOX,inline:a===0,disabled:!0})})),variant:s.BOX,groupName:"checkBoxes",legend:"This is the legend"}};var V,_,$;r.parameters={...r.parameters,docs:{...(V=r.parameters)==null?void 0:V.docs,source:{originalSource:`{
  args: {
    group: ['foo', 'bar', 'baz'].map(item => ({
      label: item,
      name: \`checkBoxes.\${item}\`
    })),
    groupName: 'checkBoxes',
    legend: 'This is the legend',
    disabled: false
  }
}`,...($=(_=r.parameters)==null?void 0:_.docs)==null?void 0:$.source}}};var q,G,N;d.parameters={...d.parameters,docs:{...(q=d.parameters)==null?void 0:q.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    variant: CheckboxVariant.BOX
  }
}`,...(N=(G=d.parameters)==null?void 0:G.docs)==null?void 0:N.source}}};var X,j,D;p.parameters={...p.parameters,docs:{...(X=p.parameters)==null?void 0:X.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    inline: true,
    variant: CheckboxVariant.BOX
  }
}`,...(D=(j=p.parameters)==null?void 0:j.docs)==null?void 0:D.source}}};var z,E,S;m.parameters={...m.parameters,docs:{...(z=m.parameters)==null?void 0:z.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    group: ['foo', 'bar', 'baz'].map(item => ({
      label: item,
      name: \`checkBoxes.\${item}\`,
      childrenOnChecked: <span>Child content for {item}</span>
    })),
    variant: CheckboxVariant.BOX
  }
}`,...(S=(E=m.parameters)==null?void 0:E.docs)==null?void 0:S.source}}};var T,I,W;b.parameters={...b.parameters,docs:{...(T=b.parameters)==null?void 0:T.docs,source:{originalSource:`{
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
}`,...(W=(I=b.parameters)==null?void 0:I.docs)==null?void 0:W.source}}};var F,L,A;h.parameters={...h.parameters,docs:{...(F=h.parameters)==null?void 0:F.docs,source:{originalSource:`{
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
}`,...(A=(L=h.parameters)==null?void 0:L.docs)==null?void 0:A.source}}};var H,M,R;g.parameters={...g.parameters,docs:{...(H=g.parameters)==null?void 0:H.docs,source:{originalSource:`{
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
}`,...(R=(M=g.parameters)==null?void 0:M.docs)==null?void 0:R.source}}};const ue=["Default","Box","BoxInline","BoxWithChildren","BoxWithCheckboxGroupChildren","BoxWithCheckboxGroupChildrenNoLegend","BoxWithCheckboxGroupChildrenDisabled"];export{d as Box,p as BoxInline,b as BoxWithCheckboxGroupChildren,g as BoxWithCheckboxGroupChildrenDisabled,h as BoxWithCheckboxGroupChildrenNoLegend,m as BoxWithChildren,r as Default,ue as __namedExportsOrder,te as default};
