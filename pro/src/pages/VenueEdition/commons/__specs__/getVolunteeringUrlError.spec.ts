import { describe, expect, it } from 'vitest'

import { getVolunteeringUrlError } from '../getVolunteeringUrlError'

describe('getVolunteeringUrlError', () => {
  it('should return undefined when empty or whitespace', () => {
    expect(getVolunteeringUrlError('')).toBeUndefined()
    expect(getVolunteeringUrlError(' ')).toBeUndefined()
  })

  it('should reject wrong host', () => {
    expect(getVolunteeringUrlError('https://coucou.fr/organisations/yop')).toBe(
      'Veuillez renseigner une URL provenant de la plateforme jeveuxaider.gouv'
    )
  })

  it('should reject wrong path', () => {
    expect(getVolunteeringUrlError('https://jeveuxaider.gouv.fr/kikou')).toBe(
      'Veuillez renseigner l’URL de votre page organisation. Ex : https://www.jeveuxaider.gouv.fr/organisations/exemple'
    )
  })

  it('should accept a valid organisation URL', () => {
    expect(
      getVolunteeringUrlError('https://jeveuxaider.gouv.fr/organisations/yop')
    ).toBeUndefined()
  })

  it('should return invalid URL message when not parseable', () => {
    expect(getVolunteeringUrlError('not-a-url')).toBe(
      'Veuillez renseigner une URL valide. Ex : https://exemple.com'
    )
  })
})
