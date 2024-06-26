import React from 'react'

import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import { formatPrice } from 'utils/formatPrice'

import styles from './PriceCategoriesSection.module.scss'

interface Props {
  offer: GetIndividualOfferResponseModel
  canBeDuo?: boolean
}

export const PriceCategoriesSection = ({ offer, canBeDuo }: Props) => {
  const mode = useOfferWizardMode()

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.TARIFS,
    mode:
      mode === OFFER_WIZARD_MODE.READ_ONLY ? OFFER_WIZARD_MODE.EDITION : mode,
  })

  return (
    <SummarySection
      title="Tarifs"
      editLink={editLink}
      aria-label="Modifier les tarifs de l’offre"
    >
      {offer.priceCategories?.map((priceCategory) => (
        <div key={priceCategory.id} className={styles['price-category']}>
          {formatPrice(priceCategory.price)} - {priceCategory.label}
        </div>
      ))}
      {canBeDuo && (
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Accepter les réservations "Duo"',
              text: offer.isDuo ? 'Oui' : 'Non',
            },
          ]}
        />
      )}
    </SummarySection>
  )
}
