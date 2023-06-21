import { action } from '@storybook/addon-actions'
import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import RadioButton from './RadioButton'

export default {
  title: 'ui-kit/forms/RadioButton',
  component: RadioButton,
}

const Template: Story<{
  label1: JSX.Element | string
  label2: JSX.Element | string
  withBorder?: boolean
}> = ({ withBorder, label1, label2 }) => (
  <Formik initialValues={{}} onSubmit={action('onSubmit')}>
    {({ getFieldProps }) => {
      return (
        <>
          <RadioButton
            {...getFieldProps('gender')}
            label={label1}
            name="gender"
            value="male"
            withBorder={withBorder}
          />
          <RadioButton
            {...getFieldProps('gender')}
            label={label2}
            name="gender"
            value="female"
            withBorder={withBorder}
          />
        </>
      )
    }}
  </Formik>
)

export const Default = Template.bind({})
Default.args = {
  label1: 'Male',
  label2: 'Female',
}

export const WithBorder = Template.bind({})
WithBorder.args = {
  withBorder: true,
  label1: 'Male',
  label2: 'Female',
}

const WithImage = ({ src }: { src: string }) => (
  <div style={{ display: 'flex', gap: '1rem' }}>
    <img src={src} width={100} />
    <p style={{ display: 'flex', flexDirection: 'column' }}>
      <strong>Long titre lorem ipsum mon offre</strong>
      Test de sous-titre
    </p>
  </div>
)

export const WithChildren = Template.bind({})
WithChildren.args = {
  label1: <WithImage src="/icons/logo-pass-culture-dark.svg" />,
  label2: <WithImage src="/icons/logo-pass-culture.svg" />,
}
