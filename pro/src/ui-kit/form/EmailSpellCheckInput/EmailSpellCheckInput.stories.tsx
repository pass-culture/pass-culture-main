import type { Meta, StoryObj } from '@storybook/react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

import { EmailSpellCheckInput } from './EmailSpellCheckInput'

// <FormWrapper> provides a react-hook-form context, which is necessary for the storybook demo to work
type WrapperFormValues = { email: string }
const FormWrapper = ({ children }: { children: React.ReactNode }) => {
  const hookForm = useForm<WrapperFormValues>({
    defaultValues: { email: 'jmclery@htomil.com' },
  })

  return <FormProvider {...hookForm}>{children}</FormProvider>
}

const meta: Meta<typeof EmailSpellCheckInput> = {
  title: '@/ui-kit/formsV2/EmailSpellCheckInput',
  component: EmailSpellCheckInput,

  decorators: [
    (Story: any) => (
      <FormWrapper>
        <Story />
      </FormWrapper>
    ),
  ],
}

export default meta

type Story = StoryObj<typeof EmailSpellCheckInput>

export const Default: Story = {
  args: {
    name: 'email',
    label: 'Adresse email',
    description: 'Format: email@exemple.com',
    error: '',
    required: true,
    asterisk: true,
  },
  render: (args) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const { setValue, register } = useFormContext<WrapperFormValues>()

    return (
      <EmailSpellCheckInput
        {...args}
        {...register('email')}
        onApplyTip={(tip) => {
          setValue('email', tip)
        }}
      />
    )
  },
}
