import { StoryObj } from '@storybook/react'
import { useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { BoxRounded } from 'ui-kit/BoxRounded/BoxRounded'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import { BoxFormLayout, BoxFormLayoutProps } from './BoxFormLayout'

export default {
  title: 'ui-kit/BoxFormLayout',
  component: BoxFormLayout,
}

const DefaultBoxFormLayout = (args: BoxFormLayoutProps) => {
  const [showForm, setShowForm] = useState(false)

  // Use useForm to initialize form state and handle submission
  const methods = useForm({
    defaultValues: { email: '', password: '' },
    mode: 'onChange', // or 'onBlur', based on your validation strategy
  })

  const {
    handleSubmit,
    formState: { isSubmitting },
  } = methods

  const onSubmit = (data: { email: string; password: string }) => {
    console.log(data) // Handle form submission logic
    setShowForm(false) // Hide form after submission
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
                        // Register input field with React Hook Form
                        {...methods.register('email', {
                          required: 'Email is required',
                        })}
                      />
                    </FormLayout.Row>
                    <FormLayout.Row>
                      <TextInput
                        label="Mot de passe (requis pour modifier votre email)"
                        type="password"
                        // Register input field with React Hook Form
                        {...methods.register('password', {
                          required: 'Password is required',
                        })}
                      />
                    </FormLayout.Row>
                  </FormLayout>
                  <div>
                    <Button
                      style={{ marginTop: 24, marginRight: 24 }}
                      onClick={() => setShowForm(false)}
                      variant={ButtonVariant.SECONDARY}
                    >
                      Annuler
                    </Button>
                    <Button type="submit" isLoading={isSubmitting}>
                      Enregistrer
                    </Button>
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
