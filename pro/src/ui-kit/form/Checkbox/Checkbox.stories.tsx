import type { StoryObj } from '@storybook/react'
import { Formik } from 'formik'

import { Checkbox } from './Checkbox'

export default {
  title: 'ui-kit/forms/Checkbox',
  component: Checkbox,
  decorators: [
    (Story: any) => (
      <Formik initialValues={{ accessibility: false }} onSubmit={() => {}}>
        {({ getFieldProps }) => {
          return <Story {...getFieldProps('accessibility')} />
        }}
      </Formik>
    ),
  ],
}

export const Default: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Accessible',
    name: 'accessibility',
    value: 'accessible',
  },
}
