import { useId } from 'react'
import { useFormContext } from 'react-hook-form'

import { ProUserCreationBodyV2Model } from '@/apiClient//v1'
import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { LegalInfos } from '@/components/LegalInfos/LegalInfos'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import iconFullNext from '@/icons/full-next.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { EmailSpellCheckInput } from '@/ui-kit/form/EmailSpellCheckInput/EmailSpellCheckInput'
import { PasswordInput } from '@/ui-kit/form/PasswordInput/PasswordInput'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'
import { ValidationMessageList } from '@/ui-kit/form/ValidationMessageList/ValidationMessageList'

import styles from './SignupContainer.module.scss'

export const SignupForm = (): JSX.Element => {
  const isLaptopScreenAtLeast = useMediaQuery('(min-width: 64rem)')
  const formId = useId()

  const {
    formState: { isSubmitting, errors },
    register,
    watch,
    setValue,
  } = useFormContext<ProUserCreationBodyV2Model>()

  const newPassword = watch('password')

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
          />
        </FormLayout.Row>

        <FormLayout.Row mdSpaceAfter>
          <PasswordInput
            {...register('password')}
            label="Mot de passe"
            autoComplete="new-password"
            required
          />
          <ValidationMessageList
            passwordValue={newPassword}
            hasError={!!errors.password}
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
            className={styles['buttons']}
            isLoading={isSubmitting}
            disabled={isSubmitting}
          >
            S’inscrire
          </Button>
        </div>
        <div className={styles['no-account']}>
          <p className={styles['no-account-text']}>
            Vous avez déjà un compte ?
          </p>
          <ButtonLink
            to="/connexion"
            icon={iconFullNext}
            variant={
              isLaptopScreenAtLeast
                ? ButtonVariant.TERNARY
                : ButtonVariant.QUATERNARY
            }
          >
            Se connecter
          </ButtonLink>
        </div>
      </FormLayout>
    </>
  )
}
