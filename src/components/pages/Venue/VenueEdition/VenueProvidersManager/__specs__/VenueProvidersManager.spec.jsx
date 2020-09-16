import { mount } from 'enzyme'
import React from 'react'

import AllocineProviderFormContainer from '../AllocineProviderForm/AllocineProviderFormContainer'
import FnacProviderForm from '../FnacProviderForm/FnacProviderFormContainer'
import LibrairesProviderForm from '../LibrairesProviderForm/LibrairesProviderFormContainer'
import TiteliveProviderFormContainer from '../TiteliveProviderForm/TiteliveProviderFormContainer'
import VenueProviderItem from '../VenueProviderItem/VenueProviderItem'
import VenueProvidersManager from '../VenueProvidersManager'
import { Provider } from 'react-redux'
import { getStubStore } from '../../../../../../utils/stubStore'
import { MemoryRouter } from 'react-router'

describe('src | VenueProvidersManager', () => {
  let props
  let loadProvidersAndVenueProviders
  let history
  let store

  beforeEach(() => {
    history = {
      push: jest.fn(),
    }
    loadProvidersAndVenueProviders = jest.fn()
    props = {
      history,
      loadProvidersAndVenueProviders,
      match: {
        params: {
          offererId: 'CC',
          venueId: 'AB',
        },
      },
      providers: [
        { id: 'DD', requireProviderIdentifier: true, name: 'Cinema provider' },
        { id: 'EE', requireProviderIdentifier: true, name: 'Movies provider' },
      ],
      venueProviders: [],
      venueSiret: '12345678901234',
    }
    store = getStubStore({
      data: (state = {}) => state,
    })
  })

  it('should initialize VenueProvidersManager component with default state', () => {
    // when
    const wrapper = mount(<VenueProvidersManager {...props} />)

    // then
    expect(wrapper.state()).toStrictEqual({
      isCreationMode: false,
      providerId: null,
      providerSelectedIsAllocine: false,
      providerSelectedIsFnac: false,
      providerSelectedIsTitelive: false,
      providerSelectedIsLibraires: false,
      venueIdAtOfferProviderIsRequired: true,
    })
  })

  describe('render', () => {
    it('should display a list of VenueProviderItem', () => {
      // given
      props.venueProviders = [{ id: 'AD', provider: { name: 'AA' } }]

      // when
      const wrapper = mount(<VenueProvidersManager {...props} />)

      // then
      const venueProviderItem = wrapper.find(VenueProviderItem)
      expect(venueProviderItem).toHaveLength(1)
      expect(venueProviderItem.at(0).prop('venueProvider')).toStrictEqual({
        id: 'AD',
        provider: { name: 'AA' },
      })
    })

    it('should retrieve providers and venue providers when component is mounted', () => {
      // when
      mount(<VenueProvidersManager {...props} />)

      // then
      expect(loadProvidersAndVenueProviders).toHaveBeenCalledWith()
    })

    describe('the import button', () => {
      it('is displayed when at least one provider is given and no venueProviders is given', () => {
        // when
        const wrapper = mount(<VenueProvidersManager {...props} />)

        // then
        const importButton = wrapper.find({ children: '+ Importer des offres' })
        expect(importButton).toHaveLength(1)
        expect(importButton.prop('id')).toBe('add-venue-provider-btn')
        expect(importButton.prop('type')).toBe('button')
      })

      it('is hidden when no providers are given', () => {
        // given
        props.providers = []

        // when
        const wrapper = mount(<VenueProvidersManager {...props} />)

        // then
        const importButton = wrapper.find({ children: '+ Importer des offres' })
        expect(importButton).toHaveLength(0)
      })

      it('is hidden when provider and a venue provider are given', () => {
        // Given
        props.venueProviders = [{ id: 'AD', provider: { name: 'AA' } }]

        // when
        const wrapper = mount(<VenueProvidersManager {...props} />)

        // then
        const importButton = wrapper.find({ children: '+ Importer des offres' })
        expect(importButton).toHaveLength(0)
      })
    })

    describe('when selecting the import button', () => {
      it('should display a select input to choose a provider', () => {
        // given
        const wrapper = mount(<VenueProvidersManager {...props} />)
        const addOfferBtn = wrapper.find({ children: '+ Importer des offres' })

        // when
        addOfferBtn.simulate('click')

        // then
        const selectButton = wrapper.find('.select-source')
        expect(selectButton).toHaveLength(1)
        const selectButtonOptions = wrapper.find('select').find('option')
        expect(selectButtonOptions).toHaveLength(3)
        expect(selectButtonOptions.at(0).text()).toStrictEqual('Choix de la source')
        expect(selectButtonOptions.at(1).text()).toStrictEqual('Cinema provider')
        expect(selectButtonOptions.at(2).text()).toStrictEqual('Movies provider')
      })
    })

    describe('when venue provider is added from the store', () => {
      it('is not possible to select another venue provider', () => {
        // given
        props.venueProviders = []
        const store = getStubStore({})
        const wrapper = mount(
          <Provider store={store}>
            <VenueProvidersManager {...props} />
          </Provider>
        )
        wrapper.setState({ isCreationMode: true })

        // when
        wrapper.setProps({ venueProviders: [{ id: 'AD', provider: { name: 'AA' } }] })

        // then
        const addProviderForm = wrapper.find('li')
        expect(addProviderForm).toHaveLength(0)
      })
    })
  })

  describe('handleChange', () => {
    it('should display the allocine form when the user choose Allocine onChange', () => {
      // given
      props.providers = [{ id: 'EM', name: 'Allociné', lastSyncDate: '2020-01-01' }]
      const chooseAllocineEvent = {
        target: {
          value: '{"id":"EM","name":"Allociné"}',
        },
      }
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <VenueProvidersManager {...props} />
          </MemoryRouter>
        </Provider>
      )

      // when
      wrapper.find({ children: '+ Importer des offres' }).invoke('onClick')()
      wrapper.find('select').invoke('onChange')(chooseAllocineEvent)

      // then
      const allocineProviderForm = wrapper.find(AllocineProviderFormContainer)
      expect(allocineProviderForm).toHaveLength(1)
    })

    it('should display the allocine form when the user choose Allocine onBlur', () => {
      // given
      props.providers = [{ id: 'EM', name: 'Allociné', lastSyncDate: '2020-01-01' }]
      const chooseAllocineEvent = {
        target: {
          value: '{"id":"EM","name":"Allociné"}',
        },
      }
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <VenueProvidersManager {...props} />
          </MemoryRouter>
        </Provider>
      )

      // when
      wrapper.find({ children: '+ Importer des offres' }).invoke('onClick')()
      wrapper.find('select').invoke('onBlur')(chooseAllocineEvent)

      // then
      const allocineProviderForm = wrapper.find(AllocineProviderFormContainer)
      expect(allocineProviderForm).toHaveLength(1)
    })

    it('should display the titelive form when the user choose Titelive', () => {
      // given
      props.providers = [
        { id: 'EM', name: 'Allociné' },
        { id: 'EM', name: 'TiteLive Stocks (Epagine / Place des libraires.com)' },
      ]
      const chooseTiteliveEvent = {
        target: {
          value: '{"id":"EM","name":"TiteLive Stocks (Epagine / Place des libraires.com)"}',
        },
      }
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <VenueProvidersManager {...props} />
          </MemoryRouter>
        </Provider>
      )

      // when
      wrapper.find({ children: '+ Importer des offres' }).invoke('onClick')()
      wrapper.find('select').invoke('onBlur')(chooseTiteliveEvent)

      // then
      const titeliveProviderForm = wrapper.find(TiteliveProviderFormContainer)
      expect(titeliveProviderForm).toHaveLength(1)
    })

    it('should display the libraires form when the user choose Libraires', () => {
      // given
      props.providers = [
        { id: 'EM', name: 'Leslibraires.fr' },
        { id: 'EM', name: 'TiteLive Stocks (Epagine / Place des libraires.com)' },
      ]
      const chooseLibrairesEvent = {
        target: {
          value: '{"id":"EM","name":"Leslibraires.fr"}',
        },
      }
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <VenueProvidersManager {...props} />
          </MemoryRouter>
        </Provider>
      )

      // when
      wrapper.find({ children: '+ Importer des offres' }).invoke('onClick')()
      wrapper.find('select').invoke('onBlur')(chooseLibrairesEvent)

      // then
      const librairesProviderForm = wrapper.find(LibrairesProviderForm)
      expect(librairesProviderForm).toHaveLength(1)
    })

    it('should display the Fnac form when the user choose Fnac', () => {
      // given
      props.providers = [
        { id: 'EM', name: 'FNAC' },
        { id: 'EM', name: 'TiteLive Stocks (Epagine / Place des libraires.com)' },
      ]
      const chooseFnacEvent = {
        target: {
          value: '{"id":"EM","name":"FNAC"}',
        },
      }
      const wrapper = mount(
        <Provider store={store}>
          <MemoryRouter>
            <VenueProvidersManager {...props} />
          </MemoryRouter>
        </Provider>
      )

      // when
      wrapper.find({ children: '+ Importer des offres' }).invoke('onClick')()
      wrapper.find('select').invoke('onBlur')(chooseFnacEvent)

      // then
      const fnacProviderForm = wrapper.find(FnacProviderForm)
      expect(fnacProviderForm).toHaveLength(1)
    })

    it('should update state values when selected option is valid and different from default value', () => {
      // given
      const event = {
        target: {
          value: '{"id":"AE", "requireProviderIdentifier": true}',
        },
      }
      const wrapper = mount(<VenueProvidersManager {...props} />)

      // when
      wrapper.find({ children: '+ Importer des offres' }).invoke('onClick')()
      wrapper.find('select').invoke('onBlur')(event)

      // then
      expect(wrapper.state('venueIdAtOfferProviderIsRequired')).toBe(true)
    })
  })
})
