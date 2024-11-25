import { useFormikContext } from 'formik'

import {
  GetIndividualOfferWithAddressResponseModel,
  VenueListItemResponseModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from 'commons/core/Finances/constants'
import { useAccessibilityOptions } from 'commons/hooks/useAccessibilityOptions'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { OfferRefundWarning } from 'components/Banner/OfferRefundWarning'
import { WithdrawalReminder } from 'components/Banner/WithdrawalReminder'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { Select } from 'ui-kit/form/Select/Select'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
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
}

export const UsefulInformationForm = ({
  conditionalFields,
  offer,
  selectedVenue,
}: UsefulInformationFormProps): JSX.Element => {
  const {
    values: { withdrawalType, receiveNotificationEmails, bookingEmail },
    setFieldValue,
    handleChange,
  } = useFormikContext<UsefulInformationFormValues>()
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')
  const accessibilityOptionsGroups = useAccessibilityOptions(setFieldValue)

  const { subCategories } = useIndividualOfferContext()

  const offerSubCategory = subCategories.find(
    (s) => s.id === offer.subcategoryId
  )

  const venue = offer.venue
  const readOnlyFields = setFormReadOnlyFields(offer)

  // we use venue is virtual here because we cannot infer it from the offerSubCategory
  // because of CATEGORY_STATUS.ONLINE_OR_OFFLINE who can be both virtual or not
  const isVenueVirtual = venue.isVirtual || false

  const {
    currentUser: { isAdmin, email },
  } = useCurrentUser()

  const displayNoRefundWarning =
    offerSubCategory?.reimbursementRule === REIMBURSEMENT_RULES.NOT_REIMBURSED

  const displayWithdrawalReminder =
    !offerSubCategory?.isEvent && !isVenueVirtual

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
      {isOfferAddressEnabled && !isVenueVirtual && (
        <OfferLocation venue={selectedVenue} offer={offer} />
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

        {(conditionalFields.includes('withdrawalType') ||
          Boolean(withdrawalType)) && (
          <>
            <FormLayout.Row mdSpaceAfter>
              {/*
                IN_APP withdrawal type is only selectable by offers created by the event API
                Theses offers are not editable by the user
              */}
              <RadioGroup
                group={
                  withdrawalType === WithdrawalTypeEnum.IN_APP
                    ? providedTicketWithdrawalTypeRadios
                    : ticketWithdrawalTypeRadios
                }
                legend="Précisez la façon dont vous distribuerez les billets :"
                name="withdrawalType"
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
              {isVenueVirtual
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
              isVenueVirtual
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

        {isVenueVirtual && (
          <FormLayout.Row
            sideComponent={
              <InfoBox>
                Lien vers lequel seront renvoyés les bénéficiaires ayant réservé
                votre offre sur l’application pass Culture.
              </InfoBox>
            }
          >
            <TextInput
              label="URL d’accès à l’offre"
              name="url"
              type="text"
              description="Format : https://exemple.com"
              disabled={readOnlyFields.includes('url')}
            />
          </FormLayout.Row>
        )}
        {isAdmin && (
          <FormLayout.Row>
            <Checkbox
              hideFooter
              label={'Rayonnement national'}
              name="isNational"
              value=""
              disabled={readOnlyFields.includes('isNational')}
            />
          </FormLayout.Row>
        )}
      </FormLayout.Section>
      <FormLayout.Section title="Modalités d’accessibilité">
        <FormLayout.Row>
          <CheckboxGroup
            className={styles['accessibility-checkbox-group']}
            group={accessibilityOptionsGroups}
            groupName="accessibility"
            disabled={readOnlyFields.includes('accessibility')}
            legend="Cette offre est accessible au public en situation de handicap :"
          />
        </FormLayout.Row>
      </FormLayout.Section>
      <FormLayout.Section title="Notifications">
        <FormLayout.Row>
          <Checkbox
            label="Être notifié par email des réservations"
            name="receiveNotificationEmails"
            value=""
            onChange={async (e) => {
              if (
                e.target.checked &&
                bookingEmail ===
                  DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES.bookingEmail
              ) {
                await setFieldValue('bookingEmail', venue.bookingEmail ?? email)
              }
              handleChange(e)
            }}
            disabled={readOnlyFields.includes('receiveNotificationEmails')}
          />
        </FormLayout.Row>

        {receiveNotificationEmails && (
          <FormLayout.Row>
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
