import React from 'react'
import { shallow } from 'enzyme'

import VersoContentOffer from '../VersoContentOffer'
import Icon from '../../../../Icon'
import { navigationLink } from '../../../../../../utils/geolocation'

jest.mock('../../../../../../utils/geolocation', () => ({
  navigationLink: jest.fn(),
}))
describe('src | components | layout | Verso | verso-content | VersoContentOffer | VersoContentOffer', () => {
  let offer

  beforeEach(() => {
    offer = {
      description: 'fake description',
      id: 'X9',
      isEvent: false,
      isThing: true,
      offerType: {
        appLabel: 'Presse — Abonnements',
      },
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
    }
  })

  it('should open link in new navigator tab', () => {
    // given
    const props = {
      distance: '1',
      handleRequestMusicAndShowTypes: jest.fn(),
      offer,
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const distanceElement = wrapper.find('.distance')
    expect(distanceElement.props()).toHaveProperty('target', '_blank')
  })

  it('should match the snapshot', () => {
    // given
    offer.isThing = false
    offer.isEvent = true

    const props = {
      bookables: [],
      distance: '1',
      handleRequestMusicAndShowTypes: jest.fn(),
      isFinished: false,
      maxShownDates: 7,
      offer,
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
      isFinished: false,
      maxShownDates: 7,
      offer,
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
      isFinished: false,
      maxShownDates: 7,
      offer,
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
      isFinished: false,
      maxShownDates: 1,
      offer,
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
        { bookinglimitDatetime: '2019-04-01', id: 2 },
      ],
      distance: '1',
      handleRequestMusicAndShowTypes: jest.fn(),
      isFinished: false,
      maxShownDates: 1,
      offer,
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const liElements = wrapper.find('.dates-info').find('li')
    expect(liElements.at(0).text()).toBe('Dès maintenant et jusqu’au 2019-04-01')
  })

  it('should render offer is unavailable when offer is finished', () => {
    // given
    const props = {
      bookables: [{ id: 1 }, { id: 2 }],
      distance: '1',
      handleRequestMusicAndShowTypes: jest.fn(),
      isFinished: true,
      maxShownDates: 1,
      offer,
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
      isFinished: true,
      maxShownDates: 1,
      offer,
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const venueInfos = wrapper.find('.address-info').find('span')
    expect(venueInfos.at(0).text()).toBe('fake publicName')
    expect(venueInfos.at(1).text()).toBe('72 rue Carnot')
    expect(venueInfos.at(2).text()).toBe('93230')
    expect(venueInfos.at(3).text()).toBe('ROMAINVILLE')
  })

  it('should render informations of the venue and venue name when venue public name is not given', () => {
    // given
    offer.venue.publicName = null
    const props = {
      bookables: [{ id: 1 }, { id: 2 }],
      distance: '1',
      handleRequestMusicAndShowTypes: jest.fn(),
      isFinished: true,
      maxShownDates: 1,
      offer,
    }

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const venueInfos = wrapper.find('.address-info').find('span')
    expect(venueInfos.at(0).text()).toBe('fake name')
    expect(venueInfos.at(1).text()).toBe('72 rue Carnot')
    expect(venueInfos.at(2).text()).toBe('93230')
    expect(venueInfos.at(3).text()).toBe('ROMAINVILLE')
  })

  it('should render distance to the venue when latitude & longitude are given', () => {
    // given
    const nbsp = '\u00a0'
    const props = {
      bookables: [{ id: 1 }, { id: 2 }],
      distance: '1',
      handleRequestMusicAndShowTypes: jest.fn(),
      isFinished: true,
      maxShownDates: 1,
      offer,
    }
    navigationLink.mockReturnValue('this is a fake url')

    // when
    const wrapper = shallow(<VersoContentOffer {...props} />)

    // then
    const venueDistance = wrapper.find('.distance')
    const iconComponent = wrapper.find('.distance').find(Icon)
    expect(venueDistance.prop('href')).toBe('this is a fake url')
    expect(venueDistance.find('span').text()).toBe(`1${nbsp}`)
    expect(iconComponent.prop('svg')).toBe('ico-geoloc-solid2')
    expect(iconComponent.prop('alt')).toBe('Géolocalisation dans Open Street Map')
  })
})
