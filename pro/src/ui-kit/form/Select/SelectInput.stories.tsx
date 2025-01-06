import { StoryObj } from '@storybook/react'
import { Formik } from 'formik'

import { SelectInput } from './SelectInput'

export default {
  title: 'ui-kit/forms/SelectInput',
  component: SelectInput,
}

const mockCategoriesOptions = [
  { value: 'cinema', label: 'Cinéma' },
  { value: 'theatre', label: 'Théatre' },
  { value: 'musique', label: 'Musique' },
]

export const Default: StoryObj<typeof SelectInput> = {
  args: {
    name: 'select',
    hasError: false,
    options: mockCategoriesOptions,
    disabled: false,
  },
}

export const SelectInputFilter: StoryObj<typeof SelectInput> = {
  args: {
    name: 'select',
    options: mockCategoriesOptions,
    filterVariant: true,
  },
  decorators: [
    (Story) => (
      <Formik initialValues={{ category: 'theatre' }} onSubmit={() => {}}>
        <Story />
      </Formik>
    ),
  ],
}
