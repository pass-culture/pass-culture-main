import { Meta, StoryObj } from '@storybook/react/*'
import { PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

import { DatePicker } from './DatePicker'

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

const meta: Meta<typeof DatePicker> = {
  title: 'ui-kit/formsV2/DatePicker',
  component: DatePicker,
}

export default meta
type Story = StoryObj<typeof DatePicker>

export const Default: Story = {
  args: {
    name: 'date',
    label: 'Date',
    value: '2025-11-22',
    onChange: () => {
      //    Control changes
    },
  },
}

export const WithinForm: Story = {
  args: {
    label: 'Date',
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
    const { register } = useFormContext<{ date: string }>()

    return <DatePicker {...args} {...register('date')} />
  },
}
