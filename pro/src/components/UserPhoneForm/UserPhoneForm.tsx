import { yupResolver } from '@hookform/resolvers/yup'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { UserPhoneBodyModel } from '@/apiClient/v1'
import { parseAndValidateFrenchPhoneNumber } from '@/commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { updateUser } from '@/commons/store/user/reducer'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'

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
  const dispatch = useAppDispatch()
  const snackBar = useSnackBar()

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
    <form onSubmit={handleSubmit(onSubmit)}>
      <FormLayout mediumWidthForm>
        <FormLayout.Row mdSpaceAfter>
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
                } catch (_e) {
                  // phone is considered invalid by the lib, so we does nothing here and let yup indicates the error
                }
              },
            })}
            required
            error={errors.phoneNumber?.message}
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
