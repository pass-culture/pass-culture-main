import { venueHasCollectiveInformation } from '../venueHasCollectiveInformation'

describe('venueHasCollectiveInformation', () => {
  it('should return false when venue has no collective information', () => {
    const venue = {
      collectiveDescription: '',
      collectiveDomains: [],
      collectiveEmail: '',
      collectiveInterventionArea: [],
      collectiveLegalStatus: null,
      collectiveNetwork: [],
      collectivePhone: '',
      collectiveStudents: [],
      collectiveWebsite: '',
    }

    expect(venueHasCollectiveInformation(venue)).toBeFalsy()
  })

  it('should return true when at least one string is not empty', () => {
    const venue = {
      collectiveDescription: 'blabla',
      collectiveDomains: [],
      collectiveEmail: '',
      collectiveInterventionArea: [],
      collectiveLegalStatus: null,
      collectiveNetwork: [],
      collectivePhone: '',
      collectiveStudents: [],
      collectiveWebsite: '',
    }

    expect(venueHasCollectiveInformation(venue)).toBeTruthy()
  })

  it('should return true when at least one array is not empty', () => {
    const venue = {
      collectiveDescription: '',
      collectiveDomains: [],
      collectiveEmail: '',
      collectiveInterventionArea: ['Toute la France'],
      collectiveLegalStatus: null,
      collectiveNetwork: [],
      collectivePhone: '',
      collectiveStudents: [],
      collectiveWebsite: '',
    }

    expect(venueHasCollectiveInformation(venue)).toBeTruthy()
  })
})
