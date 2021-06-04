import { mount } from 'enzyme'
import React from 'react'
import { Router } from 'react-router'
import OfferTile, { noOp } from '../OfferTile'
import { Link } from 'react-router-dom'
import { DEFAULT_THUMB_URL } from '../../../../../../../utils/thumb'
import { formatSearchResultDate } from '../../../../../../../utils/date/date'
import { createMemoryHistory } from 'history'

jest.mock('../../../../../../../utils/date/date', () => ({
  formatSearchResultDate: jest.fn(),
}))
jest.mock('../../../../../../../utils/config', () => ({
  OBJECT_STORAGE_URL: 'http://storage_path',
}))


describe('src | components | OfferTile', () => {
  let props
  let history

  beforeEach(() => {
    history = createMemoryHistory()
    props = {
      historyPush: history.push,
      hit: {
        offer: {
          dates: [],
          id: 'AE',
          isDuo: false,
          isEvent: false,
          name: 'Avengers - Age of Ultron',
          priceMin: 1.2,
          priceMax: 1.2,
          thumbUrl: '/thumbs/path_to_image',
        },
        venue: {
          departementCode: '54',
          name: 'Librairie kléber',
          publicName: null,
        },
      },
      moduleName: 'Nom du module',
      isSwitching: false,
      trackConsultOffer: jest.fn(),
    }
  })

  it('should render an offer tile with a link', () => {
    // when
    const wrapper = mount(
      <Router history={history}>
        <OfferTile {...props} />
      </Router>
    )

    // then
    const link = wrapper.find(Link)
    expect(link).toHaveLength(1)
    expect(link.prop('to')).toBe(noOp)
    expect(link.prop('onMouseDown')).toStrictEqual(expect.any(Function))
    expect(link.prop('onClick')).toStrictEqual(expect.any(Function))
  })

  it('should render an offer tile with an image when provided', () => {
    // when
    const wrapper = mount(
      <Router history={history}>
        <OfferTile {...props} />
      </Router>
    )

    // then
    const img = wrapper.find('img')
    expect(img).toHaveLength(1)
    expect(img.prop('alt')).toBe('')
    expect(img.prop('src')).toBe('http://storage_path/thumbs/path_to_image')
  })

  it('should render an offer tile with default thumb when no image', () => {
    // given
    props.hit.offer.thumbUrl = null

    // when
    const wrapper = mount(
      <Router history={history}>
        <OfferTile {...props} />
      </Router>
    )

    // then
    const img = wrapper.find('img')
    expect(img).toHaveLength(1)
    expect(img.prop('src')).toBe(DEFAULT_THUMB_URL)
  })

  it('should render an offer tile with venue name when public name is not provided', () => {
    // when
    const wrapper = mount(
      <Router history={history}>
        <OfferTile {...props} />
      </Router>
    )

    // then
    const venue = wrapper.find({ children: 'Librairie kléber' })
    expect(venue).toHaveLength(1)
  })

  it('should render an offer tile with the price', () => {
    // when
    const wrapper = mount(
      <Router history={history}>
        <OfferTile {...props} />
      </Router>
    )

    // then
    const price = wrapper.find({ children: '1,20 €' })
    expect(price).toHaveLength(1)
  })

  it('should render an offer tile with dates when event', () => {
    // given
    const mockedDate = 'À partir du 8 juillet'
    props.hit.offer.dates = [1594300450]
    props.hit.offer.isEvent = true
    formatSearchResultDate.mockReturnValue(mockedDate)

    // when
    const wrapper = mount(
      <Router history={history}>
        <OfferTile {...props} />
      </Router>
    )

    // then
    const date = wrapper.find({ children: `${mockedDate} - ` })
    expect(date).toHaveLength(1)
  })

  it('should render an offer tile with the offer name', () => {
    // when
    const wrapper = mount(
      <Router history={history}>
        <OfferTile {...props} />
      </Router>
    )

    // then
    const offerName = wrapper.find({ children: 'Avengers - Age of Ultron' })
    expect(offerName).toHaveLength(1)
  })

  it('should render an offer tile with venue public name when provided', () => {
    // given
    props.hit.venue.publicName = 'Un autre nom pour la librairie'

    // when
    const wrapper = mount(
      <Router history={history}>
        <OfferTile {...props} />
      </Router>
    )

    // then
    const venue = wrapper.find({ children: 'Un autre nom pour la librairie' })
    expect(venue).toHaveLength(1)
  })

  it('should go to offer when clicking on the link', () => {
    // given
    props.hit.venue.publicName = 'Un autre nom pour la librairie'

    // when
    const wrapper = mount(
      <Router history={history}>
        <OfferTile {...props} />
      </Router>
    )
    const offerLink = wrapper.find(Link)
    offerLink.simulate('click')

    // then
    expect(history.location.pathname).toStrictEqual(`/accueil/details/AE`)
    expect(history.location.search).toStrictEqual('')
    expect(history.location.state).toStrictEqual({ moduleName: 'Nom du module' })
    expect(props.trackConsultOffer).toHaveBeenCalledWith('AE')
  })
})
