/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { FetchHttpRequest } from './core/FetchHttpRequest';
import { DPrCiEApiContremarqueService } from './services/DPrCiEApiContremarqueService';
import { DPrCiEApiStocksService } from './services/DPrCiEApiStocksService';
type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;
export class AppClientV2 {
  public readonly dPrCiEApiContremarque: DPrCiEApiContremarqueService;
  public readonly dPrCiEApiStocks: DPrCiEApiStocksService;
  public readonly request: BaseHttpRequest;
  constructor(config?: Partial<OpenAPIConfig>, HttpRequest: HttpRequestConstructor = FetchHttpRequest) {
    this.request = new HttpRequest({
      BASE: config?.BASE ?? 'http://localhost:5001',
      VERSION: config?.VERSION ?? '0.1',
      WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
      CREDENTIALS: config?.CREDENTIALS ?? 'include',
      TOKEN: config?.TOKEN,
      USERNAME: config?.USERNAME,
      PASSWORD: config?.PASSWORD,
      HEADERS: config?.HEADERS,
      ENCODE_PATH: config?.ENCODE_PATH,
    });
    this.dPrCiEApiContremarque = new DPrCiEApiContremarqueService(this.request);
    this.dPrCiEApiStocks = new DPrCiEApiStocksService(this.request);
  }
}

