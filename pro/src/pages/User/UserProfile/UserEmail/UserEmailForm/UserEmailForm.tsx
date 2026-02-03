import { yupResolver } from '@hookform/resolvers/yup'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { UserResetEmailBodyModel } from '@/apiClient/v1'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { PasswordInput } from '@/design-system/PasswordInput/PasswordInput'
import { TextInput } from '@/design-system/TextInput/TextInput'

import styles from './UserEmailForm.module.scss'
import { validationSchema } from './validationSchema'

export interface UserEmailFormProps {
  closeForm: () => void
  getPendingEmailRequest: () => void
}

type UserEmailFormValues = {
  email: string
  password: string
}

export const UserEmailForm = ({
  closeForm,
  getPendingEmailRequest,
}: UserEmailFormProps): JSX.Element => {
  const { currentUser } = useCurrentUser()

  const initialValues: UserEmailFormValues = {
    email: '',
    password: '',
  }

  const hookForm = useForm<UserEmailFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(validationSchema),
    mode: 'onBlur',
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors },
    watch,
  } = hookForm

  const onSubmit = async (values: UserResetEmailBodyModel) => {
    try {
      await api.postUserEmail(values)

      getPendingEmailRequest()
      closeForm()
    } catch (error) {
      if (isErrorAPIError(error)) {
        // Handle server-side errors and set field errors
        for (const field of Object.keys(error.body)) {
          hookForm.setError('password', {
            message: error.body[field],
          })
        }
      }
    }
  }

  const onCancel = () => {
    reset()
    closeForm()
  }

  return (
    <>
      <span className={styles['header-secondary']}>
        Adresse email actuelle:
      </span>
      <span>{currentUser.email}</span>
      <form onSubmit={handleSubmit(onSubmit)}>
        <FormLayout mediumWidthForm>
          <FormLayout.Row mdSpaceAfter>
            <TextInput
              label="Nouvelle adresse email"
              description="Format : email@exemple.com"
              error={errors.email?.message}
              required
              type="email"
              {...register('email')}
              requiredIndicator="explicit"
            />
          </FormLayout.Row>
          <FormLayout.Row mdSpaceAfter>
            <PasswordInput
              label="Mot de passe (requis pour modifier votre email)"
              error={errors.password?.message}
              required={true}
              {...register('password')}
              value={watch('password')}
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

            <Button
              type="submit"
              isLoading={isSubmitting}
              label="Enregistrer"
            />
          </FormLayout.Row>
        </FormLayout>
      </form>
    </>
  )
}
