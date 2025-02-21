import type { StoryObj } from '@storybook/react'
import { Form, FormikProvider, useFormik } from 'formik'
import { useState } from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { BoxRounded } from 'ui-kit/BoxRounded/BoxRounded'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { BoxFormLayout, BoxFormLayoutProps } from './BoxFormLayout'

export default {
  title: 'ui-kit/BoxFormLayout',
  component: BoxFormLayout,
}

const DefaultBoxFormLayout = (args: BoxFormLayoutProps) => {
  const [showForm, setShowForm] = useState(false)
  const formik = useFormik({
    initialValues: { email: '', password: '' },
    onSubmit: () => {
      formik.setSubmitting(false)
      setShowForm(false)
    },
    validateOnChange: false,
  })
  return (
    <BoxFormLayout {...args}>
      <BoxRounded
        onClickModify={!showForm ? () => setShowForm(true) : undefined}
      >
        {showForm ? (
          <>
            <BoxFormLayout.RequiredMessage />
            <BoxFormLayout.Fields>
              <FormikProvider value={formik}>
                <Form onSubmit={formik.handleSubmit}>
                  <FormLayout>
                    <FormLayout.Row>
                      <TextInput
                        label="Nouvelle adresse email"
                        name="email"
                        description="Format : email@exemple.com"
                      />
                    </FormLayout.Row>
                    <FormLayout.Row>
                      <TextInput
                        label="Mot de passe (requis pour modifier votre email)"
                        name="password"
                        type="password"
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
                    <Button type="submit" isLoading={formik.isSubmitting}>
                      Enregistrer
                    </Button>
                  </div>
                </Form>
              </FormikProvider>
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
