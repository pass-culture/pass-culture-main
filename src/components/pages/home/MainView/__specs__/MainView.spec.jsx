import { mount } from 'enzyme'
import { parse } from 'query-string'
import React from 'react'
import { MemoryRouter } from 'react-router'
import { Link } from 'react-router-dom'

import { fetchHomepage } from '../../../../../vendor/contentful/contentful'
import AnyError from '../../../../layout/ErrorBoundaries/ErrorsPage/AnyError/AnyError'
import Icon from '../../../../layout/Icon/Icon'
import User from '../../../profile/ValueObjects/User'
import BusinessModule from '../BusinessModule/BusinessModule'
import BusinessPane from '../domain/ValueObjects/BusinessPane'
import ExclusivityPane from '../domain/ValueObjects/ExclusivityPane'
import Offers from '../domain/ValueObjects/Offers'
import OffersWithCover from '../domain/ValueObjects/OffersWithCover'
import ExclusivityModule from '../ExclusivityModule/ExclusivityModule'
import MainView from '../MainView'
import Module from '../Module/Module'

jest.mock('../Module/domain/buildTiles', () => ({
  buildPairedTiles: jest.fn().mockReturnValue([]),
  buildTiles: jest.fn().mockReturnValue([]),
}))
jest.mock('query-string', () => ({
  parse: jest.fn(),
}))
jest.mock('../../../../../vendor/contentful/contentful', () => ({
  fetchHomepage: jest.fn(),
}))
jest.mock('../../../../../vendor/algolia/algolia', () => ({
  fetchAlgolia: jest.fn().mockResolvedValue({ hits: [], nbHits: 5 }),
}))
jest.mock('../domain/parseAlgoliaParameters', () => ({
  parseAlgoliaParameters: jest.fn().mockReturnValue({}),
}))

