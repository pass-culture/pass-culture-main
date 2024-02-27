import React, { useEffect, useState } from 'react'

import { AppLayout } from 'app/AppLayout'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import {
  EducationalCategories,
  getEducationalCategoriesAdapter,
  Mode,
} from 'core/OfferEducational'
import useNotification from 'hooks/useNotification'
import CollectiveOfferSummaryEditionScreen from 'screens/CollectiveOfferSummaryEdition'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import Spinner from 'ui-kit/Spinner/Spinner'

const CollectiveOfferSummaryEdition = ({
  offer,
  reloadCollectiveOffer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps) => {
  const notify = useNotification()

  const [categories, setCategories] = useState<EducationalCategories | null>(
    null
  )

  useEffect(() => {
    const loadData = async () => {
      const categoriesResponse = await getEducationalCategoriesAdapter()

      if (!categoriesResponse.isOk) {
        return notify.error(categoriesResponse.message)
      }

      setCategories(categoriesResponse.payload)
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadData()
  }, [])

  const isReady = offer !== null && categories !== null

  return (
    <AppLayout layout={'sticky-actions'}>
      {!isReady ? (
        <Spinner />
      ) : (
        <CollectiveOfferLayout subTitle={offer.name} isTemplate={isTemplate}>
          <CollectiveOfferSummaryEditionScreen
            offer={offer}
            categories={categories}
            reloadCollectiveOffer={reloadCollectiveOffer}
            mode={Mode.EDITION}
          />
        </CollectiveOfferLayout>
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferSummaryEdition
)
