import{j as n}from"./jsx-runtime-CfatFE5O.js";import{u as A,F as J}from"./formik.esm-DyanDbCL.js";import{B as K,C as o}from"./BaseCheckbox-CAknIdKI.js";import{c as P}from"./index-DeARc5FM.js";import{F as Q}from"./FieldSetLayout-DzzARNTO.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./SvgIcon-CUWb-Ez8.js";import"./FieldError-DblMbt5C.js";import"./stroke-error-DSZD431a.js";const U="_inline_1nmte_7",y={"checkbox-group":"_checkbox-group_1nmte_1",inline:U},v=({setGroupTouched:e,label:a,name:g,hasError:f,icon:x,disabled:k,onChange:c,ariaDescribedBy:B,variant:i,childrenOnChecked:C})=>{const[l]=A({name:g,type:"checkbox"}),s=O=>{e(),l.onChange(O),c&&c(O)};return n.jsx(K,{...l,icon:x,hasError:f,label:a,onChange:s,disabled:k,ariaDescribedBy:B,variant:i,childrenOnChecked:C})};try{v.displayName="CheckboxGroupItem",v.__docgenInfo={description:"",displayName:"CheckboxGroupItem",props:{setGroupTouched:{defaultValue:null,description:"",name:"setGroupTouched",required:!0,type:{name:"() => void"}},name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},icon:{defaultValue:null,description:"",name:"icon",required:!1,type:{name:"string"}},hasError:{defaultValue:null,description:"",name:"hasError",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"((event: ChangeEvent<HTMLInputElement>) => void)"}},ariaDescribedBy:{defaultValue:null,description:"",name:"ariaDescribedBy",required:!1,type:{name:"string"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"box"'}]}},childrenOnChecked:{defaultValue:null,description:"",name:"childrenOnChecked",required:!1,type:{name:"Element"}}}}}catch{}const t=({group:e,groupName:a,legend:g,describedBy:f,disabled:x,isOptional:k,variant:c,inline:B=!1})=>{const[,i,C]=A({name:a}),l=i.touched&&!!i.error;return n.jsx(Q,{error:l?i.error:void 0,legend:g,name:a,ariaDescribedBy:f,isOptional:k,hideFooter:!0,children:n.jsx("div",{className:P(y["checkbox-group"],{[y.inline]:B}),children:e.map(s=>n.jsx("div",{className:y["checkbox-group-item"],children:n.jsx(v,{icon:s.icon,hasError:l,label:s.label,name:s.name,setGroupTouched:()=>i.touched?null:C.setTouched(!0),disabled:x,onChange:s.onChange,...l?{ariaDescribedBy:`error-${a}`}:{},variant:c,childrenOnChecked:s.childrenOnChecked})},s.name))})})};try{t.displayName="CheckboxGroup",t.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"box"'}]}},group:{defaultValue:null,description:"",name:"group",required:!0,type:{name:"{ name: string; label: string; icon?: string | undefined; onChange?: ((event: ChangeEvent<HTMLInputElement>) => void) | undefined; childrenOnChecked?: Element | undefined; }[]"}},inline:{defaultValue:{value:"false"},description:"",name:"inline",required:!1,type:{name:"boolean"}},isOptional:{defaultValue:null,description:"",name:"isOptional",required:!1,type:{name:"boolean"}},groupName:{defaultValue:null,description:"",name:"groupName",required:!0,type:{name:"string"}},legend:{defaultValue:null,description:"",name:"legend",required:!1,type:{name:"string"}},describedBy:{defaultValue:null,description:"",name:"describedBy",required:!1,type:{name:"string"}}}}}catch{}const te={title:"ui-kit/forms/CheckboxGroup",component:t,decorators:[e=>n.jsx(J,{initialValues:{checkBoxes:{foo:!0,bar:!1,baz:!1,"sub-foo-0":!0,"sub-bar-0":!1,"sub-foo-1":!1,"sub-bar-1":!1,"sub-foo-2":!1,"sub-bar-2":!1}},onSubmit:()=>{},children:({getFieldProps:a})=>n.jsx(e,{...a("group")})})]},r={args:{group:["foo","bar","baz"].map(e=>({label:e,name:`checkBoxes.${e}`})),groupName:"checkBoxes",legend:"This is the legend",disabled:!1}},u={args:{...r.args,variant:o.BOX}},d={args:{...r.args,inline:!0,variant:o.BOX}},p={args:{...r.args,group:["foo","bar","baz"].map(e=>({label:e,name:`checkBoxes.${e}`,childrenOnChecked:n.jsxs("span",{children:["Child content for ",e]})})),variant:o.BOX}},m={args:{...r.args,group:["foo","bar","baz"].map((e,a)=>({label:e,name:`checkBoxes.${e}`,childrenOnChecked:n.jsx(t,{legend:"Sub group legend",groupName:"sub-name",group:[{label:"sub-foo",name:`checkBoxes.sub-foo-${a}`},{label:"sub-bar",name:`checkBoxes.sub-bar-${a}`}],variant:o.BOX})})),variant:o.BOX}},b={args:{...r.args,group:["foo","bar","baz"].map((e,a)=>({label:n.jsx("span",{children:e}),name:`checkBoxes.${e}`,childrenOnChecked:n.jsx(t,{describedBy:"parent-name-id",groupName:"sub-name",group:[{label:"sub-foo",name:`checkBoxes.sub-foo-${a}`},{label:"sub-bar",name:`checkBoxes.sub-bar-${a}`}],variant:o.BOX,inline:a===0})})),variant:o.BOX}},h={args:{...r.args,disabled:!0,group:["foo","bar","baz"].map((e,a)=>({label:n.jsx("span",{children:e}),name:`checkBoxes.${e}`,childrenOnChecked:n.jsx(t,{describedBy:"parent-name-id",groupName:"sub-name",group:[{label:"sub-foo",name:`checkBoxes.sub-foo-${a}`},{label:"sub-bar",name:`checkBoxes.sub-bar-${a}`}],variant:o.BOX,inline:a===0,disabled:!0})})),variant:o.BOX,groupName:"checkBoxes",legend:"This is the legend"}};var V,_,$;r.parameters={...r.parameters,docs:{...(V=r.parameters)==null?void 0:V.docs,source:{originalSource:`{
  args: {
    group: ['foo', 'bar', 'baz'].map(item => ({
      label: item,
      name: \`checkBoxes.\${item}\`
    })),
    groupName: 'checkBoxes',
    legend: 'This is the legend',
    disabled: false
  }
}`,...($=(_=r.parameters)==null?void 0:_.docs)==null?void 0:$.source}}};var G,q,N;u.parameters={...u.parameters,docs:{...(G=u.parameters)==null?void 0:G.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    variant: CheckboxVariant.BOX
  }
}`,...(N=(q=u.parameters)==null?void 0:q.docs)==null?void 0:N.source}}};var X,j,D;d.parameters={...d.parameters,docs:{...(X=d.parameters)==null?void 0:X.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    inline: true,
    variant: CheckboxVariant.BOX
  }
}`,...(D=(j=d.parameters)==null?void 0:j.docs)==null?void 0:D.source}}};var z,E,S;p.parameters={...p.parameters,docs:{...(z=p.parameters)==null?void 0:z.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    group: ['foo', 'bar', 'baz'].map(item => ({
      label: item,
      name: \`checkBoxes.\${item}\`,
      childrenOnChecked: <span>Child content for {item}</span>
    })),
    variant: CheckboxVariant.BOX
  }
}`,...(S=(E=p.parameters)==null?void 0:E.docs)==null?void 0:S.source}}};var T,I,W;m.parameters={...m.parameters,docs:{...(T=m.parameters)==null?void 0:T.docs,source:{originalSource:`{
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
}`,...(W=(I=m.parameters)==null?void 0:I.docs)==null?void 0:W.source}}};var F,L,H;b.parameters={...b.parameters,docs:{...(F=b.parameters)==null?void 0:F.docs,source:{originalSource:`{
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
}`,...(H=(L=b.parameters)==null?void 0:L.docs)==null?void 0:H.source}}};var M,R,w;h.parameters={...h.parameters,docs:{...(M=h.parameters)==null?void 0:M.docs,source:{originalSource:`{
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
}`,...(w=(R=h.parameters)==null?void 0:R.docs)==null?void 0:w.source}}};const ce=["Default","Box","BoxInline","BoxWithChildren","BoxWithCheckboxGroupChildren","BoxWithCheckboxGroupChildrenNoLegend","BoxWithCheckboxGroupChildrenDisabled"];export{u as Box,d as BoxInline,m as BoxWithCheckboxGroupChildren,h as BoxWithCheckboxGroupChildrenDisabled,b as BoxWithCheckboxGroupChildrenNoLegend,p as BoxWithChildren,r as Default,ce as __namedExportsOrder,te as default};
