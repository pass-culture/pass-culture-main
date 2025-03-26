import { Form, useFormContext } from 'react-hook-form'
import { useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useMediaQuery } from 'commons/hooks/useMediaQuery'
import { UNAVAILABLE_ERROR_PAGE } from 'commons/utils/routes'
import { BannerRGS } from 'components/BannerRGS/BannerRGS'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { ScrollToFirstHookFormErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import fullKeyIcon from 'icons/full-key.svg'
import iconFullNext from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PasswordInput } from 'ui-kit/formV2/PasswordInput/PasswordInput'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import { SigninFormValues } from './SignIn'
import styles from './Signin.module.scss'

type SigninFormProps = {
  onSubmit(): void
}

export const SigninForm = ({ onSubmit }: SigninFormProps): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()
  const isAccountCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const is2025SignUpEnabled = useActiveFeature('WIP_2025_SIGN_UP')
  const isLaptopScreenAtLeast = useMediaQuery('(min-width: 64rem)')

  const accountCreationUrl = isAccountCreationAvailable
    ? '/inscription'
    : UNAVAILABLE_ERROR_PAGE

  const { formState, register } = useFormContext<SigninFormValues>()
  const { errors } = formState

  return (
    <Form onSubmit={onSubmit}>
      <ScrollToFirstHookFormErrorAfterSubmit />

      <FormLayout>
        <div className={styles['text-input']}>
          <TextInput
            label="Adresse email"
            required={true}
            error={errors.email?.message}
            description="Format : email@exemple.com"
            {...register('email')}
            asterisk={false}
            className={styles['text-input']}
          />
        </div>
        <div className={styles['text-input']}>
          <PasswordInput
            label="Mot de passe"
            required={true}
            error={errors.password?.message}
            {...register('password')}
            asterisk={false}
          />
        </div>
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
          {!is2025SignUpEnabled && (
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
          )}
          <Button
            type="submit"
            className={styles['buttons']}
            isLoading={formState.isSubmitting}
          >
            Se connecter
          </Button>
        </div>
        {is2025SignUpEnabled && (
          <aside className={styles['no-account']}>
            <p className={styles['no-account-text']}>
              Vous n’avez pas encore de compte ?
            </p>
            <ButtonLink
              to={accountCreationUrl}
              icon={iconFullNext}
              variant={
                isLaptopScreenAtLeast
                  ? ButtonVariant.TERNARY
                  : ButtonVariant.QUATERNARY
              }
            >
              S’inscrire
            </ButtonLink>
          </aside>
        )}
        {!is2025SignUpEnabled && <BannerRGS />}
      </FormLayout>
    </Form>
  )
}
