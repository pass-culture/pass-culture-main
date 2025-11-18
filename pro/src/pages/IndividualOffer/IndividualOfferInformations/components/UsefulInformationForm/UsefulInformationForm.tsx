import { useFormContext } from 'react-hook-form'

import {
  type VenueListItemResponseModel,
  WithdrawalTypeEnum,
} from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from '@/commons/core/Finances/constants'
import {
  type SetAccessibilityFieldValue,
  useAccessibilityOptions,
} from '@/commons/hooks/useAccessibilityOptions'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { Select } from '@/ui-kit/form/Select/Select'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import {
  DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES,
  providedTicketWithdrawalTypeRadios,
  ticketSentDateOptions,
  ticketWithdrawalHourOptions,
  ticketWithdrawalTypeRadios,
} from '../../commons/constants'
import type { UsefulInformationFormValues } from '../../commons/types'
import { getFormReadOnlyFields } from '../../commons/utils'
import { OfferLocation } from '../OfferLocation/OfferLocation'
import { OfferRefundWarning } from './OfferRefundWarning'
import styles from './UsefulInformationForm.module.scss'
import { WithdrawalReminder } from './WithdrawalReminder'

export interface UsefulInformationFormProps {
  conditionalFields: string[]
  selectedVenue: VenueListItemResponseModel | undefined // It is the selected venue at step 1 (Qui propose l'offre)
  hasPublishedOfferWithSameEan?: boolean
}

export function getFirstWithdrawalTypeEnumValue(value: string) {
  switch (value) {
    case WithdrawalTypeEnum.BY_EMAIL:
      return ticketSentDateOptions[0].value

    case WithdrawalTypeEnum.ON_SITE:
      return ticketWithdrawalHourOptions[0].value

    default:
      return null
  }
}

