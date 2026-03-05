import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'

import { getTitle } from './getTitle'

describe('getTitle', () => {
  const testCases = [
    { mode: OFFER_WIZARD_MODE.CREATION, expected: 'Créer une offre' },
    { mode: OFFER_WIZARD_MODE.READ_ONLY, expected: 'Godzilla' },
    { mode: OFFER_WIZARD_MODE.EDITION, expected: 'Modifier l’offre' },
  ]

  it.each(testCases)('return right title with mode %s', ({
    mode,
    expected,
  }) => {
    const offerName = 'Godzilla'
    const isConfirmationPage = false

    expect(getTitle(mode, isConfirmationPage, offerName)).toEqual(expected)
  })

  it('return right title', () => {
    const offerName = 'Godzilla'
    const isConfirmationPage = true

    expect(
      getTitle(OFFER_WIZARD_MODE.CREATION, isConfirmationPage, offerName)
    ).toEqual('Votre offre a été publiée avec succès')
  })
})
