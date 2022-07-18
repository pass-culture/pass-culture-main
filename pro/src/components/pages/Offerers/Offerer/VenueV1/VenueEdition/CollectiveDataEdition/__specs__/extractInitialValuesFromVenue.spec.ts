import { COLLECTIVE_DATA_FORM_INITIAL_VALUES } from '../CollectiveDataForm/initialValues'
import { StudentLevels } from 'apiClient/v1'
import { VenueCollectiveInformation } from 'core/Venue/types'
import { extractInitialValuesFromVenue } from '../CollectiveDataForm/utils/extractInitialValuesFromVenue'

describe('extractInitialValuesFromVenue', () => {
  it('should extract initial values', () => {
    const venue: VenueCollectiveInformation = {
      collectiveDescription: 'description EAC',
      collectiveDomains: [{ id: 1, name: 'domain1' }],
      collectiveEmail: null,
      collectiveInterventionArea: null,
      collectiveLegalStatus: { id: 2, name: 'Entreprise' },
      collectiveNetwork: null,
      collectivePhone: null,
      collectiveStudents: [
        StudentLevels.CAP_1RE_ANN_E,
        StudentLevels.CAP_2E_ANN_E,
      ],
      collectiveWebsite: null,
    }

    expect(extractInitialValuesFromVenue(venue)).toStrictEqual({
      collectiveDescription: 'description EAC',
      collectiveStudents: [
        StudentLevels.CAP_1RE_ANN_E,
        StudentLevels.CAP_2E_ANN_E,
      ],
      collectiveWebsite: COLLECTIVE_DATA_FORM_INITIAL_VALUES.collectiveWebsite,
      collectivePhone: COLLECTIVE_DATA_FORM_INITIAL_VALUES.collectivePhone,
      collectiveEmail: COLLECTIVE_DATA_FORM_INITIAL_VALUES.collectiveEmail,
      collectiveLegalStatus: '2',
      collectiveDomains: ['1'],
      collectiveNetwork: [],
      collectiveInterventionArea:
        COLLECTIVE_DATA_FORM_INITIAL_VALUES.collectiveInterventionArea,
      'search-collectiveDomains': '',
      'search-collectiveInterventionArea': '',
      'search-collectiveNetwork': '',
      'search-collectiveStudents': '',
    })
  })
})
