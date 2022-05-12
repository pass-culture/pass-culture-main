// Empty service worker so the build creates and serves this empty file
// If a former bundle still has a service worker and request for the /service-worker.js file
// it won't fail thanks to the empty file.

// Required following https://create-react-app.dev/docs/making-a-progressive-web-app/#customization
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const ignored = self.__WB_MANIFEST
