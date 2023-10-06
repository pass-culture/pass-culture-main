import { useFormikContext } from 'formik'
import React from 'react'

import { OfferRefundWarning, WithdrawalReminder } from 'components/Banner'
import FormLayout from 'components/FormLayout'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { OffererName } from 'core/Offerers/types'
import { OfferSubCategory } from 'core/Offers/types'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import useActiveFeature from 'hooks/useActiveFeature'
import { Checkbox, InfoBox, TextArea, TextInput } from 'ui-kit'

import styles from '../IndividualOfferForm.module.scss'
import { IndividualOfferFormValues } from '../types'

import { TicketWithdrawal } from './TicketWithdrawal'
import { Venue } from './Venue'

export interface UsefulInformationsProps {
  offererNames: OffererName[]
  venueList: IndividualOfferVenueItem[]
  isUserAdmin: boolean
  offerSubCategory?: OfferSubCategory
  isVenueVirtual: boolean
  readOnlyFields?: string[]
}

const UsefulInformations = ({
  offererNames,
  venueList,
  isUserAdmin,
  offerSubCategory,
  isVenueVirtual,
  readOnlyFields = [],
}: UsefulInformationsProps): JSX.Element => {
  const {
    values: { subCategoryFields, withdrawalType },
  } = useFormikContext<IndividualOfferFormValues>()
  const isBookingContactEnabled = useActiveFeature(
    'WIP_MANDATORY_BOOKING_CONTACT'
  )

  const displayNoRefundWarning =
    offerSubCategory?.reimbursementRule === REIMBURSEMENT_RULES.NOT_REIMBURSED

  const displayWithdrawalReminder =
    !offerSubCategory?.isEvent && !isVenueVirtual

  const displayBookingContact =
    isBookingContactEnabled && offerSubCategory?.canBeWithdrawable

  return (
    <FormLayout.Section title="Informations pratiques">
      <Venue
        offererNames={offererNames}
        venueList={venueList}
        readOnlyFields={readOnlyFields}
      />

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

      {(subCategoryFields.includes('withdrawalType') ||
        Boolean(withdrawalType)) && (
        <TicketWithdrawal readOnlyFields={readOnlyFields} />
      )}

      <FormLayout.Row
        sideComponent={
          <InfoBox
            link={{
              isExternal: true,
              to: 'https://aide.passculture.app/hc/fr/articles/4413389597329--Acteurs-Culturels-Quelles-modalit%C3%A9s-de-retrait-indiquer-pour-ma-structure-',
              text: 'En savoir plus',
              'aria-label': 'en savoir plus sur les modalités de retrait',
              target: '_blank',
              rel: 'noopener noreferrer',
            }}
          >
            {isVenueVirtual
              ? 'Indiquez ici tout ce qui peut être utile au bénéficiaire pour le retrait de l’offre.'
              : 'Indiquez ici tout ce qui peut être utile au bénéficiaire pour le retrait de l’offre. En renseignant ces informations depuis votre page lieu, elles s’appliqueront par défaut à toutes vos offres.'}
          </InfoBox>
        }
      >
        <TextArea
          countCharacters
          isOptional
          label={'Informations de retrait'}
          name="withdrawalDetails"
          maxLength={500}
          disabled={readOnlyFields.includes('withdrawalDetails')}
          placeholder={
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
            placeholder="email@exemple.com"
            disabled={readOnlyFields?.includes('bookingContact')}
          />
        </FormLayout.Row>
      )}

      {isVenueVirtual && (
        <FormLayout.Row
          sideComponent={
            <InfoBox>
              Lien vers lequel seront renvoyés les bénéficiaires ayant réservé
              votre offre sur l'application pass Culture.
            </InfoBox>
          }
        >
          <TextInput
            label="URL d’accès à l’offre"
            name="url"
            type="text"
            placeholder="https://exemple.com"
            disabled={readOnlyFields.includes('url')}
          />
        </FormLayout.Row>
      )}
      {isUserAdmin && (
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
  )
}

export default UsefulInformations
