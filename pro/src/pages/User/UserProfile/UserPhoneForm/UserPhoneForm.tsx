import { yupResolver } from '@hookform/resolvers/yup'
import { useForm } from 'react-hook-form'

import { apiNew } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import { parseAndValidateFrenchPhoneNumber } from '@/commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { updateUser } from '@/commons/store/user/reducer'
import { ensureCurrentUser } from '@/commons/store/user/selectors'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'

import { validationSchema } from './validationSchema'

export interface UserPhoneInitialValues {
  phoneNumber: string
}

export interface UserPhoneFormProps {
  closeForm: () => void
  initialValues: UserPhoneInitialValues
}

export const UserPhoneForm = ({
  closeForm,
  initialValues,
}: UserPhoneFormProps): JSX.Element => {
  const currentUser = useAppSelector(ensureCurrentUser)
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
  } = hookForm

  const onSubmit = async (values: UserPhoneInitialValues) => {
    values.phoneNumber = parseAndValidateFrenchPhoneNumber(
      values.phoneNumber
    ).number

    try {
      const response = await apiNew.patchUserPhone({ body: values })
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
            {...register('phoneNumber')}
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
