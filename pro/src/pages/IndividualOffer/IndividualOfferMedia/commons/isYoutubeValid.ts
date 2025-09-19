// This regex is a replicate of what exists backend-side.
// Mind that frontend / backend controls regarding video url always match.
const youtubeVideoRegex = new RegExp(
  /^(https?:\/\/)?(www\.)?(m\.)?(youtube\.com|youtu\.be)(\/watch\?v=|\/embed\/|\/v\/|\/e\/|\/)([^"&?/\s]{11})/
)

export const isYoutubeValid = (url?: string): boolean => {
  if (!url) {
    return false
  }
  try {
    new URL(url)
    return youtubeVideoRegex.test(url)
  } catch {
    return false
  }
}
