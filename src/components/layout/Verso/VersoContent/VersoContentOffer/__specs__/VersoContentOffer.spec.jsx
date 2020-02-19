import { shallow } from 'enzyme'
import React from 'react'

import { navigationLink } from '../../../../../../utils/geolocation'
import Icon from '../../../../Icon/Icon'
import VersoActionsBar from '../VersoActionsBar/VersoActionsBar'
import VersoContentOffer from '../VersoContentOffer'

jest.mock('../../../../../../utils/geolocation', () => ({
  navigationLink: jest.fn()
}))

describe('components | VersoContentOffer', () => {
  let offer

  beforeEach(() => {
    offer = {
      description: 'fake description',
      id: 'X9',
      isEvent: false,
      isThing: true,
      offerType: {
        appLabel: 'Presse — Abonnements'
      },
      product: {
        description: 'fake description do not use'
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
        publicName: 'fake publicName'
      }
    }
  })

  it('should match the snapshot', () => {
    // given
    offer.isThing = false
    offer.isEvent = true

    const props = {
      bookables: [],
      distance: '1',
      handleRequestMusicAndShowTypes: jest.fn(),
      isNotBookable: false,
      maxShownDates: 7,
      offer,
      style: 'Rap / Contenders',
      userGeolocation: {
        latitude: null,
        longitude: null
      }
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render offer "what" when description is given', () => {
    // given
    const props = {
      bookables: [],
      distance: '1',
      handleRequestMusicAndShowTypes: jest.fn(),
      isNotBookable: false,
      maxShownDates: 7,
      offer,
      userGeolocation: {
        latitude: null,
        longitude: null
      }
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
      handleRequestMusicAndShowTypes: jest.fn(),
      isNotBookable: false,
      maxShownDates: 7,
      offer,
      userGeolocation: {
        latitude: null,
        longitude: null
      }
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
      handleRequestMusicAndShowTypes: jest.fn(),
      isNotBookable: false,
      maxShownDates: 1,
      offer,
      userGeolocation: {
        latitude: null,
        longitude: null
      }
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
        { bookinglimitDatetime: '2019-04-09', id: 2 }
      ],
      distance: '1',
      handleRequestMusicAndShowTypes: jest.fn(),
      isNotBookable: false,
      maxShownDates: 1,
      offer,
      userGeolocation: {
        latitude: null,
        longitude: null
      }
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
        { bookinglimitDatetime: undefined, id: 2 }
      ],
      distance: '1',
      handleRequestMusicAndShowTypes: jest.fn(),
      isNotBookable: false,
      maxShownDates: 1,
      offer,
      userGeolocation: {
        latitude: null,
        longitude: null
      }
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
      bookables: [
      ],
      distance: '1',
      handleRequestMusicAndShowTypes: jest.fn(),
      isNotBookable: false,
      maxShownDates: 1,
      offer,
      userGeolocation: {
        latitude: null,
        longitude: null
      }
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
      handleRequestMusicAndShowTypes: jest.fn(),
      isNotBookable: true,
      maxShownDates: 1,
      offer,
      userGeolocation: {
        latitude: null,
        longitude: null
      }
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
      handleRequestMusicAndShowTypes: jest.fn(),
      isNotBookable: true,
      maxShownDates: 1,
      offer,
      userGeolocation: {
        latitude: null,
        longitude: null
      }
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const address = wrapper
      .find('address')
      .at(0)
      .text()
    expect(address).toBe('fake publicName72 rue Carnot93230ROMAINVILLE')
  })

  it('should render informations of the venue and venue name when venue public name is not given', () => {
    // given
    offer.venue.publicName = null
    const props = {
      bookables: [{ id: 1 }, { id: 2 }],
      distance: '1',
      handleRequestMusicAndShowTypes: jest.fn(),
      isNotBookable: true,
      maxShownDates: 1,
      offer,
      userGeolocation: {
        latitude: null,
        longitude: null
      }
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const address = wrapper
      .find('address')
      .at(0)
      .text()
    expect(address).toBe('fake name72 rue Carnot93230ROMAINVILLE')
  })

  describe('distance informations', () => {
    describe('when it is an event or a cultural thing', () => {
      it('should render distance and itinerary link to the venue', () => {
        // given
        const props = {
          bookables: [{ id: 1 }, { id: 2 }],
          distance: '1',
          handleRequestMusicAndShowTypes: jest.fn(),
          offer,
          userGeolocation: {
            latitude: null,
            longitude: null
          }
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
          handleRequestMusicAndShowTypes: jest.fn(),
          offer,
          userGeolocation: {
            latitude: null,
            longitude: null
          }
        }
        navigationLink.mockReturnValue('this is a fake url')

        // when
        const wrapper = shallow(<VersoContentOffer {...props} />)

        // then
        const venueDistance = wrapper.find({ children: 'À 1 km' })
        const iconComponent = wrapper
          .find(Icon)
          .at(0)
          .find(Icon)
        expect(venueDistance).toHaveLength(1)
        expect(iconComponent.prop('svg')).toBeDefined()
        expect(iconComponent.prop('alt')).toBe('')
      })

      it('should open distance link in new navigator tab', () => {
        // given
        const props = {
          bookables: [],
          distance: '1',
          handleRequestMusicAndShowTypes: jest.fn(),
          offer,
          userGeolocation: {
            latitude: null,
            longitude: null
          }
        }

        // when
        const wrapper = shallow(<VersoContentOffer {...props} />)

        // then
        const distanceVenue = wrapper.find('a').first()
        expect(distanceVenue.props()).toHaveProperty('target', '_blank')
      })

      it('should remove "À" character when user position is unknown', () => {
        // given
        const props = {
          bookables: [{ id: 1 }, { id: 2 }],
          distance: '-',
          handleRequestMusicAndShowTypes: jest.fn(),
          offer,
          userGeolocation: {
            latitude: null,
            longitude: null
          }
        }
        navigationLink.mockReturnValue('this is a fake url')

        // when
        const wrapper = shallow(<VersoContentOffer {...props} />)

        // then
        const venueDistance = wrapper.find({ children: '-' })
        expect(venueDistance).toHaveLength(1)
      })

      it('should render itinerary link', () => {
        // given
        const props = {
          bookables: [{ id: 1 }, { id: 2 }],
          distance: '1',
          handleRequestMusicAndShowTypes: jest.fn(),
          offer,
          userGeolocation: {
            latitude: null,
            longitude: null
          }
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
          handleRequestMusicAndShowTypes: jest.fn(),
          offer,
          userGeolocation: {
            latitude: null,
            longitude: null
          }
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
          handleRequestMusicAndShowTypes: jest.fn(),
          offer: offerWithoutCoordinates,
          userGeolocation: {
            latitude: null,
            longitude: null
          }
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
        booking: {
          completedUrl: 'http://fake-url.com'
        },
        bookables: [],
        isCancelled: false,
        distance: '1',
        handleRequestMusicAndShowTypes: jest.fn(),
        offer: {
          id: 'ID'
        },
        userGeolocation: {
          latitude: null,
          longitude: null
        }
      }

      // when
      const wrapper = shallow(<VersoContentOffer {...props} />)

      // then
      const linkOffer = wrapper.find(VersoActionsBar)
      expect(linkOffer).toHaveLength(1)
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
        handleRequestMusicAndShowTypes: jest.fn(),
        offer: {
          id: 'ID'
        },
        userGeolocation: {
          latitude: null,
          longitude: null
        }
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
        handleRequestMusicAndShowTypes: jest.fn(),
        offer: {
          id: 'ID'
        },
        userGeolocation: {
          latitude: null,
          longitude: null
        }
      }

      // when
      const wrapper = shallow(<VersoContentOffer {...props} />)

      // then
      const linkOffer = wrapper.find(VersoActionsBar)
      expect(linkOffer).toHaveLength(0)
    })
  })
})
