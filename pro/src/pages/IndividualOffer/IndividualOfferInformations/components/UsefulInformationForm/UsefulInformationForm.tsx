import { useFormContext } from 'react-hook-form'

import {
  GetActiveEANOfferResponseModel,
  GetIndividualOfferWithAddressResponseModel,
  VenueListItemResponseModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from 'commons/core/Finances/constants'
import { useAccessibilityOptions } from 'commons/hooks/useAccessibilityOptions'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OfferRefundWarning } from 'components/IndividualOffer/UsefulInformationScreen/UsefulInformationForm/components/OfferRefundWarning'
import { WithdrawalReminder } from 'components/IndividualOffer/UsefulInformationScreen/UsefulInformationForm/components/WithdrawalReminder'
import { Checkbox } from 'design-system/Checkbox/Checkbox'
import { CheckboxGroup } from 'ui-kit/formV2/CheckboxGroup/CheckboxGroup'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'
import { Select } from 'ui-kit/formV2/Select/Select'
import { TextArea } from 'ui-kit/formV2/TextArea/TextArea'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import {
  DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES,
  providedTicketWithdrawalTypeRadios,
  ticketSentDateOptions,
  ticketWithdrawalHourOptions,
  ticketWithdrawalTypeRadios,
} from '../../commons/constants'
import { setFormReadOnlyFields } from '../../commons/utils'
import { OfferLocation } from '../OfferLocation/OfferLocation'

import styles from './UsefulInformationForm.module.scss'

interface UsefulInformationFormProps {
  conditionalFields: string[]
  offer: GetIndividualOfferWithAddressResponseModel
  selectedVenue: VenueListItemResponseModel | undefined // It is the selected venue at step 1 (Qui propose l'offre)
  publishedOfferWithSameEAN?: GetActiveEANOfferResponseModel
}

const getFirstWithdrawalTypeEnumValue = (value: string) => {
  switch (value) {
    case WithdrawalTypeEnum.BY_EMAIL:
      return ticketSentDateOptions[0].value

    case WithdrawalTypeEnum.ON_SITE:
      return ticketWithdrawalHourOptions[0].value

    default:
      return undefined
  }
}

