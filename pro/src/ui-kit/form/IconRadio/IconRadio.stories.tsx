import type { Meta, StoryObj } from '@storybook/react'
import { PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

import { IconRadio } from './IconRadio'

const meta: Meta<typeof IconRadio> = {
  title: 'ui-kit/formsV2/IconRadio',
  component: IconRadio,
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
type Story = StoryObj<typeof IconRadio>

export const Default: Story = {
  args: {
    label: 'Radio input',
    name: 'myField',
    icon: 'A',
    checked: false,
    onChange: () => {
      //  Control the result here with e.target.checked
    },
  },
  decorators: [
    (Story) => {
      return (
        <div style={{ padding: '2rem' }}>
          <Story />
        </div>
      )
    },
  ],
}

export const WithinForm: Story = {
  args: {
    label: 'Radio input',
    name: 'myField',
    icon: 'B',
  },
  decorators: [
    (Story) => (
      <div style={{ padding: '2rem' }}>
        <Wrapper>
          <Story />
        </Wrapper>
      </div>
    ),
  ],
  render: (args) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const { register } = useFormContext<{ myField: boolean }>()

    return <IconRadio {...args} {...register('myField')} />
  },
}
