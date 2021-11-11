export function getPageY(event) {
  if (window.TouchEvent && event instanceof TouchEvent) {
    const lastTouchIndex = event.changedTouches.length - 1
    return event.changedTouches[lastTouchIndex].pageY
  }
  return event.pageY
}
