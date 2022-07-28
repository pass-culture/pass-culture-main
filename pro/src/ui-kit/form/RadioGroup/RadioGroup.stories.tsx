import { action } from '@storybook/addon-actions'
import { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import RadioGroup, { Direction, IRadioGroupProps } from './RadioGroup'

export default {
  title: 'ui-kit/forms/RadioGroup',
  component: RadioGroup,
}
const args = {
  name: 'question',
  legend: 'This is the legend',
  direction: Direction.VERTICAL,
  group: [
    {
      label: 'Oui',
      value: `question1`,
    },
    {
      label: 'Non',
      value: `question2`,
    },
  ],
  withBorder: false,
}

const Template: Story<IRadioGroupProps> = ({
  direction,
  name,
  group,
  legend,
  withBorder,
}) => (
  <Formik
    initialValues={{
      question: {},
    }}
    onSubmit={action('onSubmit')}
  >
    {({ getFieldProps }) => {
      return (
        <RadioGroup
          {...getFieldProps('group')}
          direction={direction}
          group={group}
          name={name}
          legend={legend}
          withBorder={withBorder}
        />
      )
    }}
  </Formik>
)

export const Default = Template.bind({})
Default.args = args

export const WithBorder = Template.bind({})
WithBorder.args = {
  ...args,
  withBorder: true,
}

export const Horizontal = Template.bind({})
Horizontal.args = {
  ...args,
  direction: Direction.HORIZONTAL,
}
