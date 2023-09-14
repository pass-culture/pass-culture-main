import { GetOffererResponseModel } from 'apiClient/v1'

interface ApiKeyType {
  maxAllowed: number
  savedApiKeys: string[]
}

export interface Offerer {
  address: string
  apiKey: ApiKeyType
  city: string
  name: string
  postalCode: string
  siren: string
  id: number
  demarchesSimplifieesApplicationId: string
  dsToken: string
}

export const transformOffererResponseModelToOfferer = (
  offerer: GetOffererResponseModel
): Offerer => ({
  address: offerer.address || '',
  apiKey: {
    maxAllowed: offerer.apiKey ? offerer.apiKey.maxAllowed : 0,
    savedApiKeys: offerer.apiKey ? offerer.apiKey.prefixes : [],
  },
  city: offerer.city || '',
  name: offerer.name || '',
  postalCode: offerer.postalCode || '',
  siren: offerer.siren || '',
  id: offerer.id || 0,
  demarchesSimplifieesApplicationId:
    offerer.demarchesSimplifieesApplicationId || '',
  dsToken: offerer.dsToken,
})

export const formatSiren = (siren: string) => {
  if (!siren) {
    return ''
  }

  const blocks = []
  for (let i = 0; i < siren.length; i += 3) {
    blocks.push(siren.substr(i, 3))
  }

  return blocks.join(' ')
}
