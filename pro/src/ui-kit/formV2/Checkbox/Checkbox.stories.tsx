import type { Meta, StoryObj } from '@storybook/react'
import { PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

import { Checkbox } from './Checkbox'

const meta: Meta<typeof Checkbox> = {
  title: 'ui-kit/formsV2/Checkbox',
  component: Checkbox,
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
type Story = StoryObj<typeof Checkbox>

export const Default: Story = {
  args: {
    label: 'Accessible',
    name: 'accessibility',
    checked: true,
    onChange: () => {
      //  Control the result here with e.target.checked
    },
  },
}

export const WithinForm: Story = {
  args: {
    label: 'Accessible',
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

    return <Checkbox {...args} {...register('myField')} />
  },
}
