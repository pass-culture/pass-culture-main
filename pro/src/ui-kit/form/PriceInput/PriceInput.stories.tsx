import type { Meta, StoryObj } from '@storybook/react'

import { PriceInput } from './PriceInput'
import { PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

const Wrapper = ({ children }: PropsWithChildren) => {
  const hookForm = useForm<{ price?: number }>({
    defaultValues: { price: 100 },
  })

  return (
    <FormProvider {...hookForm}>
      <form>{children}</form>
    </FormProvider>
  )
}

const meta: Meta<typeof PriceInput> = {
  title: '@/ui-kit/forms/PriceInput',
  component: PriceInput,
}

export default meta
type Story = StoryObj<typeof PriceInput>

export const Default: Story = {
  args: {
    name: 'price',
    label: 'Prix',
  },
}

export const WithCheckbox: Story = {
  args: {
    name: 'price',
    label: 'Prix',
    showFreeCheckbox: true,
  },
}

export const WithinForm: Story = {
  args: {
    name: 'price',
    label: 'Prix',
    currency: 'EUR'
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
    const { setValue, watch } = useFormContext<{ price?: number }>()

    return (
      <PriceInput
        {...args}
        value={watch('price')}
        onChange={(e) => {
          setValue(
            'price',
            e.target.value ? Number(e.target.value) : undefined
          )
        }}
       />
    )
  },
}
