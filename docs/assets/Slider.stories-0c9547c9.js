import{j as r}from"./jsx-runtime-4cb93332.js";import{b as o}from"./formik.esm-8d42c991.js";import{S as a}from"./Slider-cc757242.js";import"./index-83a10e79.js";import"./_commonjsHelpers-de833af9.js";const f={title:"ui-kit/forms/Slider",component:a},m=l=>r.jsx(o,{initialValues:{sliderValue:0},onSubmit:()=>{},style:{width:300,height:300},children:r.jsx(a,{fieldName:"sliderValue",scale:"km",...l})}),e=m.bind({});e.args={min:0,max:100,label:"Distance :"};var i,s,t;e.parameters={...e.parameters,docs:{...(i=e.parameters)==null?void 0:i.docs,source:{originalSource:`args => <Formik initialValues={{
  sliderValue: 0
}} onSubmit={() => {}} style={{
  width: 300,
  height: 300
}}>
    <Slider fieldName="sliderValue" scale="km" {...args} />
  </Formik>`,...(t=(s=e.parameters)==null?void 0:s.docs)==null?void 0:t.source}}};const S=["Default"];export{e as Default,S as __namedExportsOrder,f as default};
