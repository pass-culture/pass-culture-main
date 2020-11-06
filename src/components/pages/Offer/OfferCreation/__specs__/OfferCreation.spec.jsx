import { mount } from 'enzyme'
import { CheckboxInput, Field, Form } from 'pass-culture-shared'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import Insert from 'components/layout/Insert/Insert'
import OfferPreviewLink from 'components/layout/OfferPreviewLink/OfferPreviewLink'
import Titles from 'components/layout/Titles/Titles'
import LocalProviderInformation from 'components/pages/Offer/LocalProviderInformation/LocalProviderInformationContainer'
import MediationsManager from 'components/pages/Offer/MediationsManager/MediationsManagerContainer'
import StocksManagerContainer from 'components/pages/Offer/StocksManager/StocksManagerContainer'
import { ALL_OFFERERS, ALL_STATUS, ALL_TYPES, ALL_VENUES } from 'components/pages/Offers/_constants'
import { showModal } from 'store/reducers/modal'
import { getStubStore } from 'utils/stubStore'

import OfferCreation from '../OfferCreation'

const buildStore = (store = {}) => {
  const currentUser = {
    id: 'EY',
    isAdmin: false,
    name: 'Current User',
    publicName: 'USER',
  }
  return getStubStore({
    data: (
      state = {
        offerers: [],
        mediations: [],
        users: [currentUser],
        venues: [{ id: 'JI', name: 'Venue' }],
      }
    ) => (store.data ? { ...state, ...store.data } : state),
    modal: (
      state = {
        config: {},
      }
    ) => (store.modal ? { ...state, ...store.modal } : state),
    offers: (
      state = {
        list: [
          {
            id: '6GD',
            name: 'Super Livre',
            lastProvider: null,
          },
        ],
        searchFilters: {},
      }
    ) => (store.offers ? { ...state, ...store.offers } : state),
  })
}

const getMountedOfferCreationWrapper = (props, store) => {
  const wrapper = mount(
    <Provider store={store}>
      <MemoryRouter>
        <OfferCreation {...props} />
      </MemoryRouter>
    </Provider>
  )
  wrapper.update()
  return wrapper.find(OfferCreation)
}

