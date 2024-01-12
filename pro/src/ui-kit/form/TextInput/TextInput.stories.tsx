import type { StoryObj } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import strokeSearch from 'icons/stroke-search.svg'

import TextInput from './TextInput'

export default {
  title: 'ui-kit/forms/TextInput',
  component: TextInput,
  decorators: [
    (Story: any) => (
      <Formik initialValues={{ email: '' }} onSubmit={() => {}}>
        <Story />
      </Formik>
    ),
  ],
}

export const WithoutLabel: StoryObj<typeof TextInput> = {
  args: {
    name: 'email',
    placeholder: 'Input placeholder',
  },
}

export const WithLabel: StoryObj<typeof TextInput> = {
  args: {
    name: 'email',
    label: 'Email',
    placeholder: 'Input placeholder',
  },
}

export const WithLeftIcon: StoryObj<typeof TextInput> = {
  args: {
    name: 'email',
    label: 'Email',
    placeholder: 'Input placeholder',
    leftIcon: strokeSearch,
  },
}
