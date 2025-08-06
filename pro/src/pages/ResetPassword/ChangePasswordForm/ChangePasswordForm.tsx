import { useFormContext } from 'react-hook-form'

import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import iconFullNext from '@/icons/full-next.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { PasswordInput } from '@/ui-kit/form/PasswordInput/PasswordInput'
import { ValidationMessageList } from '@/ui-kit/form/ValidationMessageList/ValidationMessageList'

import { type ResetPasswordValues } from '../ResetPassword'
import styles from './ChangePasswordForm.module.scss'

type ChangePasswordFormProps = {
  onSubmit(values: ResetPasswordValues): void
}

export const ChangePasswordForm = ({
  onSubmit,
}: ChangePasswordFormProps): JSX.Element => {
  const isLaptopScreenAtLeast = useMediaQuery('(min-width: 64rem)')

  const {
    register,
    handleSubmit,
    watch,
    formState: { isSubmitting, errors },
  } = useFormContext<ResetPasswordValues>()

  const newPassword = watch('newPassword')

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className={styles['change-password-form']}
    >
      <ScrollToFirstHookFormErrorAfterSubmit />

      <FormLayout>
        <div className={styles['text-input']}>
          <PasswordInput
            label="Nouveau mot de passe"
            {...register('newPassword')}
          />
          <ValidationMessageList
            passwordValue={newPassword}
            hasError={!!errors.newPassword}
          />
        </div>
        <div className={styles['text-input']}>
          <PasswordInput
            label="Confirmez votre nouveau mot de passe"
            error={errors.newConfirmationPassword?.message}
            {...register('newConfirmationPassword')}
          />
        </div>

        <div className={styles['buttons-field']}>
          <Button
            type="submit"
            className={styles['buttons']}
            isLoading={isSubmitting}
            disabled={isSubmitting}
          >
            Confirmer
          </Button>
        </div>
        <aside className={styles['no-account']}>
          <p className={styles['no-account-text']}>
            Vous n’êtes pas à l’origine de cette demande ?
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
        </aside>
      </FormLayout>
    </form>
  )
}
