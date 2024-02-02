import { renderHook, waitFor } from '@testing-library/react'

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
          'https://localhost/storage/thumbs/venues/CU_1661432578',
        crop_params: {
          x_crop_percent: 0.005169172932330823,
          y_crop_percent: 0,
          height_crop_percent: 1,
          width_crop_percent: 0.9896616541353384,
        },
      },
      bannerUrl: 'https://localhost/storage/thumbs/venues/CU_1661432577',
      city: 'Paris',
      collectiveDomains: [],
      contact: {
        email: 'test@test.com',
        phoneNumber: '0606060606',
        website: 'https://test.com',
      },
      dateCreated: '2022-07-29T12:18:43.087097Z',
      dmsToken: 'dms-token-12345',
      isVirtual: false,
      isPermanent: true,
      latitude: 12.3,
      longitude: 14.2,
      managingOfferer: {
        city: 'Paris',
        dateCreated: '2022-07-29T12:18:43.087097Z',
        id: 1,
        isValidated: true,
        name: 'Test structure name',
        postalCode: '75001',
      },
      name: 'Lieu name',
      id: 12,
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
      hasAdageId: false,
      collectiveDmsApplications: [],
      visualDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      audioDisabilityCompliant: false,
      motorDisabilityCompliant: false,
    }

    vi.spyOn(api, 'getVenue').mockResolvedValue(apiVenue)

    const { result } = renderHook(() => useGetVenue(12))
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
      banId: '',
      bannerMeta: {
        image_credit: '',
        original_image_url:
          'https://localhost/storage/thumbs/venues/CU_1661432578',
        crop_params: {
          x_crop_percent: 0.005169172932330823,
          y_crop_percent: 0,
          height_crop_percent: 1,
          width_crop_percent: 0.9896616541353384,
        },
      },
      bannerUrl: 'https://localhost/storage/thumbs/venues/CU_1661432577',
      city: 'Paris',
      collectiveDomains: [],
      contact: {
        email: 'test@test.com',
        phoneNumber: '0606060606',
        webSite: 'https://test.com',
      },
      dateCreated: '2022-07-29T12:18:43.087097Z',
      demarchesSimplifieesApplicationId: null,
      hasPendingBankInformationApplication: null,
      isPermanent: true,
      latitude: 12.3,
      longitude: 14.2,
      postalCode: '75000',
      publicName: 'Cinéma des iles',
      departmentCode: '',
      description: 'description du lieu',
      dmsToken: 'dms-token-12345',
      isVirtual: false,
      managingOfferer: {
        city: 'Paris',
        dateCreated: '2022-07-29T12:18:43.087097Z',
        id: 1,
        isValidated: true,
        name: 'Test structure name',
        postalCode: '75001',
      },
      id: 12,
      pricingPoint: null,
      reimbursementPointId: null,
      isVenueVirtual: false,
      mail: 'test@example.com',
      name: 'Lieu name',
      siret: '',
      comment: 'commentaire lieu sans siret',
      venueLabel: null,
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
      adageInscriptionDate: null,
      hasAdageId: false,
      collectiveDmsApplication: null,
      bankAccount: null,
    }

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
    expect(api.getVenue).toHaveBeenCalledWith(12)
    expect(result.current.data).toEqual(venue)
    expect(result.current.error).toBeUndefined()
  })
})
