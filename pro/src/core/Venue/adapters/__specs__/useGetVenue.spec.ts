import { renderHook } from '@testing-library/react-hooks'

import { api } from 'apiClient/api'
import { GetVenueResponseModel, VenueTypeCode } from 'apiClient/v1'
import { AccessiblityEnum } from 'core/shared'

import { useGetVenue } from '../getVenueAdapter'

describe('useGetVenue', () => {
  it('should return loading payload then success payload', async () => {
    const apiVenue: GetVenueResponseModel = {
      address: '12 rue du pilas',
      bannerMeta: {
        image_credit: null,
        original_image_url:
          'http://localhost/storage/thumbs/venues/CU_1661432578',
        crop_params: {
          x_crop_percent: 0.005169172932330823,
          y_crop_percent: 0,
          height_crop_percent: 1,
          width_crop_percent: 0.9896616541353384,
        },
      },
      bannerUrl: 'http://localhost/storage/thumbs/venues/CU_1661432577',
      city: 'Paris',
      collectiveDomains: [],
      contact: {
        email: 'test@test.com',
        phoneNumber: '0606060606',
        website: 'http://test.com',
      },
      dateCreated: '2022-07-29T12:18:43.087097Z',
      fieldsUpdated: [],
      id: 'AE',
      isVirtual: false,
      isPermanent: true,
      latitude: 12.3,
      longitude: 14.2,
      managingOfferer: {
        city: 'Paris',
        dateCreated: '2022-07-29T12:18:43.087097Z',
        fieldsUpdated: [],
        id: 'AA',
        isValidated: true,
        name: 'Test structure name',
        postalCode: '75001',
      },
      managingOffererId: 'AA',
      name: 'Lieu name',
      nonHumanizedId: 12,
      postalCode: '75000',
      publicName: 'Cinéma des iles',
      description: 'description du lieu',
      comment: 'commentaire lieu sans siret',
      bookingEmail: 'test@example.com',
      venueTypeCode: VenueTypeCode.LIBRAIRIE,
      withdrawalDetails: '',
      collectiveAccessInformation: '',
      collectiveDescription: 'Description',
      collectiveEmail: 'email@email.email',
      collectiveInterventionArea: [],
      collectiveLegalStatus: null,
      collectiveNetwork: [],
      collectivePhone: '',
      collectiveStudents: [],
      collectiveWebsite: '',
    }

    jest.spyOn(api, 'getVenue').mockResolvedValue(apiVenue)

    const { result, waitForNextUpdate } = renderHook(() => useGetVenue('AE'))
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    const venue = {
      accessibility: {
        [AccessiblityEnum.AUDIO]: false,
        [AccessiblityEnum.MENTAL]: false,
        [AccessiblityEnum.MOTOR]: false,
        [AccessiblityEnum.VISUAL]: false,
        [AccessiblityEnum.NONE]: true,
      },
      address: '12 rue du pilas',
      bannerMeta: {
        image_credit: '',
        original_image_url:
          'http://localhost/storage/thumbs/venues/CU_1661432578',
        crop_params: {
          x_crop_percent: 0.005169172932330823,
          y_crop_percent: 0,
          height_crop_percent: 1,
          width_crop_percent: 0.9896616541353384,
        },
      },
      bannerUrl: 'http://localhost/storage/thumbs/venues/CU_1661432577',
      city: 'Paris',
      collectiveDomains: [],
      contact: {
        email: 'test@test.com',
        phoneNumber: '0606060606',
        webSite: 'http://test.com',
      },
      dateCreated: '2022-07-29T12:18:43.087097Z',
      demarchesSimplifieesApplicationId: null,
      hasPendingBankInformationApplication: null,
      id: 'AE',
      isPermanent: true,
      latitude: 12.3,
      longitude: 14.2,
      postalCode: '75000',
      publicName: 'Cinéma des iles',
      departmentCode: '',
      description: 'description du lieu',
      dmsToken: '',
      fieldsUpdated: [],
      isVirtual: false,
      managingOfferer: {
        city: 'Paris',
        dateCreated: '2022-07-29T12:18:43.087097Z',
        fieldsUpdated: [],
        id: 'AA',
        isValidated: true,
        name: 'Test structure name',
        postalCode: '75001',
      },
      managingOffererId: 'AA',
      nonHumanizedId: 12,
      pricingPoint: null,
      reimbursementPointId: null,
      isVenueVirtual: false,
      mail: 'test@example.com',
      name: 'Lieu name',
      siret: '',
      comment: 'commentaire lieu sans siret',
      venueLabel: '',
      venueType: 'Librairie',
      withdrawalDetails: '',
      collectiveAccessInformation: '',
      collectiveDescription: 'Description',
      collectiveEmail: 'email@email.email',
      collectiveInterventionArea: [],
      collectiveLegalStatus: null,
      collectiveNetwork: [],
      collectivePhone: '',
      collectiveStudents: [],
      collectiveWebsite: '',
    }

    await waitForNextUpdate()
    expect(api.getVenue).toHaveBeenCalledWith('AE')
    const updatedState = result.current
    expect(updatedState.isLoading).toBe(false)
    expect(updatedState.data).toEqual(venue)
    expect(updatedState.error).toBeUndefined()
  })
})
