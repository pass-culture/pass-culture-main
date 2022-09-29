import { useFormikContext } from 'formik'
import React from 'react'

import { REIMBURSEMENT_RULES } from 'core/Finances'
import { TOffererName } from 'core/Offerers/types'
import { IOfferSubCategory } from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { OfferRefundWarning, WithdrawalReminder } from 'new_components/Banner'
import FormLayout from 'new_components/FormLayout'
import { Checkbox, InfoBox, TextArea, TextInput } from 'ui-kit'

import { IOfferIndividualFormValues } from '../types'

import { TicketWithdrawal } from './TicketWithdrawal'
import { Venue } from './Venue'

export interface IUsefulInformationsProps {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  isUserAdmin: boolean
  offerSubCategory?: IOfferSubCategory
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
}: IUsefulInformationsProps): JSX.Element => {
  const {
    values: { subCategoryFields },
  } = useFormikContext<IOfferIndividualFormValues>()

  const displayNoRefundWarning =
    offerSubCategory?.reimbursementRule === REIMBURSEMENT_RULES.NOT_REIMBURSED

  const displayWithdrawalReminder =
    !offerSubCategory?.isEvent && !isVenueVirtual

  return (
    <FormLayout.Section
      title="Informations pratiques"
      description="Les informations pratiques permettent de donner aux utilisateurs des informations sur le retrait de leur commande."
    >
      <Venue
        offererNames={offererNames}
        venueList={venueList}
        readOnlyFields={readOnlyFields}
      />

      {displayNoRefundWarning && (
        <FormLayout.Row>
          <OfferRefundWarning />
        </FormLayout.Row>
      )}
      {displayWithdrawalReminder && (
        <FormLayout.Row>
          <WithdrawalReminder />
        </FormLayout.Row>
      )}

      {subCategoryFields.includes('withdrawalType') && (
        <TicketWithdrawal readOnlyFields={readOnlyFields} />
      )}

      <FormLayout.Row
        sideComponent={
          <InfoBox
            type="info"
            text={
              isVenueVirtual
                ? 'Indiquez ici tout ce qui peut être utile au bénéficiaire pour le retrait de l’offre. En renseignant ces informations depuis votre page lieu, elles s’appliqueront par défaut à toutes vos offres.'
                : 'Indiquez ici tout ce qui peut être utile au bénéficiaire pour le retrait de l’offre.'
            }
            link={{
              isExternal: true,
              to: 'https://aide.passculture.app/hc/fr/articles/4413389597329--Acteurs-Culturels-Quelles-modalit%C3%A9s-de-retrait-indiquer-pour-ma-structure-',
              text: 'En savoir plus',
              'aria-label': 'en savoir plus sur les modalités de retrait',
            }}
          />
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
            'Exemples : une autre adresse, un horaire d’accès, un délai de retrait, un guichet spécifique, un code d’accès, une communication par e-mail...'
          }
        />
      </FormLayout.Row>
      {isVenueVirtual && (
        <FormLayout.Row
          sideComponent={
            <InfoBox
              type="info"
              text={
                "Lien vers lequel seront renvoyés les bénéficiaires ayant réservé votre offre sur l'application pass Culture."
              }
            />
          }
        >
          <TextInput
            label="URL d’accès à l’offre"
            name="url"
            type="text"
            placeholder="https://exemple.com"
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