export const UsefulInformationForm = ({
  conditionalFields,
  selectedVenue,
  hasPublishedOfferWithSameEan,
}: UsefulInformationFormProps) => {
  const {
    register,
    watch,
    setValue,
    trigger,
    formState: { errors },
  } = useFormContext<UsefulInformationFormValues>()
  const withdrawalType = watch('withdrawalType')
  const bookingEmail = watch('bookingEmail')
  const receiveNotificationEmails = watch('receiveNotificationEmails')
  const accessibility = watch('accessibility')

  const setAccessibilityValue: SetAccessibilityFieldValue = (name, value) => {
    setValue(name, value)
    trigger('accessibility')
  }
  const accessibilityOptions = useAccessibilityOptions(
    setAccessibilityValue,
    accessibility
  )

  const { offer, subCategories } = useIndividualOfferContext()
  const {
    currentUser: { email },
  } = useCurrentUser()

  // This shouldn't happen since UsefulInformationForm is rendered
  // within IndividualOfferInformationsScreen, which itself is only
  // rendered when offer is defined - this is to keep TS quiet.
  if (!offer) {
    return null
  }

  const offerSubCategory = subCategories.find(
    (s) => s.id === offer.subcategoryId
  )

  const readOnlyFields = hasPublishedOfferWithSameEan
    ? Object.keys(DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES)
    : getFormReadOnlyFields(offer)

  const displayNoRefundWarning =
    offerSubCategory?.reimbursementRule === REIMBURSEMENT_RULES.NOT_REIMBURSED
  const displayWithdrawalReminder =
    !offerSubCategory?.isEvent && !offer.isDigital

  if (!selectedVenue) {
    return <Spinner />
  }

  return (
    <>
      {!offer.isDigital && (
        <FormLayout.Section title="Où profiter de l’offre ?">
          <OfferLocation
            venue={selectedVenue}
            readOnlyFields={readOnlyFields}
          />
        </FormLayout.Section>
      )}

      <FormLayout.Section title="Retrait de l’offre">
        {displayNoRefundWarning && (
          <FormLayout.Row className={styles['info-banners']}>
            <OfferRefundWarning />
          </FormLayout.Row>
        )}
        {displayWithdrawalReminder && (
          <FormLayout.Row className={styles['info-banners']}>
            <WithdrawalReminder />
          </FormLayout.Row>
        )}

        {conditionalFields.includes('withdrawalType') && (
          <>
            <FormLayout.Row mdSpaceAfter>
              {/*
                IN_APP withdrawal type is only selectable by offers created by the event API
                Theses offers are not editable by the user
              */}
              <RadioButtonGroup
                variant="detailed"
                name="withdrawalType"
                checkedOption={withdrawalType}
                options={
                  withdrawalType === WithdrawalTypeEnum.IN_APP
                    ? providedTicketWithdrawalTypeRadios
                    : ticketWithdrawalTypeRadios
                }
                label="Précisez la façon dont vous distribuerez les billets :"
                // when withdrawal Type is IN_APP the field should also be readOnly.
                // I find it better to be explicit about it
                disabled={
                  readOnlyFields.includes('withdrawalType') ||
                  withdrawalType === WithdrawalTypeEnum.IN_APP
                }
                onChange={(e) => {
                  setValue(
                    'withdrawalType',
                    e.target.value as WithdrawalTypeEnum
                  )
                  setValue(
                    'withdrawalDelay',
                    getFirstWithdrawalTypeEnumValue(e.target.value) || undefined
                  )
                }}
              />
            </FormLayout.Row>

            {withdrawalType === WithdrawalTypeEnum.BY_EMAIL && (
              <FormLayout.Row mdSpaceAfter>
                <Select
                  {...register('withdrawalDelay')}
                  label="Date d’envoi - avant le début de l’évènement"
                  options={ticketSentDateOptions}
                  disabled={readOnlyFields.includes('withdrawalDelay')}
                  error={errors.withdrawalDelay?.message}
                />
              </FormLayout.Row>
            )}

            {withdrawalType === WithdrawalTypeEnum.ON_SITE && (
              <FormLayout.Row mdSpaceAfter>
                <Select
                  {...register('withdrawalDelay')}
                  label="Heure de retrait - avant le début de l’évènement"
                  options={ticketWithdrawalHourOptions}
                  disabled={readOnlyFields.includes('withdrawalDelay')}
                />
              </FormLayout.Row>
            )}
          </>
        )}

        <FormLayout.Row mdSpaceAfter>
          <TextArea
            {...register('withdrawalDetails')}
            label={'Informations de retrait'}
            maxLength={500}
            disabled={readOnlyFields.includes('withdrawalDetails')}
            error={errors.withdrawalDetails?.message}
            description={
              offer.isDigital
                ? 'Exemples : une création de compte, un code d’accès spécifique, une communication par email...'
                : 'Exemples : une autre adresse, un horaire d’accès, un délai de retrait, un guichet spécifique, un code d’accès, une communication par email...'
            }
          />
        </FormLayout.Row>
        {conditionalFields.includes('bookingContact') && (
          <FormLayout.Row mdSpaceAfter>
            <TextInput
              {...register('bookingContact')}
              label="Email de contact communiqué aux bénéficiaires"
              maxCharactersCount={90}
              description="Format : email@exemple.com"
              disabled={readOnlyFields.includes('bookingContact')}
              error={errors.bookingContact?.message}
              required
            />
          </FormLayout.Row>
        )}
      </FormLayout.Section>
      <FormLayout.Section title="Lien de réservation externe en l’absence de crédit">
        <p className={styles['infotext']}>
          S’ils ne disposent pas ou plus de crédit, les utilisateurs de
          l’application seront redirigés sur ce lien pour pouvoir néanmoins
          profiter de votre offre.
        </p>
        <FormLayout.Row>
          <TextInput
            {...register('externalTicketOfficeUrl')}
            label="URL de votre site ou billetterie"
            description="Format : https://exemple.com"
            disabled={readOnlyFields.includes('externalTicketOfficeUrl')}
            error={errors.externalTicketOfficeUrl?.message}
          />
        </FormLayout.Row>
      </FormLayout.Section>
      {accessibilityOptions && (
        <FormLayout.Section title="Modalités d’accessibilité">
          <FormLayout.Row>
            <CheckboxGroup
              options={accessibilityOptions}
              disabled={readOnlyFields.includes('accessibility')}
              label="Cette offre est accessible au public en situation de handicap :"
              description="Sélectionnez au moins une option"
              variant="detailed"
              error={errors.accessibility?.message}
            />
          </FormLayout.Row>
        </FormLayout.Section>
      )}
      <FormLayout.Section title="Notifications">
        <FormLayout.Row>
          <Checkbox
            label="Être notifié par email des réservations"
            checked={!!receiveNotificationEmails}
            // TODO (igabriele, 2025-07-24): Move that to a named function once the FF is enabled in production.
            onChange={(e) => {
              if (
                e.target.checked &&
                bookingEmail ===
                  DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES.bookingEmail
              ) {
                setValue('bookingEmail', offer.venue.bookingEmail ?? email)
              }

              setValue('receiveNotificationEmails', e.target.checked)
            }}
            disabled={readOnlyFields.includes('receiveNotificationEmails')}
          />
        </FormLayout.Row>
        {receiveNotificationEmails && (
          <FormLayout.Row className={styles['email-row']}>
            <TextInput
              {...register('bookingEmail')}
              label="Email auquel envoyer les notifications"
              maxCharactersCount={90}
              description="Format : email@exemple.com"
              disabled={readOnlyFields.includes('bookingEmail')}
              required
              error={errors.bookingEmail?.message}
            />
          </FormLayout.Row>
        )}
      </FormLayout.Section>
    </>
  )
}
