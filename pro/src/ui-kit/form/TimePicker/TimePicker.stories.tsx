import type { PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

import { TimePicker } from './TimePicker'
import { Meta, StoryObj } from '@storybook/react-vite'

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

const meta: Meta<typeof TimePicker> = {
  title: '@/ui-kit/forms/TimePicker',
  component: TimePicker,
}

export default meta
type Story = StoryObj<typeof TimePicker>

export const Default: Story = {
  args: {
    label: 'Select an option',
    value: '22:11',
    onChange: () => {
      //    Control changes
    },
  },
}

export const WithinForm: Story = {
  args: {
    label: 'Select a time',
  },
  decorators: [
    (Story) => (
      <Wrapper>
        <Story />
      </Wrapper>
    ),
  ],
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const { register } = useFormContext<{ time: string }>()

    return <TimePicker {...args} {...register('time')} />
  },
}
