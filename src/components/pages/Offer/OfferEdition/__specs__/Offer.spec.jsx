import React from 'react'
import { shallow } from 'enzyme'
import { Field, Form, showModal } from 'pass-culture-shared'

import Offer from '../Offer'
import MediationsManager from '../../MediationsManager/MediationsManagerContainer'
import Titles from '../../../../layout/Titles/Titles'
import LocalProviderInformation from '../../LocalProviderInformation/LocalProviderInformationContainer'
import { VenueName } from '../VenueName'
import { OffererName } from '../OffererName'
import StocksManagerContainer from '../../StocksManager/StocksManagerContainer'

describe('components | OfferEdition | Offer ', () => {
  let dispatch
  let props
  let history

  beforeEach(() => {
    history = {
      push: jest.fn(),
    }
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
      selectedOfferType: {},
      showOfferModificationValidationNotification: () => {},
      offer: {
        id: 'SN',
        name: 'Super Livre',
        lastProvider: null,
      },
      history,
      trackCreateOffer: jest.fn(),
      trackModifyOffer: jest.fn(),
      venuesMatchingOfferType: [],
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Offer {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('handleSuccess', () => {
    describe('when the offer is successfully modified', () => {
      it('should redirect to offer page', () => {
        // given
        const queryChangeToReadOnly = jest.fn()

        props.offer.id = '26B'
        props.match.params = {}
        props.query.changeToReadOnly = queryChangeToReadOnly

        const wrapper = shallow(<Offer {...props} />)

        // when
        wrapper.instance().onHandleFormSuccess({})

        // then
        expect(history.push).toHaveBeenCalledWith('/offres/26B')
      })

      it('should display a validation modification notification', () => {
        // given
        const showOfferModificationValidationNotificationStub = jest.fn()
        const showOfferModificationErrorNotificationStub = jest.fn()

        props.showOfferModificationValidationNotification = showOfferModificationValidationNotificationStub
        props.showOfferModificationErrorNotification = showOfferModificationErrorNotificationStub

        props.offer.id = '26B'
        props.match.params = {}

        const wrapper = shallow(<Offer {...props} />)

        // when
        wrapper.instance().onHandleFormSuccess({})

        // then
        expect(props.showOfferModificationValidationNotification).toHaveBeenCalledWith()
      })
    })
  })

  describe('handleShowStocksManager', () => {
    it('should pass offerId as a props to the StocksManagerContainer', () => {
      // given
      const wrapper = shallow(<Offer {...props} />)
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

  describe('isNational', () => {
    it('should display isNational if admin user', () => {
      // given
      props.currentUser.isAdmin = true
      const wrapper = shallow(<Offer {...props} />)

      // when
      const result = wrapper.find(Field).find('[name="isNational"]')

      // then
      expect(result.prop('label')).toBe('Rayonnement national')
    })
  })

  describe('hasConditionalField', () => {
    it('should return false without selected offer type', () => {
      // given
      props.selectedOfferType = undefined
      const wrapper = shallow(<Offer {...props} />)

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
        const wrapper = shallow(<Offer {...props} />)

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
        props.match.params.offerId = 'N9'
        props.offer = {
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

        // when
        const wrapper = shallow(<Offer {...props} />)
        const mediationsManagerComponent = wrapper.find(MediationsManager)

        // then
        expect(mediationsManagerComponent).toHaveLength(1)
      })
    })

    describe('when updating the offer', () => {
      it('should display a limited textarea field to define name of the offer', () => {
        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        const field = wrapper.find(Field).at(0)
        expect(field).toHaveLength(1)
        expect(field.prop('label')).toBe('Titre de l’offre')
        expect(field.prop('required')).toBe(true)
        expect(field.prop('maxLength')).toBe(90)
        expect(field.prop('displayMaxLength')).toBe(true)
        expect(field.prop('type')).toBe('textarea')
      })

      describe('when the offer is imported from Allocine', () => {
        it('should allow to update isDuo but no other fields', () => {
          // given
          props.match.params = {
            offerId: 'VAG',
          }
          props.selectedOfferType = {
            type: 'Event',
          }
          props.offer = {
            id: 'VAG',
            productId: '6GD',
            isEvent: true,
            isThing: false,
            lastProvider: {
              name: 'Allociné',
            },
            activeMediation: {
              id: 'MED',
              isActive: true,
            },
            mediationsIds: ['MED'],
          }

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const form_fields = wrapper.find(Field)
          const isDuoForm = wrapper.find('#isDuo')
          expect(isDuoForm.props()).not.toHaveProperty('disabled')
          expect(isDuoForm.props()).not.toHaveProperty('readOnly')

          expect(form_fields.find("[label='Titre de l’offre']").prop('readOnly')).toBe(true)
          expect(form_fields.find("[label='Durée']").prop('readOnly')).toBe(true)
          expect(
            form_fields.find("[label='Email auquel envoyer les réservations']").prop('readOnly')
          ).toBe(true)
          expect(form_fields.find("[label='Description']").prop('readOnly')).toBe(true)
        })

        it('should be possible to manage stocks', () => {
          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const manageStockButton = wrapper.find('#manage-stocks')
          expect(manageStockButton.prop('disabled')).toStrictEqual('')
        })
      })

      describe('when the offer is imported from Titelive', () => {
        beforeEach(() => {
          props.offer = {
            id: 'VAG',
            productId: '6GD',
            isEvent: true,
            isThing: false,
            lastProvider: {
              name: 'Titelive',
            },
            activeMediation: {
              id: 'MED',
              isActive: true,
            },
            mediationsIds: ['MED'],
          }
        })

        it('should not allow to edit title', () => {
          // given
          props.match.params = {
            offerId: 'VAG',
          }
          props.selectedOfferType = {
            type: 'Event',
          }

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const form_fields = wrapper.find(Field)
          expect(form_fields.find("[label='Titre de l’offre']").prop('readOnly')).toBe(true)
        })

        it('should not allow to edit description', () => {
          // given
          props.match.params = {
            offerId: 'VAG',
          }
          props.selectedOfferType = {
            type: 'Event',
          }

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const form_fields = wrapper.find(Field)
          expect(form_fields.find("[label='Description']").prop('readOnly')).toBe(true)
        })

        it('should not be possible to manage stocks', () => {
          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const manageStockButton = wrapper.find('#manage-stocks')
          expect(manageStockButton.prop('disabled')).toStrictEqual('disabled')
        })
      })

      describe('when the offer is not imported', () => {
        beforeEach(() => {
          props.offer = {
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
        })

        it('should update a product when no offer type', () => {
          // given
          props.match.params = {
            offerId: 'VAG',
          }
          props.query.context = () => ({
            isCreatedEntity: false,
            isModifiedEntity: false,
            readOnly: true,
          })

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          expect(wrapper.find(Form).prop('action')).toStrictEqual('/offers/VAG')
        })

        it('should create a new Event when event type given', () => {
          // given
          props.match.params = {
            offerId: 'VAG',
          }
          props.selectedOfferType = {
            type: 'Event',
          }
          props.offer = {
            id: 'VAG',
            mediationId: 'TR',
            productId: '6GD',
            isEvent: true,
            isThing: false,
            lastProvider: null,
          }

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          expect(wrapper.find(Form).prop('action')).toStrictEqual('/offers/VAG')
        })

        it('should display preview link', () => {
          // given
          props.match.params = {
            offerId: 'VAG',
          }
          props.selectedOfferType = {
            type: 'Event',
          }
          props.offer = {
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
          const wrapper = shallow(<Offer {...props} />)

          // when
          const preview_section = wrapper.find(Titles)

          // then
          const preview_link = preview_section.dive().find('OfferPreviewLink')
          expect(preview_link.prop('href')).toMatch('/offre/details/VAG/MED')
        })

        it('should allow to update every fields', () => {
          // given
          props.match.params = {
            offerId: 'VAG',
          }
          props.selectedOfferType = {
            type: 'Event',
          }
          props.offer = {
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

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const form_fields = wrapper.find(Field)
          expect(form_fields.find("[label='Titre de l’offre']").prop('readOnly')).toBe(false)
          expect(form_fields.find("[label='Durée']").prop('readOnly')).toBe(false)
          expect(
            form_fields.find("[label='Email auquel envoyer les réservations']").prop('readOnly')
          ).toBe(false)
          expect(form_fields.find("[label='Description']").prop('readOnly')).toBe(false)
        })

        it('should be possible to manage stocks', () => {
          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const manageStockButton = wrapper.find('#manage-stocks')
          expect(manageStockButton.prop('disabled')).toStrictEqual('')
        })
      })
    })

    describe('display venue informations', () => {
      it('should display venue name when venue publicName is not provided', () => {
        // given
        props.venue = { name: 'Théatre 12', publicName: null }

        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        const venueName = wrapper.find(VenueName)
        expect(venueName.prop('name')).toStrictEqual('Théatre 12')
      })

      it('should display venue public name when venue public name is provided', () => {
        // given
        props.venue = { name: 'Théatre 12', publicName: 'Théâtre de la nouvelle êre' }

        // when
        const wrapper = shallow(<Offer {...props} />)

        // then
        const venueName = wrapper.find(VenueName)
        expect(venueName.prop('name')).toStrictEqual('Théâtre de la nouvelle êre')
      })
    })

    it('should display offerer', () => {
      // given
      props.offerer = { name: 'Nom de la structure' }

      // when
      const wrapper = shallow(<Offer {...props} />)

      // then
      const offererName = wrapper.find(OffererName)
      expect(offererName.prop('name')).toStrictEqual('Nom de la structure')
    })

    it('should display LocalProviderInformation if offer was generated from local provider', () => {
      // given
      props.query.context = () => ({
        isCreatedEntity: false,
        isModifiedEntity: false,
        readOnly: true,
      })
      props.isEditableOffer = false
      props.offerer = {
        id: 'AZERT',
      }
      props.product = {
        id: '6GD',
        name: 'super livre',
        thumbUrl: 'http://localhost/image/6GD',
      }
      props.offer = {
        id: 'VAG',
        productId: '6GD',
        isEvent: true,
        isThing: false,
        activeMediation: {
          id: 'MED',
        },
        lastProvider: {
          name: 'TiteLive Stocks',
        },
      }

      // when
      const wrapper = shallow(<Offer {...props} />)

      // then
      const localProviderInformationComponent = wrapper.find(LocalProviderInformation)
      expect(localProviderInformationComponent).toHaveLength(1)
      expect(localProviderInformationComponent.prop('offererId')).toBe('AZERT')
      expect(localProviderInformationComponent.prop('isTiteLive')).toBe(true)
      expect(localProviderInformationComponent.prop('isAllocine')).toBe(false)
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
        const wrapper = shallow(<Offer {...props} />)

        // then
        const manageStockButton = wrapper.find('#manage-stocks')
        expect(manageStockButton.prop('disabled')).toStrictEqual('')
      })
    })

    describe('stock management button', () => {
      describe('when offer is from Titelive provider', () => {
        it('should not be possible to change stock values', () => {
          // given
          props.offer.lastProvider = {
            name: 'Titelive',
          }

          // when
          const wrapper = shallow(<Offer {...props} />)

          // then
          const manageStockButton = wrapper.find('#manage-stocks')
          expect(manageStockButton.prop('disabled')).toStrictEqual('disabled')
        })
      })

      describe('when offer is from Allociné provider', () => {
        it('should be possible to change stock values', () => {
          // given
          props.offer.lastProvider = {
            name: 'Allociné',
          }

          // when
          const wrapper = shallow(<Offer {...props} />)

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
          const wrapper = shallow(<Offer {...props} />)

          // then
          const manageStockButton = wrapper.find('#manage-stocks')
          expect(manageStockButton.prop('disabled')).toStrictEqual('')
        })
      })
    })

    describe('event tracking', () => {
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
        const wrapper = shallow(<Offer {...props} />)

        // when
        wrapper.instance().onHandleFormSuccess(state, action)

        // then
        expect(props.trackModifyOffer).toHaveBeenCalledWith('A9')
      })
    })
  })
})
