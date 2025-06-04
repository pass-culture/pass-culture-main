import { useFormikContext } from 'formik'

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
import { Select } from 'ui-kit/form/Select/Select'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { CheckboxGroup } from 'ui-kit/formV2/CheckboxGroup/CheckboxGroup'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import {
  DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES,
  providedTicketWithdrawalTypeRadios,
  ticketSentDateOptions,
  ticketWithdrawalHourOptions,
  ticketWithdrawalTypeRadios,
} from '../../commons/constants'
import { UsefulInformationFormValues } from '../../commons/types'
import { setFormReadOnlyFields } from '../../commons/utils'
import { OfferLocation } from '../OfferLocation/OfferLocation'

import styles from './UsefulInformationForm.module.scss'

interface UsefulInformationFormProps {
  conditionalFields: string[]
  offer: GetIndividualOfferWithAddressResponseModel
  selectedVenue: VenueListItemResponseModel | undefined // It is the selected venue at step 1 (Qui propose l'offre)
  publishedOfferWithSameEAN?: GetActiveEANOfferResponseModel
}

export const UsefulInformationForm = ({
  conditionalFields,
  offer,
  selectedVenue,
  publishedOfferWithSameEAN,
}: UsefulInformationFormProps): JSX.Element => {
  const {
    values: {
      withdrawalType,
      receiveNotificationEmails,
      bookingEmail,
      accessibility,
    },
    setFieldValue,
    handleChange,
    getFieldProps,
    getFieldMeta,
  } = useFormikContext<UsefulInformationFormValues>()
  const accessibilityOptionsGroups = useAccessibilityOptions(
    setFieldValue,
    accessibility
  )

  const { subCategories } = useIndividualOfferContext()

  const offerSubCategory = subCategories.find(
    (s) => s.id === offer.subcategoryId
  )

  const venue = offer.venue
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
                variant="detailed"
                group={
                  withdrawalType === WithdrawalTypeEnum.IN_APP
                    ? providedTicketWithdrawalTypeRadios
                    : ticketWithdrawalTypeRadios
                }
                legend="Précisez la façon dont vous distribuerez les billets :"
                name="withdrawalType"
                checkedOption={withdrawalType || WithdrawalTypeEnum.NO_TICKET}
                // when withdrawal Type is IN_APP the field should also be readOnly.
                // I find it better to be explicit about it
                disabled={
                  readOnlyFields.includes('withdrawalType') ||
                  withdrawalType === WithdrawalTypeEnum.IN_APP
                }
                onChange={async (e) => {
                  await setFieldValue(
                    'withdrawalDelay',
                    getFirstWithdrawalTypeEnumValue(e.target.value)
                  )
                  handleChange(e)
                }}
              />
            </FormLayout.Row>

            {withdrawalType === WithdrawalTypeEnum.BY_EMAIL && (
              <FormLayout.Row>
                <Select
                  label="Date d’envoi"
                  description="avant le début de l’évènement"
                  name="withdrawalDelay"
                  options={ticketSentDateOptions}
                  disabled={readOnlyFields.includes('withdrawalDelay')}
                />
              </FormLayout.Row>
            )}

            {withdrawalType === WithdrawalTypeEnum.ON_SITE && (
              <FormLayout.Row>
                <Select
                  label="Heure de retrait"
                  description="avant le début de l’évènement"
                  name="withdrawalDelay"
                  options={ticketWithdrawalHourOptions}
                  disabled={readOnlyFields.includes('withdrawalDelay')}
                />
              </FormLayout.Row>
            )}
          </>
        )}

        <FormLayout.Row
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
            isOptional
            label={'Informations de retrait'}
            name="withdrawalDetails"
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
              label="Email de contact"
              maxLength={90}
              name="bookingContact"
              description="Format : email@exemple.com"
              disabled={readOnlyFields.includes('bookingContact')}
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
            isOptional
            label="URL de votre site ou billetterie"
            name="externalTicketOfficeUrl"
            type="text"
            description="Format : https://exemple.com"
            disabled={readOnlyFields.includes('externalTicketOfficeUrl')}
          />
        </FormLayout.Row>
      </FormLayout.Section>
      <FormLayout.Section title="Modalités d’accessibilité">
        <FormLayout.Row>
          <CheckboxGroup
            group={accessibilityOptionsGroups}
            name="accessibility"
            disabled={readOnlyFields.includes('accessibility')}
            legend="Cette offre est accessible au public en situation de handicap :"
            required
            error={getFieldMeta('accessibility').error}
          />
        </FormLayout.Row>
      </FormLayout.Section>
      <FormLayout.Section title="Notifications">
        <FormLayout.Row>
          <Checkbox
            label="Être notifié par email des réservations"
            checked={Boolean(getFieldProps('receiveNotificationEmails').value)}
            onChange={(e) => {
              if (
                e.target.checked &&
                bookingEmail ===
                  DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES.bookingEmail
              ) {
                // eslint-disable-next-line @typescript-eslint/no-floating-promises
                setFieldValue('bookingEmail', venue.bookingEmail ?? email)
              }
              // eslint-disable-next-line @typescript-eslint/no-floating-promises
              setFieldValue('receiveNotificationEmails', e.target.checked)
            }}
            disabled={readOnlyFields.includes('receiveNotificationEmails')}
          />
        </FormLayout.Row>

        {receiveNotificationEmails && (
          <FormLayout.Row className={styles['email-row']}>
            <TextInput
              label="Email auquel envoyer les notifications"
              maxLength={90}
              name="bookingEmail"
              description="Format : email@exemple.com"
              disabled={readOnlyFields.includes('bookingEmail')}
            />
          </FormLayout.Row>
        )}
      </FormLayout.Section>
    </>
  )
}
