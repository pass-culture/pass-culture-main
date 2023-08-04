import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import Slider from './Slider'

export default {
  title: 'ui-kit/forms/Slider',
  component: Slider,
}
const Template: Story = args => (
  <Formik
    initialValues={{ sliderValue: 0 }}
    onSubmit={() => {}}
    style={{ width: 300, height: 300 }}
  >
    <Slider fieldName="sliderValue" scale="km" {...args} />
  </Formik>
)

export const Default = Template.bind({})
Default.args = {
  min: 0,
  max: 100,
  label: 'Distance :',
}
