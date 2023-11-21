import { Feature } from 'pages/AdageIframe/app/types'
import { EducationalDomain } from 'pages/AdageIframe/app/types/offers'

import { client } from './pcapiClient'

export const preBookStock = (stockId: number): Promise<number> => {
  return client.post('/adage-iframe/bookings', { stockId })
}

export const getFeatures = (): Promise<Feature[]> =>
  client.get('/adage-iframe/features')

export const getEducationalDomains = (): Promise<EducationalDomain[]> =>
  client.get('/collective/educational-domains')
