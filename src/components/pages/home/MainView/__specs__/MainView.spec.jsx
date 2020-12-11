import { mount } from 'enzyme'
import { parse } from 'query-string'
import React from 'react'
import { act } from 'react-dom/test-utils'
import { MemoryRouter } from 'react-router'

import { fetchHomepage } from '../../../../../vendor/contentful/contentful'
import User from '../../../profile/ValueObjects/User'
import BusinessModule from '../BusinessModule/BusinessModule'
import BusinessPane from '../domain/ValueObjects/BusinessPane'
import ExclusivityPane from '../domain/ValueObjects/ExclusivityPane'
import OffersWithCover from '../domain/ValueObjects/OffersWithCover'
import ExclusivityModule from '../ExclusivityModule/ExclusivityModule'
import MainView from '../MainView'
import Module from '../Module/Module'
import { Link } from 'react-router-dom'
import Icon from '../../../../layout/Icon/Icon'
import { Provider } from 'react-redux'
import { getStubStore } from '../../../../../utils/stubStore'
import { setCustomUserId } from '../../../../../notifications/setUpBatchSDK'

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
jest.mock('../../../../../notifications/setUpBatchSDK', () => ({
  setCustomUserId: jest.fn(),
}))

const moduleId = 'moduleId'

describe('src | components | MainView', () => {
  let props

  beforeEach(() => {
    fetchHomepage.mockResolvedValue([])
    parse.mockReturnValue({})
    props = {
      algoliaMapping: {},
      displayedModules: [],
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

  it('should render a module component when module is for offers with cover', async () => {
    // given
    const results = { hits: [], nbHits: 0, parsedParameters: {} }
    props.algoliaMapping = { moduleId: results }
    const offersWithCover = new OffersWithCover({
      moduleId,
      algolia: { isDuo: true },
      cover: 'my-cover',
      display: { layout: 'one-item-medium' },
    })
    props.displayedModules = [offersWithCover]

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
      results,
    })
  })

  it('should render a module component when module is for offers', async () => {
    // given
    const results = { hits: [], nbHits: 0, parsedParameters: {} }
    props.algoliaMapping = { moduleId: results }
    const offers = new OffersWithCover({
      algolia: { isDuo: true },
      display: { layout: 'one-item-medium' },
      moduleId,
    })
    props.displayedModules = [offers]

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
      results,
    })
  })

  it('should render a business module component when module is for business information', async () => {
    // given
    props.displayedModules = [
      new BusinessPane({
        image: 'my-image',
        title: 'my-title',
        url: 'my-url',
      }),
    ]

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
    props.displayedModules = [
      new ExclusivityPane({
        alt: 'my alt text',
        image: 'https://www.link-to-my-image.com',
        offerId: 'AE',
      }),
    ]

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

  it('should have called batchSDK custom id setup with userId to enable notifications', () => {
    // given
    props.user = new User({
      email: 'john.doe@example.fr',
      expenses: {
        all: { actual: 287, max: 500 },
        digital: { actual: 11, max: 200 },
        physical: { actual: 23, max: 200 },
      },
      firstName: 'PC Test Jeune',
      publicName: 'Iron Man',
      wallet_balance: 200.1,
      id: 'myID',
    })

    // when
    mount(
      <MemoryRouter>
        <MainView {...props} />
      </MemoryRouter>
    )

    // then
    expect(setCustomUserId).toHaveBeenCalledWith('myID')
  })

  describe('modules tracking', () => {
    it('should track the user who have seen all modules after scroll', async () => {
      // Given
      props.displayedModules = [
        new BusinessPane({ image: 'my-image-1' }),
        new BusinessPane({ image: 'my-image-2' }),
        new BusinessPane({ image: 'my-image-3' }),
      ]
      const wrapper = await mount(
        <MemoryRouter>
          <MainView {...props} />
        </MemoryRouter>
      )
      jest.spyOn(document.documentElement, 'clientHeight', 'get').mockImplementationOnce(() => 36)

      // When
      const homeWrapper = wrapper.find('div').first()
      act(() => {
        homeWrapper.invoke('onScroll')()
      })

      // Then
      expect(props.trackAllModulesSeen).toHaveBeenCalledWith(3)
    })

    it('should not track the user who have not seen all modules after scroll', async () => {
      // Given
      props.displayedModules = [
        new BusinessPane({ image: 'my-image-1' }),
        new BusinessPane({ image: 'my-image-2' }),
        new BusinessPane({ image: 'my-image-3' }),
      ]
      const wrapper = await mount(
        <MemoryRouter>
          <MainView {...props} />
        </MemoryRouter>
      )
      jest.spyOn(document.documentElement, 'clientHeight', 'get').mockImplementationOnce(() => 35)

      // When
      const homeWrapper = wrapper.find('div').first()
      act(() => {
        homeWrapper.invoke('onScroll')()
      })

      // Then
      expect(props.trackAllModulesSeen).not.toHaveBeenCalled()
    })

    it('should track the user who have seen all modules without scroll', async () => {
      // Given
      props.algoliaMapping = {}
      props.displayedModules = [
        new BusinessPane({ image: 'my-image-1' }),
        new BusinessPane({ image: 'my-image-2' }),
        new BusinessPane({ image: 'my-image-3' }),
      ]
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
      props.displayedModules = [
        new BusinessPane({ image: 'my-image-1' }),
        new BusinessPane({ image: 'my-image-2' }),
        new BusinessPane({ image: 'my-image-3' }),
      ]
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

  it('should render a profil page when navigating to /accueil/profil', async () => {
    // Given
    props.match.path = '/accueil'
    const mockStore = getStubStore({
      currentUser: (
        state = new User({
          email: 'john.doe@example.fr',
          expenses: {
            all: { actual: 287, max: 500 },
            digital: { actual: 11, max: 200 },
            physical: { actual: 23, max: 200 },
          },
          firstName: 'PC Test Jeune',
          publicName: 'Iron Man',
          wallet_balance: 200.1,
        })
      ) => state,
      data: (
        state = {
          features: [],
          readRecommendations: [],
        }
      ) => state,
    })
    props.displayedModules = [new BusinessPane({ image: 'my-image-1' })]

    // When
    const wrapper = await mount(
      <Provider store={mockStore}>
        <MemoryRouter initialEntries={['/accueil/profil']}>
          <MainView {...props} />
        </MemoryRouter>
      </Provider>
    )

    // Then
    const profile = wrapper.find({ children: 'Informations personnelles' })
    expect(profile).toHaveLength(1)
  })
})
