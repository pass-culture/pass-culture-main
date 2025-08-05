import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { UserPhoneBodyModel } from 'apiClient/v1'
import { yupResolver } from '@hookform/resolvers/yup'
import { parseAndValidateFrenchPhoneNumber } from 'commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { useNotification } from 'commons/hooks/useNotification'
import { updateUser } from 'commons/store/user/reducer'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { useForm } from 'react-hook-form'
import { useDispatch } from 'react-redux'
import { BoxFormLayout } from 'ui-kit/BoxFormLayout/BoxFormLayout'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'

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
    setValue,
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
            <PhoneNumberInput
              label="Téléphone"
              {...register('phoneNumber', {
                onBlur(event) {
                  // This is because entries like "+33600110011invalid" are considered valid by libphonenumber-js,
                  // We need to explicitely extract "+33600110011" that is in the .number property
                  try {
                    const phoneNumber = parseAndValidateFrenchPhoneNumber(
                      event.target.value
                    ).number
                    setValue('phoneNumber', phoneNumber)
                    // eslint-disable-next-line @typescript-eslint/no-unused-vars
                  } catch (e) {
                    // phone is considered invalid by the lib, so we does nothing here and let yup indicates the error
                  }
                },
              })}
              required={true}
              error={errors.phoneNumber?.message}
              asterisk={false}
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
