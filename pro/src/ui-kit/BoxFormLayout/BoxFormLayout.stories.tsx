import type { StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'

import { FormLayout } from '@/components/FormLayout/FormLayout'
import { BoxRounded } from '@/ui-kit/BoxRounded/BoxRounded'

import { BoxFormLayout, type BoxFormLayoutProps } from './BoxFormLayout'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { ButtonVariant, ButtonColor } from '@/design-system/Button/types';
import { Button } from '@/design-system/Button/Button';

export default {
  title: '@/ui-kit/BoxFormLayout',
  component: BoxFormLayout,
}

const DefaultBoxFormLayout = (args: BoxFormLayoutProps) => {
  const [showForm, setShowForm] = useState(false)

  const methods = useForm({
    defaultValues: { email: '', password: '' },
    mode: 'onChange',
  })

  const {
    handleSubmit,
    formState: { isSubmitting },
  } = methods

  const onSubmit = () => {
    setShowForm(false)
  }

  return (
    <BoxFormLayout {...args}>
      <BoxRounded
        onClickModify={!showForm ? () => setShowForm(true) : undefined}
      >
        {showForm ? (
          <>
            <BoxFormLayout.RequiredMessage />
            <BoxFormLayout.Fields>
              <FormProvider {...methods}>
                <form onSubmit={handleSubmit(onSubmit)}>
                  <FormLayout>
                    <FormLayout.Row>
                      <TextInput
                        label="Nouvelle adresse email"
                        description="Format : email@exemple.com"
                        {...methods.register('email', {
                          required: 'Email is required',
                        })}
                      />
                    </FormLayout.Row>
                    <FormLayout.Row>
                      <TextInput
                        label="Mot de passe (requis pour modifier votre email)"
                        type="password"
                        {...methods.register('password', {
                          required: 'Password is required',
                        })}
                      />
                    </FormLayout.Row>
                  </FormLayout>
                  <div>
                    <Button
                      style={{ marginTop: 24, marginRight: 16 }}
                      onClick={() => setShowForm(false)}
                      variant={ButtonVariant.SECONDARY}
                      color={ButtonColor.NEUTRAL}
                      label="Annuler"
                    />
                    <Button
                      type="submit"
                      style={{ marginTop: 24 }}
                      isLoading={isSubmitting}
                      label="Enregistrer"
                    />
                  </div>
                </form>
              </FormProvider>
            </BoxFormLayout.Fields>
          </>
        ) : (
          <>
            <BoxFormLayout.Header
              subtitle={'Je suis le sous-titre'}
              title="Adresse email"
            />
          </>
        )}
      </BoxRounded>
    </BoxFormLayout>
  )
}

export const Default: StoryObj<typeof BoxFormLayout> = {
  render: () => <DefaultBoxFormLayout />,
}
