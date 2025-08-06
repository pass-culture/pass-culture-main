import {
  CollectiveLocationType,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import {
  Description,
  SummaryDescriptionList,
} from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'
import { getInterventionAreaLabels } from '@/pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/Offers/OfferDetails/OfferInterventionArea'

import styles from '../CollectiveOfferSummary.module.scss'

interface CollectiveOfferLocationSectionProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
}

const getLocationInformation = ({
  offer,
}: CollectiveOfferLocationSectionProps) => {
  const offerLocation = offer.location
  if (offerLocation?.locationType === CollectiveLocationType.ADDRESS) {
    const { label, street, city, postalCode } = offerLocation.address || {}
    return (
      <div className={styles['location-information']}>
        <p>Intitulé : {label ?? '-'}</p>
        <p>
          Adresse : {street}, {postalCode}, {city}
        </p>
      </div>
    )
  }

  const interventionAreas = getInterventionAreaLabels(offer.interventionArea)
  if (offerLocation?.locationType === CollectiveLocationType.SCHOOL) {
    return (
      <div className={styles['location-information']}>
        <p>Dans l’établissement scolaire</p>
        <p>Zone de mobilité : {interventionAreas}</p>
      </div>
    )
  }

  return (
    <div className={styles['location-information']}>
      <p>À déterminer avec l’enseignant</p>
      <p>Commentaire : {offerLocation?.locationComment ?? '-'}</p>
      <p>Zone de mobilité : {interventionAreas}</p>
    </div>
  )
}

export const CollectiveOfferLocationSection = ({
  offer,
}: CollectiveOfferLocationSectionProps) => {
  const descriptions: Description[] = [
    { text: getLocationInformation({ offer }) },
  ]

  return (
    <SummarySubSection title="Localisation de l’événement">
      <SummaryDescriptionList descriptions={descriptions} />
    </SummarySubSection>
  )
}
