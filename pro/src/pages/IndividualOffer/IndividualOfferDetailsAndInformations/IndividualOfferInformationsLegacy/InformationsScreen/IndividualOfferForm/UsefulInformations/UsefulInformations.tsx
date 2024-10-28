import { useFormikContext } from 'formik'
import React from 'react'

import {
  GetOffererNameResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { REIMBURSEMENT_RULES } from 'commons/core/Finances/constants'
import { OfferRefundWarning } from 'components/Banner/OfferRefundWarning'
import { WithdrawalReminder } from 'components/Banner/WithdrawalReminder'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { IndividualOfferFormValues } from 'pages/IndividualOffer/commons/types'
import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import styles from '../IndividualOfferForm.module.scss'

import { TicketWithdrawal } from './TicketWithdrawal/TicketWithdrawal'
import { Venue } from './Venue/Venue'

export interface UsefulInformationsProps {
  offererNames: GetOffererNameResponseModel[]
  venueList: VenueListItemResponseModel[]
  isUserAdmin: boolean
  offerSubCategory?: SubcategoryResponseModel
  isVenueVirtual: boolean
  readOnlyFields?: string[]
}

export const UsefulInformations = ({
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

  const displayNoRefundWarning =
    offerSubCategory?.reimbursementRule === REIMBURSEMENT_RULES.NOT_REIMBURSED

  const displayWithdrawalReminder =
    !offerSubCategory?.isEvent && !isVenueVirtual

  const displayBookingContact = offerSubCategory?.canBeWithdrawable

  return (
    <FormLayout.Section title="Informations pratiques">
      <Venue
        offererNames={offererNames}
        venueList={venueList}
        readOnlyFields={readOnlyFields}
        hideOfferer
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
