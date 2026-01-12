import { Form, useFormContext } from 'react-hook-form'
import { useLocation } from 'react-router'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { PasswordInput } from '@/design-system/PasswordInput/PasswordInput'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullKeyIcon from '@/icons/full-key.svg'
import iconFullNext from '@/icons/full-next.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'

import type { SigninFormValues } from './SignIn'
import styles from './Signin.module.scss'

type SigninFormProps = {
  onSubmit(): void
}

export const SigninForm = ({ onSubmit }: SigninFormProps): JSX.Element => {
  const location = useLocation()
  const { logEvent } = useAnalytics()
  const isAccountCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const isLaptopScreenAtLeast = useMediaQuery('(min-width: 64rem)')

  const accountCreationUrl = isAccountCreationAvailable
    ? '/inscription/compte/creation'
    : '/erreur/indisponible'

  const { formState, register, watch } = useFormContext<SigninFormValues>()
  const { errors } = formState

  return (
    <Form onSubmit={onSubmit}>
      <ScrollToFirstHookFormErrorAfterSubmit />

      <FormLayout>
        <div className={styles['text-input']}>
          <div className={styles['text-input']}>
            <TextInput
              autoComplete="username"
              label="Adresse email"
              required
              type="email"
              error={errors.email?.message}
              description="Format : email@exemple.com"
              {...register('email')}
              requiredIndicator="hidden"
            />
          </div>
        </div>
        <div className={styles['text-input']}>
          <PasswordInput
            autoComplete="current-password"
            label="Mot de passe"
            required
            error={errors.password?.message}
            {...register('password')}
            value={watch('password')}
            requiredIndicator="hidden"
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
          Réinitialisez votre mot de passe
        </ButtonLink>
        <div className={styles['buttons-field']}>
          <Button
            type="submit"
            className={styles['buttons']}
            isLoading={formState.isSubmitting}
          >
            Se connecter
          </Button>
        </div>
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
            onClick={() =>
              logEvent(Events.CLICKED_CREATE_ACCOUNT, {
                from: location.pathname,
              })
            }
          >
            S’inscrire
          </ButtonLink>
        </aside>
      </FormLayout>
    </Form>
  )
}
