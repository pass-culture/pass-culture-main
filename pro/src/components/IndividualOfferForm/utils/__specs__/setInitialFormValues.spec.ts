import {
  GetIndividualOfferWithAddressResponseModel,
  SubcategoryIdEnum,
  SubcategoryResponseModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { AccessibilityEnum } from 'core/shared/types'
import {
  getOfferVenueFactory,
  getOfferManagingOffererFactory,
  getIndividualOfferFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'

import { buildAccessibilityFormValues } from '../setDefaultInitialFormValues'
import { setInitialFormValues } from '../setInitialFormValues'

describe('buildAccessibilityFormValues', () => {
  it('should return false if venue and access libre values are not defined', () => {
    expect(
      buildAccessibilityFormValues(
        venueListItemFactory({
          audioDisabilityCompliant: null,
          mentalDisabilityCompliant: null,
          motorDisabilityCompliant: null,
          visualDisabilityCompliant: null,
          externalAccessibilityData: null,
        })
      )
    ).toEqual({
      [AccessibilityEnum.AUDIO]: false,
      [AccessibilityEnum.MENTAL]: false,
      [AccessibilityEnum.MOTOR]: false,
      [AccessibilityEnum.VISUAL]: false,
      [AccessibilityEnum.NONE]: false,
    })
  })

  it('should return the venue values if they are defined', () => {
    expect(
      buildAccessibilityFormValues(
        venueListItemFactory({
          audioDisabilityCompliant: true,
          mentalDisabilityCompliant: true,
          motorDisabilityCompliant: true,
          visualDisabilityCompliant: true,
          externalAccessibilityData: null,
        })
      )
    ).toEqual({
      [AccessibilityEnum.AUDIO]: true,
      [AccessibilityEnum.MENTAL]: true,
      [AccessibilityEnum.MOTOR]: true,
      [AccessibilityEnum.VISUAL]: true,
      [AccessibilityEnum.NONE]: false,
    })
  })

  it('should return the acces libre values if they are defined', () => {
    expect(
      buildAccessibilityFormValues(
        venueListItemFactory({
          audioDisabilityCompliant: null,
          mentalDisabilityCompliant: null,
          motorDisabilityCompliant: null,
          visualDisabilityCompliant: null,
          externalAccessibilityData: {
            isAccessibleAudioDisability: true,
            isAccessibleMotorDisability: true,
            isAccessibleMentalDisability: true,
            isAccessibleVisualDisability: true,
          },
        })
      )
    ).toEqual({
      [AccessibilityEnum.AUDIO]: true,
      [AccessibilityEnum.MENTAL]: true,
      [AccessibilityEnum.MOTOR]: true,
      [AccessibilityEnum.VISUAL]: true,
      [AccessibilityEnum.NONE]: false,
    })
  })

  it('should prioritize acces libre values over venue values', () => {
    expect(
      buildAccessibilityFormValues(
        venueListItemFactory({
          audioDisabilityCompliant: true,
          mentalDisabilityCompliant: true,
          motorDisabilityCompliant: true,
          visualDisabilityCompliant: true,
          externalAccessibilityData: {
            isAccessibleAudioDisability: false,
            isAccessibleMotorDisability: false,
            isAccessibleMentalDisability: false,
            isAccessibleVisualDisability: false,
          },
        })
      )
    ).toEqual({
      [AccessibilityEnum.AUDIO]: false,
      [AccessibilityEnum.MENTAL]: false,
      [AccessibilityEnum.MOTOR]: false,
      [AccessibilityEnum.VISUAL]: false,
      [AccessibilityEnum.NONE]: true,
    })
  })
})

describe('setFormReadOnlyFields', () => {
  let offer: GetIndividualOfferWithAddressResponseModel
  let subCategoryList: SubcategoryResponseModel[]
  const venueId = 13
  const offererId = 12

  beforeEach(() => {
    offer = getIndividualOfferFactory({
      id: 12,
      extraData: {
        author: 'Offer author',
        gtl_id: '',
        musicType: '',
        musicSubType: '',
        performer: 'Offer performer',
        ean: '',
        showSubType: '',
        showType: '',
        stageDirector: 'Offer stageDirector',
        speaker: 'Offer speaker',
        visa: '',
      },
      bookingEmail: 'booking@email.com',
      bookingContact: 'roberto@example.com',
      description: 'Offer description',
      durationMinutes: 140,
      isActive: true,
      isDuo: false,
      isEvent: true,
      isDigital: false,
      isNational: false,
      name: 'Offer name',
      subcategoryId: SubcategoryIdEnum.CONCERT,
      url: 'https://offer.example.com',
      externalTicketOfficeUrl: 'https://external.example.com',
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalDelay: 140,
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      venue: getOfferVenueFactory({
        id: venueId,
        managingOfferer: getOfferManagingOffererFactory({ id: offererId }),
      }),
    })
    subCategoryList = [
      subcategoryFactory({
        id: SubcategoryIdEnum.CONCERT,
        categoryId: 'CID',
        isEvent: true,
        conditionalFields: ['stageDirector', 'speaker', 'author', 'performer'],
        canBeDuo: true,
      }),
    ]
  })

  it('should fill initial form values from offer', () => {
    const expectedResult = {
      accessibility: {
        [AccessibilityEnum.AUDIO]: true,
        [AccessibilityEnum.MENTAL]: true,
        [AccessibilityEnum.MOTOR]: true,
        [AccessibilityEnum.VISUAL]: true,
        [AccessibilityEnum.NONE]: false,
      },
      bookingEmail: 'booking@email.com',
      bookingContact: 'roberto@example.com',
      categoryId: 'CID',
      description: 'Offer description',
      isEvent: true,
      isNational: false,
      isDuo: false,
      gtl_id: '',
      musicSubType: '',
      musicType: '',
      name: 'Offer name',
      offererId: offererId.toString(),
      receiveNotificationEmails: true,
      showSubType: '',
      showType: '',
      subCategoryFields: [
        'stageDirector',
        'speaker',
        'author',
        'performer',
        'durationMinutes',
        'isDuo',
      ],
      subcategoryId: SubcategoryIdEnum.CONCERT,
      venueId: venueId.toString(),
      withdrawalDelay: 140,
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      author: 'Offer author',
      performer: 'Offer performer',
      ean: '',
      speaker: 'Offer speaker',
      stageDirector: 'Offer stageDirector',
      visa: '',
      durationMinutes: '2:20',
      url: 'https://offer.example.com',
      externalTicketOfficeUrl: 'https://external.example.com',
    }

    const initialFormValues = setInitialFormValues(offer, subCategoryList, true)
    expect(initialFormValues).toStrictEqual(expectedResult)
  })

  it("should throw error if sub category don't exist", () => {
    expect(() => setInitialFormValues(offer, [], true)).toThrow(
      'La categorie de l’offre est introuvable'
    )
  })
})