export const UsefulInformationForm = ({
  conditionalFields,
  offer,
  selectedVenue,
  publishedOfferWithSameEAN,
}: UsefulInformationFormProps): JSX.Element => {
  const {
    register,
    setValue,
    watch,
    getValues,
    formState: { errors },
  } = useFormContext() // retrieve all hook methods

  const accessibilityOptionsGroups = useAccessibilityOptions(
    setValue,
    getValues('accessibility')
  )

  const formValues = watch()

  const { subCategories } = useIndividualOfferContext()

  const offerSubCategory = subCategories.find(
    (s) => s.id === offer.subcategoryId
  )

  const readOnlyFields = publishedOfferWithSameEAN
    ? Object.keys(DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES)
    : setFormReadOnlyFields(offer)

  const {
    currentUser: { email },
  } = useCurrentUser()

  const displayNoRefundWarning =
    offerSubCategory?.reimbursementRule === REIMBURSEMENT_RULES.NOT_REIMBURSED

  const displayWithdrawalReminder =
    !offerSubCategory?.isEvent && !offer.isDigital

  const displayBookingContact = offerSubCategory?.canBeWithdrawable

  if (!selectedVenue) {
    return <Spinner />
  }

  return (
    <>
      {!offer.isDigital && (
        <OfferLocation venue={selectedVenue} readOnlyFields={readOnlyFields} />
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
              <RadioGroup
                {...register('withdrawalType')}
                checkedOption={watch('withdrawalType')}
                group={
                  formValues.withdrawalType === WithdrawalTypeEnum.IN_APP
                    ? providedTicketWithdrawalTypeRadios
                    : ticketWithdrawalTypeRadios
                }
                legend="Précisez la façon dont vous distribuerez les billets :"
                // when withdrawal Type is IN_APP the field should also be readOnly.
                // I find it better to be explicit about it
                disabled={
                  readOnlyFields.includes('withdrawalType') ||
                  formValues.withdrawalType === WithdrawalTypeEnum.IN_APP
                }
                onChange={(e) => {
                  setValue('withdrawalType', e.target.value)
                  setValue(
                    'withdrawalDelay',
                    getFirstWithdrawalTypeEnumValue(e.target.value)
                  )
                }}
              />
            </FormLayout.Row>

            {formValues.withdrawalType === WithdrawalTypeEnum.BY_EMAIL && (
              <FormLayout.Row inline>
                <Select
                  {...register('withdrawalDelay')}
                  label="Date d’envoi"
                  required={true}
                  options={ticketSentDateOptions}
                  disabled={readOnlyFields.includes('withdrawalDelay')}
                />
                <div>avant le début de l’évènement</div>
              </FormLayout.Row>
            )}

            {formValues.withdrawalType === WithdrawalTypeEnum.ON_SITE && (
              <FormLayout.Row inline>
                <Select
                  {...register('withdrawalDelay')}
                  label="Heure de retrait"
                  required={true}
                  options={ticketWithdrawalHourOptions}
                  disabled={readOnlyFields.includes('withdrawalDelay')}
                />
                <div>avant le début de l’évènement</div>
              </FormLayout.Row>
            )}
          </>
        )}

        <FormLayout.Row
          mdSpaceAfter
          sideComponent={
            <InfoBox
              link={{
                isExternal: true,
                to: 'https://aide.passculture.app/hc/fr/articles/4413389597329--Acteurs-Culturels-Quelles-modalit%C3%A9s-de-retrait-indiquer-pour-ma-structure-',
                text: 'Quelles modalités de retrait choisir ?',
              }}
            >
              {offer.isDigital
                ? 'Indiquez ici tout ce qui peut être utile au bénéficiaire pour le retrait de l’offre.'
                : 'Indiquez ici tout ce qui peut être utile au bénéficiaire pour le retrait de l’offre. En renseignant ces informations depuis les paramètres généraux de votre page partenaire, elles s’appliqueront par défaut à toutes vos offres.'}
            </InfoBox>
          }
        >
          <TextArea
            label={'Informations de retrait'}
            {...register('withdrawalDetails')}
            maxLength={500}
            disabled={readOnlyFields.includes('withdrawalDetails')}
            description={
              offer.isDigital
                ? 'Exemples : une création de compte, un code d’accès spécifique, une communication par email...'
                : 'Exemples : une autre adresse, un horaire d’accès, un délai de retrait, un guichet spécifique, un code d’accès, une communication par email...'
            }
          />
        </FormLayout.Row>

        {displayBookingContact && (
          <FormLayout.Row
            mdSpaceAfter
            sideComponent={
              <InfoBox>
                Cette adresse email sera communiquée aux bénéficiaires ayant
                réservé votre offre.
              </InfoBox>
            }
          >
            <TextInput
              {...register('bookingContact')}
              label="Email de contact"
              maxLength={90}
              description="Format : email@exemple.com"
              disabled={readOnlyFields.includes('bookingContact')}
              error={errors.bookingContact?.message as string | undefined}
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
            type="text"
            description="Format : https://exemple.com"
            disabled={readOnlyFields.includes('externalTicketOfficeUrl')}
            error={
              errors.externalTicketOfficeUrl?.message as string | undefined
            }
            required={true}
          />
        </FormLayout.Row>
      </FormLayout.Section>
      <FormLayout.Section title="Modalités d’accessibilité">
        <FormLayout.Row>
          <CheckboxGroup
            name="accessibility"
            group={accessibilityOptionsGroups}
            disabled={readOnlyFields.includes('accessibility')}
            legend="Cette offre est accessible au public en situation de handicap :"
            error={
              Object.values(formValues.accessibility).some(Boolean)
                ? undefined
                : 'Veuillez sélectionner au moins un critère d’accessibilité'
            }
          />
        </FormLayout.Row>
      </FormLayout.Section>
      <FormLayout.Section title="Notifications">
        <FormLayout.Row mdSpaceAfter>
          <Checkbox
            label="Être notifié par email des réservations"
            checked={Boolean(getValues('receiveNotificationEmails'))}
            onChange={(e) => {
              if (
                e.target.checked &&
                formValues.bookingEmail ===
                  DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES.bookingEmail
              ) {
                // eslint-disable-next-line @typescript-eslint/no-floating-promises
                setValue('bookingEmail', selectedVenue.bookingEmail ?? email)
              }
              // eslint-disable-next-line @typescript-eslint/no-floating-promises
              setValue('receiveNotificationEmails', e.target.checked)
            }}
            disabled={readOnlyFields.includes('receiveNotificationEmails')}
          />
        </FormLayout.Row>
        {formValues.receiveNotificationEmails && (
          <FormLayout.Row>
            <TextInput
              {...register('bookingEmail')}
              label="Email auquel envoyer les notifications"
              maxLength={90}
              name="bookingEmail"
              description="Format : email@exemple.com"
              disabled={readOnlyFields.includes('bookingEmail')}
              required={true}
              error={errors.bookingEmail?.message as string | undefined}
            />
          </FormLayout.Row>
        )}
      </FormLayout.Section>
    </>
  )
}
