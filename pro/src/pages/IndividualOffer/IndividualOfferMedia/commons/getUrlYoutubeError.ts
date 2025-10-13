// This regex is a replicate of what exists backend-side.
// Mind that frontend / backend controls always match regarding video url.
const youtubeVideoRegex = new RegExp(
  /^(https?:\/\/)(www\.)?(m\.)?(youtube\.com\b|youtu\.be\b)(\/watch\?v=|\/embed\/|\/v\/|\/e\/|\/)([\w-]{11}\b)/
)

export const getUrlYoutubeError = (url?: string): string | undefined => {
  const INVALID_URL_MSG =
    'Veuillez renseigner une URL valide. Ex : https://exemple.com'
  const NOT_YOUTUBE_MSG =
    'Veuillez renseigner une URL provenant de la plateforme Youtube. Les shorts et les chaînes ne sont pas acceptées.'

  if (!url || url.trim() === '') {
    return NOT_YOUTUBE_MSG
  }

  try {
    const parsed = new URL(url)

    const host = parsed.hostname.toLowerCase()
    const isYoutubeHost =
      host === 'youtu.be' ||
      host === 'www.youtu.be' ||
      host === 'youtube.com' ||
      host === 'www.youtube.com' ||
      host === 'www.m.youtube.com' ||
      host === 'm.youtube.com'
    if (!isYoutubeHost) {
      return NOT_YOUTUBE_MSG
    }

    return youtubeVideoRegex.test(url) ? undefined : NOT_YOUTUBE_MSG
  } catch {
    return INVALID_URL_MSG
  }
}
