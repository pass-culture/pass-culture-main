import { yupResolver } from '@hookform/resolvers/yup'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { updateUser } from '@/commons/store/user/reducer'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { BoxFormLayout } from '@/ui-kit/BoxFormLayout/BoxFormLayout'

import styles from '../UserPhoneForm/UserForm.module.scss'
import type { UserIdentityFormValues } from './types'
import { validationSchema } from './validationSchema'

export interface UserIdentityFormProps {
  closeForm: () => void
  initialValues: UserIdentityFormValues
}
export const UserIdentityForm = ({
  closeForm,
  initialValues,
}: UserIdentityFormProps): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const dispatch = useAppDispatch()
  const snackBar = useSnackBar()

  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors },
  } = useForm<UserIdentityFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(validationSchema),
    mode: 'onBlur',
  })

  const onSubmit = async (values: UserIdentityFormValues) => {
    try {
      const response = await api.patchUserIdentity(values)
      dispatch(
        updateUser({
          ...currentUser,
          ...response,
        })
      )
      closeForm()
    } catch (error) {
      if (isErrorAPIError(error)) {
        // Handle server-side errors and set field errors
        for (const field of Object.keys(error.body)) {
          snackBar.error(error.body[field])
        }
      }
    }
  }

  const onCancel = () => {
    reset()
    closeForm()
  }

  return (
    <BoxFormLayout.Fields>
      <form onSubmit={handleSubmit(onSubmit)}>
        <FormLayout>
          <div className={styles['text-input']}>
            <TextInput
              label="Prénom"
              error={errors.firstName?.message}
              required
              requiredIndicator="explicit"
              {...register('firstName')}
            />
          </div>
          <div className={styles['text-input']}>
            <TextInput
              label="Nom"
              error={errors.lastName?.message}
              required
              requiredIndicator="explicit"
              {...register('lastName')}
            />
          </div>
        </FormLayout>
        <div className={styles['buttons-field']}>
          <Button
            onClick={onCancel}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label="Annuler"
          />
          <Button type="submit" isLoading={isSubmitting} label="Enregistrer" />
        </div>
      </form>
    </BoxFormLayout.Fields>
  )
}