describe('src | OfferCreation', () => {
  let dispatch
  let props
  let store

  beforeEach(() => {
    dispatch = jest.fn()
    props = {
      currentUser: {
        isAdmin: false,
      },
      dispatch: dispatch,
      formInitialValues: {
        isDuo: false,
      },
      isEditableOffer: true,
      loadVenue: jest.fn(),
      location: {
        search: '?lieu=AQ',
      },
      match: {
        params: {
          offerId: 'creation',
        },
      },
      mergeOfferError: jest.fn(),
      query: {
        change: () => ({}),
        changeToReadOnly: () => ({}),
        context: () => ({}),
        parse: () => ({
          lieu: 'AQ',
          gestion: 'gestion',
        }),
        translate: () => ({ venue: 'AQ ' }),
      },
      selectedOfferType: {
        value: 'ThingType.SPECTACLE_VIVANT_ABO',
      },
      showValidationNotification: jest.fn(),
      offer: {
        id: '6GD',
        name: 'Super Livre',
        lastProvider: null,
      },
      history: {},
      loadOffer: jest.fn(),
      offersSearchFilters: {
        venueId: ALL_VENUES,
        typeId: ALL_TYPES,
        offererId: ALL_OFFERERS,
        page: 1,
        status: ALL_STATUS,
      },
      offerers: [],
      offerer: {
        id: 'AZERT',
      },
      types: [],
      providers: [],
      trackCreateOffer: jest.fn(),
      trackModifyOffer: jest.fn(),
      venuesMatchingOfferType: [],
    }

    store = buildStore()
  })

  describe('handleSuccess', () => {
    describe('when the offer is successfully modified', () => {
      it('should redirect to offer page', () => {
        // given
        const queryChangeToReadOnly = jest.fn()

        props.match.params = {}
        props.query.changeToReadOnly = queryChangeToReadOnly
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // when
        const queryParams = {}
        const offer = { id: 'SN' }
        const action = {
          config: { method: 'PATCH' },
          payload: { datum: offer },
        }
        wrapper.instance().onHandleFormSuccess({}, action)

        // then
        expect(queryChangeToReadOnly).toHaveBeenCalledWith(queryParams, offer)
      })
    })

    describe('when the offer is successfully modified (réécrire)', () => {
      it('should redirect to gestion page', () => {
        // given
        const queryChangeToReadOnly = jest.fn()
        const initialProps = {
          ...props,
          location: {
            search: '?lieu=AQ',
          },
          match: {
            params: {
              offerId: 'creation',
            },
          },
          currentUser: {
            isAdmin: false,
          },
          isEditableOffer: true,
          formInitialValues: {
            isDuo: false,
          },
          query: {
            changeToReadOnly: queryChangeToReadOnly,
            context: () => ({}),
            parse: () => ({ lieu: 'AQ' }),
            translate: () => ({ venue: 'AQ ' }),
          },
          dispatch: dispatch,
          history: {},
          selectedOfferType: undefined,
          trackCreateOffer: jest.fn(),
          trackModifyOffer: jest.fn(),
          showValidationNotification: jest.fn(),
        }

        const wrapper = getMountedOfferCreationWrapper({ ...initialProps }, store)

        // when
        const queryParams = {}
        const offer = { id: 'SN' }
        const action = { config: { method: 'POST' }, payload: { datum: offer } }
        wrapper.instance().onHandleFormSuccess({}, action)

        // then
        expect(queryChangeToReadOnly).toHaveBeenCalledWith(queryParams, offer)
      })
    })

    describe('when the offer is successfully created', () => {
      it('should display a success notification', () => {
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // when
        const offer = { id: 'SN' }
        const action = { config: { method: 'POST' }, payload: { datum: offer } }
        wrapper.instance().onHandleFormSuccess({}, action)

        // then
        expect(props.showValidationNotification).toHaveBeenCalledWith()
      })
    })
  })

  describe('isNational', () => {
    it('should display isNational if admin user', () => {
      // given
      props.currentUser.isAdmin = true
      store = buildStore({ data: { currentUser: props.currentUser } })
      const wrapper = getMountedOfferCreationWrapper(props, store)

      // when
      const result = wrapper.find(CheckboxInput).first('[name="isNational"]')

      // then
      expect(result.prop('label')).toBe('Rayonnement national')
    })
  })

  describe('handleShowStocksManager', () => {
    it('should pass offerId as a props to the StocksManagerContainer', () => {
      // given
      const wrapper = getMountedOfferCreationWrapper(props, store)
      props.match.params.offerId = 'N9'

      // when
      wrapper.instance().handleShowStocksManager()

      // then
      const modalParams = {
        isUnclosable: true,
      }
      expect(props.dispatch).toHaveBeenCalledWith(
        showModal(<StocksManagerContainer offerId="N9" />, modalParams)
      )
    })
  })

  describe('hasConditionalField', () => {
    it('should return false without selected offer type', () => {
      // given
      props.selectedOfferType = undefined
      const wrapper = getMountedOfferCreationWrapper(props, store)

      // when
      const result = wrapper.instance().hasConditionalField(null)

      // then
      expect(result).toBe(false)
    })

    describe('when offer type is a subscription on show', () => {
      it('should show event type', () => {
        // given
        props.selectedOfferType = {
          value: 'ThingType.SPECTACLE_VIVANT_ABO',
        }
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // when
        const result = wrapper.instance().hasConditionalField('showType')

        // then
        expect(result).toBe(true)
      })
    })
  })

  describe('render', () => {
    describe('mediationsManager', () => {
      it("should be displayed when it's not a new offer", () => {
        // given
        const offer = {
          bookingEmail: 'fake@email.com',
          dateCreated: '2019-03-29T15:38:23.806900Z',
          dateModifiedAtLastProvider: '2019-03-29T15:38:23.806874Z',
          id: 'N9',
          idAtProviders: null,
          isActive: true,
          isDuo: false,
          isEvent: true,
          isThing: false,
          lastProviderId: null,
          lastProvider: null,
          modelName: 'Offer',
          productId: '94',
          venueId: 'AQ',
        }

        props.match.params.offerId = offer.id
        props.offer = offer

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)
        const mediationsManagerComponent = wrapper.find(MediationsManager)

        // then
        expect(mediationsManagerComponent).toHaveLength(1)
      })
    })

    describe('when creating a new offer', () => {
      it('should display back link with default offers search filters', () => {
        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        const backButton = wrapper.find('a.back-button')
        expect(backButton.prop('href')).toMatch(
          `/offres?lieu=${ALL_VENUES}&categorie=${ALL_TYPES}&structure=${ALL_OFFERERS}&page=1&statut=${ALL_STATUS}`
        )
      })

      it('should display back link without search filters if none are provided', () => {
        // given
        props.offersSearchFilters = {}

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        const backButton = wrapper.find('a.back-button')
        expect(backButton.prop('href')).toMatch('/offres')
      })

      it('should display back link with given offers search filters', () => {
        // given
        props.offersSearchFilters = {
          name: 'searchValue',
        }

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        const backButton = wrapper.find('a.back-button')
        expect(backButton.prop('href')).toMatch('/offres?nom=searchValue')
      })

      it('should translate status filter value in back link when not default', () => {
        // given
        props.offersSearchFilters = {
          status: 'soldOut',
        }

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        const backButton = wrapper.find('a.back-button')
        expect(backButton.prop('href')).toMatch('/offres?statut=epuisee')
      })

      it('should create a new Product when no offer type', () => {
        // given
        props.query.context = () => ({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        })
        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        expect(wrapper.find(Form).prop('action')).toStrictEqual('/offers')
      })

      it('should create a new Event when event type given', () => {
        // given
        props.query.context = () => ({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        })
        props.selectedOfferType = {
          type: 'Event',
        }

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        expect(wrapper.find(Form).prop('action')).toStrictEqual('/offers')
      })

      it('should display a limited textarea field to define name of the offer', () => {
        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        const field = wrapper.find(Field).at(0)
        expect(field).toHaveLength(1)
        expect(field.prop('label')).toBe('Titre de l’offre')
        expect(field.prop('required')).toBe(true)
        expect(field.prop('maxLength')).toBe(90)
        expect(field.prop('displayMaxLength')).toBe(true)
        expect(field.prop('type')).toBe('textarea')
      })

      describe('when the offer is an Event', () => {
        it('should allow to set an event duration', () => {
          // given
          props.match = {
            params: {
              offerId: 'QU',
            },
          }
          props.selectedOfferType = {
            type: 'Event',
          }

          // when
          const wrapper = getMountedOfferCreationWrapper(props, store)

          // then
          const fieldGroups = wrapper.find('.field-group')
          const fieldGroupForUsefulInformation = fieldGroups.at(2)
          const durationField = fieldGroupForUsefulInformation.find(Field).at(0)
          expect(fieldGroups).toHaveLength(5)
          expect(durationField.prop('name')).toStrictEqual('durationMinutes')
        })

        it('should allow to configure the offer as DUO', () => {
          // given
          props.match = {
            params: {
              offerId: 'QU',
            },
          }
          props.selectedOfferType = {
            type: 'Event',
          }
          const wrapper = getMountedOfferCreationWrapper(props, store)

          // when
          const isDuoCheckbox = wrapper.find('#isDuo')

          // then
          expect(isDuoCheckbox).toHaveLength(1)
          expect(isDuoCheckbox.prop('type')).toStrictEqual('checkbox')
        })
      })

      describe('when the offer is a Thing', () => {
        it('should have a bookingEmail', () => {
          // given
          props.match = {
            params: {
              offerId: 'QU',
            },
          }
          props.selectedOfferType = {
            type: 'Thing',
          }

          // when
          const wrapper = getMountedOfferCreationWrapper(props, store)

          // then
          const fieldGroups = wrapper.find('.field-group')
          const fieldGroupForUsefulInformation = fieldGroups.at(2)
          const bookingEmailField = fieldGroupForUsefulInformation.find(Field).at(0)
          expect(fieldGroups).toHaveLength(5)
          expect(bookingEmailField.prop('name')).toStrictEqual('bookingEmail')
        })

        it('should not have the duo option', () => {
          // given
          props.match = {
            params: {
              offerId: 'QU',
            },
          }
          props.selectedOfferType = {
            type: 'Thing',
          }
          const wrapper = getMountedOfferCreationWrapper(props, store)

          // when
          const isDuoCheckbox = wrapper.find('#isDuo')

          // then
          expect(isDuoCheckbox).toHaveLength(0)
        })
      })

      describe('when the offer is digital only and selected venue is virtual', () => {
        it('should display an information insert', () => {
          // given
          props.match = {
            params: {
              offerId: 'QU',
            },
          }
          props.selectedOfferType = {
            offlineOnly: false,
            onlineOnly: true,
            value: 'ThingType.JEUX_VIDEO',
          }

          props.venue = {
            isVirtual: true,
          }

          // when
          const wrapper = getMountedOfferCreationWrapper(props, store)

          // then
          const warningText = wrapper.find(Insert).find('p').first().text()
          expect(warningText).toStrictEqual(
            "Cette offre numérique ne fera pas l'objet d'un remboursement. Pour plus d'informations sur les catégories éligibles au remboursement, merci de consulter les CGU."
          )
          const insertLink = wrapper.find('.yellow-insert a')
          expect(insertLink.prop('href')).toStrictEqual(
            'https://docs.passculture.app/textes-normatifs'
          )
        })
      })

      describe('when the offer is digital only selected venue is virtual', () => {
        it('should not display a warning message about reimbursement of digital offers', () => {
          // given
          props.match = {
            params: {
              offerId: 'QU',
            },
          }
          props.selectedOfferType = {
            offlineOnly: false,
            onlineOnly: true,
            value: 'ThingType.CINEMA_CARD',
          }

          props.venue = {
            isVirtual: true,
          }

          // when
          const wrapper = getMountedOfferCreationWrapper(props, store)

          // then
          const insert = wrapper.find('.yellow-insert')
          expect(insert).toHaveLength(0)
        })
      })
    })

    describe('when updating the offer', () => {
      it('should update a product when no offer type', () => {
        // given
        const offer = {
          id: 'VAG',
          productId: 'V24',
          lastProvider: {
            name: 'Open Agenda',
          },
        }
        props.match.params = {
          offerId: offer.id,
        }
        props.query.context = () => ({
          isCreatedEntity: false,
          isModifiedEntity: false,
          readOnly: true,
        })
        props.offer = offer
        store = buildStore({
          offer: offer,
          mediations: [
            {
              id: 'fake_id',
              thumbPath: '/',
              isActive: true,
              offerId: offer.id,
            },
          ],
        })

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        expect(wrapper.find(Form).prop('action')).toStrictEqual('/offers/VAG')
      })

      it('should create a new Event when event type given', () => {
        // given
        const offer = {
          id: 'VAG',
          mediationId: 'TR',
          productId: '6GD',
          isEvent: true,
          isThing: false,
          lastProvider: null,
        }
        props.match.params = {
          offerId: offer.id,
        }
        props.selectedOfferType = {
          type: 'Event',
        }
        props.offer = offer

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        expect(wrapper.find(Form).prop('action')).toStrictEqual('/offers/VAG')
      })

      it('should display preview link', () => {
        // given
        const offer = {
          id: 'VAG',
          productId: '6GD',
          isEvent: true,
          isThing: false,
          lastProvider: null,
          activeMediation: {
            id: 'MED',
            isActive: true,
          },
          mediationsIds: ['MED'],
        }
        props.match.params = {
          offerId: offer.id,
        }
        props.selectedOfferType = {
          type: 'Event',
        }
        props.offer = offer

        const wrapper = getMountedOfferCreationWrapper(props, store)

        // when
        const preview_section = wrapper.find(Titles)

        // then
        const preview_link = preview_section.find(OfferPreviewLink)
        expect(preview_link.prop('offerWebappUrl')).toMatch('/offre/details/VAG/MED')
      })
    })

    describe('display venue informations', () => {
      it('should display venue name when venue publicName is not provided', () => {
        // given
        props.query.context = () => ({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        })
        props.venuesMatchingOfferType = [{ name: 'quel beau théâtre' }, { name: 'quel beau musée' }]
        const expectedOptions = [{ name: 'quel beau théâtre' }, { name: 'quel beau musée' }]

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        const fieldGroups = wrapper.find('.field-group')
        const fieldGroupForUsefulInformation = fieldGroups.at(1)
        const venueField = fieldGroupForUsefulInformation.find(Field).at(1)
        expect(fieldGroups).toHaveLength(5)
        expect(venueField.prop('options')).toStrictEqual(expectedOptions)
      })

      it('should display venue public name when venue public name is provided', () => {
        // given
        props.venuesMatchingOfferType = [
          { name: 'quel beau théâtre', publicName: 'quel beau théâtre public' },
          { name: 'quel beau musée', publicName: 'quel beau musée public' },
        ]
        const expectedOptions = [
          {
            name: 'quel beau théâtre public',
            publicName: 'quel beau théâtre public',
          },
          {
            name: 'quel beau musée public',
            publicName: 'quel beau musée public',
          },
        ]

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        const fieldGroups = wrapper.find('.field-group')
        const fieldGroupForUsefulInformation = fieldGroups.at(1)
        const venueField = fieldGroupForUsefulInformation.find(Field).at(1)
        expect(fieldGroups).toHaveLength(5)
        expect(venueField.prop('options')).toStrictEqual(expectedOptions)
      })
    })

    describe('when offer is not editable', () => {
      it('should not be possible to modify offer', () => {
        // given
        props.query.context = () => ({
          isCreatedEntity: false,
          isModifiedEntity: false,
          readOnly: true,
        })
        props.isEditableOffer = false

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        const modifyOfferButton = wrapper.find('#modify-offer-button')
        expect(modifyOfferButton.exists()).toBe(false)
      })

      it('should display LocalProviderInformation if offer was generated from local provider', () => {
        // given
        const offer = {
          id: 'VAG',
          name: 'Test offer',
          productId: '6GD',
          isEvent: true,
          isThing: false,
          activeMediation: {
            id: 'MED',
          },
          lastProvider: {
            name: 'Fnac',
          },
        }
        props.query.context = () => ({
          isCreatedEntity: false,
          isModifiedEntity: false,
          readOnly: true,
        })
        props.isEditableOffer = false
        props.product = {
          id: '6GD',
          name: 'super livre',
          thumbUrl: 'http://localhost/image/6GD',
        }
        props.offer = offer
        store = buildStore({ offers: { list: [offer] } })

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        const localProviderInformationComponent = wrapper.find(LocalProviderInformation)
        expect(localProviderInformationComponent).toHaveLength(1)
        expect(localProviderInformationComponent.prop('providerName')).toBe('fnac')
        expect(localProviderInformationComponent.prop('offererId')).toBe('AZERT')
      })
    })

    describe('when offer is editable', () => {
      beforeEach(() => {
        props.query.context = () => ({
          isCreatedEntity: false,
          isModifiedEntity: false,
          readOnly: true,
        })
        props.isEditableOffer = true
      })

      it('should be possible to manage stocks', () => {
        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        const manageStockButton = wrapper.find('#manage-stocks')
        expect(manageStockButton.prop('disabled')).toStrictEqual('')
      })

      it('should be possible to modify offer', () => {
        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // then
        const modifyOfferButton = wrapper.find('#modify-offer-button')
        expect(modifyOfferButton.exists()).toBe(true)
      })
    })

    describe('stock management button', () => {
      describe('when offer is from Titelive provider', () => {
        it('should not be possible to change stock values', () => {
          // given
          props.offer.lastProvider = {
            name: 'titelive (epagine / place des libraires.com)',
          }

          // when
          const wrapper = getMountedOfferCreationWrapper(props, store)

          // then
          const manageStockButton = wrapper.find('#manage-stocks')
          expect(manageStockButton.prop('disabled')).toStrictEqual('disabled')
        })
      })

      describe('when offer is from Allociné provider', () => {
        it('should be possible to change stock values', () => {
          // given
          const offer = {
            id: 'test_id',
            name: 'test name',
            lastProvider: {
              name: 'Allociné',
            },
          }
          props.offer = offer
          store = buildStore({ offers: { list: [offer] } })

          // when
          const wrapper = getMountedOfferCreationWrapper(props, store)

          // then
          const manageStockButton = wrapper.find('#manage-stocks')
          expect(manageStockButton.prop('disabled')).toStrictEqual('')
        })
      })

      describe('when offer has been created manually', () => {
        it('should be possible to change stock values', () => {
          // given
          props.offer.lastProvider = null

          // when
          const wrapper = getMountedOfferCreationWrapper(props, store)

          // then
          const manageStockButton = wrapper.find('#manage-stocks')
          expect(manageStockButton.prop('disabled')).toStrictEqual('')
        })
      })
    })

    describe('event tracking', () => {
      it('should track offer creation', () => {
        // given
        const state = {}

        const action = {
          payload: {
            datum: {
              id: 'Ty5645dgfd',
            },
          },
        }
        jest.spyOn(props.query, 'context').mockReturnValue({
          isCreatedEntity: true,
        })
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // when
        wrapper.instance().onHandleFormSuccess(state, action)

        // then
        expect(props.trackCreateOffer).toHaveBeenCalledWith('Ty5645dgfd')
      })

      it('should track offer update', () => {
        // given
        const state = {}

        props.offer = {
          id: 'A9',
          lastProvider: null,
        }

        jest.spyOn(props.query, 'context').mockReturnValue({
          isCreatedEntity: false,
          isModifiedEntity: false,
          readOnly: false,
        })

        const action = {
          payload: {
            datum: {
              id: 'Ty5645dgfd',
            },
          },
        }
        const wrapper = getMountedOfferCreationWrapper(props, store)

        // when
        wrapper.instance().onHandleFormSuccess(state, action)

        // then
        expect(props.trackModifyOffer).toHaveBeenCalledWith('A9')
      })
    })

    describe('when offer is an event', () => {
      it('should display checked isDuo checkbox when offer is duo', () => {
        // given
        props.offer.isEvent = true
        props.formInitialValues.isDuo = true

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)
        const isDuoCheckbox = wrapper.find('.offer-duo-checkbox')

        // then
        expect(isDuoCheckbox.prop('checked')).toBe(true)
      })

      it('should display unchecked isDuo checkbox when offer is not duo', () => {
        // given
        props.offer.isEvent = true

        // when
        const wrapper = getMountedOfferCreationWrapper(props, store)
        const isDuoCheckbox = wrapper.find('.offer-duo-checkbox')

        // then
        expect(isDuoCheckbox.prop('checked')).toBe(false)
      })
    })
  })
})
