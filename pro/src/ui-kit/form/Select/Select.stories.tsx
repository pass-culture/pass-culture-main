import { StoryObj } from '@storybook/react'
import { Formik } from 'formik'

import { Select } from './Select'

export default {
  title: 'ui-kit/forms/Select',
  component: Select,
}

const mockCategoriesOptions = [
  { value: 'cinema', label: 'Cinéma' },
  { value: 'theatre', label: 'Théatre' },
  { value: 'musique', label: 'Musique' },
]

export const Default: StoryObj<typeof Select> = {
  args: {
    label: 'Catégorie',
    options: mockCategoriesOptions,
    disabled: false,
    name: 'select',
  },
  decorators: [
    (Story) => (
      <Formik initialValues={{ category: 'theatre' }} onSubmit={() => {}}>
        <Story />
      </Formik>
    ),
  ],
}

export const SelectInline: StoryObj<typeof Select> = {
  args: {
    label: 'Catégorie',
    options: mockCategoriesOptions,
    disabled: false,
    name: 'select',
    description: 'super select inline',
  },
  decorators: [
    (Story) => (
      <Formik initialValues={{ category: 'theatre' }} onSubmit={() => {}}>
        <Story />
      </Formik>
    ),
  ],
}
