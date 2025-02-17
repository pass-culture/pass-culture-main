import { yupResolver } from '@hookform/resolvers/yup'
import { useForm } from 'react-hook-form'
import { useDispatch } from 'react-redux'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { UserPhoneBodyModel } from 'apiClient/v1'
import { parseAndValidateFrenchPhoneNumber } from 'commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { useNotification } from 'commons/hooks/useNotification'
import { updateUser } from 'commons/store/user/reducer'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { BoxFormLayout } from 'ui-kit/BoxFormLayout/BoxFormLayout'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import styles from './UserForm.module.scss'
import { validationSchema } from './validationSchema'

export interface UserPhoneFormProps {
  closeForm: () => void
  initialValues: UserPhoneBodyModel
}

export const UserPhoneForm = ({
  closeForm,
  initialValues,
}: UserPhoneFormProps): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()
  const notify = useNotification()

  const hookForm = useForm({
    defaultValues: initialValues,
    resolver: yupResolver(validationSchema),
    mode: 'onBlur',
  })

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = hookForm

  const onSubmit = async (values: UserPhoneBodyModel) => {
    values.phoneNumber = parseAndValidateFrenchPhoneNumber(
      values.phoneNumber
    ).number

    try {
      const response = await api.patchUserPhone(values)
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
    <BoxFormLayout.Fields>
      <form onSubmit={handleSubmit(onSubmit)}>
        <FormLayout>
          <FormLayout.Row>
            <TextInput
              label="Téléphone"
              {...register('phoneNumber')}
              required={true}
              error={errors.phoneNumber?.message}
              hideAsterisk={true}
            />
          </FormLayout.Row>
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
  )
}
