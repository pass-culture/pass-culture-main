import type { UserPhoneBodyModel } from '@/apiClient/v1'
import { UserPhoneForm } from '@/components/UserPhoneForm/UserPhoneForm'
import { BoxFormLayout } from '@/ui-kit/BoxFormLayout/BoxFormLayout'

import { Forms } from '../constants'

interface UserPhoneProps {
  setCurrentForm: (value: Forms | null) => void
  initialValues: UserPhoneBodyModel
  showForm: boolean
}

/**
 * if phone number is valid:
 * - 10 digit starting by 0
 * - n digits starting by +
 *
 * return formated phone number:
 * - 01 23 45 67 89
 * - +213 1 23 45 67 89
 *
 * otherwise, return given argument phoneNumber unchanged
 */
export const formatPhoneNumber = (phoneNumber: string | null | undefined) => {
  let formatedNumber = phoneNumber
  if (phoneNumber) {
    formatedNumber = phoneNumber.replace(/ /g, '')
    const r = /(\+?[0-9]+)([0-9])([0-9]{8})/g
    const parts = formatedNumber.split(r).slice(1, -1)

    if (parts.length !== 3) {
      return phoneNumber
    }

    const [internationalPrefix, areaPrefix, number] = parts
    const isReginalNumber = internationalPrefix === '0'
    const isInternationalNumber = /\+[0-9]+/.test(internationalPrefix)
    if (!(isReginalNumber || isInternationalNumber)) {
      return phoneNumber
    }

    let prefix = internationalPrefix + areaPrefix
    if (isInternationalNumber) {
      prefix = [internationalPrefix, areaPrefix].join(' ')
    }

    return [prefix, ...number.split(/([0-9]{2})/g).filter((num) => num)].join(
      ' '
    )
  }
  return phoneNumber
}

export const UserPhone = ({
  setCurrentForm,
  initialValues,
  showForm,
}: UserPhoneProps) => {
  const onClickModify = () => setCurrentForm(Forms.USER_PHONE)
  const resetForm = () => setCurrentForm(null)
  return (
    <BoxFormLayout>
      {showForm ? (
        <UserPhoneForm closeForm={resetForm} initialValues={initialValues} />
      ) : (
        <BoxFormLayout.Header
          subtitle={`${formatPhoneNumber(initialValues.phoneNumber)}`}
          title="Téléphone"
          onClickModify={onClickModify}
        />
      )}
    </BoxFormLayout>
  )
}
