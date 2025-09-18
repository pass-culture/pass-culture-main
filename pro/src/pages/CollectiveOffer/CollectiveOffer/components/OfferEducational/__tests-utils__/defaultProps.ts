import { Mode } from '@/commons/core/OfferEducational/types'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { makeVenueListItem } from '@/commons/utils/factories/individualApiFactories'
import { userOffererFactory } from '@/commons/utils/factories/userOfferersFactories'

import type { OfferEducationalProps } from '../OfferEducational'

const mockUserOfferer = userOffererFactory({})

export const defaultCreationProps: OfferEducationalProps = {
  userOfferer: mockUserOfferer,
  mode: Mode.CREATION,
  domainsOptions: [
    {
      id: '1',
      label: 'domain1',
      nationalPrograms: [{ id: 1, name: 'nationalProgram1' }],
    },
  ],
  isTemplate: false,
  venues: [makeVenueListItem({ id: 1 })],
}

export const defaultEditionProps: OfferEducationalProps = {
  offer: getCollectiveOfferFactory(),
  userOfferer: mockUserOfferer,
  mode: Mode.EDITION,
  domainsOptions: [
    {
      id: '1',
      label: 'domain1',
      nationalPrograms: [{ id: 1, name: 'nationalProgram1' }],
    },
  ],
  isTemplate: false,
  venues: [makeVenueListItem({ id: 2 })],
}
