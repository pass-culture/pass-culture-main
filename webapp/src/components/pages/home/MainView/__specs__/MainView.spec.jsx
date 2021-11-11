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
import { setCustomUserId } from '../../../../../notifications/setUpBatchSDK'
import RecommendationPane from '../domain/ValueObjects/RecommendationPane'
import RecommendationModule from '../Module/RecommendationModule'

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

jest.mock('react-intersection-observer', () => ({
  useInView: () => ({
    ref: jest.fn(),
    inView: true,
  }),
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
      recommendedHits: [],
      trackAllModulesSeen: jest.fn(),
      trackAllTilesSeen: jest.fn(),
      trackConsultOffer: jest.fn(),
      trackSeeMoreHasBeenClicked: jest.fn(),
      trackRecommendationModuleSeen: jest.fn(),
      updateCurrentUser: jest.fn(),
      user: new User({
        deposit_version: 1,
        email: 'john.doe@example.fr',
        domainsCredit: {
          all: { initial: 500, remaining: 213 },
          digital: { initial: 200, remaining: 189 },
          physical: { initial: 200, remaining: 177 },
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
      trackConsultOffer: props.trackConsultOffer,
      trackSeeMoreHasBeenClicked: props.trackSeeMoreHasBeenClicked,
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
      trackConsultOffer: props.trackConsultOffer,
      trackSeeMoreHasBeenClicked: props.trackSeeMoreHasBeenClicked,
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

  it('should render a recommendation module component when module is for recos', async () => {
    // given
    props.displayedModules = [
      new RecommendationPane({
        display: {
          layout: 'one-item-medium',
          minOffers: 0,
          title: 'Voici tes offres recommandées',
        },
      }),
    ]
    props.recommendedHits = []

    // when
    const wrapper = await mount(
      <MemoryRouter>
        <MainView {...props} />
      </MemoryRouter>
    )
    await wrapper.update()

    // then
    const module = wrapper.find(RecommendationModule)
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
    window.batchSDK = () => {}
    props.user = new User({
      deposit_version: 1,
      email: 'john.doe@example.fr',
      domainsCredit: {
        all: { initial: 500, remaining: 213 },
        digital: { initial: 200, remaining: 189 },
        physical: { initial: 200, remaining: 177 },
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
    it('should track the user who have seen all modules after scroll - only once', async () => {
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
      expect(props.trackAllModulesSeen).toHaveBeenCalledTimes(1)

      act(() => {
        homeWrapper.invoke('onScroll')()
      })

      // Then
      expect(props.trackAllModulesSeen).toHaveBeenCalledTimes(1)
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
})
