module.exports = {
  collectCoverageFrom: [
    '**/*.{js,jsx}',
    '!**/*Mock.jsx',
    '!jest.setup.js',
    '!.jest-polyfill.js',
    // "!**/node_modules/**",
  ],
  moduleFileExtensions: ['web.js', 'js', 'json', 'web.jsx', 'jsx', 'node'],
  moduleNameMapper: {
    '^react-native$': 'react-native-web',
  },
  modulePaths: ['node_modules', 'src'],
  setupFiles: ['<rootDir>/.jest-polyfill.js', '<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom-sixteen',
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx}',
    '<rootDir>/src/**/?(*.)(spec|test).{js,jsx}',
    '**/?(*.)+(spec).js?(x)',
  ],
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/'],
  testURL: 'http://localhost',
  transform: {
    '^.+\\.js$': 'babel-jest',
    '^.+\\.(js|jsx)$': '<rootDir>/node_modules/babel-jest',
    '^.+\\.css$': '<rootDir>/config/jest/cssTransform.js',
    '^(?!.*\\.(js|jsx|css|json)$)': '<rootDir>/config/jest/fileTransform.js',
  },
  transformIgnorePatterns: ['<rootDir>/node_modules/', '[/\\\\]node_modules[/\\\\].+\\.(js|jsx)$'],
  verbose: true,
}
