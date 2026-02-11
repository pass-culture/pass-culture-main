import type { StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'

import { FormLayout } from '@/components/FormLayout/FormLayout'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { Panel, PanelProps } from './Panel'

export default {
  title: '@/ui-kit/Panel',
  component: Panel,
}

const DefaultPanel = (args: PanelProps) => {
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
    <Panel {...args}>
        {showForm ? (
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
                      onClick={() => setShowForm(false)}
                      variant={ButtonVariant.SECONDARY}
                      color={ButtonColor.NEUTRAL}
                      label="Annuler"
                    />
                    <Button
                      type="submit"
                      isLoading={isSubmitting}
                      label="Enregistrer"
                    />
                  </div>
                </form>
              </FormProvider>
        ) : (
          <>
            <Panel.Header
              subtitle={'Je suis le sous-titre'}
              title="Adresse email"
              onClickModify={() => setShowForm(true) }
            />
          </>
        )}
    </Panel>
  )
}

export const Default: StoryObj<typeof Panel> = {
  render: () => <DefaultPanel />,
}
