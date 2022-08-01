import { IOfferIndividual } from 'core/Offers/types'
import { useAdapter } from 'hooks'

import { getOfferIndividualAdapter } from '.'

const useGetOfferIndividual = (offerId?: string) =>
  useAdapter<IOfferIndividual, null>(() => getOfferIndividualAdapter(offerId))

export default useGetOfferIndividual
