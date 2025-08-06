import type { Meta, StoryObj } from '@storybook/react'
import { PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

import { DayCheckbox } from './DayCheckbox'

const meta: Meta<typeof DayCheckbox> = {
  title: '@/ui-kit/formsV2/DayCheckbox',
  component: DayCheckbox,
}

const Wrapper = ({ children }: PropsWithChildren) => {
  const hookForm = useForm<{ myField: boolean }>({
    defaultValues: { myField: true },
  })

  return (
    <FormProvider {...hookForm}>
      <form>{children}</form>
    </FormProvider>
  )
}

export default meta
type Story = StoryObj<typeof DayCheckbox>

export const Default: Story = {
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: true,
    onChange: () => {
      //  Control the result here with e.target.checked
    },
  },
}

export const Disabled: Story = {
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: false,
    disabled: true,
    onChange: () => {
      //  Control the result here with e.target.checked
    },
  },
}

export const WithinAGroupInError: Story = {
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
    name: 'myField',
    checked: false,
    error: 'error',
    displayErrorMessage: false,
    onChange: () => {
      //  Control the result here with e.target.checked
    },
  },
}

export const WithinForm: Story = {
  args: {
    label: 'L',
    tooltipContent: 'Lundi',
  },
  decorators: [
    (Story) => (
      <Wrapper>
        <Story />
      </Wrapper>
    ),
  ],
  render: (args) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const { register } = useFormContext<{ myField: boolean }>()

    return <DayCheckbox {...args} {...register('myField')} />
  },
}
