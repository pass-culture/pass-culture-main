import { pluralizeWord } from '../pluralizeWord'

describe('utils | pluralizeWord', () => {
  it('should render singular word', () => {
    // When
    const result = pluralizeWord(1, 'réservation')

    // Then
    expect(result).toBe('réservation')
  })

  it('should render plural word', () => {
    // When
    const result = pluralizeWord(2, 'réservation')

    // Then
    expect(result).toBe('réservations')
  })
})
