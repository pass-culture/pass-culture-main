import { GetOffererResponseModel } from '@/apiClient//v1'
import { defaultDMSApplicationForEAC } from '@/commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from '@/commons/utils/factories/individualApiFactories'
import {
  getLastCollectiveDmsApplication,
  getLastDmsApplicationForOfferer,
} from '@/commons/utils/getLastCollectiveDmsApplication'

describe('getLastCollectiveDmsApplication', () => {
  it('should return collective dms application with most recent last change date', () => {
    const firstDmsApplication = {
      ...defaultDMSApplicationForEAC,
      lastChangeDate: '2021-02-01T00:00:00Z',
    }
    const lastDmsApplication = {
      ...defaultDMSApplicationForEAC,
      lastChangeDate: '2023-12-25T00:00:00Z',
    }
    const otherDmsApplication = {
      ...defaultDMSApplicationForEAC,
      lastChangeDate: '2022-12-25T00:00:00Z',
    }
    expect(
      getLastCollectiveDmsApplication([
        firstDmsApplication,
        lastDmsApplication,
        otherDmsApplication,
      ])
    ).toEqual(lastDmsApplication)
  })

  describe('getLastDmsApplicationForOfferer', () => {
    it('should return the last DMS application for a specific venue', () => {
      const venueId = 1
      const offerer: GetOffererResponseModel = {
        ...defaultGetOffererResponseModel,
        managedVenues: [
          {
            ...defaultGetOffererVenueResponseModel,
            id: venueId,
            collectiveDmsApplications: [
              {
                ...defaultDMSApplicationForEAC,
                venueId: venueId,
                application: 1,
                lastChangeDate: '2021-01-01T00:00:00Z',
              },
            ],
          },
          {
            ...defaultGetOffererVenueResponseModel,
            id: venueId + 1, // not the same venue
            collectiveDmsApplications: [
              {
                ...defaultDMSApplicationForEAC,
                venueId: venueId + 1, // not the same venue
                application: 2,
                lastChangeDate: '2023-01-01T00:00:00Z',
              },
            ],
          },
        ],
      }

      const lastDmsApplication = getLastDmsApplicationForOfferer(
        venueId.toString(),
        offerer
      )
      expect(lastDmsApplication?.application).toEqual(1)
    })

    it('should return the last DMS application across all venues if no venueId is provided', () => {
      const offerer: GetOffererResponseModel = {
        ...defaultGetOffererResponseModel,
        managedVenues: [
          {
            ...defaultGetOffererVenueResponseModel,
            collectiveDmsApplications: [
              {
                ...defaultDMSApplicationForEAC,
                application: 1,
                lastChangeDate: '2021-01-01T00:00:00Z',
              },
            ],
          },
          {
            ...defaultGetOffererVenueResponseModel,
            collectiveDmsApplications: [
              {
                ...defaultDMSApplicationForEAC,
                application: 2,
                lastChangeDate: '2020-01-01T00:00:00Z',
              },
            ],
          },
        ],
      }

      const lastDmsApplication = getLastDmsApplicationForOfferer(null, offerer)

      expect(lastDmsApplication?.application).toEqual(1)
    })

    it('should return null if there are no venues', () => {
      const offerer: GetOffererResponseModel = {
        ...defaultGetOffererResponseModel,
        managedVenues: [],
      }

      const lastDmsApplication = getLastDmsApplicationForOfferer(
        'venueId',
        offerer
      )

      expect(lastDmsApplication).toBeNull()
    })

    it('should return null if there are no DMS applications', () => {
      const offerer: GetOffererResponseModel = {
        ...defaultGetOffererResponseModel,
        managedVenues: [
          {
            ...defaultGetOffererVenueResponseModel,
            collectiveDmsApplications: [],
          },
          {
            ...defaultGetOffererVenueResponseModel,
            collectiveDmsApplications: [],
          },
        ],
      }

      const result = getLastDmsApplicationForOfferer(null, offerer)

      expect(result).toBeNull()
    })
  })
})
