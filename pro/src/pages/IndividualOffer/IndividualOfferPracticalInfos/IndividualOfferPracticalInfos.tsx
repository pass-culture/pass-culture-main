import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_STOCKS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from '@/components/IndividualOfferLayout/utils/getTitle'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferPracticalInfosScreen } from './components/IndividualOfferPracticalInfosScreen'

const IndividualOfferPracticalInfos = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, hasPublishedOfferWithSameEan } = useIndividualOfferContext()

  const getStocksQuery = useSWR(
    offer?.id ? [GET_STOCKS_QUERY_KEY, offer.id] : null,
    ([, offerId]) => api.getStocks(offerId)
  )

  if (!offer || !getStocksQuery.data) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout
      offer={offer}
      title={getTitle(mode)}
      mode={mode}
      venueHasPublishedOfferWithSameEan={hasPublishedOfferWithSameEan}
    >
      <IndividualOfferPracticalInfosScreen
        offer={offer}
        stocks={getStocksQuery.data.stocks}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferPracticalInfos
