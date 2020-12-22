module.exports = {
  moduleNameMapper: {
    '\\.svg': '<rootDir>/src/utils/svgrMock.js',
  },
  modulePaths: ['node_modules', 'src'],
  setupFiles: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom-sixteen',
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{spec,test}.{js,jsx,ts,tsx}',
  ],
  verbose: false,
}
