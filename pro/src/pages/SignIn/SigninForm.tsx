import { Form, useFormContext } from 'react-hook-form'

import type { LoginUserBodyModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { PasswordInput } from '@/design-system/PasswordInput/PasswordInput'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullKeyIcon from '@/icons/full-key.svg'
import iconFullNext from '@/icons/full-next.svg'

import styles from './Signin.module.scss'

type SigninFormProps = {
  onSubmit(): void
}

export const SigninForm = ({ onSubmit }: SigninFormProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const { formState, register, watch } = useFormContext<LoginUserBodyModel>()
  const { errors } = formState

  return (
    <Form onSubmit={onSubmit}>
      <ScrollToFirstHookFormErrorAfterSubmit />

      <FormLayout>
        <div className={styles['text-input']}>
          <div className={styles['text-input']}>
            <TextInput
              label="Adresse email"
              required
              type="email"
              error={errors.identifier?.message}
              description="Format : email@exemple.com"
              {...register('identifier')}
              requiredIndicator="explicit"
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
            requiredIndicator="explicit"
          />
        </div>
        <Button
          as="router-link"
          icon={fullKeyIcon}
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          to="/demande-mot-de-passe"
          onClick={() => logEvent(Events.CLICKED_FORGOTTEN_PASSWORD)}
          label="Réinitialisez votre mot de passe"
        />
        <div className={styles['buttons-field']}>
          <Button
            type="submit"
            isLoading={formState.isSubmitting}
            label="Se connecter"
          />
        </div>
        <aside
          aria-label="Pas encore de compte"
          className={styles['no-account']}
        >
          <p className={styles['no-account-text']}>
            Vous n’avez pas encore de compte ?
          </p>
          <Button
            as="router-link"
            to="/inscription"
            icon={iconFullNext}
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            onClick={() => logEvent(Events.CLICKED_CREATE_ACCOUNT)}
            label="S’inscrire"
          />
        </aside>
      </FormLayout>
    </Form>
  )
}
