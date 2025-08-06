import { Meta, StoryObj } from '@storybook/react/*'
import { PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

import { Select } from './Select'

const Wrapper = ({ children }: PropsWithChildren) => {
  const hookForm = useForm<{ group: string }>({
    defaultValues: { group: 'option1' },
  })

  return (
    <FormProvider {...hookForm}>
      <form>{children}</form>
    </FormProvider>
  )
}

const meta: Meta<typeof Select> = {
  title: '@/ui-kit/formsV2/Select',
  component: Select,
}

export default meta
type Story = StoryObj<typeof Select>

export const Default: Story = {
  args: {
    label: 'Select an option',
    options: [
      { label: 'option 1', value: 'option1' },
      { label: 'option 2', value: 'option2' },
    ],
    value: 'option1',
    onChange: () => {
      //    Control changes
    },
  },
}

export const WithinForm: Story = {
  args: {
    label: 'Select an option',
    options: [
      { label: 'option 1', value: 'option1' },
      { label: 'option 2', value: 'option2' },
    ],
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
    const { register } = useFormContext<{ option: string }>()

    return <Select {...args} {...register('option')} />
  },
}
