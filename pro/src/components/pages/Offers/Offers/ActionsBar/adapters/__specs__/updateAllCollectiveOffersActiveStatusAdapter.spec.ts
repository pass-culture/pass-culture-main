import { updateAllCollectiveOffersActiveStatusAdapter } from '../updateAllCollectiveOffersActiveStatusAdapter'

describe('updateAllCollectiveOffersActiveStatusAdapter', () => {
  it('should deactivate all collective offers and confirm', async () => {
    // given
    // @ts-ignore
    jest
      .spyOn(window, 'fetch')
      .mockResolvedValueOnce(new Response(new Blob(), { status: 204 }))

    const response = await updateAllCollectiveOffersActiveStatusAdapter({
      searchFilters: { isActive: false },
      nbSelectedOffers: 10,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(
      'Les offres sont en cours de désactivation, veuillez rafraichir dans quelques instants'
    )
  })

  it('should activate all collective offers and confirm', async () => {
    // given
    // @ts-ignore
    jest
      .spyOn(window, 'fetch')
      .mockResolvedValueOnce(new Response(new Blob(), { status: 204 }))

    const response = await updateAllCollectiveOffersActiveStatusAdapter({
      searchFilters: { isActive: true },
      nbSelectedOffers: 10,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(
      'Les offres sont en cours d’activation, veuillez rafraichir dans quelques instants'
    )
  })

  it('should return an error when the update has failed', async () => {
    // given
    // @ts-ignore
    jest.spyOn(window, 'fetch').mockResolvedValueOnce({
      status: 422,
    })

    // when
    const response = await updateAllCollectiveOffersActiveStatusAdapter({
      searchFilters: { isActive: false },
      nbSelectedOffers: 10,
    })

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Une erreur est survenue lors de la désactivation des offres'
    )
  })
})