describe('src | components | MainView', () => {
  let props

  beforeEach(() => {
    fetchHomepage.mockResolvedValue([])
    parse.mockReturnValue({})
    props = {
      geolocation: {
        latitude: 5,
        longitude: 10,
      },
      history: {
        location: {
          search: '',
        },
        push: jest.fn(),
      },
      match: {},
      trackAllModulesSeen: jest.fn(),
      trackAllTilesSeen: jest.fn(),
      updateCurrentUser: jest.fn(),
      user: new User({
        email: 'john.doe@example.fr',
        expenses: {
          all: { actual: 287, max: 500 },
          digital: { actual: 11, max: 200 },
          physical: { actual: 23, max: 200 },
        },
        firstName: 'PC Test Jeune',
        publicName: 'Iron Man',
        wallet_balance: 200.1,
      }),
    }
  })

  afterEach(() => {
    fetchHomepage.mockReset()
  })

  it('should render a Link component with the profil icon', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <MainView {...props} />
      </MemoryRouter>
    )

    // then
    const link = wrapper.find(Link)
    expect(link).toHaveLength(1)
    expect(link.prop('to')).toBe('/accueil/profil')

    const icon = link.find(Icon)
    expect(icon).toHaveLength(1)
    expect(icon.prop('svg')).toBe('ico-informations-white')
  })

  it('should render a title with the user public name', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <MainView {...props} />
      </MemoryRouter>
    )

    // then
    const title = wrapper.find({ children: 'Bonjour Iron Man' })
    expect(title).toHaveLength(1)
  })

  it('should render a subtitle with the user wallet balance', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <MainView {...props} />
      </MemoryRouter>
    )

    // then
    const subtitle = wrapper.find({ children: 'Tu as 200,1 € sur ton pass' })
    expect(subtitle).toHaveLength(1)
  })

  it('should render a module component when module is for offers with cover', async () => {
    // given
    const offersWithCover = new OffersWithCover({
      algolia: { isDuo: true },
      cover: 'my-cover',
      display: { layout: 'one-item-medium' },
    })
    fetchHomepage.mockResolvedValue([offersWithCover])

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <MainView {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    const moduleWithCover = wrapper.find(Module)
    expect(moduleWithCover).toHaveLength(1)
    expect(moduleWithCover.props()).toStrictEqual({
      geolocation: { latitude: 5, longitude: 10 },
      historyPush: expect.any(Function),
      module: offersWithCover,
      row: 0,
      trackAllTilesSeen: props.trackAllTilesSeen,
    })
  })

  it('should render a module component when module is for offers', async () => {
    // given
    const offers = new OffersWithCover({
      algolia: { isDuo: true },
      display: { layout: 'one-item-medium' },
    })
    fetchHomepage.mockResolvedValue([offers])

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <MainView {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    const module = wrapper.find(Module)
    expect(module).toHaveLength(1)
    expect(module.props()).toStrictEqual({
      geolocation: { latitude: 5, longitude: 10 },
      historyPush: expect.any(Function),
      module: offers,
      row: 0,
      trackAllTilesSeen: props.trackAllTilesSeen,
    })
  })

  it('should render a business module component when module is for business information', async () => {
    // given
    fetchHomepage.mockResolvedValue([
      new BusinessPane({
        image: 'my-image',
        title: 'my-title',
        url: 'my-url',
      }),
    ])

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <MainView {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    const module = wrapper.find(BusinessModule)
    expect(module).toHaveLength(1)
  })

  it('should render an exclusivity module component when module is for an exclusive offer', async () => {
    // given
    fetchHomepage.mockResolvedValue([
      new ExclusivityPane({
        alt: 'my alt text',
        image: 'https://www.link-to-my-image.com',
        offerId: 'AE',
      }),
    ])

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <MainView {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    const module = wrapper.find(ExclusivityModule)
    expect(module).toHaveLength(1)
  })

  it('should fetch homepage using entry id from url when provided', async () => {
    // given
    const entryId = 'ABCDE'
    parse.mockReturnValue({ entryId })
    props.history.location.search = entryId
    fetchHomepage.mockResolvedValue([new Offers({})])

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <MainView {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    expect(fetchHomepage).toHaveBeenCalledWith({ entryId })
  })

  it('should render an error page when homepage is not loadable', async () => {
    // Given
    const flushPromises = () => new Promise(setImmediate)
    fetchHomepage.mockRejectedValue(new Error('fetching error'))

    // When
    const wrapper = mount(
      <MemoryRouter>
        <MainView {...props} />
      </MemoryRouter>
    )
    await flushPromises()
    wrapper.update()

    // Then
    const anyError = wrapper.find(AnyError)
    expect(anyError).toHaveLength(1)
  })

  it('should update user last connection date when on page', () => {
    // when
    mount(
      <MemoryRouter>
        <MainView {...props} />
      </MemoryRouter>
    )

    // then
    expect(props.updateCurrentUser).toHaveBeenCalledTimes(1)
  })

  describe('modules tracking', () => {
    it('should track the user who have seen all modules after scroll', async () => {
      // Given
      fetchHomepage.mockResolvedValueOnce([
        new BusinessPane({
          title: 'my-title-1',
        }),
        new BusinessPane({
          title: 'my-title-2',
        }),
        new BusinessPane({
          title: 'my-title-3',
        }),
      ])
      const wrapper = await mount(
        <MemoryRouter>
          <MainView {...props} />
        </MemoryRouter>
      )
      jest.spyOn(document.documentElement, 'clientHeight', 'get').mockImplementationOnce(() => 36)

      // When
      const homeWrapper = wrapper.find('div').first()
      homeWrapper.invoke('onScroll')()

      // Then
      expect(props.trackAllModulesSeen).toHaveBeenCalledWith(3)
    })

    it('should not track the user who have not seen all modules after scroll', async () => {
      // Given
      fetchHomepage.mockResolvedValueOnce([
        new BusinessPane({
          title: 'my-title-1',
        }),
        new BusinessPane({
          title: 'my-title-2',
        }),
        new BusinessPane({
          title: 'my-title-3',
        }),
      ])
      const wrapper = await mount(
        <MemoryRouter>
          <MainView {...props} />
        </MemoryRouter>
      )
      jest.spyOn(document.documentElement, 'clientHeight', 'get').mockImplementationOnce(() => 35)

      // When
      const homeWrapper = wrapper.find('div').first()
      homeWrapper.invoke('onScroll')()

      // Then
      expect(props.trackAllModulesSeen).not.toHaveBeenCalled()
    })

    it('should track the user who have seen all modules without scroll', async () => {
      // Given
      fetchHomepage.mockResolvedValueOnce([
        new BusinessPane({
          title: 'my-title-1',
        }),
        new BusinessPane({
          title: 'my-title-2',
        }),
        new BusinessPane({
          title: 'my-title-3',
        }),
      ])
      jest.spyOn(document.documentElement, 'clientHeight', 'get').mockImplementationOnce(() => 37)

      // When
      await mount(
        <MemoryRouter>
          <MainView {...props} />
        </MemoryRouter>
      )

      // Then
      expect(props.trackAllModulesSeen).toHaveBeenCalledWith(3)
    })

    it('should not track the user who have not seen all modules without scroll', async () => {
      // Given
      fetchHomepage.mockResolvedValueOnce([
        new BusinessPane({
          title: 'my-title-1',
        }),
        new BusinessPane({
          title: 'my-title-2',
        }),
        new BusinessPane({
          title: 'my-title-3',
        }),
      ])
      jest.spyOn(document.documentElement, 'clientHeight', 'get').mockImplementationOnce(() => 35)

      // When
      await mount(
        <MemoryRouter>
          <MainView {...props} />
        </MemoryRouter>
      )

      // Then
      expect(props.trackAllModulesSeen).not.toHaveBeenCalled()
    })
  })
})
