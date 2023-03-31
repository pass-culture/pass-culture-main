import { defaultCollectiveDmsApplication } from 'utils/collectiveApiFactories'

import { getLastCollectiveDmsApplication } from '../serializers'

describe('getLastCollectiveDmsApplication', () => {
  it('should return collective dms application with most recent last change date', () => {
    const lastDmsApplication = {
      ...defaultCollectiveDmsApplication,
      lastChangeDate: '2023-02-01T00:00:00Z',
    }
    const otherDmsApplication = {
      ...defaultCollectiveDmsApplication,
      lastChangeDate: '2022-12-25T00:00:00Z',
    }
    expect(
      getLastCollectiveDmsApplication([lastDmsApplication, otherDmsApplication])
    ).toEqual(lastDmsApplication)
  })
})
