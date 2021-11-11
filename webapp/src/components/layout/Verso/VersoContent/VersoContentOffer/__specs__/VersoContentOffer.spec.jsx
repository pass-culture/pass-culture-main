import { shallow } from 'enzyme'
import React from 'react'

import { navigationLink } from '../../../../../../utils/geolocation'
import Icon from '../../../../Icon/Icon'
import VersoActionsBar from '../VersoActionsBar/VersoActionsBar'
import VersoContentOffer from '../VersoContentOffer'

jest.mock('../../../../../../utils/geolocation', () => ({
  navigationLink: jest.fn(),
}))

describe('components | VersoContentOffer', () => {
  let offer

  beforeEach(() => {
    offer = {
      description: 'fake description',
      id: 'X9',
      isEvent: false,
      isThing: true,
      product: {
        description: 'fake description do not use',
      },
      productId: 'QE',
      venue: {
        address: '72 rue Carnot',
        city: 'ROMAINVILLE',
        id: 'A9',
        latitude: 2.44072,
        longitude: 48.88381,
        name: 'fake name',
        postalCode: '93230',
        publicName: 'fake publicName',
      },
      withdrawalDetails: 'Some useless details',
    }
  })

  it('should render offer "what" when description is given', () => {
    // given
    const props = {
      bookables: [],
      distance: '1',
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: true,
      maxShownDates: 7,
      offer,
      subcategory: {},
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    expect(wrapper.find('.is-raw-description').text()).toBe('fake description')
  })

  it('should render offer "label" when appLabel is given', () => {
    // given
    const props = {
      bookables: [],
      distance: '1',
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: true,
      maxShownDates: 7,
      offer,
      subcategory: {
        appLabel: 'Presse — Abonnements',
      },
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    expect(wrapper.find('#verso-offer-label').text()).toBe('Presse — Abonnements')
  })

  it('should render event offer infos when offer is event, not finished and booking is available', () => {
    // given
    offer.isEvent = true
    offer.isThing = false

    const props = {
      bookables: [{ id: 1 }, { id: 2 }, { id: 3 }],
      distance: '1',
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: true,
      maxShownDates: 1,
      offer,
      subcategory: {},
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const liElements = wrapper.find('.dates-info').find('li')
    expect(liElements.at(1).text()).toBe('Cliquez sur "j’y vais" pour voir plus de dates.')
  })

  it('should render thing offer infos when offer is thing, not finished and booking is available', () => {
    // given
    const props = {
      bookables: [
        { bookinglimitDatetime: '2019-04-01', id: 1 },
        { bookinglimitDatetime: '2019-04-09', id: 2 },
      ],
      distance: '1',
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: true,
      maxShownDates: 1,
      offer,
      subcategory: {},
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const liElements = wrapper.find('.dates-info').find('li')
    expect(liElements.at(0).text()).toBe('Dès maintenant et jusqu’au 2019-04-01')
  })

  it('should render thing offer infos when offer is thing, not finished, booking is available and no bookinglimitDatetime', () => {
    // given
    const props = {
      bookables: [
        { bookinglimitDatetime: undefined, id: 1 },
        { bookinglimitDatetime: undefined, id: 2 },
      ],
      distance: '1',
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: true,
      maxShownDates: 1,
      offer,
      subcategory: {},
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const liElements = wrapper.find('.dates-info').find('li')
    expect(liElements.at(0).text()).toBe('Dès maintenant')
  })

  it('should render thing offer infos when offer is thing but not bookable', () => {
    // given
    const props = {
      bookables: [],
      distance: '1',
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: true,
      maxShownDates: 1,
      offer,
      subcategory: {},
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const liElements = wrapper.find('.dates-info').find('li')
    expect(liElements.at(0).text()).toBe('Dès maintenant')
  })

  it('should render offer is unavailable when offer is finished', () => {
    // given
    const props = {
      bookables: [{ id: 1 }, { id: 2 }],
      distance: '1',
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: false,
      maxShownDates: 1,
      offer,
      subcategory: {},
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const liElements = wrapper.find('.dates-info').find('li')
    expect(liElements.at(0).text()).toBe('L’offre n’est plus disponible.')
  })

  it('should render informations of the venue and publicName when given', () => {
    // given
    const props = {
      bookables: [{ id: 1 }, { id: 2 }],
      distance: '1',
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: false,
      maxShownDates: 1,
      offer,
      subcategory: {},
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const address = wrapper.find('address').at(0).text()
    expect(address).toBe('fake publicName72 rue Carnot93230ROMAINVILLE')
  })

  it('should render informations of the venue and venue name when venue public name is not given', () => {
    // given
    offer.venue.publicName = null
    const props = {
      bookables: [{ id: 1 }, { id: 2 }],
      distance: '1',
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: false,
      maxShownDates: 1,
      offer,
      subcategory: {},
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const address = wrapper.find('address').at(0).text()
    expect(address).toBe('fake name72 rue Carnot93230ROMAINVILLE')
  })

  it('should not render informations regarding offer distance when distance to reach offer is not provided', () => {
    // given
    const props = {
      bookables: [{ id: 1 }, { id: 2 }],
      distance: null,
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: false,
      maxShownDates: 1,
      offer,
      subcategory: {},
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const distance = wrapper.findWhere(node => node.text() === 'À 20km').first()
    expect(distance).toHaveLength(0)
  })

  it('should render informations regarding offer distance when distance to reach offer is provided', () => {
    // given
    const props = {
      bookables: [{ id: 1 }, { id: 2 }],
      distance: '20km',
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: false,
      maxShownDates: 1,
      offer,
      subcategory: {},
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const distance = wrapper.findWhere(node => node.text() === 'À 20km').first()
    expect(distance).toHaveLength(1)
  })

  it('should render offer withdrawal details whend given', () => {
    // given
    const props = {
      bookables: [],
      distance: '1',
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: true,
      maxShownDates: 7,
      offer,
      subcategory: {},
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const withdrawalLabel = wrapper.find({ children: 'Modalités de retrait' })
    expect(withdrawalLabel).toHaveLength(1)
    const withdrawalDetails = wrapper.find({ children: 'Some useless details' })
    expect(withdrawalDetails).toHaveLength(1)
  })

  it('should not render withdrawal labels when details are empty', () => {
    // given
    const props = {
      bookables: [],
      distance: '1',
      handleRequestCategories: jest.fn(),
      handleRequestMusicAndShowTypes: jest.fn(),
      isBookable: true,
      maxShownDates: 7,
      offer: { ...offer, withdrawalDetails: null },
      subcategory: {},
      userGeolocation: {
        latitude: null,
        longitude: null,
      },
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const withdrawalLabel = wrapper.find({ children: 'Modalités de retrait' })
    expect(withdrawalLabel).toHaveLength(0)
  })

  describe('distance informations', () => {
    describe('when it is an event or a cultural thing', () => {
      it('should render distance and itinerary link to the venue', () => {
        // given
        const props = {
          bookables: [{ id: 1 }, { id: 2 }],
          distance: '1',
          handleRequestCategories: jest.fn(),
          handleRequestMusicAndShowTypes: jest.fn(),
          offer,
          subcategory: {},
          userGeolocation: {
            latitude: null,
            longitude: null,
          },
        }

        // when
        const wrapper = shallow(<VersoContentOffer {...props} />)

        // then
        expect(wrapper.find('a')).toHaveLength(1)
      })

      it('should render distance to the venue', () => {
        // given
        const props = {
          bookables: [{ id: 1 }, { id: 2 }],
          distance: '1 km',
          handleRequestCategories: jest.fn(),
          handleRequestMusicAndShowTypes: jest.fn(),
          offer,
          subcategory: {},
          userGeolocation: {
            latitude: null,
            longitude: null,
          },
        }
        navigationLink.mockReturnValue('this is a fake url')

        // when
        const wrapper = shallow(<VersoContentOffer {...props} />)

        // then
        const venueDistance = wrapper.find({ children: 'À 1 km' })
        const iconComponent = wrapper.find(Icon).at(0).find(Icon)
        expect(venueDistance).toHaveLength(1)
        expect(iconComponent.prop('svg')).toBeDefined()
        expect(iconComponent.prop('alt')).toBe('')
      })

      it('should open distance link in new navigator tab', () => {
        // given
        const props = {
          bookables: [],
          distance: '1',
          handleRequestCategories: jest.fn(),
          handleRequestMusicAndShowTypes: jest.fn(),
          offer,
          subcategory: {},
          userGeolocation: {
            latitude: null,
            longitude: null,
          },
        }

        // when
        const wrapper = shallow(<VersoContentOffer {...props} />)

        // then
        const distanceVenue = wrapper.find('a').first()
        expect(distanceVenue.props()).toHaveProperty('target', '_blank')
      })

      it('should render itinerary link', () => {
        // given
        const props = {
          bookables: [{ id: 1 }, { id: 2 }],
          distance: '1',
          handleRequestCategories: jest.fn(),
          handleRequestMusicAndShowTypes: jest.fn(),
          offer,
          subcategory: {},
          userGeolocation: {
            latitude: null,
            longitude: null,
          },
        }
        navigationLink.mockReturnValue('this is a fake url')

        // when
        const wrapper = shallow(<VersoContentOffer {...props} />)

        // then
        const venueItinerary = wrapper.find('a').at(0)
        const iconComponent = venueItinerary.find(Icon)
        expect(venueItinerary.prop('href')).toBe('this is a fake url')
        expect(venueItinerary.prop('title')).toBe(
          'Ouverture de votre gestionnaire de carte dans une nouvelle fenêtre'
        )
        expect(venueItinerary.find('span').text()).toBe(`Itinéraire`)
        expect(iconComponent.prop('svg')).toBeDefined()
        expect(iconComponent.prop('alt')).toBe('')
      })

      it('should open itinerary link in new navigator tab', () => {
        // given
        const props = {
          bookables: [],
          distance: '1',
          handleRequestCategories: jest.fn(),
          handleRequestMusicAndShowTypes: jest.fn(),
          offer,
          subcategory: {},
          userGeolocation: {
            latitude: null,
            longitude: null,
          },
        }

        // when
        const wrapper = shallow(<VersoContentOffer {...props} />)

        // then
        const venueItinerary = wrapper.find('a').at(0)
        expect(venueItinerary.props()).toHaveProperty('target', '_blank')
      })
    })

    describe('when it is a digital thing', () => {
      let offerWithoutCoordinates
      beforeEach(() => {
        offerWithoutCoordinates = { description: 'digital thing' }
      })

      it('should not render distance nor itinerary link to the venue', () => {
        // given
        const props = {
          bookables: [{ id: 1 }, { id: 2 }],
          distance: '1',
          handleRequestCategories: jest.fn(),
          handleRequestMusicAndShowTypes: jest.fn(),
          offer: offerWithoutCoordinates,
          subcategory: {},
          userGeolocation: {
            latitude: null,
            longitude: null,
          },
        }

        // when
        const wrapper = shallow(<VersoContentOffer {...props} />)

        // then
        expect(wrapper.find('a')).toHaveLength(0)
      })
    })
  })

  describe('when the offer is booked and have a link offer', () => {
    it('should render the offer link', () => {
      // given
      const props = {
        bookables: [],
        isCancelled: false,
        distance: '1',
        handleRequestCategories: jest.fn(),
        handleRequestMusicAndShowTypes: jest.fn(),
        booking: {
          completedUrl: 'http://myfakeurl',
        },
        subcategory: {},
        userGeolocation: {
          latitude: null,
          longitude: null,
        },
      }

      // when
      const wrapper = shallow(<VersoContentOffer {...props} />)

      // then
      const linkOffer = wrapper.find(VersoActionsBar)
      expect(linkOffer).toHaveLength(1)
      expect(linkOffer.prop('url')).toBe('http://myfakeurl')
    })
  })

  describe('when the offer is not booked', () => {
    it('should not render the offer link', () => {
      // given
      offer.id = 'ID'
      const props = {
        bookables: [],
        isCancelled: null,
        distance: '1',
        handleRequestCategories: jest.fn(),
        handleRequestMusicAndShowTypes: jest.fn(),
        offer: {
          id: 'ID',
        },
        subcategory: {},
        userGeolocation: {
          latitude: null,
          longitude: null,
        },
      }

      // when
      const wrapper = shallow(<VersoContentOffer {...props} />)

      // then
      const linkOffer = wrapper.find(VersoActionsBar)
      expect(linkOffer).toHaveLength(0)
    })
  })

  describe('when the offer is cancelled', () => {
    it('should not render the offer link', () => {
      // given
      offer.id = 'ID'
      const props = {
        bookables: [],
        isCancelled: true,
        distance: '1',
        handleRequestCategories: jest.fn(),
        handleRequestMusicAndShowTypes: jest.fn(),
        offer: {
          id: 'ID',
        },
        subcategory: {},
        userGeolocation: {
          latitude: null,
          longitude: null,
        },
      }

      // when
      const wrapper = shallow(<VersoContentOffer {...props} />)

      // then
      const linkOffer = wrapper.find(VersoActionsBar)
      expect(linkOffer).toHaveLength(0)
    })
  })
})
