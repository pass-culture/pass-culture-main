import React from 'react'

import { GetCollectiveOfferTemplateResponseModel } from 'apiClient/v1'
import useNotification from 'components/hooks/useNotification'
import {
  EducationalCategories,
  patchIsTemplateOfferActiveAdapter,
} from 'core/OfferEducational'
import OfferEducationalActions from 'new_components/OfferEducationalActions'
import { SummaryLayout } from 'new_components/SummaryLayout'

import styles from './CollectiveOfferSummary.module.scss'
import CollectiveOfferAccessibilitySection from './components/CollectiveOfferAccessibilitySection'
import CollectiveOfferContactSection from './components/CollectiveOfferContactSection'
import CollectiveOfferNotificationSection from './components/CollectiveOfferNotificationSection'
import CollectiveOfferParticipantSection from './components/CollectiveOfferParticipantSection'
import CollectiveOfferPracticalInformation from './components/CollectiveOfferPracticalInformation'
import CollectiveOfferTypeSection from './components/CollectiveOfferTypeSection'
import CollectiveOfferVenueSection from './components/CollectiveOfferVenueSection'
import { DEFAULT_RECAP_VALUE } from './components/constants'

interface ICollectiveOfferSummaryProps {
  offer: GetCollectiveOfferTemplateResponseModel
  categories: EducationalCategories
}

const CollectiveOfferSummary = ({
  offer,
  categories,
}: ICollectiveOfferSummaryProps) => {
  const notify = useNotification()

  const setIsOfferActive = async () => {
    const response = await patchIsTemplateOfferActiveAdapter({
      offerId: offer.id,
      isActive: !offer.isActive,
    })

    if (response.isOk) {
      return notify.success(response.message)
    }

    notify.error(response.message)
  }

  return (
    <>
      <OfferEducationalActions
        cancelActiveBookings={undefined}
        className={styles.actions}
        isBooked={false}
        isCancellable={offer.isCancellable}
        isOfferActive={offer.isActive}
        setIsOfferActive={setIsOfferActive}
      />
      <SummaryLayout>
        <SummaryLayout.Content fullWidth>
          <SummaryLayout.Section
            title="Détails de l’offre"
            editLink={`/offre/T-${offer.id}/collectif/edition`}
          >
            <CollectiveOfferVenueSection venue={offer.venue} />
            <CollectiveOfferTypeSection offer={offer} categories={categories} />
            <CollectiveOfferPracticalInformation offer={offer} />
            <CollectiveOfferParticipantSection students={offer.students} />
            <CollectiveOfferAccessibilitySection offer={offer} />
            <CollectiveOfferContactSection
              phone={offer.contactPhone}
              email={offer.contactEmail}
            />
            <CollectiveOfferNotificationSection
              bookingEmails={offer.bookingEmails}
            />
          </SummaryLayout.Section>
          <SummaryLayout.Section
            title="Date & Prix"
            editLink={`/offre/T-${offer.id}/collectif/stocks/edition`}
          >
            <SummaryLayout.Row
              title="Détails"
              description={offer.educationalPriceDetail || DEFAULT_RECAP_VALUE}
            />
          </SummaryLayout.Section>
        </SummaryLayout.Content>
      </SummaryLayout>
    </>
  )
}

export default CollectiveOfferSummary
