import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-BwUy_YRU.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{n as r,r as i}from"./date-BBMTuGfi.js";import{t as a}from"./format-DS6Afluf.js";import{t as o}from"./classnames-MYlGWOUq.js";import{t as s}from"./FieldFooter-Q7MR6086.js";import{a as c,o as l,t as u}from"./index.esm-D7-yi9AW.js";var d=e(t(),1),f=e(o(),1),p={"date-picker":`_date-picker_ogfoh_2`,"has-error":`_has-error_ogfoh_47`},m=n(),h=(0,d.forwardRef)(({className:e,maxDate:t,minDate:n,id:o,hasError:s,...c},l)=>(0,m.jsx)(`input`,{type:`date`,min:i(n)?a(n,r):void 0,max:i(t)?a(t,r):`2050-01-01`,id:o,ref:l,className:(0,f.default)(e,p[`date-picker`],{[p[`has-error`]]:s}),...c}));h.displayName=`BaseDatePicker`;try{h.displayName=`BaseDatePicker`,h.__docgenInfo={description:``,displayName:`BaseDatePicker`,props:{maxDate:{defaultValue:null,description:``,name:`maxDate`,required:!1,type:{name:`Date`}},minDate:{defaultValue:null,description:``,name:`minDate`,required:!1,type:{name:`Date`}},value:{defaultValue:null,description:``,name:`value`,required:!1,type:{name:`string`}},hasError:{defaultValue:null,description:``,name:`hasError`,required:!1,type:{name:`boolean`}}}}}catch{}var g={label:`_label_243fh_1`},_=d.forwardRef(({error:e,disabled:t,maxDate:n,minDate:r,onChange:i,required:a,onBlur:o,name:c,value:l,label:u,requiredIndicator:f=`symbol`,className:p},_)=>{let v=(0,d.useId)(),y=(0,d.useId)();return(0,m.jsxs)(`div`,{className:p,children:[(0,m.jsxs)(`div`,{children:[(0,m.jsxs)(`label`,{htmlFor:v,className:g.label,children:[u,a&&f===`symbol`?(0,m.jsx)(m.Fragment,{children:`\xA0*`}):``]}),(0,m.jsx)(h,{"data-testid":c,name:c,id:v,hasError:!!e,disabled:t,maxDate:n,minDate:r,onChange:i,"aria-required":a,onBlur:o,value:l,"aria-describedby":e?y:void 0,ref:_})]}),(0,m.jsx)(s,{error:e,errorId:y})]})});_.displayName=`DatePicker`;try{_.displayName=`DatePicker`,_.__docgenInfo={description:``,displayName:`DatePicker`,props:{disabled:{defaultValue:null,description:``,name:`disabled`,required:!1,type:{name:`boolean`}},required:{defaultValue:null,description:``,name:`required`,required:!1,type:{name:`boolean`}},maxDate:{defaultValue:null,description:``,name:`maxDate`,required:!1,type:{name:`Date`}},name:{defaultValue:null,description:`Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error`,name:`name`,required:!0,type:{name:`string`}},label:{defaultValue:null,description:``,name:`label`,required:!0,type:{name:`ReactNode`}},minDate:{defaultValue:null,description:``,name:`minDate`,required:!1,type:{name:`Date`}},onChange:{defaultValue:null,description:``,name:`onChange`,required:!1,type:{name:`ChangeEventHandler<HTMLInputElement, HTMLInputElement>`}},onBlur:{defaultValue:null,description:``,name:`onBlur`,required:!1,type:{name:`FocusEventHandler<HTMLInputElement>`}},requiredIndicator:{defaultValue:{value:`symbol`},description:`What type of required indicator is displayed`,name:`requiredIndicator`,required:!1,type:{name:`enum`,value:[{value:`"symbol"`},{value:`"hidden"`},{value:`"explicit"`}]}},error:{defaultValue:null,description:``,name:`error`,required:!1,type:{name:`string`}},value:{defaultValue:null,description:``,name:`value`,required:!1,type:{name:`string`}},className:{defaultValue:null,description:``,name:`className`,required:!1,type:{name:`string`}}}}}catch{}var v=({children:e})=>(0,m.jsx)(u,{...c({defaultValues:{group:`option1`}}),children:(0,m.jsx)(`form`,{children:e})}),y={title:`@/ui-kit/forms/DatePicker`,component:_},b={args:{name:`date`,label:`Date`,value:`2025-11-22`,onChange:()=>{}}},x={args:{label:`Date`},decorators:[e=>(0,m.jsx)(v,{children:(0,m.jsx)(e,{})})],render:e=>{let{register:t}=l();return(0,m.jsx)(_,{...e,...t(`date`)})}};b.parameters={...b.parameters,docs:{...b.parameters?.docs,source:{originalSource:`{
  args: {
    name: 'date',
    label: 'Date',
    value: '2025-11-22',
    onChange: () => {
      //    Control changes
    }
  }
}`,...b.parameters?.docs?.source}}},x.parameters={...x.parameters,docs:{...x.parameters?.docs,source:{originalSource:`{
  args: {
    label: 'Date'
  },
  decorators: [(Story: any) => <Wrapper>
        <Story />
      </Wrapper>],
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const {
      register
    } = useFormContext<{
      date: string;
    }>();
    return <DatePicker {...args} {...register('date')} />;
  }
}`,...x.parameters?.docs?.source}}};var S=[`Default`,`WithinForm`];export{b as Default,x as WithinForm,S as __namedExportsOrder,y as default};