import type { Meta, StoryObj } from '@storybook/react'
import { PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

import { QuantityInput } from './QuantityInput'

const Wrapper = ({ children }: PropsWithChildren) => {
  const hookForm = useForm<{ myField?: number }>({
    defaultValues: { myField: 100 },
  })

  return (
    <FormProvider {...hookForm}>
      <form>{children}</form>
    </FormProvider>
  )
}

const meta: Meta<typeof QuantityInput> = {
  title: '@/ui-kit/formsV2/QuantityInput',
  component: QuantityInput,
}

export default meta
type Story = StoryObj<typeof QuantityInput>

export const Default: Story = {
  args: {
    name: 'quantity',
    label: 'Quantité',
  },
}

export const SmallLabel: Story = {
  args: {
    name: 'quantity',
    label: 'Quantité',
    smallLabel: true,
  },
}

export const Required: Story = {
  args: {
    name: 'quantity',
    label: 'Quantité',
    required: true,
  },
}

export const WithinForm: Story = {
  args: {
    name: 'quantity',
    label: 'Quantity',
    minimum: 10,
  },
  decorators: [
    (Story: any) => (
      <Wrapper>
        <Story />
      </Wrapper>
    ),
  ],
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const { setValue, watch } = useFormContext<{ myField?: number }>()

    return (
      <QuantityInput
        {...args}
        value={watch('myField')}
        onChange={(e) => {
          setValue(
            'myField',
            e.target.value ? Number(e.target.value) : undefined
          )
        }}
      ></QuantityInput>
    )
  },
}
