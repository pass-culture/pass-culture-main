import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { yupResolver } from '@hookform/resolvers/yup'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { useNotification } from 'commons/hooks/useNotification'
import { updateUser } from 'commons/store/user/reducer'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { useForm } from 'react-hook-form'
import { useDispatch } from 'react-redux'
import { BoxFormLayout } from 'ui-kit/BoxFormLayout/BoxFormLayout'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from '../UserPhoneForm/UserForm.module.scss'

import { UserIdentityFormValues } from './types'
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
  const dispatch = useDispatch()
  const notify = useNotification()

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
          notify.error(error.body[field])
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
      <BoxFormLayout.RequiredMessage />
      <BoxFormLayout.Fields>
        <form onSubmit={handleSubmit(onSubmit)}>
          <FormLayout>
            <div className={styles['text-input']}>
              <TextInput
                label="Prénom"
                error={errors.firstName?.message}
                required={true}
                asterisk={false}
                {...register('firstName')}
              />
            </div>
            <div className={styles['text-input']}>
              <TextInput
                label="Nom"
                error={errors.lastName?.message}
                required={true}
                asterisk={false}
                {...register('lastName')}
              />
            </div>
          </FormLayout>
          <div className={styles['buttons-field']}>
            <Button onClick={onCancel} variant={ButtonVariant.SECONDARY}>
              Annuler
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Enregistrer
            </Button>
          </div>
        </form>
      </BoxFormLayout.Fields>
    </>
  )
}
