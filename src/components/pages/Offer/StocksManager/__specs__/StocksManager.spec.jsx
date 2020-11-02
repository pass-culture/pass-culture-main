import '@testing-library/jest-dom'
import { fireEvent } from '@testing-library/dom'
import { render, screen } from '@testing-library/react'
import { shallow } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from '../../../../../store/testUtils'
import StocksManager from '../StocksManager'

const renderStocksManager = (props, storeItem) => {
  const stubbedStore = configureTestStore({
    data: {},
    ...storeItem,
  })

  render(
    <Provider store={stubbedStore}>
      <MemoryRouter>
        <StocksManager {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('offer | StocksManager', () => {
  let props
  let query
  const stock = {
    available: 10,
    bookingLimitDatetime: '2019-03-06T23:00:00Z',
    bookingRecapSent: null,
    dateModified: '2019-03-06T15:51:39.253527Z',
    dateModifiedAtLastProvider: '2019-03-06T15:51:39.253504Z',
    eventOccurrenceId: null,
    id: 'ARMQ',
    idAtProviders: null,
    isSoftDeleted: false,
    lastProviderId: null,
    modelName: 'Stock',
    offerId: 'AUSQ',
    price: 17,
  }

  beforeEach(() => {
    query = {
      changeToCreation: jest.fn(),
      changeToReadOnly: jest.fn(),
      context: jest.fn().mockReturnValue({}),
    }
    props = {
      dispatch: jest.fn(),
      isEvent: true,
      location: {
        pathname: '/offres/AWHA',
        search: '?gestion',
        hash: '',
        state: undefined,
        key: '4c2v7m',
      },
      offer: {
        name: 'OfferName',
      },
      product: {
        id: 'ABDD',
      },
      query,
      isStockCreationAllowed: true,
      stocks: [stock],
    }
  })

  describe('when managing an event', () => {
    it('should display the event cancellation legal text', () => {
      // when
      renderStocksManager(props)

      // then
      const legalTextFirstSentence =
        "Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 72h avant le début de l'événement."
      const legalTextSecondSentence =
        "Si la date limite de réservation n'est pas encore passée, la place est alors automatiquement remise en vente."
      expect(screen.queryByText(legalTextFirstSentence, { selector: 'span' })).toBeInTheDocument()
      expect(screen.queryByText(legalTextSecondSentence, { selector: 'span' })).toBeInTheDocument()
    })
  })

  describe('when managing a thing', () => {
    it('should not contain the event cancellation legal text', () => {
      // given
      props.isEvent = false

      // when
      renderStocksManager(props)

      // then
      const legalTextFirstSentence =
        "Les réservations peuvent être annulées par les utilisateurs jusque 72h avant le début de l'événement."
      const legalTextSecondSentence =
        "Si la date limite de réservation n'est pas encore passée, la place est alors automatiquement remise en vente."
      expect(
        screen.queryByText(legalTextFirstSentence, { selector: 'span' })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText(legalTextSecondSentence, { selector: 'span' })
      ).not.toBeInTheDocument()
    })
  })

  describe('onClickCreateStockItem', () => {
    it('should prevent reclicking the button to add stock and display new line of stocks to validate', async () => {
      // given
      props.isEvent = true
      renderStocksManager(props)
      const stockButton = screen.getByText('+ Ajouter une date')

      // when
      await fireEvent.click(stockButton)

      // then
      expect(stockButton).toBeDisabled()

      expect(screen.getByTitle('Gratuit si vide')).toBeInTheDocument()
      expect(
        screen.getByTitle(
          "Si ce champ est vide, les réservations seront possibles jusqu'à l'heure de début de l'événement. S'il est rempli, les réservations seront bloquées à 23h59 à la date saisie."
        )
      ).toBeInTheDocument()
    })
  })

  describe('handleShouldPreventCreationOfSecondNotEventStock', () => {
    it('when the creation of second stock is allowed', () => {
      // given
      props.isStockCreationAllowed = true
      const wrapper = shallow(<StocksManager {...props} />)

      // when
      const result = wrapper.instance().handleShouldPreventCreationOfSecondNotEventStock()

      // then
      expect(result).toBeUndefined()
    })

    it('when the creation of second stock is not allowed', () => {
      // given
      props.isStockCreationAllowed = false
      props.query.context.mockReturnValue({
        isCreatedEntity: true,
      })

      const wrapper = shallow(<StocksManager {...props} />)

      // when
      wrapper.instance().handleShouldPreventCreationOfSecondNotEventStock()

      // then
      expect(query.changeToReadOnly).toHaveBeenCalledWith(null, { key: 'stock' })
    })
  }) // todo not done

  describe('handleEnterKey', () => {
    describe('when all stocks are read only', () => {
      beforeEach(() => {
        props.location.search = '?gestion&lieu=CU'
      })

      it('should do nothing when stock creation is not allowed', () => {
        // given
        props.isStockCreationAllowed = false
        const wrapper = shallow(<StocksManager {...props} />)

        // when
        const result = wrapper.instance().handleEnterKey()

        // then
        expect(result).toBeUndefined()
      })

      it('should call focus on add-stock element when it exists', () => {
        // given
        let spy = jest.spyOn(document, 'getElementById')
        const wrapper = shallow(<StocksManager {...props} />)
        let addStockElement = {}

        spy.mockReturnValue(addStockElement)
        addStockElement.focus = () => {}
        jest.spyOn(addStockElement, 'focus')

        // when
        wrapper.instance().handleEnterKey()

        // then
        expect(addStockElement.focus).toHaveBeenCalledWith()
      })

      it('should call query changeToCreation with proper params when creation is allowed', () => {
        // given
        props.isStockCreationAllowed = true
        const wrapper = shallow(<StocksManager {...props} />)

        // when
        wrapper.instance().handleEnterKey()

        // then
        expect(query.changeToCreation).toHaveBeenCalledWith(null, { key: 'stock' })
      })
    })

    describe('when all stocks are not read only', () => {
      it('should click on submit button', () => {
        // given
        props.location.search = '?gestion&lieu=CU&stockMU=modification'
        const wrapper = shallow(<StocksManager {...props} />)

        let spy = jest.spyOn(document, 'querySelector')
        let submitElement = {}

        spy.mockReturnValue(submitElement)
        submitElement.click = () => {}
        jest.spyOn(submitElement, 'click')

        // when
        wrapper.instance().handleEnterKey()

        // then
        expect(submitElement.click).toHaveBeenCalledWith()
      })
    })
  }) // todo not done

  describe('render', () => {
    it('should display an error message', async () => {
      // todo not working
      // given
      props.query = { context: () => ({}) }
      const wrapper = shallow(<StocksManager {...props} />)
      wrapper.setState({
        errors: {
          global: ['Mon message d’erreur custom'],
        },
      })

      // when
      const errorMessage = wrapper.find('[children="global : Mon message d’erreur custom"]')

      // then
      expect(errorMessage).toHaveLength(1)
    })

    it('should display a success message when state is updated with one', () => {
      // given
      props.query = { context: () => ({}) }

      // when
      renderStocksManager(props)

      // then
      const expectedSuccessMessage =
        "Les modifications ont été enregistrées.Si la date de l'évènement a été modifiée, les utilisateurs ayant déjà réservé cette offre seront prévenus par email."
      expect(screen.getByText(expectedSuccessMessage)).toBeInTheDocument()
    })
  })
})
