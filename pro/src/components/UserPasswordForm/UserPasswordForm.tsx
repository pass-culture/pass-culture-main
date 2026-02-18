import { yupResolver } from '@hookform/resolvers/yup'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { PasswordInput } from '@/design-system/PasswordInput/PasswordInput'

import { validationSchema } from './validationSchema'

export interface UserPasswordFormProps {
  closeForm: () => void
}

type UserPasswordFormValues = {
  oldPassword: string
  newPassword: string
  newConfirmationPassword: string
}

export const isUserPasswordError = (
  error: unknown
): error is Record<keyof UserPasswordFormValues, string[]> => {
  if (typeof error !== 'object' || error === null) {
    return false
  }
  if (
    'oldPassword' in error ||
    'newPassword' in error ||
    'newConfirmationPassword' in error
  ) {
    return true
  }
  return false
}

export const UserPasswordForm = ({
  closeForm,
}: UserPasswordFormProps): JSX.Element => {
  const snackBar = useSnackBar()
  const onSubmit = async (values: UserPasswordFormValues) => {
    try {
      await api.postChangePassword(values)
      closeForm()
    } catch (error) {
      // Check if we have a specific error message for one or more fields
      if (
        isErrorAPIError(error) &&
        error.status < 500 &&
        isUserPasswordError(error.body)
      ) {
        // If so, let's set the error message for each field
        for (const [field, message] of Object.entries(error.body)) {
          const typedField = field as keyof UserPasswordFormValues
          setError(typedField, { message: message.join('\n') })
        }
      } else {
        // In any other case, it's a generic error
        snackBar.error(
          'Une erreur est survenue, veuillez réessayer ultérieurement.'
        )
      }
    }
  }

  const defaultValues: UserPasswordFormValues = {
    oldPassword: '',
    newPassword: '',
    newConfirmationPassword: '',
  }

  const hookForm = useForm<UserPasswordFormValues>({
    defaultValues,
    resolver: yupResolver(validationSchema),
    mode: 'onTouched',
  })

  const {
    handleSubmit,
    register,
    formState: { isSubmitting, errors },
    watch,
    setError,
    trigger,
  } = hookForm

  const onCancel = () => {
    hookForm.reset(defaultValues)
    closeForm()
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <FormLayout mediumWidthForm>
        <FormLayout.Row mdSpaceAfter>
          <PasswordInput
            {...register('oldPassword')}
            value={watch('oldPassword')}
            error={errors.oldPassword?.message}
            label="Mot de passe actuel"
            required
            requiredIndicator="explicit"
          />
        </FormLayout.Row>
        <FormLayout.Row mdSpaceAfter>
          <PasswordInput
            {...register('newPassword', {
              onChange: () => trigger('newPassword'),
            })}
            value={watch('newPassword')}
            error={errors.newPassword?.message}
            label="Nouveau mot de passe"
            required
            requiredIndicator="explicit"
            displayValidation
          />
        </FormLayout.Row>
        <FormLayout.Row mdSpaceAfter>
          <PasswordInput
            {...register('newConfirmationPassword')}
            value={watch('newConfirmationPassword')}
            error={errors.newConfirmationPassword?.message}
            label="Confirmez votre nouveau mot de passe"
            required
            requiredIndicator="explicit"
          />
        </FormLayout.Row>

        <FormLayout.Row inline>
          <Button
            onClick={onCancel}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label="Annuler"
          />
          <Button type="submit" isLoading={isSubmitting} label="Enregistrer" />
        </FormLayout.Row>
      </FormLayout>
    </form>
  )
}
