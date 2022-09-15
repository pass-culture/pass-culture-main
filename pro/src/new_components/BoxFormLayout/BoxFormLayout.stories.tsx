import type { Story } from '@storybook/react'
import { Form, FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import FormLayout from 'new_components/FormLayout'
import { Button, SubmitButton, TextInput } from 'ui-kit'
import { BoxRounded } from 'ui-kit/BoxRounded'
import { ButtonVariant } from 'ui-kit/Button/types'

import { BoxFormLayout } from '.'

type Props = React.ComponentProps<typeof BoxFormLayout>

const Template: Story<Props> = () => {
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
    <BoxFormLayout>
      <BoxRounded
        onClickModify={() => setShowForm(true)}
        showButtonModify={!showForm}
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
                        label="Nouvelle adresse e-mail"
                        name="email"
                        placeholder="email@exemple.com"
                      />
                    </FormLayout.Row>
                    <FormLayout.Row>
                      <TextInput
                        label="Mot de passe (requis pour modifier votre e-mail)"
                        name="password"
                        type="password"
                        placeholder="Votre mot de passe"
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
                    <SubmitButton
                      className="primary-button"
                      isLoading={formik.isSubmitting}
                    >
                      Enregistrer
                    </SubmitButton>
                  </div>
                </Form>
              </FormikProvider>
            </BoxFormLayout.Fields>
          </>
        ) : (
          <>
            <BoxFormLayout.Header
              subtitle={'Je suis le sous-titre'}
              title="Adresse e-mail"
            />
          </>
        )}
      </BoxRounded>
    </BoxFormLayout>
  )
}

export const BasicBoxFormLayout = Template.bind({})
BasicBoxFormLayout.storyName = 'Box Form Layout'

export default {
  title: 'components/BoxFormLayout',
}
