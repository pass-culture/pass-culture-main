import{j as r}from"./jsx-runtime-BYYWji4R.js";import{u as R,F as w}from"./formik.esm-Dmsc_7od.js";import{c as J}from"./index-DeARc5FM.js";import{F as K}from"./FieldSetLayout-Dccuoj0L.js";import{C as P}from"./Checkbox-Bshzw36k.js";import"./index-ClcD9ViR.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./FieldError-ky1_Lcaw.js";import"./stroke-error-DSZD431a.js";import"./SvgIcon-CyWUmZpn.js";import"./Tag-CkFWeImt.js";import"./full-thumb-up-Bb4kpRpM.js";const Q="_inline_1d5x2_7",B={"checkbox-group":"_checkbox-group_1d5x2_1",inline:Q},y=({setGroupTouched:e,label:a,name:t,hasError:f,icon:d,disabled:x,onChange:u,collapsed:k})=>{const[o]=R({name:t,type:"checkbox"}),C=s=>{e(),o.onChange(s),u&&u(s)};return r.jsx(P,{asset:d?{variant:"icon",src:d}:void 0,hasError:f,label:a,onChange:C,disabled:x,variant:"detailed",display:"fill",collapsed:k,name:t,checked:!!o.checked})};try{y.displayName="CheckboxGroupItem",y.__docgenInfo={description:"",displayName:"CheckboxGroupItem",props:{setGroupTouched:{defaultValue:null,description:"",name:"setGroupTouched",required:!0,type:{name:"() => void"}},name:{defaultValue:null,description:"",name:"name",required:!0,type:{name:"string"}},label:{defaultValue:null,description:"",name:"label",required:!0,type:{name:"string"}},description:{defaultValue:null,description:"",name:"description",required:!1,type:{name:"string"}},icon:{defaultValue:null,description:"",name:"icon",required:!1,type:{name:"string"}},hasError:{defaultValue:null,description:"",name:"hasError",required:!1,type:{name:"boolean"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},onChange:{defaultValue:null,description:"",name:"onChange",required:!1,type:{name:"((event: ChangeEvent<HTMLInputElement>) => void)"}},ariaDescribedBy:{defaultValue:null,description:"",name:"ariaDescribedBy",required:!1,type:{name:"string"}},variant:{defaultValue:null,description:"",name:"variant",required:!1,type:{name:"enum",value:[{value:'"default"'},{value:'"detailed"'}]}},collapsed:{defaultValue:null,description:"",name:"collapsed",required:!1,type:{name:"Element"}}}}}catch{}const i=({group:e,groupName:a,legend:t,describedBy:f,disabled:d,isOptional:x,inline:u=!1,hideAsterisk:k})=>{const[,o,C]=R({name:a}),s=o.touched&&!!o.error;return r.jsx(K,{error:s?o.error:void 0,legend:t,name:a,ariaDescribedBy:f,isOptional:x,hideFooter:!0,hideAsterisk:k,children:r.jsx("div",{className:J(B["checkbox-group"],{[B.inline]:u}),children:e.map(l=>r.jsx("div",{className:B["checkbox-group-item"],children:r.jsx(y,{icon:l.icon,hasError:s,label:l.label,name:l.name,setGroupTouched:()=>o.touched?null:C.setTouched(!0),disabled:d,onChange:l.onChange,...s?{ariaDescribedBy:`error-${a}`}:{},collapsed:l.collapsed})},l.name))})})};try{i.displayName="CheckboxGroup",i.__docgenInfo={description:"",displayName:"CheckboxGroup",props:{groupName:{defaultValue:null,description:"",name:"groupName",required:!0,type:{name:"string"}},legend:{defaultValue:null,description:"",name:"legend",required:!0,type:{name:"ReactNode"}},describedBy:{defaultValue:null,description:"",name:"describedBy",required:!1,type:{name:"string"}},group:{defaultValue:null,description:"",name:"group",required:!0,type:{name:"{ name: string; label: string; icon?: string | undefined; onChange?: ((event: ChangeEvent<HTMLInputElement>) => void) | undefined; collapsed?: Element | undefined; }[]"}},disabled:{defaultValue:null,description:"",name:"disabled",required:!1,type:{name:"boolean"}},isOptional:{defaultValue:null,description:"",name:"isOptional",required:!1,type:{name:"boolean"}},inline:{defaultValue:{value:"false"},description:"",name:"inline",required:!1,type:{name:"boolean"}},hideAsterisk:{defaultValue:null,description:"",name:"hideAsterisk",required:!1,type:{name:"boolean"}}}}}catch{}const te={title:"ui-kit/forms/CheckboxGroup",component:i,decorators:[e=>r.jsx(w,{initialValues:{checkBoxes:{foo:!0,bar:!1,baz:!1,"sub-foo-0":!0,"sub-bar-0":!1,"sub-foo-1":!1,"sub-bar-1":!1,"sub-foo-2":!1,"sub-bar-2":!1}},onSubmit:()=>{},children:({getFieldProps:a})=>r.jsx(e,{...a("group")})})]},n={args:{group:["foo","bar","baz"].map(e=>({label:e,name:`checkBoxes.${e}`})),groupName:"checkBoxes",legend:"This is the legend",disabled:!1}},c={args:{...n.args,variant:"detailed"}},p={args:{...n.args,inline:!0,variant:"detailed"}},m={args:{...n.args,group:["foo","bar","baz"].map(e=>({label:e,name:`checkBoxes.${e}`,childrenOnChecked:r.jsxs("span",{children:["Child content for ",e]})})),variant:"detailed"}},b={args:{...n.args,group:["foo","bar","baz"].map((e,a)=>({label:e,name:`checkBoxes.${e}`,childrenOnChecked:r.jsx(i,{legend:"Sub group legend",groupName:"sub-name",group:[{label:"sub-foo",name:`checkBoxes.sub-foo-${a}`},{label:"sub-bar",name:`checkBoxes.sub-bar-${a}`}]})})),variant:"detailed"}},h={args:{...n.args,group:["foo","bar","baz"].map((e,a)=>({label:r.jsx("span",{children:e}),name:`checkBoxes.${e}`,childrenOnChecked:r.jsx(i,{legend:"Group legend",groupName:"sub-name",group:[{label:"sub-foo",name:`checkBoxes.sub-foo-${a}`},{label:"sub-bar",name:`checkBoxes.sub-bar-${a}`}],inline:a===0})})),variant:"detailed"}},g={args:{...n.args,disabled:!0,group:["foo","bar","baz"].map((e,a)=>({label:r.jsx("span",{children:e}),name:`checkBoxes.${e}`,childrenOnChecked:r.jsx(i,{legend:"Group legend",groupName:"sub-name",group:[{label:"sub-foo",name:`checkBoxes.sub-foo-${a}`},{label:"sub-bar",name:`checkBoxes.sub-bar-${a}`}],inline:a===0,disabled:!0})})),variant:"detailed",groupName:"checkBoxes",legend:"This is the legend"}};var v,_,G;n.parameters={...n.parameters,docs:{...(v=n.parameters)==null?void 0:v.docs,source:{originalSource:`{
  args: {
    group: ['foo', 'bar', 'baz'].map(item => ({
      label: item,
      name: \`checkBoxes.\${item}\`
    })),
    groupName: 'checkBoxes',
    legend: 'This is the legend',
    disabled: false
  }
}`,...(G=(_=n.parameters)==null?void 0:_.docs)==null?void 0:G.source}}};var $,V,q;c.parameters={...c.parameters,docs:{...($=c.parameters)==null?void 0:$.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    variant: 'detailed'
  }
}`,...(q=(V=c.parameters)==null?void 0:V.docs)==null?void 0:q.source}}};var N,j,D;p.parameters={...p.parameters,docs:{...(N=p.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    inline: true,
    variant: 'detailed'
  }
}`,...(D=(j=p.parameters)==null?void 0:j.docs)==null?void 0:D.source}}};var z,E,O;m.parameters={...m.parameters,docs:{...(z=m.parameters)==null?void 0:z.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    group: ['foo', 'bar', 'baz'].map(item => ({
      label: item,
      name: \`checkBoxes.\${item}\`,
      childrenOnChecked: <span>Child content for {item}</span>
    })),
    variant: 'detailed'
  }
}`,...(O=(E=m.parameters)==null?void 0:E.docs)==null?void 0:O.source}}};var S,T,I;b.parameters={...b.parameters,docs:{...(S=b.parameters)==null?void 0:S.docs,source:{originalSource:`{
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
      }]} />
    })),
    variant: 'detailed'
  }
}`,...(I=(T=b.parameters)==null?void 0:T.docs)==null?void 0:I.source}}};var W,F,L;h.parameters={...h.parameters,docs:{...(W=h.parameters)==null?void 0:W.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    group: ['foo', 'bar', 'baz'].map((item, i) => ({
      label: <span>{item}</span>,
      name: \`checkBoxes.\${item}\`,
      childrenOnChecked: <CheckboxGroup legend="Group legend" groupName="sub-name" group={[{
        label: 'sub-foo',
        name: \`checkBoxes.sub-foo-\${i}\`
      }, {
        label: 'sub-bar',
        name: \`checkBoxes.sub-bar-\${i}\`
      }]} inline={i === 0} />
    })),
    variant: 'detailed'
  }
}`,...(L=(F=h.parameters)==null?void 0:F.docs)==null?void 0:L.source}}};var A,H,M;g.parameters={...g.parameters,docs:{...(A=g.parameters)==null?void 0:A.docs,source:{originalSource:`{
  args: {
    ...Default.args,
    disabled: true,
    group: ['foo', 'bar', 'baz'].map((item, i) => ({
      label: <span>{item}</span>,
      name: \`checkBoxes.\${item}\`,
      childrenOnChecked: <CheckboxGroup legend="Group legend" groupName="sub-name" group={[{
        label: 'sub-foo',
        name: \`checkBoxes.sub-foo-\${i}\`
      }, {
        label: 'sub-bar',
        name: \`checkBoxes.sub-bar-\${i}\`
      }]} inline={i === 0} disabled={true} />
    })),
    variant: 'detailed',
    groupName: 'checkBoxes',
    legend: 'This is the legend'
  }
}`,...(M=(H=g.parameters)==null?void 0:H.docs)==null?void 0:M.source}}};const de=["Default","Box","BoxInline","BoxWithChildren","BoxWithCheckboxGroupChildren","BoxWithCheckboxGroupChildrenNoLegend","BoxWithCheckboxGroupChildrenDisabled"];export{c as Box,p as BoxInline,b as BoxWithCheckboxGroupChildren,g as BoxWithCheckboxGroupChildrenDisabled,h as BoxWithCheckboxGroupChildrenNoLegend,m as BoxWithChildren,n as Default,de as __namedExportsOrder,te as default};
