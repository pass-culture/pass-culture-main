import type { Meta, StoryObj } from '@storybook/react'
import { Formik } from 'formik'

import { QuantityInput } from './QuantityInput'

const meta: Meta<typeof QuantityInput> = {
  title: 'ui-kit/forms/QuantityInput',
  component: QuantityInput,
  decorators: [
    (Story: any) => (
      <Formik initialValues={{ quantity: '' }} onSubmit={() => {}}>
        <Story />
      </Formik>
    ),
  ],
}

export default meta
type Story = StoryObj<typeof QuantityInput>

export const Default: Story = {
  args: {},
}
