import { mapDispatchToProps, mapStateToProps, mergeProps } from '../OfferContainer'
import state from '../../../utils/mocks/state'

describe('src | components | pages | Offer | Offer | OfferContainer ', () => {
  let props

  beforeEach(() => {
    props = {
      match: {
        params: {
          offerId: 'UU',
        },
      },
      query: {
        translate: jest.fn(),
      },
      trackCreateOffer: jest.fn(),
      trackModifyOffer: jest.fn(),
    }
  })

  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        formInitialValues: {
          ageMax: undefined,
          ageMin: undefined,
          bookingEmail: 'booking.email@test.com',
          condition: undefined,
          description: undefined,
          durationMinutes: undefined,
          extraData: undefined,
          isDuo: undefined,
          isNational: undefined,
          mediaUrls: undefined,
          name: undefined,
          offererId: 'BA',
          type: undefined,
          url: undefined,
          venueId: 'DA',
        },
        formOffererId: 'BA',
        formVenueId: 'DA',
        isEditableOffer: undefined,
        musicSubOptions: undefined,
        offer: {
          bookingEmail: 'booking.email@test.com',
          dateCreated: '2019-03-07T10:39:23.560392Z',
          dateModifiedAtLastProvider: '2019-03-07T10:40:05.443621Z',
          id: 'UU',
          idAtProviders: null,
          isActive: true,
          isEvent: false,
          isThing: true,
          lastProviderId: null,
          mediationsIds: ['H4'],
          modelName: 'Offer',
          productId: 'LY',
          stocksIds: ['MU'],
          venueId: 'DA',
        },
        offerer: {
          address: 'RUE DES SAPOTILLES',
          bic: 'QSDFGH8Z566',
          city: 'Cayenne',
          dateCreated: '2019-03-07T10:39:23.560414Z',
          dateModifiedAtLastProvider: '2019-03-07T10:39:57.823508Z',
          iban: 'FR7630001007941234567890185',
          id: 'BA',
          idAtProviders: null,
          isActive: true,
          isValidated: true,
          lastProviderId: null,
          modelName: 'Offerer',
          nOffers: 5,
          name: 'Bar des amis',
          postalCode: '97300',
          siren: '222222233',
          thumbCount: 0,
          validationToken: null,
        },
        offerers: [
          {
            address: 'RUE DES SAPOTILLES',
            bic: 'QSDFGH8Z566',
            city: 'Cayenne',
            dateCreated: '2019-03-07T10:39:23.560414Z',
            dateModifiedAtLastProvider: '2019-03-07T10:39:57.823508Z',
            iban: 'FR7630001007941234567890185',
            id: 'BA',
            idAtProviders: null,
            isActive: true,
            isValidated: true,
            lastProviderId: null,
            modelName: 'Offerer',
            nOffers: 5,
            name: 'Bar des amis',
            postalCode: '97300',
            siren: '222222233',
            thumbCount: 0,
            validationToken: null,
          },
          {
            address: 'RUE DES POMMES ROSAS',
            city: 'Cayenne',
            dateCreated: '2019-03-07T10:39:23.560414Z',
            dateModifiedAtLastProvider: '2019-03-07T10:39:57.843884Z',
            id: 'CA',
            idAtProviders: null,
            isActive: true,
            isValidated: false,
            lastProviderId: null,
            modelName: 'Offerer',
            nOffers: 10,
            name: 'Cinéma du coin',
            postalCode: '97300',
            siren: '222222232',
            thumbCount: 0,
            validationToken: 'w3hDQgjYRIyYTxOYY08nwgH3BzI',
          },
        ],
        offerTypeError: undefined,
        providers: [],
        selectedOfferType: {
          appLabel: 'Jeux Vidéo',
          description:
            'Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?',
          id: 12,
          offlineOnly: false,
          onlineOnly: true,
          proLabel: 'Jeux Vidéo',
          sublabel: 'Jouer',
          type: 'Thing',
          value: 'ThingType.JEUX_VIDEO',
        },
        showSubOptions: undefined,
        stocks: [
          {
            available: 10,
            bookingLimitDatetime: null,
            bookingRecapSent: null,
            dateModified: '2019-03-07T10:40:07.318721Z',
            dateModifiedAtLastProvider: '2019-03-07T10:40:07.318695Z',
            eventOccurrenceId: null,
            groupSize: 1,
            id: 'MU',
            idAtProviders: null,
            isSoftDeleted: false,
            lastProviderId: null,
            modelName: 'Stock',
            offerId: 'UU',
            price: 17,
          },
        ],
        types: [
          {
            appLabel: 'Audiovisuel (Films sur supports physiques et VOD)',
            description:
              'Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?',
            id: 9,
            offlineOnly: false,
            onlineOnly: false,
            proLabel: 'Audiovisuel (Films sur supports physiques et VOD)',
            sublabel: 'Regarder',
            type: 'Thing',
            value: 'ThingType.AUDIOVISUEL',
          },
          {
            appLabel: 'Jeux Vidéo',
            description:
              'Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?',
            id: 12,
            offlineOnly: false,
            onlineOnly: true,
            proLabel: 'Jeux Vidéo',
            sublabel: 'Jouer',
            type: 'Thing',
            value: 'ThingType.JEUX_VIDEO',
          },
          {
            appLabel: 'Livre — Édition',
            description:
              'S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?',
            id: 13,
            offlineOnly: false,
            onlineOnly: false,
            proLabel: 'Livre — Édition',
            sublabel: 'Lire',
            type: 'Thing',
            value: 'ThingType.LIVRE_EDITION',
          },
          {
            appLabel: 'Musique (sur supports physiques ou en ligne)',
            description:
              'Plutôt rock, rap ou classique ? Sur un smartphone avec des écouteurs ou entre amis au concert ?',
            id: 16,
            offlineOnly: false,
            onlineOnly: false,
            proLabel: 'Musique (sur supports physiques ou en ligne)',
            sublabel: 'Écouter',
            type: 'Thing',
            value: 'ThingType.MUSIQUE',
          },
          {
            appLabel: 'pass Culture : activation en ligne',
            description: 'Activez votre pass Culture grâce à cette offre',
            id: 8,
            offlineOnly: false,
            onlineOnly: true,
            proLabel: 'pass Culture : activation en ligne',
            sublabel: 'Activation',
            type: 'Thing',
            value: 'ThingType.ACTIVATION',
          },
          {
            appLabel: 'Presse (Abonnements)',
            description:
              'S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?',
            id: 18,
            offlineOnly: false,
            onlineOnly: true,
            proLabel: 'Presse (Abonnements)',
            sublabel: 'Lire',
            type: 'Thing',
            value: 'ThingType.PRESSE_ABO',
          },
        ],
        url: 'https://ilestencoretemps.fr/',
        venue: {
          address: null,
          bookingEmail: 'john.doe@test.com',
          city: null,
          comment: null,
          dateModifiedAtLastProvider: '2019-03-07T10:40:03.234016Z',
          departementCode: null,
          id: 'DA',
          idAtProviders: null,
          isValidated: true,
          isVirtual: true,
          lastProviderId: null,
          latitude: 48.83638,
          longitude: 2.40027,
          managingOffererId: 'BA',
          modelName: 'Venue',
          name: 'Le Sous-sol (Offre numérique)',
          postalCode: null,
          siret: null,
          thumbCount: 0,
          validationToken: null,
        },
        venuesMatchingOfferType: [
          {
            address: null,
            bookingEmail: 'john.doe@test.com',
            city: null,
            comment: null,
            dateModifiedAtLastProvider: '2019-03-07T10:40:03.234016Z',
            departementCode: null,
            id: 'DA',
            idAtProviders: null,
            isValidated: true,
            isVirtual: true,
            lastProviderId: null,
            latitude: 48.83638,
            longitude: 2.40027,
            managingOffererId: 'BA',
            modelName: 'Venue',
            name: 'Le Sous-sol (Offre numérique)',
            postalCode: null,
            siret: null,
            thumbCount: 0,
            validationToken: null,
          },
        ],
      })
    })
  })

  describe('mergeProps', () => {
    it('should spread stateProps, dispatchProps and ownProps into mergedProps', () => {
      // given
      const stateProps = {}
      const dispatchProps = {}
      const ownProps = {
        match: {
          params: {},
        },
      }

      // when
      const mergedProps = mergeProps(stateProps, dispatchProps, ownProps)

      // then
      expect(mergedProps).toStrictEqual({
        match: ownProps.match,
        trackCreateOffer: expect.any(Function),
        trackModifyOffer: expect.any(Function),
      })
    })

    it('should map a tracking event for creating an offer', () => {
      // given
      const stateProps = {}
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }

      // when
      mergeProps(stateProps, {}, ownProps).trackCreateOffer('RTgfd67')

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'createOffer',
        name: 'RTgfd67',
      })
    })

    it('should map a tracking event for updating an offer', () => {
      // given
      const stateProps = {}
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }

      // when
      mergeProps(stateProps, {}, ownProps).trackModifyOffer('RTgfd67')

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'modifyOffer',
        name: 'RTgfd67',
      })
    })
  })

  describe('mapDispatchToProps', () => {
    let dispatch
    let props

    beforeEach(() => {
      dispatch = jest.fn()
      props = mapDispatchToProps(dispatch)
    })

    describe('updateFormSetIsDuo', () => {
      it('should update offer isDuo value in form', () => {
        // given
        const isDuo = true

        // when
        props.updateFormSetIsDuo(isDuo)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: undefined,
          name: 'offer',
          patch: {
            isDuo: true,
          },
          type: 'MERGE_FORM_OFFER_ISDUO',
        })
      })
    })
  })
})
