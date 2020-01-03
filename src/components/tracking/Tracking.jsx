const Traking = () => {
  if (window.location.href === 'https://app.passculture.beta.gouv.fr/beta') {
    snaptr('track', 'PAGE_VIEW')
    fbq('track', 'PageView')
  }

  return null
}

export default Traking
