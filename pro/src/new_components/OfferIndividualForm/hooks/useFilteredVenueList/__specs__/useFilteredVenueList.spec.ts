import '@testing-library/jest-dom'

import { renderHook } from '@testing-library/react-hooks'

import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers'
import { TOfferIndividualVenue } from 'core/Venue/types'

import { useFilteredVenueList } from '../'
import { IUseFilteredVenueListProps } from '../useFilteredVenueList'

describe('useFilteredVenueList', () => {
  let props: IUseFilteredVenueListProps
  let virtualVenue: TOfferIndividualVenue

  beforeEach(() => {
    virtualVenue = {
      id: 'CC',
      name: 'Lieu online CC',
      managingOffererId: 'A',
      isVirtual: true,
      withdrawalDetails: '',
      accessibility: {
        visual: false,
        mental: false,
        audio: false,
        motor: false,
        none: true,
      },
    }
    const venueList = [
      {
        id: 'AA',
        name: 'Lieu offline AA',
        managingOffererId: 'A',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
      },
      {
        id: 'BB',
        name: 'Lieu offline BB',
        managingOffererId: 'A',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
      },
    ]
    const subCategories = [
      {
        id: 'A-A',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'A-B',
        categoryId: 'A',
        proLabel: 'Sous catégorie offline de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'A-C',
        categoryId: 'A',
        proLabel: 'Sous catégorie online or offline de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE_OR_OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
    ]

    props = {
      subCategories,
      subcategoryId: '',
      venueList,
    }
  })

  it('should not filter venue on isVirtual when subCatagory is not selected', async () => {
    props = {
      ...props,
      venueList: [...props.venueList, virtualVenue],
    }
    const { result } = renderHook(() => useFilteredVenueList(props))
    expect(result.current.length).toEqual(3)
    expect(result.current[0].id).toEqual('AA')
    expect(result.current[1].id).toEqual('BB')
    expect(result.current[2].id).toEqual('CC')
  })
  it('should not filter venue on isVirtual when subCatagory is ONLINE or OFFLINE', async () => {
    props = {
      ...props,
      subcategoryId: 'A-C',
      venueList: [...props.venueList, virtualVenue],
    }
    const { result } = renderHook(() => useFilteredVenueList(props))
    expect(result.current.length).toEqual(3)
    expect(result.current[0].id).toEqual('AA')
    expect(result.current[1].id).toEqual('BB')
    expect(result.current[2].id).toEqual('CC')
  })
  it('should filter venue on isVirtual when subCatagory is ONLINE only', async () => {
    props = {
      ...props,
      subcategoryId: 'A-A',
      venueList: [...props.venueList, virtualVenue],
    }
    const { result } = renderHook(() => useFilteredVenueList(props))
    expect(result.current.length).toEqual(1)
    expect(result.current[0].id).toEqual('CC')
  })
  it('should filter venue on not isVirtual when subCatagory is OFFLINE only', async () => {
    props = {
      ...props,
      subcategoryId: 'A-B',
      venueList: [...props.venueList, virtualVenue],
    }
    const { result } = renderHook(() => useFilteredVenueList(props))
    expect(result.current.length).toEqual(2)
    expect(result.current[0].id).toEqual('AA')
    expect(result.current[1].id).toEqual('BB')
  })
})
