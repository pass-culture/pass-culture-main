import { action } from '@storybook/addon-actions'
import type { Story } from '@storybook/react'
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

export const WithDescription = Template.bind({})
WithDescription.args = {
  ...args,
  group: [
    {
      label: 'Oui',
      description:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
      value: `question1`,
    },
    {
      label: 'Non',
      description: "Vous n'etes pas d'accord.",
      value: `question2`,
    },
  ],
}

export const WithBorderAndDescription = Template.bind({})
WithBorderAndDescription.args = {
  ...args,
  withBorder: true,
  group: [
    {
      label: 'Oui',
      description:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
      value: `question1`,
    },
    {
      label: 'Non',
      description: "Vous n'etes pas d'accord.",
      value: `question2`,
    },
  ],
}

export const Horizontal = Template.bind({})
Horizontal.args = {
  ...args,
  direction: Direction.HORIZONTAL,
}
