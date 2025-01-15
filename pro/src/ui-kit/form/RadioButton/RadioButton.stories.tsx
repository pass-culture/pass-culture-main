import type { StoryObj } from '@storybook/react'
import { Formik } from 'formik'

import logoPassCultureIcon from 'icons/logo-pass-culture.svg'

import { RadioVariant } from '../shared/BaseRadio/BaseRadio'

import { RadioButton } from './RadioButton'

export default {
  title: 'ui-kit/forms/RadioButton',
  component: RadioButton,
  decorators: [
    (Story: any) => (
      <Formik initialValues={{}} onSubmit={() => {}}>
        {({ getFieldProps }) => {
          return <Story {...getFieldProps('gender')} />
        }}
      </Formik>
    ),
  ],
}

export const Default: StoryObj<typeof RadioButton> = {
  args: {
    label: 'Male',
  },
}
export const WithBorder: StoryObj<typeof RadioButton> = {
  args: {
    variant: RadioVariant.BOX,
    label: 'Male',
  },
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
  args: {
    label: <WithImage src={logoPassCultureIcon} />,
  },
}
