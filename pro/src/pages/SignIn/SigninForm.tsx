import { Form, useFormikContext } from 'formik'
import React from 'react'
import { useLocation } from 'react-router-dom'

import { BannerRGS } from 'components/Banner'
import FormLayout from 'components/FormLayout'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import fullKeyIcon from 'icons/full-key.svg'
import { ButtonLink, PasswordInput, SubmitButton, TextInput } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import styles from './Signin.module.scss'

const SigninForm = (): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()
  const isAccountCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')

  const accountCreationUrl = isAccountCreationAvailable
    ? '/inscription'
    : UNAVAILABLE_ERROR_PAGE

  const formik = useFormikContext()

  return (
    <Form>
      <ScrollToFirstErrorAfterSubmit />
      <FormLayout>
        <FormLayout.Row>
          <TextInput
            label="Adresse email"
            name="email"
            placeholder="email@exemple.com"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <PasswordInput name="password" label="Mot de passe" />
        </FormLayout.Row>
        <ButtonLink
          icon={fullKeyIcon}
          variant={ButtonVariant.TERNARY}
          link={{
            to: '/demande-mot-de-passe',
            isExternal: false,
          }}
          onClick={() =>
            logEvent?.(Events.CLICKED_FORGOTTEN_PASSWORD, {
              from: location.pathname,
            })
          }
        >
          Mot de passe oublié ?
        </ButtonLink>
        <div className={styles['buttons-field']}>
          <ButtonLink
            className={styles['buttons']}
            variant={ButtonVariant.SECONDARY}
            link={{
              to: accountCreationUrl,
              isExternal: false,
            }}
            onClick={() =>
              logEvent?.(Events.CLICKED_CREATE_ACCOUNT, {
                from: location.pathname,
              })
            }
          >
            Créer un compte
          </ButtonLink>
          <SubmitButton
            className={styles['buttons']}
            isLoading={formik.isSubmitting}
            disabled={!formik.dirty || !formik.isValid}
          >
            Se connecter
          </SubmitButton>
        </div>
        <BannerRGS />
      </FormLayout>
    </Form>
  )
}

export default SigninForm
