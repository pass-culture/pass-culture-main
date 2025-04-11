import type { Meta, ReactRenderer, StoryObj } from '@storybook/react'
import { PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'
import { PartialStoryFn } from 'storybook/internal/types'

import logoPassCultureIcon from 'icons/logo-pass-culture.svg'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'

import { RadioButton, RadioButtonProps } from './RadioButton'

const meta: Meta<typeof RadioButton> = {
  title: 'ui-kit/formsV2/RadioButton',
  component: RadioButton,
}

const demoStyles = {
  wrapper: {
    color: '#666',
    fontSize: '0.8rem',
    padding: '0 1rem',
    backgroundColor: '#f5f5f5',
    borderRadius: '0.2rem',
    border: 'thin solid #e1e1e1',
    marginTop: '1rem',
  },
  pre: { display: 'inline-block', padding: '0.5rem' },
  link: { textDecoration: 'underline' },
}

const Wrapper = ({ children }: PropsWithChildren) => {
  const hookForm = useForm<{ gender: string }>({
    defaultValues: { gender: '' },
  })

  const { reset, watch } = hookForm

  const genderValue = watch('gender')

  return (
    <FormProvider {...hookForm}>
      <form>{children}</form>
      <div style={demoStyles['wrapper']}>
        RAW value: <pre style={demoStyles['pre']}>{genderValue}</pre>
        {genderValue && (
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault()
              reset()
            }}
            style={demoStyles['link']}
          >
            (Reset value)
          </a>
        )}
      </div>
    </FormProvider>
  )
}

export default meta

const WithinFormDecorator = (
  Story: PartialStoryFn<ReactRenderer, RadioButtonProps>
) => (
  <Wrapper>
    <Story />
  </Wrapper>
)

const renderFx = (
  args: RadioButtonProps & React.RefAttributes<HTMLInputElement>
) => {
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const { register } = useFormContext<{ gender: string }>()

  return <RadioButton {...args} {...register('gender')} />
}

export const Default: StoryObj<typeof RadioButton> = {
  decorators: [WithinFormDecorator],
  args: {
    label: 'Male',
    value: 'M',
  },
  render: renderFx,
}
export const WithBorder: StoryObj<typeof RadioButton> = {
  decorators: [WithinFormDecorator],
  args: {
    variant: RadioVariant.BOX,
    label: 'Male',
    value: 'M',
  },
  render: renderFx,
}

const WithImage = ({ src }: { src: string }) => (
  <div style={{ display: 'flex', gap: '1rem' }}>
    <img src={src} width={100} />
    <p style={{ display: 'flex', flexDirection: 'column' }}>
      <strong>Long titre lorem ipsum mon offre</strong>
      Test de sous-titre
    </p>
  </div>
)

export const WithChildren: StoryObj<typeof RadioButton> = {
  decorators: [WithinFormDecorator],
  args: {
    label: <WithImage src={logoPassCultureIcon} />,
    value: 'Long titre',
  },
  render: renderFx,
}
