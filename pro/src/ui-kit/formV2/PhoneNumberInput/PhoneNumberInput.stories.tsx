import { yupResolver } from '@hookform/resolvers/yup'
import type { Meta, StoryObj } from '@storybook/react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'
import * as yup from 'yup'

import { isPhoneValid } from 'commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'

import { PhoneNumberInput } from './PhoneNumberInput'

// <FormWrapper> provides a react-hook-form context, which is necessary for the storybook demo with error to work
type WrapperFormValues = { phone: string }
const FormWrapper = ({ children }: { children: React.ReactNode }) => {
  const hookForm = useForm<WrapperFormValues>({
    defaultValues: { phone: '+33612345678' },
    resolver: yupResolver(
      yup.object().shape({
        phone: yup.string().required().test({
          name: 'is-phone-valid',
          message: 'Veuillez entrer un numéro de téléphone valide',
          test: isPhoneValid,
        }),
      })
    ),
    mode: 'onTouched',
  })

  return <FormProvider {...hookForm}>{children}</FormProvider>
}

const meta: Meta<typeof PhoneNumberInput> = {
  title: 'ui-kit/formsV2/PhoneNumberInput',
  component: PhoneNumberInput,

  decorators: [
    (Story: any) => (
      <FormWrapper>
        <Story />
      </FormWrapper>
    ),
  ],
}

export default meta

type Story = StoryObj<typeof PhoneNumberInput>

const demoStyles = {
  wrapper: {
    color: '#666',
    fontSize: '0.8rem',
    padding: '0 1rem',
    backgroundColor: '#f5f5f5',
    borderRadius: '0.2rem',
    border: 'thin solid #e1e1e1',
  },
  pre: { display: 'inline-block', padding: '0.5rem' },
}

export const Default: Story = {
  args: {
    name: 'phone',
    label: 'Custom label for my required field (with validation)',
  },
  render: (args) => {
    const {
      register,
      watch,
      formState: { errors },
      // eslint-disable-next-line react-hooks/rules-of-hooks
    } = useFormContext<WrapperFormValues>()

    const phoneNumber = watch('phone')

    return (
      <>
        <PhoneNumberInput
          {...args}
          {...register('phone')}
          required={true}
          error={errors.phone?.message}
        />
        <div style={demoStyles['wrapper']}>
          RAW value: <pre style={demoStyles['pre']}>{phoneNumber}</pre>
        </div>
      </>
    )
  },
}

export const WithOptional: Story = {
  args: {
    name: 'phone',
    label: 'Phone number input optional',
    required: false,
  },
}

export const InErrorState: Story = {
  args: {
    name: 'phone',
    label: 'Custom label in forced error state',
    error: 'Ce champs comporte une erreur',
  },
}
