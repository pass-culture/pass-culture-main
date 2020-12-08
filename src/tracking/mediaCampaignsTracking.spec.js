const { createTrackingIframe } = jest.requireActual('./mediaCampaignsTracking')

function resetDomBody() {
  document.body.innerHTML = ''
}

describe('createTrackingIframe()', () => {
  afterEach(resetDomBody)

  it('should create an iframe with the correct cat and type in src attribute', () => {
    const cat = 'test-cat'
    const iframeId = `floodlight-cat-${cat}`
    createTrackingIframe(cat)

    const iframe = document.getElementById(iframeId)
    expect(iframe.src).toContain('cat=test-cat')
    expect(iframe.src).toContain('type=site')
  })

  it('should not create an iframe if it already exists', () => {
    const documentCreateElementSpy = jest.spyOn(document, 'createElement')
    const cat = 'test-cat'
    createTrackingIframe(cat)
    createTrackingIframe(cat)
    createTrackingIframe(cat)

    expect(documentCreateElementSpy).toHaveBeenCalledTimes(1)
  })
})
