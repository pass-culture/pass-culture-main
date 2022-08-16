/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { FetchHttpRequest } from './core/FetchHttpRequest';

import { ApiContremarqueService } from './services/ApiContremarqueService';
import { ApiOffresCollectivesService } from './services/ApiOffresCollectivesService';
import { ApiStocksService } from './services/ApiStocksService';
import { DefaultService } from './services/DefaultService';

type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;

export class AppClientV2 {

  public readonly apiContremarque: ApiContremarqueService;
  public readonly apiOffresCollectives: ApiOffresCollectivesService;
  public readonly apiStocks: ApiStocksService;
  public readonly default: DefaultService;

  public readonly request: BaseHttpRequest;

  constructor(config?: Partial<OpenAPIConfig>, HttpRequest: HttpRequestConstructor = FetchHttpRequest) {
    this.request = new HttpRequest({
      BASE: config?.BASE ?? '',
      VERSION: config?.VERSION ?? '2',
      WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
      CREDENTIALS: config?.CREDENTIALS ?? 'include',
      TOKEN: config?.TOKEN,
      USERNAME: config?.USERNAME,
      PASSWORD: config?.PASSWORD,
      HEADERS: config?.HEADERS,
      ENCODE_PATH: config?.ENCODE_PATH,
    });

    this.apiContremarque = new ApiContremarqueService(this.request);
    this.apiOffresCollectives = new ApiOffresCollectivesService(this.request);
    this.apiStocks = new ApiStocksService(this.request);
    this.default = new DefaultService(this.request);
  }
}

