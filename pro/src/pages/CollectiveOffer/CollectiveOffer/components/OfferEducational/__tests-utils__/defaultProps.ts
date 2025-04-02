import { Mode } from 'commons/core/OfferEducational/types'
import { getCollectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'
import { venueListItemFactory } from 'commons/utils/factories/individualApiFactories'
import { userOffererFactory } from 'commons/utils/factories/userOfferersFactories'

import { OfferEducationalProps } from '../OfferEducational'

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
  venues: [venueListItemFactory()],
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
  venues: [venueListItemFactory()],
}
