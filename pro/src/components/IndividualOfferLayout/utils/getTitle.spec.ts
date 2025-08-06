import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'

import { getTitle } from './getTitle'

describe('getTitle', () => {
  const testCases = [
    { mode: OFFER_WIZARD_MODE.CREATION, expected: 'Créer une offre' },
    { mode: OFFER_WIZARD_MODE.READ_ONLY, expected: 'Consulter l’offre' },
    { mode: OFFER_WIZARD_MODE.EDITION, expected: 'Modifier l’offre' },
  ]

  it.each(testCases)(
    'return right title with mode %s',
    ({ mode, expected }) => {
      expect(getTitle(mode)).toEqual(expected)
    }
  )
})
