import type { StoryObj } from '@storybook/react'
import { Formik } from 'formik'

import { TextArea } from './TextArea'

export default {
  title: 'ui-kit/forms/TextArea',
  component: TextArea,
  decorators: [
    (Story: any) => (
      <Formik initialValues={{ description: '' }} onSubmit={() => {}}>
        <Story />
      </Formik>
    ),
  ],
}

export const WithoutLabel: StoryObj<typeof TextArea> = {
  args: {
    name: 'description',
  },
}

export const WithLabel: StoryObj<typeof TextArea> = {
  args: {
    name: 'description',
    label: 'Description',
  },
}
