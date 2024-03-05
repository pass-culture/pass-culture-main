import { Mode } from 'core/OfferEducational'
import { getCollectiveOfferFactory } from 'utils/collectiveApiFactories'

import { OfferEducationalProps } from '../OfferEducational'

import { userOfferersFactory } from './userOfferersFactory'

const mockUserOfferers = userOfferersFactory([{}])

export const defaultCreationProps: OfferEducationalProps = {
  userOfferers: mockUserOfferers,
  mode: Mode.CREATION,
  domainsOptions: [{ value: 1, label: 'domain1' }],
  nationalPrograms: [{ value: 1, label: 'nationalProgram1' }],
  isTemplate: false,
  setOffer: vi.fn(),
}

export const defaultEditionProps: OfferEducationalProps = {
  offer: getCollectiveOfferFactory(),
  userOfferers: mockUserOfferers,
  mode: Mode.EDITION,
  domainsOptions: [{ value: 1, label: 'domain1' }],
  nationalPrograms: [{ value: 1, label: 'nationalProgram1' }],
  isTemplate: false,
  setOffer: vi.fn(),
}
