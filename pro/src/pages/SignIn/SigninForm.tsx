import { Form, useFormikContext } from 'formik'
import React from 'react'
import { useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { BannerRGS } from 'components/Banner/BannerRGS'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Events } from 'core/FirebaseEvents/constants'
import { useActiveFeature } from 'hooks/useActiveFeature'
import fullKeyIcon from 'icons/full-key.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PasswordInput } from 'ui-kit/form/PasswordInput/PasswordInput'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import styles from './Signin.module.scss'

export const SigninForm = (): JSX.Element => {
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
            description="Format : email@exemple.com"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <PasswordInput name="password" label="Mot de passe" />
        </FormLayout.Row>
        <ButtonLink
          icon={fullKeyIcon}
          variant={ButtonVariant.TERNARY}
          to="/demande-mot-de-passe"
          onClick={() =>
            logEvent(Events.CLICKED_FORGOTTEN_PASSWORD, {
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
            to={accountCreationUrl}
            onClick={() =>
              logEvent(Events.CLICKED_CREATE_ACCOUNT, {
                from: location.pathname,
              })
            }
          >
            Créer un compte
          </ButtonLink>
          <Button
            type="submit"
            className={styles['buttons']}
            isLoading={formik.isSubmitting}
            disabled={!formik.dirty || !formik.isValid}
          >
            Se connecter
          </Button>
        </div>
        <BannerRGS />
      </FormLayout>
    </Form>
  )
}
