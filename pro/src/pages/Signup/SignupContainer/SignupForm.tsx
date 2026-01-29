import { useId } from 'react'
import { useFormContext } from 'react-hook-form'

import type { ProUserCreationBodyV2Model } from '@/apiClient/v1'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { LegalInfos } from '@/components/LegalInfos/LegalInfos'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { PasswordInput } from '@/design-system/PasswordInput/PasswordInput'
import { TextInput } from '@/design-system/TextInput/TextInput'
import iconFullNext from '@/icons/full-next.svg'
import { EmailSpellCheckInput } from '@/ui-kit/form/EmailSpellCheckInput/EmailSpellCheckInput'

import styles from './SignupContainer.module.scss'

export const SignupForm = (): JSX.Element => {
  const formId = useId()

  const {
    formState: { isSubmitting, errors },
    register,
    watch,
    setValue,
  } = useFormContext<ProUserCreationBodyV2Model>()

  return (
    <>
      <ScrollToFirstHookFormErrorAfterSubmit />

      <FormLayout>
        <div className={styles['signup-form-row']}>
          <FormLayout.Row
            mdSpaceAfter
            key={`${formId}-firstName`}
            className={styles['signup-form-group']}
          >
            <TextInput
              label="Prénom"
              {...register('firstName')}
              error={errors.firstName?.message}
              autoComplete="given-name"
              required
            />
          </FormLayout.Row>
          <FormLayout.Row
            mdSpaceAfter
            key={`${formId}-lastName`}
            className={styles['signup-form-group']}
          >
            <TextInput
              label="Nom"
              {...register('lastName')}
              error={errors.lastName?.message}
              autoComplete="family-name"
              required
            />
          </FormLayout.Row>
        </div>
        <FormLayout.Row mdSpaceAfter>
          <EmailSpellCheckInput
            {...register('email')}
            error={errors.email?.message}
            onApplyTip={(tip) => {
              setValue('email', tip)
            }}
            description="Format : email@exemple.com"
            label="Adresse email"
            required
            currentCount={watch('email').length}
          />
        </FormLayout.Row>

        <FormLayout.Row mdSpaceAfter>
          <PasswordInput
            {...register('password')}
            value={watch('password')}
            label="Mot de passe"
            autoComplete="new-password"
            required
            error={errors.password?.message}
            displayValidation
          />
        </FormLayout.Row>

        <FormLayout.Row>
          <Checkbox
            label="J’accepte d’être contacté par email pour recevoir les
                      nouveautés du pass Culture et contribuer à son
                      amélioration (facultatif)"
            {...register('contactOk')}
            checked={Boolean(watch('contactOk'))}
          />
        </FormLayout.Row>
        <LegalInfos className={styles['sign-up-infos-before-signup']} />
        <div className={styles['buttons-field']}>
          <Button
            type="submit"
            isLoading={isSubmitting}
            disabled={isSubmitting}
            label="S’inscrire"
          />
        </div>
        <div className={styles['no-account']}>
          <p className={styles['no-account-text']}>
            Vous avez déjà un compte ?
          </p>

          <Button
            as="a"
            to="/connexion"
            icon={iconFullNext}
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            label="Se connecter"
          />
        </div>
      </FormLayout>
    </>
  )
}
