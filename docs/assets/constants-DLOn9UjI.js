import{r as ct}from"./index-B2-qRKKC.js";import"./config-BqmKEuqZ.js";import{u as lt}from"./chunk-EF7DTUVF-Chk6glXc.js";/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Oe=function(e){const t=[];let a=0;for(let n=0;n<e.length;n++){let s=e.charCodeAt(n);s<128?t[a++]=s:s<2048?(t[a++]=s>>6|192,t[a++]=s&63|128):(s&64512)===55296&&n+1<e.length&&(e.charCodeAt(n+1)&64512)===56320?(s=65536+((s&1023)<<10)+(e.charCodeAt(++n)&1023),t[a++]=s>>18|240,t[a++]=s>>12&63|128,t[a++]=s>>6&63|128,t[a++]=s&63|128):(t[a++]=s>>12|224,t[a++]=s>>6&63|128,t[a++]=s&63|128)}return t},ut=function(e){const t=[];let a=0,n=0;for(;a<e.length;){const s=e[a++];if(s<128)t[n++]=String.fromCharCode(s);else if(s>191&&s<224){const r=e[a++];t[n++]=String.fromCharCode((s&31)<<6|r&63)}else if(s>239&&s<365){const r=e[a++],i=e[a++],c=e[a++],o=((s&7)<<18|(r&63)<<12|(i&63)<<6|c&63)-65536;t[n++]=String.fromCharCode(55296+(o>>10)),t[n++]=String.fromCharCode(56320+(o&1023))}else{const r=e[a++],i=e[a++];t[n++]=String.fromCharCode((s&15)<<12|(r&63)<<6|i&63)}}return t.join("")},ht={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(e,t){if(!Array.isArray(e))throw Error("encodeByteArray takes an array as a parameter");this.init_();const a=t?this.byteToCharMapWebSafe_:this.byteToCharMap_,n=[];for(let s=0;s<e.length;s+=3){const r=e[s],i=s+1<e.length,c=i?e[s+1]:0,o=s+2<e.length,l=o?e[s+2]:0,f=r>>2,h=(r&3)<<4|c>>4;let d=(c&15)<<2|l>>6,I=l&63;o||(I=64,i||(d=64)),n.push(a[f],a[h],a[d],a[I])}return n.join("")},encodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?btoa(e):this.encodeByteArray(Oe(e),t)},decodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?atob(e):ut(this.decodeStringToByteArray(e,t))},decodeStringToByteArray(e,t){this.init_();const a=t?this.charToByteMapWebSafe_:this.charToByteMap_,n=[];for(let s=0;s<e.length;){const r=a[e.charAt(s++)],c=s<e.length?a[e.charAt(s)]:0;++s;const l=s<e.length?a[e.charAt(s)]:64;++s;const h=s<e.length?a[e.charAt(s)]:64;if(++s,r==null||c==null||l==null||h==null)throw new dt;const d=r<<2|c>>4;if(n.push(d),l!==64){const I=c<<4&240|l>>2;if(n.push(I),h!==64){const O=l<<6&192|h;n.push(O)}}}return n},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let e=0;e<this.ENCODED_VALS.length;e++)this.byteToCharMap_[e]=this.ENCODED_VALS.charAt(e),this.charToByteMap_[this.byteToCharMap_[e]]=e,this.byteToCharMapWebSafe_[e]=this.ENCODED_VALS_WEBSAFE.charAt(e),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[e]]=e,e>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(e)]=e,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(e)]=e)}}};class dt extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const ft=function(e){const t=Oe(e);return ht.encodeByteArray(t,!0)},Le=function(e){return ft(e).replace(/\./g,"")};function gt(){const e=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof e=="object"&&e.id!==void 0}function Q(){try{return typeof indexedDB=="object"}catch{return!1}}function Re(){return new Promise((e,t)=>{try{let a=!0;const n="validate-browser-context-for-indexeddb-analytics-module",s=self.indexedDB.open(n);s.onsuccess=()=>{s.result.close(),a||self.indexedDB.deleteDatabase(n),e(!0)},s.onupgradeneeded=()=>{a=!1},s.onerror=()=>{var r;t(((r=s.error)==null?void 0:r.message)||"")}}catch(a){t(a)}})}function pt(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const mt="FirebaseError";class D extends Error{constructor(t,a,n){super(a),this.code=t,this.customData=n,this.name=mt,Object.setPrototypeOf(this,D.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,k.prototype.create)}}class k{constructor(t,a,n){this.service=t,this.serviceName=a,this.errors=n}create(t,...a){const n=a[0]||{},s=`${this.service}/${t}`,r=this.errors[t],i=r?Ct(r,n):"Error",c=`${this.serviceName}: ${i} (${s}).`;return new D(s,c,n)}}function Ct(e,t){return e.replace(_t,(a,n)=>{const s=t[n];return s!=null?String(s):`<${n}?>`})}const _t=/\{\$([^}]+)}/g;/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Et=1e3,It=2,bt=4*60*60*1e3,St=.5;function q(e,t=Et,a=It){const n=t*Math.pow(a,e),s=Math.round(St*n*(Math.random()-.5)*2);return Math.min(bt,n+s)}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Fe(e){return e&&e._delegate?e._delegate:e}class y{constructor(t,a,n){this.name=t,this.instanceFactory=a,this.type=n,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */var u;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(u||(u={}));const wt={debug:u.DEBUG,verbose:u.VERBOSE,info:u.INFO,warn:u.WARN,error:u.ERROR,silent:u.SILENT},Tt=u.INFO,yt={[u.DEBUG]:"log",[u.VERBOSE]:"log",[u.INFO]:"info",[u.WARN]:"warn",[u.ERROR]:"error"},At=(e,t,...a)=>{if(t<e.logLevel)return;const n=new Date().toISOString(),s=yt[t];if(s)console[s](`[${n}]  ${e.name}:`,...a);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};class Z{constructor(t){this.name=t,this._logLevel=Tt,this._logHandler=At,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in u))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?wt[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,u.DEBUG,...t),this._logHandler(this,u.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,u.VERBOSE,...t),this._logHandler(this,u.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,u.INFO,...t),this._logHandler(this,u.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,u.WARN,...t),this._logHandler(this,u.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,u.ERROR,...t),this._logHandler(this,u.ERROR,...t)}}const Dt=(e,t)=>t.some(a=>e instanceof a);let ce,le;function Ot(){return ce||(ce=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Lt(){return le||(le=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Me=new WeakMap,z=new WeakMap,Pe=new WeakMap,v=new WeakMap,ee=new WeakMap;function Rt(e){const t=new Promise((a,n)=>{const s=()=>{e.removeEventListener("success",r),e.removeEventListener("error",i)},r=()=>{a(T(e.result)),s()},i=()=>{n(e.error),s()};e.addEventListener("success",r),e.addEventListener("error",i)});return t.then(a=>{a instanceof IDBCursor&&Me.set(a,e)}).catch(()=>{}),ee.set(t,e),t}function Ft(e){if(z.has(e))return;const t=new Promise((a,n)=>{const s=()=>{e.removeEventListener("complete",r),e.removeEventListener("error",i),e.removeEventListener("abort",i)},r=()=>{a(),s()},i=()=>{n(e.error||new DOMException("AbortError","AbortError")),s()};e.addEventListener("complete",r),e.addEventListener("error",i),e.addEventListener("abort",i)});z.set(e,t)}let Y={get(e,t,a){if(e instanceof IDBTransaction){if(t==="done")return z.get(e);if(t==="objectStoreNames")return e.objectStoreNames||Pe.get(e);if(t==="store")return a.objectStoreNames[1]?void 0:a.objectStore(a.objectStoreNames[0])}return T(e[t])},set(e,t,a){return e[t]=a,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function Mt(e){Y=e(Y)}function Pt(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...a){const n=e.call(H(this),t,...a);return Pe.set(n,t.sort?t.sort():[t]),T(n)}:Lt().includes(e)?function(...t){return e.apply(H(this),t),T(Me.get(this))}:function(...t){return T(e.apply(H(this),t))}}function kt(e){return typeof e=="function"?Pt(e):(e instanceof IDBTransaction&&Ft(e),Dt(e,Ot())?new Proxy(e,Y):e)}function T(e){if(e instanceof IDBRequest)return Rt(e);if(v.has(e))return v.get(e);const t=kt(e);return t!==e&&(v.set(e,t),ee.set(t,e)),t}const H=e=>ee.get(e);function ke(e,t,{blocked:a,upgrade:n,blocking:s,terminated:r}={}){const i=indexedDB.open(e,t),c=T(i);return n&&i.addEventListener("upgradeneeded",o=>{n(T(i.result),o.oldVersion,o.newVersion,T(i.transaction),o)}),a&&i.addEventListener("blocked",o=>a(o.oldVersion,o.newVersion,o)),c.then(o=>{r&&o.addEventListener("close",()=>r()),s&&o.addEventListener("versionchange",l=>s(l.oldVersion,l.newVersion,l))}).catch(()=>{}),c}const Nt=["get","getKey","getAll","getAllKeys","count"],Bt=["put","add","delete","clear"],U=new Map;function ue(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(U.get(t))return U.get(t);const a=t.replace(/FromIndex$/,""),n=t!==a,s=Bt.includes(a);if(!(a in(n?IDBIndex:IDBObjectStore).prototype)||!(s||Nt.includes(a)))return;const r=async function(i,...c){const o=this.transaction(i,s?"readwrite":"readonly");let l=o.store;return n&&(l=l.index(c.shift())),(await Promise.all([l[a](...c),s&&o.done]))[0]};return U.set(t,r),r}Mt(e=>({...e,get:(t,a,n)=>ue(t,a)||e.get(t,a,n),has:(t,a)=>!!ue(t,a)||e.has(t,a)}));/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class $t{constructor(t){this.container=t}getPlatformInfoString(){return this.container.getProviders().map(a=>{if(Kt(a)){const n=a.getImmediate();return`${n.library}/${n.version}`}else return null}).filter(a=>a).join(" ")}}function Kt(e){const t=e.getComponent();return(t==null?void 0:t.type)==="VERSION"}const X="@firebase/app",he="0.14.0";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const E=new Z("@firebase/app"),vt="@firebase/app-compat",Ht="@firebase/analytics-compat",Ut="@firebase/analytics",Vt="@firebase/app-check-compat",xt="@firebase/app-check",jt="@firebase/auth",Gt="@firebase/auth-compat",Wt="@firebase/database",qt="@firebase/data-connect",zt="@firebase/database-compat",Yt="@firebase/functions",Xt="@firebase/functions-compat",Jt="@firebase/installations",Qt="@firebase/installations-compat",Zt="@firebase/messaging",ea="@firebase/messaging-compat",ta="@firebase/performance",aa="@firebase/performance-compat",na="@firebase/remote-config",sa="@firebase/remote-config-compat",ra="@firebase/storage",ia="@firebase/storage-compat",oa="@firebase/firestore",ca="@firebase/ai",la="@firebase/firestore-compat",ua="firebase",ha="12.0.0",da={[X]:"fire-core",[vt]:"fire-core-compat",[Ut]:"fire-analytics",[Ht]:"fire-analytics-compat",[xt]:"fire-app-check",[Vt]:"fire-app-check-compat",[jt]:"fire-auth",[Gt]:"fire-auth-compat",[Wt]:"fire-rtdb",[qt]:"fire-data-connect",[zt]:"fire-rtdb-compat",[Yt]:"fire-fn",[Xt]:"fire-fn-compat",[Jt]:"fire-iid",[Qt]:"fire-iid-compat",[Zt]:"fire-fcm",[ea]:"fire-fcm-compat",[ta]:"fire-perf",[aa]:"fire-perf-compat",[na]:"fire-rc",[sa]:"fire-rc-compat",[ra]:"fire-gcs",[ia]:"fire-gcs-compat",[oa]:"fire-fst",[la]:"fire-fst-compat",[ca]:"fire-vertex","fire-js":"fire-js",[ua]:"fire-js-all"};/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const fa=new Map,ga=new Map,de=new Map;function fe(e,t){try{e.container.addComponent(t)}catch(a){E.debug(`Component ${t.name} failed to register with FirebaseApp ${e.name}`,a)}}function A(e){const t=e.name;if(de.has(t))return E.debug(`There were multiple attempts to register component ${t}.`),!1;de.set(t,e);for(const a of fa.values())fe(a,e);for(const a of ga.values())fe(a,e);return!0}function Ne(e,t){const a=e.container.getProvider("heartbeat").getImmediate({optional:!0});return a&&a.triggerHeartbeat(),e.container.getProvider(t)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const pa={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},te=new k("app","Firebase",pa);/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ma=ha;function _(e,t,a){let n=da[e]??e;a&&(n+=`-${a}`);const s=n.match(/\s|\//),r=t.match(/\s|\//);if(s||r){const i=[`Unable to register library "${n}" with version "${t}":`];s&&i.push(`library name "${n}" contains illegal characters (whitespace or "/")`),s&&r&&i.push("and"),r&&i.push(`version name "${t}" contains illegal characters (whitespace or "/")`),E.warn(i.join(" "));return}A(new y(`${n}-version`,()=>({library:n,version:t}),"VERSION"))}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ca="firebase-heartbeat-database",_a=1,P="firebase-heartbeat-store";let V=null;function Be(){return V||(V=ke(Ca,_a,{upgrade:(e,t)=>{switch(t){case 0:try{e.createObjectStore(P)}catch(a){console.warn(a)}}}}).catch(e=>{throw te.create("idb-open",{originalErrorMessage:e.message})})),V}async function Ea(e){try{const a=(await Be()).transaction(P),n=await a.objectStore(P).get($e(e));return await a.done,n}catch(t){if(t instanceof D)E.warn(t.message);else{const a=te.create("idb-get",{originalErrorMessage:t==null?void 0:t.message});E.warn(a.message)}}}async function ge(e,t){try{const n=(await Be()).transaction(P,"readwrite");await n.objectStore(P).put(t,$e(e)),await n.done}catch(a){if(a instanceof D)E.warn(a.message);else{const n=te.create("idb-set",{originalErrorMessage:a==null?void 0:a.message});E.warn(n.message)}}}function $e(e){return`${e.name}!${e.options.appId}`}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ia=1024,ba=30;class Sa{constructor(t){this.container=t,this._heartbeatsCache=null;const a=this.container.getProvider("app").getImmediate();this._storage=new Ta(a),this._heartbeatsCachePromise=this._storage.read().then(n=>(this._heartbeatsCache=n,n))}async triggerHeartbeat(){var t,a;try{const s=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),r=pe();if(((t=this._heartbeatsCache)==null?void 0:t.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((a=this._heartbeatsCache)==null?void 0:a.heartbeats)==null)||this._heartbeatsCache.lastSentHeartbeatDate===r||this._heartbeatsCache.heartbeats.some(i=>i.date===r))return;if(this._heartbeatsCache.heartbeats.push({date:r,agent:s}),this._heartbeatsCache.heartbeats.length>ba){const i=ya(this._heartbeatsCache.heartbeats);this._heartbeatsCache.heartbeats.splice(i,1)}return this._storage.overwrite(this._heartbeatsCache)}catch(n){E.warn(n)}}async getHeartbeatsHeader(){var t;try{if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((t=this._heartbeatsCache)==null?void 0:t.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const a=pe(),{heartbeatsToSend:n,unsentEntries:s}=wa(this._heartbeatsCache.heartbeats),r=Le(JSON.stringify({version:2,heartbeats:n}));return this._heartbeatsCache.lastSentHeartbeatDate=a,s.length>0?(this._heartbeatsCache.heartbeats=s,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),r}catch(a){return E.warn(a),""}}}function pe(){return new Date().toISOString().substring(0,10)}function wa(e,t=Ia){const a=[];let n=e.slice();for(const s of e){const r=a.find(i=>i.agent===s.agent);if(r){if(r.dates.push(s.date),me(a)>t){r.dates.pop();break}}else if(a.push({agent:s.agent,dates:[s.date]}),me(a)>t){a.pop();break}n=n.slice(1)}return{heartbeatsToSend:a,unsentEntries:n}}class Ta{constructor(t){this.app=t,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return Q()?Re().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const a=await Ea(this.app);return a!=null&&a.heartbeats?a:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(t){if(await this._canUseIndexedDBPromise){const n=await this.read();return ge(this.app,{lastSentHeartbeatDate:t.lastSentHeartbeatDate??n.lastSentHeartbeatDate,heartbeats:t.heartbeats})}else return}async add(t){if(await this._canUseIndexedDBPromise){const n=await this.read();return ge(this.app,{lastSentHeartbeatDate:t.lastSentHeartbeatDate??n.lastSentHeartbeatDate,heartbeats:[...n.heartbeats,...t.heartbeats]})}else return}}function me(e){return Le(JSON.stringify({version:2,heartbeats:e})).length}function ya(e){if(e.length===0)return-1;let t=0,a=e[0].date;for(let n=1;n<e.length;n++)e[n].date<a&&(a=e[n].date,t=n);return t}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Aa(e){A(new y("platform-logger",t=>new $t(t),"PRIVATE")),A(new y("heartbeat",t=>new Sa(t),"PRIVATE")),_(X,he,e),_(X,he,"esm2020"),_("fire-js","")}Aa("");const Ke="@firebase/installations",ae="0.6.19";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ve=1e4,He=`w:${ae}`,Ue="FIS_v2",Da="https://firebaseinstallations.googleapis.com/v1",Oa=60*60*1e3,La="installations",Ra="Installations";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Fa={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},R=new k(La,Ra,Fa);function Ve(e){return e instanceof D&&e.code.includes("request-failed")}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function xe({projectId:e}){return`${Da}/projects/${e}/installations`}function je(e){return{token:e.token,requestStatus:2,expiresIn:Pa(e.expiresIn),creationTime:Date.now()}}async function Ge(e,t){const n=(await t.json()).error;return R.create("request-failed",{requestName:e,serverCode:n.code,serverMessage:n.message,serverStatus:n.status})}function We({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function Ma(e,{refreshToken:t}){const a=We(e);return a.append("Authorization",ka(t)),a}async function qe(e){const t=await e();return t.status>=500&&t.status<600?e():t}function Pa(e){return Number(e.replace("s","000"))}function ka(e){return`${Ue} ${e}`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Na({appConfig:e,heartbeatServiceProvider:t},{fid:a}){const n=xe(e),s=We(e),r=t.getImmediate({optional:!0});if(r){const l=await r.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const i={fid:a,authVersion:Ue,appId:e.appId,sdkVersion:He},c={method:"POST",headers:s,body:JSON.stringify(i)},o=await qe(()=>fetch(n,c));if(o.ok){const l=await o.json();return{fid:l.fid||a,registrationStatus:2,refreshToken:l.refreshToken,authToken:je(l.authToken)}}else throw await Ge("Create Installation",o)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function ze(e){return new Promise(t=>{setTimeout(t,e)})}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ba(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const $a=/^[cdef][\w-]{21}$/,J="";function Ka(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const a=va(e);return $a.test(a)?a:J}catch{return J}}function va(e){return Ba(e).substr(0,22)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function $(e){return`${e.appName}!${e.appId}`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ye=new Map;function Xe(e,t){const a=$(e);Je(a,t),Ha(a,t)}function Je(e,t){const a=Ye.get(e);if(a)for(const n of a)n(t)}function Ha(e,t){const a=Ua();a&&a.postMessage({key:e,fid:t}),Va()}let L=null;function Ua(){return!L&&"BroadcastChannel"in self&&(L=new BroadcastChannel("[Firebase] FID Change"),L.onmessage=e=>{Je(e.data.key,e.data.fid)}),L}function Va(){Ye.size===0&&L&&(L.close(),L=null)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const xa="firebase-installations-database",ja=1,F="firebase-installations-store";let x=null;function ne(){return x||(x=ke(xa,ja,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(F)}}})),x}async function B(e,t){const a=$(e),s=(await ne()).transaction(F,"readwrite"),r=s.objectStore(F),i=await r.get(a);return await r.put(t,a),await s.done,(!i||i.fid!==t.fid)&&Xe(e,t.fid),t}async function Qe(e){const t=$(e),n=(await ne()).transaction(F,"readwrite");await n.objectStore(F).delete(t),await n.done}async function K(e,t){const a=$(e),s=(await ne()).transaction(F,"readwrite"),r=s.objectStore(F),i=await r.get(a),c=t(i);return c===void 0?await r.delete(a):await r.put(c,a),await s.done,c&&(!i||i.fid!==c.fid)&&Xe(e,c.fid),c}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function se(e){let t;const a=await K(e.appConfig,n=>{const s=Ga(n),r=Wa(e,s);return t=r.registrationPromise,r.installationEntry});return a.fid===J?{installationEntry:await t}:{installationEntry:a,registrationPromise:t}}function Ga(e){const t=e||{fid:Ka(),registrationStatus:0};return Ze(t)}function Wa(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const s=Promise.reject(R.create("app-offline"));return{installationEntry:t,registrationPromise:s}}const a={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},n=qa(e,a);return{installationEntry:a,registrationPromise:n}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:za(e)}:{installationEntry:t}}async function qa(e,t){try{const a=await Na(e,t);return B(e.appConfig,a)}catch(a){throw Ve(a)&&a.customData.serverCode===409?await Qe(e.appConfig):await B(e.appConfig,{fid:t.fid,registrationStatus:0}),a}}async function za(e){let t=await Ce(e.appConfig);for(;t.registrationStatus===1;)await ze(100),t=await Ce(e.appConfig);if(t.registrationStatus===0){const{installationEntry:a,registrationPromise:n}=await se(e);return n||a}return t}function Ce(e){return K(e,t=>{if(!t)throw R.create("installation-not-found");return Ze(t)})}function Ze(e){return Ya(e)?{fid:e.fid,registrationStatus:0}:e}function Ya(e){return e.registrationStatus===1&&e.registrationTime+ve<Date.now()}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Xa({appConfig:e,heartbeatServiceProvider:t},a){const n=Ja(e,a),s=Ma(e,a),r=t.getImmediate({optional:!0});if(r){const l=await r.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const i={installation:{sdkVersion:He,appId:e.appId}},c={method:"POST",headers:s,body:JSON.stringify(i)},o=await qe(()=>fetch(n,c));if(o.ok){const l=await o.json();return je(l)}else throw await Ge("Generate Auth Token",o)}function Ja(e,{fid:t}){return`${xe(e)}/${t}/authTokens:generate`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function re(e,t=!1){let a;const n=await K(e.appConfig,r=>{if(!et(r))throw R.create("not-registered");const i=r.authToken;if(!t&&en(i))return r;if(i.requestStatus===1)return a=Qa(e,t),r;{if(!navigator.onLine)throw R.create("app-offline");const c=an(r);return a=Za(e,c),c}});return a?await a:n.authToken}async function Qa(e,t){let a=await _e(e.appConfig);for(;a.authToken.requestStatus===1;)await ze(100),a=await _e(e.appConfig);const n=a.authToken;return n.requestStatus===0?re(e,t):n}function _e(e){return K(e,t=>{if(!et(t))throw R.create("not-registered");const a=t.authToken;return nn(a)?{...t,authToken:{requestStatus:0}}:t})}async function Za(e,t){try{const a=await Xa(e,t),n={...t,authToken:a};return await B(e.appConfig,n),a}catch(a){if(Ve(a)&&(a.customData.serverCode===401||a.customData.serverCode===404))await Qe(e.appConfig);else{const n={...t,authToken:{requestStatus:0}};await B(e.appConfig,n)}throw a}}function et(e){return e!==void 0&&e.registrationStatus===2}function en(e){return e.requestStatus===2&&!tn(e)}function tn(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+Oa}function an(e){const t={requestStatus:1,requestTime:Date.now()};return{...e,authToken:t}}function nn(e){return e.requestStatus===1&&e.requestTime+ve<Date.now()}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function sn(e){const t=e,{installationEntry:a,registrationPromise:n}=await se(t);return n?n.catch(console.error):re(t).catch(console.error),a.fid}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function rn(e,t=!1){const a=e;return await on(a),(await re(a,t)).token}async function on(e){const{registrationPromise:t}=await se(e);t&&await t}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function cn(e){if(!e||!e.options)throw j("App Configuration");if(!e.name)throw j("App Name");const t=["projectId","apiKey","appId"];for(const a of t)if(!e.options[a])throw j(a);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function j(e){return R.create("missing-app-config-values",{valueName:e})}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const tt="installations",ln="installations-internal",un=e=>{const t=e.getProvider("app").getImmediate(),a=cn(t),n=Ne(t,"heartbeat");return{app:t,appConfig:a,heartbeatServiceProvider:n,_delete:()=>Promise.resolve()}},hn=e=>{const t=e.getProvider("app").getImmediate(),a=Ne(t,tt).getImmediate();return{getId:()=>sn(a),getToken:s=>rn(a,s)}};function dn(){A(new y(tt,un,"PUBLIC")),A(new y(ln,hn,"PRIVATE"))}dn();_(Ke,ae);_(Ke,ae,"esm2020");/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ee="analytics",fn="firebase_id",gn="origin",pn=60*1e3,mn="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",ie="https://www.googletagmanager.com/gtag/js";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const g=new Z("@firebase/analytics");/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Cn={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-initialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},m=new k("analytics","Analytics",Cn);/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function _n(e){if(!e.startsWith(ie)){const t=m.create("invalid-gtag-resource",{gtagURL:e});return g.warn(t.message),""}return e}function at(e){return Promise.all(e.map(t=>t.catch(a=>a)))}function En(e,t){let a;return window.trustedTypes&&(a=window.trustedTypes.createPolicy(e,t)),a}function In(e,t){const a=En("firebase-js-sdk-policy",{createScriptURL:_n}),n=document.createElement("script"),s=`${ie}?l=${e}&id=${t}`;n.src=a?a==null?void 0:a.createScriptURL(s):s,n.async=!0,document.head.appendChild(n)}function bn(e){let t=[];return Array.isArray(window[e])?t=window[e]:window[e]=t,t}async function Sn(e,t,a,n,s,r){const i=n[s];try{if(i)await t[i];else{const o=(await at(a)).find(l=>l.measurementId===s);o&&await t[o.appId]}}catch(c){g.error(c)}e("config",s,r)}async function wn(e,t,a,n,s){try{let r=[];if(s&&s.send_to){let i=s.send_to;Array.isArray(i)||(i=[i]);const c=await at(a);for(const o of i){const l=c.find(h=>h.measurementId===o),f=l&&t[l.appId];if(f)r.push(f);else{r=[];break}}}r.length===0&&(r=Object.values(t)),await Promise.all(r),e("event",n,s||{})}catch(r){g.error(r)}}function Tn(e,t,a,n){async function s(r,...i){try{if(r==="event"){const[c,o]=i;await wn(e,t,a,c,o)}else if(r==="config"){const[c,o]=i;await Sn(e,t,a,n,c,o)}else if(r==="consent"){const[c,o]=i;e("consent",c,o)}else if(r==="get"){const[c,o,l]=i;e("get",c,o,l)}else if(r==="set"){const[c]=i;e("set",c)}else e(r,...i)}catch(c){g.error(c)}}return s}function yn(e,t,a,n,s){let r=function(...i){window[n].push(arguments)};return window[s]&&typeof window[s]=="function"&&(r=window[s]),window[s]=Tn(r,e,t,a),{gtagCore:r,wrappedGtag:window[s]}}function An(e){const t=window.document.getElementsByTagName("script");for(const a of Object.values(t))if(a.src&&a.src.includes(ie)&&a.src.includes(e))return a;return null}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Dn=30,On=1e3;class Ln{constructor(t={},a=On){this.throttleMetadata=t,this.intervalMillis=a}getThrottleMetadata(t){return this.throttleMetadata[t]}setThrottleMetadata(t,a){this.throttleMetadata[t]=a}deleteThrottleMetadata(t){delete this.throttleMetadata[t]}}const nt=new Ln;function Rn(e){return new Headers({Accept:"application/json","x-goog-api-key":e})}async function Fn(e){var i;const{appId:t,apiKey:a}=e,n={method:"GET",headers:Rn(a)},s=mn.replace("{app-id}",t),r=await fetch(s,n);if(r.status!==200&&r.status!==304){let c="";try{const o=await r.json();(i=o.error)!=null&&i.message&&(c=o.error.message)}catch{}throw m.create("config-fetch-failed",{httpStatus:r.status,responseMessage:c})}return r.json()}async function Mn(e,t=nt,a){const{appId:n,apiKey:s,measurementId:r}=e.options;if(!n)throw m.create("no-app-id");if(!s){if(r)return{measurementId:r,appId:n};throw m.create("no-api-key")}const i=t.getThrottleMetadata(n)||{backoffCount:0,throttleEndTimeMillis:Date.now()},c=new Nn;return setTimeout(async()=>{c.abort()},pn),st({appId:n,apiKey:s,measurementId:r},i,c,t)}async function st(e,{throttleEndTimeMillis:t,backoffCount:a},n,s=nt){var c;const{appId:r,measurementId:i}=e;try{await Pn(n,t)}catch(o){if(i)return g.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${i} provided in the "measurementId" field in the local Firebase config. [${o==null?void 0:o.message}]`),{appId:r,measurementId:i};throw o}try{const o=await Fn(e);return s.deleteThrottleMetadata(r),o}catch(o){const l=o;if(!kn(l)){if(s.deleteThrottleMetadata(r),i)return g.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${i} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:r,measurementId:i};throw o}const f=Number((c=l==null?void 0:l.customData)==null?void 0:c.httpStatus)===503?q(a,s.intervalMillis,Dn):q(a,s.intervalMillis),h={throttleEndTimeMillis:Date.now()+f,backoffCount:a+1};return s.setThrottleMetadata(r,h),g.debug(`Calling attemptFetch again in ${f} millis`),st(e,h,n,s)}}function Pn(e,t){return new Promise((a,n)=>{const s=Math.max(t-Date.now(),0),r=setTimeout(a,s);e.addEventListener(()=>{clearTimeout(r),n(m.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function kn(e){if(!(e instanceof D)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class Nn{constructor(){this.listeners=[]}addEventListener(t){this.listeners.push(t)}abort(){this.listeners.forEach(t=>t())}}async function Bn(e,t,a,n,s){if(s&&s.global){e("event",a,n);return}else{const r=await t,i={...n,send_to:r};e("event",a,i)}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function $n(){if(Q())try{await Re()}catch(e){return g.warn(m.create("indexeddb-unavailable",{errorInfo:e==null?void 0:e.toString()}).message),!1}else return g.warn(m.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function Kn(e,t,a,n,s,r,i){const c=Mn(e);c.then(d=>{a[d.measurementId]=d.appId,e.options.measurementId&&d.measurementId!==e.options.measurementId&&g.warn(`The measurement ID in the local Firebase config (${e.options.measurementId}) does not match the measurement ID fetched from the server (${d.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(d=>g.error(d)),t.push(c);const o=$n().then(d=>{if(d)return n.getId()}),[l,f]=await Promise.all([c,o]);An(r)||In(r,l.measurementId),s("js",new Date);const h=(i==null?void 0:i.config)??{};return h[gn]="firebase",h.update=!0,f!=null&&(h[fn]=f),s("config",l.measurementId,h),l.measurementId}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class vn{constructor(t){this.app=t}_delete(){return delete M[this.app.options.appId],Promise.resolve()}}let M={},Ie=[];const be={};let G="dataLayer",Hn="gtag",Se,rt,we=!1;function Un(){const e=[];if(gt()&&e.push("This is a browser extension environment."),pt()||e.push("Cookies are not available."),e.length>0){const t=e.map((n,s)=>`(${s+1}) ${n}`).join(" "),a=m.create("invalid-analytics-context",{errorInfo:t});g.warn(a.message)}}function Vn(e,t,a){Un();const n=e.options.appId;if(!n)throw m.create("no-app-id");if(!e.options.apiKey)if(e.options.measurementId)g.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${e.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw m.create("no-api-key");if(M[n]!=null)throw m.create("already-exists",{id:n});if(!we){bn(G);const{wrappedGtag:r,gtagCore:i}=yn(M,Ie,be,G,Hn);rt=r,Se=i,we=!0}return M[n]=Kn(e,Ie,be,t,Se,G,a),new vn(e)}function xn(e,t,a,n){e=Fe(e),Bn(rt,M[e.app.options.appId],t,a,n).catch(s=>g.error(s))}const Te="@firebase/analytics",ye="0.10.18";function jn(){A(new y(Ee,(t,{options:a})=>{const n=t.getProvider("app").getImmediate(),s=t.getProvider("installations-internal").getImmediate();return Vn(n,s,a)},"PUBLIC")),A(new y("analytics-internal",e,"PRIVATE")),_(Te,ye),_(Te,ye,"esm2020");function e(t){try{const a=t.getProvider(Ee).getImmediate();return{logEvent:(n,s,r)=>xn(a,n,s,r)}}catch(a){throw m.create("interop-component-reg-failed",{reason:a})}}}jn();const W="@firebase/remote-config",Ae="0.6.6";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Gn="remote-config",De=100;/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Wn={"already-initialized":"Remote Config already initialized","registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser","custom-signal-max-allowed-signals":"Setting more than {$maxSignals} custom signals is not supported."},p=new k("remoteconfig","Remote Config",Wn);function qn(e){const t=Fe(e);return t._initializePromise||(t._initializePromise=t._storageCache.loadFromStorage().then(()=>{t._isInitializationComplete=!0})),t._initializePromise}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class zn{constructor(t,a,n,s){this.client=t,this.storage=a,this.storageCache=n,this.logger=s}isCachedDataFresh(t,a){if(!a)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const n=Date.now()-a,s=n<=t;return this.logger.debug(`Config fetch cache check. Cache age millis: ${n}. Cache max age millis (minimumFetchIntervalMillis setting): ${t}. Is cache hit: ${s}.`),s}async fetch(t){const[a,n]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(n&&this.isCachedDataFresh(t.cacheMaxAgeMillis,a))return n;t.eTag=n&&n.eTag;const s=await this.client.fetch(t),r=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return s.status===200&&r.push(this.storage.setLastSuccessfulFetchResponse(s)),await Promise.all(r),s}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Yn(e=navigator){return e.languages&&e.languages[0]||e.language}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Xn{constructor(t,a,n,s,r,i){this.firebaseInstallations=t,this.sdkVersion=a,this.namespace=n,this.projectId=s,this.apiKey=r,this.appId=i}async fetch(t){const[a,n]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),r=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":t.eTag||"*"},c={sdk_version:this.sdkVersion,app_instance_id:a,app_instance_id_token:n,app_id:this.appId,language_code:Yn(),custom_signals:t.customSignals},o={method:"POST",headers:i,body:JSON.stringify(c)},l=fetch(r,o),f=new Promise((C,S)=>{t.signal.addEventListener(()=>{const oe=new Error("The operation was aborted.");oe.name="AbortError",S(oe)})});let h;try{await Promise.race([l,f]),h=await l}catch(C){let S="fetch-client-network";throw(C==null?void 0:C.name)==="AbortError"&&(S="fetch-timeout"),p.create(S,{originalErrorMessage:C==null?void 0:C.message})}let d=h.status;const I=h.headers.get("ETag")||void 0;let O,b;if(h.status===200){let C;try{C=await h.json()}catch(S){throw p.create("fetch-client-parse",{originalErrorMessage:S==null?void 0:S.message})}O=C.entries,b=C.state}if(b==="INSTANCE_STATE_UNSPECIFIED"?d=500:b==="NO_CHANGE"?d=304:(b==="NO_TEMPLATE"||b==="EMPTY_CONFIG")&&(O={}),d!==304&&d!==200)throw p.create("fetch-status",{httpStatus:d});return{status:d,eTag:I,config:O}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Jn(e,t){return new Promise((a,n)=>{const s=Math.max(t-Date.now(),0),r=setTimeout(a,s);e.addEventListener(()=>{clearTimeout(r),n(p.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function Qn(e){if(!(e instanceof D)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class Zn{constructor(t,a){this.client=t,this.storage=a}async fetch(t){const a=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(t,a)}async attemptFetch(t,{throttleEndTimeMillis:a,backoffCount:n}){await Jn(t.signal,a);try{const s=await this.client.fetch(t);return await this.storage.deleteThrottleMetadata(),s}catch(s){if(!Qn(s))throw s;const r={throttleEndTimeMillis:Date.now()+q(n),backoffCount:n+1};return await this.storage.setThrottleMetadata(r),this.attemptFetch(t,r)}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const es=60*1e3,ts=12*60*60*1e3;class as{get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}constructor(t,a,n,s,r){this.app=t,this._client=a,this._storageCache=n,this._storage=s,this._logger=r,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:es,minimumFetchIntervalMillis:ts},this.defaultConfig={}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function N(e,t){const a=e.target.error||void 0;return p.create(t,{originalErrorMessage:a&&(a==null?void 0:a.message)})}const w="app_namespace_store",ns="firebase_remote_config",ss=1;function rs(){return new Promise((e,t)=>{try{const a=indexedDB.open(ns,ss);a.onerror=n=>{t(N(n,"storage-open"))},a.onsuccess=n=>{e(n.target.result)},a.onupgradeneeded=n=>{const s=n.target.result;switch(n.oldVersion){case 0:s.createObjectStore(w,{keyPath:"compositeKey"})}}}catch(a){t(p.create("storage-open",{originalErrorMessage:a==null?void 0:a.message}))}})}class it{getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(t){return this.set("last_fetch_status",t)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(t){return this.set("last_successful_fetch_timestamp_millis",t)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(t){return this.set("last_successful_fetch_response",t)}getActiveConfig(){return this.get("active_config")}setActiveConfig(t){return this.set("active_config",t)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(t){return this.set("active_config_etag",t)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(t){return this.set("throttle_metadata",t)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}getCustomSignals(){return this.get("custom_signals")}}class is extends it{constructor(t,a,n,s=rs()){super(),this.appId=t,this.appName=a,this.namespace=n,this.openDbPromise=s}async setCustomSignals(t){const n=(await this.openDbPromise).transaction([w],"readwrite"),s=await this.getWithTransaction("custom_signals",n),r=ot(t,s||{});return await this.setWithTransaction("custom_signals",r,n),r}async getWithTransaction(t,a){return new Promise((n,s)=>{const r=a.objectStore(w),i=this.createCompositeKey(t);try{const c=r.get(i);c.onerror=o=>{s(N(o,"storage-get"))},c.onsuccess=o=>{const l=o.target.result;n(l?l.value:void 0)}}catch(c){s(p.create("storage-get",{originalErrorMessage:c==null?void 0:c.message}))}})}async setWithTransaction(t,a,n){return new Promise((s,r)=>{const i=n.objectStore(w),c=this.createCompositeKey(t);try{const o=i.put({compositeKey:c,value:a});o.onerror=l=>{r(N(l,"storage-set"))},o.onsuccess=()=>{s()}}catch(o){r(p.create("storage-set",{originalErrorMessage:o==null?void 0:o.message}))}})}async get(t){const n=(await this.openDbPromise).transaction([w],"readonly");return this.getWithTransaction(t,n)}async set(t,a){const s=(await this.openDbPromise).transaction([w],"readwrite");return this.setWithTransaction(t,a,s)}async delete(t){const a=await this.openDbPromise;return new Promise((n,s)=>{const i=a.transaction([w],"readwrite").objectStore(w),c=this.createCompositeKey(t);try{const o=i.delete(c);o.onerror=l=>{s(N(l,"storage-delete"))},o.onsuccess=()=>{n()}}catch(o){s(p.create("storage-delete",{originalErrorMessage:o==null?void 0:o.message}))}})}createCompositeKey(t){return[this.appId,this.appName,this.namespace,t].join()}}class os extends it{constructor(){super(...arguments),this.storage={}}async get(t){return Promise.resolve(this.storage[t])}async set(t,a){return this.storage[t]=a,Promise.resolve(void 0)}async delete(t){return this.storage[t]=void 0,Promise.resolve()}async setCustomSignals(t){const a=this.storage.custom_signals||{};return this.storage.custom_signals=ot(t,a),Promise.resolve(this.storage.custom_signals)}}function ot(e,t){const a={...t,...e},n=Object.fromEntries(Object.entries(a).filter(([s,r])=>r!==null).map(([s,r])=>typeof r=="number"?[s,r.toString()]:[s,r]));if(Object.keys(n).length>De)throw p.create("custom-signal-max-allowed-signals",{maxSignals:De});return n}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class cs{constructor(t){this.storage=t}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}getCustomSignals(){return this.customSignals}async loadFromStorage(){const t=this.storage.getLastFetchStatus(),a=this.storage.getLastSuccessfulFetchTimestampMillis(),n=this.storage.getActiveConfig(),s=this.storage.getCustomSignals(),r=await t;r&&(this.lastFetchStatus=r);const i=await a;i&&(this.lastSuccessfulFetchTimestampMillis=i);const c=await n;c&&(this.activeConfig=c);const o=await s;o&&(this.customSignals=o)}setLastFetchStatus(t){return this.lastFetchStatus=t,this.storage.setLastFetchStatus(t)}setLastSuccessfulFetchTimestampMillis(t){return this.lastSuccessfulFetchTimestampMillis=t,this.storage.setLastSuccessfulFetchTimestampMillis(t)}setActiveConfig(t){return this.activeConfig=t,this.storage.setActiveConfig(t)}async setCustomSignals(t){this.customSignals=await this.storage.setCustomSignals(t)}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function ls(){A(new y(Gn,e,"PUBLIC").setMultipleInstances(!0)),_(W,Ae),_(W,Ae,"esm2020");function e(t,{options:a}){const n=t.getProvider("app").getImmediate(),s=t.getProvider("installations-internal").getImmediate(),{projectId:r,apiKey:i,appId:c}=n.options;if(!r)throw p.create("registration-project-id");if(!i)throw p.create("registration-api-key");if(!c)throw p.create("registration-app-id");const o=(a==null?void 0:a.templateId)||"firebase",l=Q()?new is(c,n.name,o):new os,f=new cs(l),h=new Z(W);h.logLevel=u.ERROR;const d=new Xn(s,ma,o,r,i,c),I=new Zn(d,l),O=new zn(I,l,f,h),b=new as(n,O,f,l,h);return qn(b),b}}ls();const us=e=>Object.fromEntries(new URLSearchParams(e)),hs=()=>{const e=lt(),t=us(e.search);return"utm_campaign"in t&&"utm_medium"in t&&"utm_source"in t?{traffic_campaign:t.utm_campaign,traffic_medium:t.utm_medium,traffic_source:t.utm_source}:{}},ms=()=>{const e=hs();return{logEvent:ct.useCallback((a,n)=>{},[e])}};var ds=(e=>(e.CLICKED_BOOKING="hasClickedBooking",e.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",e.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",e.CLICKED_CONSULT_CGU="hasClickedConsultCGU",e.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",e.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",e.CLICKED_CREATE_VENUE="hasClickedCreateVenue",e.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",e.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",e.CLICKED_SAVE_VENUE="hasClickedSaveVenue",e.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",e.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",e.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",e.CLICKED_EDIT_PROFILE="hasClickedEditProfile",e.CLICKED_EDIT_COLLECTIVE_OFFER="hasClickedEditCollectiveOffer",e.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ="hasClickedHomeStatsPendingOffersFaq",e.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",e.CLICKED_HELP_CENTER="hasClickedHelpCenter",e.CLICKED_HOME="hasClickedHome",e.CLICKED_LOGOUT="hasClickedLogout",e.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER="hasClickedConfirmedAddHeadlineOffer",e.CLICKED_DISCOVERED_HEADLINE_OFFER="hasClickedDiscoveredHeadlineOffer",e.CLICKED_OFFER="hasClickedOffer",e.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",e.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",e.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",e.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK="hasClickedPartnerBlockPreviewVenueLink",e.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK="hasClickedPartnerBlockCopyVenueLink",e.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK="hasClickedPartnerBlockDmsApplicationLink",e.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK="hasClickedPartnerBlockCollectiveHelpLink",e.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",e.CLICKED_PRO="hasClickedPro",e.CLICKED_REIMBURSEMENT="hasClickedReimbursement",e.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",e.CLICKED_STATS="hasClickedOffererStats",e.CLICKED_TICKET="hasClickedTicket",e.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",e.CLICKED_DUPLICATE_BOOKABLE_OFFER="hasClickedDuplicateBookableOffer",e.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",e.CLICKED_HELP_LINK="hasClickedHelpLink",e.CLICKED_RESET_FILTERS="hasClickedResetFilter",e.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",e.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",e.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",e.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",e.CLICKED_CONTACT_OUR_TEAMS="hasClickedContactOurTeams",e.CLICKED_ARCHIVE_COLLECTIVE_OFFER="hasClickedArchiveCollectiveOffer",e.CLICKED_SAVE_DRAFT_AND_EXIT_COLLECTIVE_OFFER="hasClickedSaveDraftAndExitCollectiveOffer",e.CLICKED_SEE_TEMPLATE_OFFER_EXAMPLE="hasClickedSeeTemplateOfferExample",e.FIRST_LOGIN="firstLogin",e.PAGE_VIEW="page_view",e.SIGNUP_FORM_ABORT="signupFormAbort",e.SIGNUP_FORM_SUCCESS="signupFormSuccess",e.TUTO_PAGE_VIEW="tutoPageView",e.DELETE_DRAFT_OFFER="DeleteDraftOffer",e.CLICKED_NO_VENUE="hasClickedNoVenue",e.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",e.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",e.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",e.CLICKED_ADD_IMAGE="hasClickedAddImage",e.DRAG_OR_SELECTED_IMAGE="hasDragOrSelectedImage",e.CLICKED_SAVE_IMAGE="hasClickedSaveImage",e.CLICKED_DELETE_STOCK="hasClickedDeleteStock",e.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",e.CLICKED_DOWNLOAD_OFFER_BOOKINGS="hasDownloadedBookings",e.CLICKED_PAGE_FOR_APP_HOME="hasClickedPageForAppHome",e.CLICKED_PAGE_FOR_ADAGE_HOME="hasClickedPageForAdageHome",e.CLICKED_INVOICES_DOWNLOAD="hasClickedInvoicesDownload",e.CLICKED_PUBLISH_FUTURE_OFFER_EARLIER="hasClickedPublishFutureOfferEarlier",e.EXTRA_PRO_DATA="extra_pro_data",e.CLICKED_NEW_EVOLUTIONS="hasClickedNewEvolutions",e.CLICKED_CONSULT_HELP="hasClickedConsultHelp",e.UPDATED_BOOKING_LIMIT_DATE="hasUpdatedBookingLimitDate",e.CLICKED_GENERATE_TEMPLATE_DESCRIPTION="hasClickedGenerateTemplateDescription",e.UPDATED_EVENT_STOCK_FILTERS="hasUpdatedEventStockFilters",e.CLICKED_VALIDATE_ADD_RECURRENCE_DATES="hasClickedValidateAddRecurrenceDates",e.FAKE_DOOR_VIDEO_INTERESTED="fakeDoorVideoInterested",e.CLICKED_SORT_STOCKS_TABLE="hasClickedSortStocksTable",e))(ds||{});export{ds as E,ms as u};
