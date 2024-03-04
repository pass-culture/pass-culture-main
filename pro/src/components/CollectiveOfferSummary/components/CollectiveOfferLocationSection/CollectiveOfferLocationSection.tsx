import { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import {
  Description,
  SummaryDescriptionList,
} from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import useNotification from 'hooks/useNotification'
import { getInterventionAreaLabels } from 'pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/Offers/OfferDetails/OfferInterventionArea/OfferInterventionArea'
import Spinner from 'ui-kit/Spinner/Spinner'

import { formatOfferEventAddress } from '../utils/formatOfferEventAddress'

interface CollectiveOfferLocationSectionProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
}

export default function CollectiveOfferLocationSection({
  offer,
}: CollectiveOfferLocationSectionProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [descriptions, setDescription] = useState<Description[]>([])
  const notify = useNotification()

  useEffect(() => {
    const getVenue = async () => {
      setIsLoading(true)
      try {
        const venueApi = await api.getVenue(offer.venue.id)

        setDescription([
          ...descriptions,
          {
            text: formatOfferEventAddress(offer.offerVenue, venueApi),
          },
        ])
      } catch (e) {
        notify.error(
          'Une erreur est survenue lors de la récupération de votre lieu'
        )
      }
      setIsLoading(false)
    }

    getVenue()
  }, [offer.venue.id, offer.offerVenue])

  const interventionAreas = getInterventionAreaLabels(offer.interventionArea)

  if (isLoading) {
    return <Spinner />
  }

  if (interventionAreas) {
    descriptions.push({
      title: 'Zone de mobilité pour l’évènement',
      text: interventionAreas,
    })
  }

  return (
    <SummarySubSection title="Lieu de l’évènement">
      <SummaryDescriptionList descriptions={descriptions} />
    </SummarySubSection>
  )
}
