import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { DisplayOfferInAppLink } from '@/components/DisplayOfferInAppLink/DisplayOfferInAppLink'
import { OfferAppPreview } from '@/components/OfferAppPreview/OfferAppPreview'
import { SummaryAside } from '@/components/SummaryLayout/SummaryAside'
import { SummaryContent } from '@/components/SummaryLayout/SummaryContent'
import { SummaryDescriptionList } from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummaryLayout } from '@/components/SummaryLayout/SummaryLayout'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'
import phoneStrokeIcon from '@/icons/stroke-phone.svg'
import { computeAddressDisplayName } from '@/repository/venuesService'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './IndividualOfferSummaryLocationScreen.module.scss'

export interface IndividualOfferSummaryLocationScreenProps {
  offer: GetIndividualOfferWithAddressResponseModel
}
export function IndividualOfferSummaryLocationScreen({
  offer,
}: Readonly<IndividualOfferSummaryLocationScreenProps>) {
  const mode = useOfferWizardMode()

  return (
    <SummaryLayout>
      <SummaryContent>
        <SummarySection
          title="Localisation"
          editLink={getIndividualOfferUrl({
            offerId: offer.id,
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION,
            mode: OFFER_WIZARD_MODE.EDITION,
          })}
          aria-label="Modifier la localisation de l’offre"
        >
          {!offer.isDigital && (
            <SummarySubSection title="Où profiter de l’offre ?">
              <SummaryDescriptionList
                descriptions={[
                  {
                    title: 'Intitulé',
                    text: offer.location?.label || '-',
                  },
                  {
                    title: 'Adresse',
                    text: offer.location
                      ? computeAddressDisplayName(offer.location, false)
                      : '-',
                  },
                ]}
              />
            </SummarySubSection>
          )}
          {offer.isDigital && (
            <SummarySubSection title="Où profiter de l’offre ?">
              <SummaryDescriptionList
                descriptions={[
                  {
                    title: 'URL d’accès à l’offre',
                    text: offer.url || ' - ',
                  },
                ]}
              />
            </SummarySubSection>
          )}
        </SummarySection>
      </SummaryContent>
      <SummaryAside>
        <div className={styles['title-container']}>
          <SvgIcon
            src={phoneStrokeIcon}
            alt=""
            width="24"
            className={styles['icon-info-phone']}
          />
          <h2 className={styles['title']}>Aperçu dans l’app</h2>
        </div>

        <OfferAppPreview offer={offer} />

        {mode === OFFER_WIZARD_MODE.READ_ONLY && (
          <div>
            <DisplayOfferInAppLink
              id={offer.id}
              variant={ButtonVariant.SECONDARY}
              className={styles['app-link']}
            >
              Visualiser dans l’app
            </DisplayOfferInAppLink>
          </div>
        )}
      </SummaryAside>
    </SummaryLayout>
  )
}
