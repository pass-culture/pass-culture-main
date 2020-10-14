import { render, screen, fireEvent } from '@testing-library/react'
import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { getStubStore } from 'utils/stubStore'
import { fetchAllVenuesByProUser } from 'services/venuesService'
import { ALL_OFFERS, ALL_VENUES, ALL_VENUES_OPTION, DEFAULT_PAGE } from '../_constants'
import Offers from '../Offers'

const mountOffers = (props, store) => {
  return mount(
    <Provider store={store}>
      <MemoryRouter>
        <Offers {...props} />
      </MemoryRouter>
    </Provider>
  )
}

const renderOffer = (props, store) => {
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <Offers {...props} />
      </MemoryRouter>
    </Provider>
  )
}

jest.mock('../../../../services/venuesService', () => ({
  fetchAllVenuesByProUser: jest.fn(),
}))
describe('src | components | pages | Offers | Offers', () => {
  let change
  let parse
  let props
  let currentUser
  let store
  const proVenues = [
    {
      id: 'JI',
      name: 'Ma venue',
      offererName: 'Mon offerer',
      isVirtual: false,
    },
    {
      id: 'JQ',
      name: 'Ma venue virtuelle',
      offererName: 'Mon offerer',
      isVirtual: true,
    },
  ]

  beforeEach(() => {
    change = jest.fn()
    parse = jest.fn().mockReturnValue({})
    currentUser = { id: 'EY', isAdmin: false, name: 'Current User', publicName: 'USER' }
    store = getStubStore({
      data: (
        state = {
          offerers: [],
          users: [currentUser],
          venues: [{ id: 'JI', name: 'Venue' }],
        }
      ) => state,
      modal: (
        state = {
          config: {},
        }
      ) => state,
      offers: (
        state = {
          searchFilters: {},
        }
      ) => state,
    })

    props = {
      closeNotification: jest.fn(),
      currentUser,
      handleOnActivateAllVenueOffersClick: jest.fn(),
      handleOnDeactivateAllVenueOffersClick: jest.fn(),
      loadOffers: jest.fn().mockResolvedValue({ page: 1, pageCount: 2, offersCount: 5 }),
      loadTypes: jest.fn(),
      saveSearchFilters: jest.fn(),
      offers: [
        {
          id: 'N9',
          venueId: 'JI',
        },
      ],
      query: {
        change,
        parse,
      },
      types: [],
      venue: { name: 'Ma Venue', id: 'JI' },
    }
    fetchAllVenuesByProUser.mockResolvedValue(proVenues)
  })

  afterEach(() => {
    fetchAllVenuesByProUser.mockReset()
  })

  describe('render', () => {
    it('should load offers from API with defaults props', () => {
      // when
      mountOffers(props, store)

      // then
      expect(props.loadOffers).toHaveBeenCalledWith({
        nameSearchValue: ALL_OFFERS,
        page: DEFAULT_PAGE,
        selectedVenueId: ALL_VENUES,
      })
    })

    it('should display column titles when offers are returned', async () => {
      // Given
      props.offers = [{ id: 'KE', availabilityMessage: 'Pas de stock', venueId: 'JI' }]

      // When
      const wrapper = await mountOffers(props, store)

      wrapper.update()

      // Then
      const venueColumn = wrapper.find('th').find({ children: 'Lieu' })
      const stockColumn = wrapper.find('th').find({ children: 'Stock' })
      expect(venueColumn).toHaveLength(1)
      expect(stockColumn).toHaveLength(1)
    })

    it('should not display column titles when no offers are returned', async () => {
      // Given
      props.offers = []

      // When
      const wrapper = await mountOffers(props, store)

      wrapper.update()

      // Then
      const venueColumn = wrapper.find('th').find({ children: 'Lieu' })
      const stockColumn = wrapper.find('th').find({ children: 'Stock' })
      expect(venueColumn).toHaveLength(0)
      expect(stockColumn).toHaveLength(0)
    })

    it('should render as much offers as given in props', async () => {
      // given
      props.offers = [
        {
          id: 'M4',
          isActive: true,
          isEditable: true,
          isFullyBooked: false,
          isEvent: true,
          isThing: false,
          hasBookingLimitDatetimesPassed: false,
          name: 'My little offer',
          thumbUrl: '/my-fake-thumb',
          venueId: 'JI',
        },
        {
          id: 'AE3',
          isActive: true,
          isEditable: true,
          isFullyBooked: true,
          isEvent: false,
          isThing: true,
          hasBookingLimitDatetimesPassed: false,
          name: 'My other offer',
          thumbUrl: '/my-other-fake-thumb',
          venueId: 'JI',
        },
      ]

      // when
      const wrapper = await mountOffers(props, store)

      wrapper.update()

      // then
      const firstOfferItem = wrapper.find({ children: 'My little offer' }).first()
      const secondOfferItem = wrapper.find({ children: 'My other offer' }).first()
      expect(firstOfferItem).toHaveLength(1)
      expect(secondOfferItem).toHaveLength(1)
    })

    describe('total number of offers', () => {
      it('should display total number of offers in plural if multiple offers', async () => {
        // Given
        const page = 1
        const pageCount = 2
        const offersCount = 17
        props.loadOffers.mockResolvedValueOnce({ page, pageCount, offersCount })

        // When
        const wrapper = await mount(
          <Provider store={store}>
            <MemoryRouter>
              <Offers {...props} />
            </MemoryRouter>
          </Provider>
        )

        wrapper.update()

        // Then
        const offersCounter = wrapper.find({ children: '17 offres' })
        expect(offersCounter).toHaveLength(1)
      })

      it('should display total number of offers in singular if one or no offer', async () => {
        // Given
        const page = 1
        const pageCount = 1
        const offersCount = 1
        props.loadOffers.mockResolvedValueOnce({ page, pageCount, offersCount })

        // When
        const wrapper = await mount(
          <Provider store={store}>
            <MemoryRouter>
              <Offers {...props} />
            </MemoryRouter>
          </Provider>
        )

        wrapper.update()

        // Then
        const offersCounter = wrapper.find({ children: '1 offre' })
        expect(offersCounter).toHaveLength(1)
      })
    })

    describe('filters', () => {
      it('should render venue filter with default option and given venues', async () => {
        // when
        const wrapper = await mountOffers(props, store)

        // then
        wrapper.update()
        const venueSelect = wrapper.find('select[name="lieu"]')
        expect(venueSelect.props().value).toBe(ALL_VENUES_OPTION.id)
        const options = venueSelect.find('option')
        expect(options).toHaveLength(3)
        expect(options.at(0).text()).toBe(ALL_VENUES_OPTION.displayName)
        expect(options.at(1).text()).toBe(proVenues[0].name)
        expect(options.at(2).text()).toBe(`${proVenues[1].offererName} - Offre numérique`)
      })

      it('should render venue filter with given venue selected', async () => {
        // given
        jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: proVenues[0].id })

        // when
        const wrapper = await mountOffers(props, store)

        // then
        wrapper.update()
        const venueSelect = wrapper.find('select[name="lieu"]')
        expect(venueSelect.props().value).toBe(proVenues[0].id)
      })
    })
  })

  describe('on click on search button', () => {
    it('should load offers with default filters when no changes where made', () => {
      // given
      const wrapper = mountOffers(props, store)
      const launchSearchButton = wrapper.find('form')

      // when
      launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // then
      expect(props.loadOffers).toHaveBeenCalledWith({
        nameSearchValue: ALL_OFFERS,
        page: DEFAULT_PAGE,
        selectedVenueId: ALL_VENUES,
      })
    })

    it('should load offers with written offer name filter', () => {
      // given
      const wrapper = mountOffers(props, store)
      const offerNameInput = wrapper.find('input[placeholder="Rechercher par nom d’offre"]')
      const launchSearchButton = wrapper.find('form')
      offerNameInput.invoke('onChange')({ target: { value: 'Any word' } })

      // when
      launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // then
      expect(props.loadOffers).toHaveBeenCalledWith({
        nameSearchValue: 'Any word',
        page: DEFAULT_PAGE,
        selectedVenueId: ALL_VENUES,
      })
    })

    it('should load offers with selected venue filter', () => {
      // given
      const wrapper = mountOffers(props, store)
      const venueSelect = wrapper.find('select[name="lieu"]')
      const launchSearchButton = wrapper.find('form')
      venueSelect.invoke('onChange')({ target: { value: proVenues[0].id } })

      // when
      launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // then
      expect(props.loadOffers).toHaveBeenCalledWith({
        nameSearchValue: ALL_OFFERS,
        page: DEFAULT_PAGE,
        selectedVenueId: proVenues[0].id,
      })
    })
  })

  describe('button to create an offer', () => {
    it('should not be displayed when user is an admin', () => {
      // given
      props.currentUser.isAdmin = true

      // when
      const wrapper = mountOffers(props, store)
      const navLink = wrapper.find({ children: 'Créer une offre' })

      // then
      expect(navLink).toHaveLength(0)
    })

    it('should be displayed when user is not an admin', () => {
      // given
      props.currentUser.isAdmin = false

      // when
      const wrapper = mountOffers(props, store)
      const offerCreationLink = wrapper.find({ children: 'Créer une offre' }).parent()

      // then
      expect(offerCreationLink).toHaveLength(1)
      expect(offerCreationLink.prop('href')).toBe('/offres/creation')
    })
  })

  describe('deactivate all offers from a venue', () => {
    it('should be displayed when offers and venue are given', () => {
      // given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'GY' })

      // when
      const wrapper = mountOffers(props, store)
      const deactivateButton = wrapper.find({ children: 'Désactiver toutes les offres' })

      // then
      expect(deactivateButton).toHaveLength(1)
    })

    it('should not be displayed when venue is missing', () => {
      // given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: undefined })

      // when
      const wrapper = mountOffers(props, store)
      const deactivateButton = wrapper.find({ children: 'Désactiver toutes les offres' })

      // then
      expect(deactivateButton).toHaveLength(0)
    })

    it('should not be displayed when offers are missing', () => {
      // given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'GY' })
      props.offers = []

      // when
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <Offers {...props} />
          </MemoryRouter>
        </Provider>
      )
      const deactivateButton = wrapper.find({ children: 'Désactiver toutes les offres' })

      // then
      expect(deactivateButton).toHaveLength(0)
    })

    it('should send a request to api when clicked', () => {
      // given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'GY' })

      // given
      const wrapper = mountOffers(props, store)

      // when
      const deactivateButton = wrapper.find({ children: 'Désactiver toutes les offres' })
      deactivateButton.simulate('click')

      // then
      expect(props.handleOnDeactivateAllVenueOffersClick).toHaveBeenCalledWith('GY')
    })
  })

  describe('activate all offers from a venue', () => {
    it('should be displayed when offers and venue are given', () => {
      // given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'GY' })

      // when
      const wrapper = mountOffers(props, store)
      const activateButton = wrapper.find({ children: 'Activer toutes les offres' })

      // then
      expect(activateButton).toHaveLength(1)
    })

    it('should not be displayed when venue is missing', () => {
      // given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: undefined })

      // when
      const wrapper = mountOffers(props, store)
      const activateButton = wrapper.find({ children: 'Activer toutes les offres' })

      // then
      expect(activateButton).toHaveLength(0)
    })

    it('should not be displayed when offers are missing', () => {
      // given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'GY' })
      props.offers = []

      // when
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <Offers {...props} />
          </MemoryRouter>
        </Provider>
      )
      const activateButton = wrapper.find({ children: 'Activer toutes les offres' })

      // then
      expect(activateButton).toHaveLength(0)
    })

    it('should send a request to api when clicked', () => {
      // given
      jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'GY' })

      const wrapper = mountOffers(props, store)

      // when
      const activateButton = wrapper.find({ children: 'Activer toutes les offres' })
      activateButton.simulate('click')

      // then
      expect(props.handleOnActivateAllVenueOffersClick).toHaveBeenCalledWith('GY')
    })
  })

  describe('url query params', () => {
    it('should have page value when page value is not first page', async () => {
      // given
      props.loadOffers.mockResolvedValueOnce({ page: 2, pageCount: 2, offersCount: 5 })
      const wrapper = await mountOffers(props, store)
      wrapper.update()
      const rightArrow = wrapper.find('img[alt="Aller à la page suivante"]').closest('button')

      // When
      rightArrow.invoke('onClick')()

      // then
      wrapper.update()
      expect(props.query.change).toHaveBeenCalledWith({
        lieu: null,
        nom: null,
        page: 2,
      })
    })

    it('should have page value be removed when page value is first page', async () => {
      // given
      const wrapper = await mountOffers(props, store)
      wrapper.update()
      const rightArrow = wrapper.find('img[alt="Aller à la page suivante"]').closest('button')
      const leftArrow = wrapper.find('img[alt="Aller à la page précédente"]').closest('button')
      rightArrow.invoke('onClick')()

      // When
      leftArrow.invoke('onClick')()

      // then
      expect(props.query.change).toHaveBeenCalledWith({
        lieu: null,
        nom: null,
        page: null,
      })
    })

    it('should have offer name value when name search value is not an empty string', async () => {
      // given
      const wrapper = mountOffers(props, store)
      const searchInput = wrapper.find('input[placeholder="Rechercher par nom d’offre"]')
      const launchSearchButton = wrapper.find('form')
      searchInput.invoke('onChange')({ target: { value: 'AnyWord' } })

      // when
      await launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      wrapper.update()

      // then
      expect(props.query.change).toHaveBeenCalledWith({
        lieu: null,
        nom: 'AnyWord',
        page: null,
      })
    })

    it('should store search value', () => {
      // given
      renderOffer(props, store)
      const searchInput = screen.getByPlaceholderText('Rechercher par nom d’offre')

      // when
      fireEvent.change(searchInput, { target: { value: 'search string' } })
      fireEvent.click(screen.getByText('Lancer la recherche'))

      // then
      expect(props.saveSearchFilters).toHaveBeenCalledWith({
        venueId: ALL_VENUES,
        name: 'search string',
        page: DEFAULT_PAGE,
      })
    })

    it('should have offer name value be removed when name search value is an empty string', async () => {
      // given
      const wrapper = mountOffers(props, store)
      const searchInput = wrapper.find('input[placeholder="Rechercher par nom d’offre"]')
      const launchSearchButton = wrapper.find('form')
      searchInput.invoke('onChange')({ target: { value: ALL_OFFERS } })

      // when
      await launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // then
      expect(props.query.change).toHaveBeenCalledWith({
        lieu: null,
        nom: null,
        page: null,
      })
    })

    it('should have venue value when user filter by venue', async () => {
      // given
      const wrapper = mountOffers(props, store)
      const venueSelect = wrapper.find('select[name="lieu"]')
      const launchSearchButton = wrapper.find('form')
      venueSelect.invoke('onChange')({ target: { value: proVenues[0].id } })

      // when
      await launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // then
      expect(props.query.change).toHaveBeenCalledWith({
        lieu: proVenues[0].id,
        nom: null,
        page: null,
      })
    })

    it('should have venue value be removed when user ask for all venues', async () => {
      // given
      const wrapper = mountOffers(props, store)
      const venueSelect = wrapper.find('select[name="lieu"]')
      const launchSearchButton = wrapper.find('form')
      venueSelect.invoke('onChange')({ target: { value: ALL_VENUES } })

      // when
      await launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

      // then
      expect(props.query.change).toHaveBeenCalledWith({
        lieu: null,
        nom: null,
        page: null,
      })
    })
  })

  describe('when leaving page', () => {
    it('should close offers activation / deactivation notification', () => {
      // given
      props = {
        ...props,
        closeNotification: jest.fn(),
        notification: {
          tag: 'offers-activation',
        },
      }
      const wrapper = mountOffers(props, store)

      // when
      wrapper.unmount()

      // then
      expect(props.closeNotification).toHaveBeenCalledWith()
    })

    it('should not fail on null notification', () => {
      // given
      props = {
        ...props,
        closeNotification: jest.fn(),
        notification: null,
      }
      const wrapper = mountOffers(props, store)
      // when
      wrapper.unmount()

      // then
      expect(props.closeNotification).not.toHaveBeenCalledWith()
    })
  })

  describe('page navigation', () => {
    it('should display next page when clicking on right arrow', async () => {
      // Given
      props.loadOffers.mockResolvedValueOnce({ page: 1, pageCount: 4, offersCount: 5 })
      const wrapper = await mountOffers(props, store)
      wrapper.update()
      const rightArrow = wrapper.find('img[alt="Aller à la page suivante"]').closest('button')

      // When
      rightArrow.invoke('onClick')()

      // Then
      expect(props.loadOffers).toHaveBeenLastCalledWith({
        nameSearchValue: ALL_OFFERS,
        page: 2,
        selectedVenueId: ALL_VENUES,
      })
    })

    it('should display previous page when clicking on left arrow', async () => {
      // Given
      props.loadOffers.mockResolvedValueOnce({ page: 2, pageCount: 2, offersCount: 5 })

      const wrapper = await mountOffers(props, store)
      wrapper.update()
      const rightArrow = wrapper.find('img[alt="Aller à la page précédente"]').closest('button')

      // When
      rightArrow.invoke('onClick')()

      // Then
      expect(props.loadOffers).toHaveBeenLastCalledWith({
        nameSearchValue: ALL_OFFERS,
        page: DEFAULT_PAGE,
        selectedVenueId: ALL_VENUES,
      })
    })

    it('should not be able to click on previous arrow when being on the first page', async () => {
      // Given
      props.query.parse.mockReturnValue({ page: DEFAULT_PAGE })

      // When
      const wrapper = await mountOffers(props, store)

      wrapper.update()

      // Then
      const rightArrow = wrapper.find('img[alt="Aller à la page précédente"]').closest('button')
      expect(rightArrow.prop('disabled')).toBe(true)
    })

    it('should not be able to click on next arrow when being on the last page', async () => {
      // Given
      props.loadOffers.mockResolvedValueOnce({ page: 2, pageCount: 2, offersCount: 5 })

      // When
      const wrapper = await mountOffers(props, store)

      wrapper.update()

      // Then
      const rightArrow = wrapper.find('img[alt="Aller à la page suivante"]').closest('button')
      expect(rightArrow.prop('disabled')).toBe(true)
    })
  })
})
