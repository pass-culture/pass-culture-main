import { Mode } from 'commons/core/OfferEducational/types'
import { getCollectiveOfferFactory } from 'commons/utils/collectiveApiFactories'

import { OfferEducationalProps } from '../OfferEducational'

import { userOffererFactory } from './userOfferersFactory'

const mockUserOfferer = userOffererFactory({})

export const defaultCreationProps: OfferEducationalProps = {
  userOfferer: mockUserOfferer,
  mode: Mode.CREATION,
  domainsOptions: [{ value: 1, label: 'domain1' }],
  nationalPrograms: [{ value: 1, label: 'nationalProgram1' }],
  isTemplate: false,
}

export const defaultEditionProps: OfferEducationalProps = {
  offer: getCollectiveOfferFactory(),
  userOfferer: mockUserOfferer,
  mode: Mode.EDITION,
  domainsOptions: [{ value: 1, label: 'domain1' }],
  nationalPrograms: [{ value: 1, label: 'nationalProgram1' }],
  isTemplate: false,
}
