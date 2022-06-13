import { Formik } from 'formik'
import RadioGroup from './RadioGroup'
import React from 'react'
import { Story } from '@storybook/react'
import { action } from '@storybook/addon-actions'
export default {
  title: 'ui-kit/forms/RadioGroup',
  component: RadioGroup,
}

const Template: Story<{ withBorder: boolean }> = ({ withBorder = false }) => (
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
          group={[
            {
              label: 'Oui',
              value: `question1`,
            },
            {
              label: 'Non',
              value: `question2`,
            },
          ]}
          name="question"
          legend="This is the legend"
          withBorder={withBorder}
        />
      )
    }}
  </Formik>
)

export const Default = Template.bind({})

export const WithBorder = Template.bind({})
WithBorder.args = { withBorder: true }
