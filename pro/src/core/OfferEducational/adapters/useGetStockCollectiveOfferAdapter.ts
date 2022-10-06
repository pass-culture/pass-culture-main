import { useAdapter } from 'hooks'

import { GetStockOfferSuccessPayload } from '../types'

import { getStockCollectiveOfferAdapter } from './getStockCollectiveOfferAdapter'

const useGetStockCollectiveOfferAdapter = (offerId: string) =>
  useAdapter<GetStockOfferSuccessPayload, null>(() =>
    getStockCollectiveOfferAdapter(offerId)
  )

export default useGetStockCollectiveOfferAdapter
