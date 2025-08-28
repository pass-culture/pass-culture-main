import { useLocation } from 'react-router'

import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'
import { formatPrice } from '@/commons/utils/formatPrice'
import { SummaryDescriptionList } from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'

import styles from './PriceCategoriesSection.module.scss'

interface Props {
  offer: GetIndividualOfferResponseModel
  canBeDuo?: boolean
  shouldShowDivider?: boolean
}

export const PriceCategoriesSection = ({
  offer,
  canBeDuo,
  shouldShowDivider = false,
}: Props) => {
  const mode = useOfferWizardMode()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1

  const isCaledonian = useIsCaledonian()

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
    mode:
      mode === OFFER_WIZARD_MODE.READ_ONLY ? OFFER_WIZARD_MODE.EDITION : mode,
    isOnboarding,
  })

  return (
    <SummarySection
      title="Tarifs"
      editLink={editLink}
      aria-label="Modifier les tarifs de l’offre"
      shouldShowDivider={shouldShowDivider}
    >
      {offer.priceCategories?.map((priceCategory) => (
        <div key={priceCategory.id} className={styles['price-category']}>
          {isCaledonian
            ? formatPacificFranc(convertEuroToPacificFranc(priceCategory.price))
            : formatPrice(priceCategory.price)}{' '}
          - {priceCategory.label}
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
