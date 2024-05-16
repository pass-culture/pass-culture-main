import{j as D}from"./jsx-runtime-X2b_N9AH.js";import{r as N}from"./index-uCp2LrAq.js";import"./config-yp2pWrHW.js";import{f as It}from"./full-help-Co3hxUDJ.js";import{S as bt}from"./SvgIcon-DP_815J1.js";import"./_commonjsHelpers-BosuxZz1.js";/**
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
 */const Be=function(e){const t=[];let n=0;for(let r=0;r<e.length;r++){let s=e.charCodeAt(r);s<128?t[n++]=s:s<2048?(t[n++]=s>>6|192,t[n++]=s&63|128):(s&64512)===55296&&r+1<e.length&&(e.charCodeAt(r+1)&64512)===56320?(s=65536+((s&1023)<<10)+(e.charCodeAt(++r)&1023),t[n++]=s>>18|240,t[n++]=s>>12&63|128,t[n++]=s>>6&63|128,t[n++]=s&63|128):(t[n++]=s>>12|224,t[n++]=s>>6&63|128,t[n++]=s&63|128)}return t},wt=function(e){const t=[];let n=0,r=0;for(;n<e.length;){const s=e[n++];if(s<128)t[r++]=String.fromCharCode(s);else if(s>191&&s<224){const a=e[n++];t[r++]=String.fromCharCode((s&31)<<6|a&63)}else if(s>239&&s<365){const a=e[n++],i=e[n++],o=e[n++],c=((s&7)<<18|(a&63)<<12|(i&63)<<6|o&63)-65536;t[r++]=String.fromCharCode(55296+(c>>10)),t[r++]=String.fromCharCode(56320+(c&1023))}else{const a=e[n++],i=e[n++];t[r++]=String.fromCharCode((s&15)<<12|(a&63)<<6|i&63)}}return t.join("")},yt={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(e,t){if(!Array.isArray(e))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=t?this.byteToCharMapWebSafe_:this.byteToCharMap_,r=[];for(let s=0;s<e.length;s+=3){const a=e[s],i=s+1<e.length,o=i?e[s+1]:0,c=s+2<e.length,l=c?e[s+2]:0,d=a>>2,f=(a&3)<<4|o>>4;let g=(o&15)<<2|l>>6,p=l&63;c||(p=64,i||(g=64)),r.push(n[d],n[f],n[g],n[p])}return r.join("")},encodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?btoa(e):this.encodeByteArray(Be(e),t)},decodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?atob(e):wt(this.decodeStringToByteArray(e,t))},decodeStringToByteArray(e,t){this.init_();const n=t?this.charToByteMapWebSafe_:this.charToByteMap_,r=[];for(let s=0;s<e.length;){const a=n[e.charAt(s++)],o=s<e.length?n[e.charAt(s)]:0;++s;const l=s<e.length?n[e.charAt(s)]:64;++s;const f=s<e.length?n[e.charAt(s)]:64;if(++s,a==null||o==null||l==null||f==null)throw new St;const g=a<<2|o>>4;if(r.push(g),l!==64){const p=o<<4&240|l>>2;if(r.push(p),f!==64){const b=l<<6&192|f;r.push(b)}}}return r},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let e=0;e<this.ENCODED_VALS.length;e++)this.byteToCharMap_[e]=this.ENCODED_VALS.charAt(e),this.charToByteMap_[this.byteToCharMap_[e]]=e,this.byteToCharMapWebSafe_[e]=this.ENCODED_VALS_WEBSAFE.charAt(e),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[e]]=e,e>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(e)]=e,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(e)]=e)}}};class St extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const Tt=function(e){const t=Be(e);return yt.encodeByteArray(t,!0)},$e=function(e){return Tt(e).replace(/\./g,"")};function At(){try{return typeof indexedDB=="object"}catch{return!1}}function Dt(){return new Promise((e,t)=>{try{let n=!0;const r="validate-browser-context-for-indexeddb-analytics-module",s=self.indexedDB.open(r);s.onsuccess=()=>{s.result.close(),n||self.indexedDB.deleteDatabase(r),e(!0)},s.onupgradeneeded=()=>{n=!1},s.onerror=()=>{var a;t(((a=s.error)===null||a===void 0?void 0:a.message)||"")}}catch(n){t(n)}})}/**
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
 */const Ot="FirebaseError";let re=class He extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=Ot,Object.setPrototypeOf(this,He.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,xe.prototype.create)}},xe=class{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},s=`${this.service}/${t}`,a=this.errors[t],i=a?Rt(a,r):"Error",o=`${this.serviceName}: ${i} (${s}).`;return new re(s,o,r)}};function Rt(e,t){return e.replace(Lt,(n,r)=>{const s=t[r];return s!=null?String(s):`<${r}?>`})}const Lt=/\{\$([^}]+)}/g;let X=class{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}};/**
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
 */var h;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(h||(h={}));const Nt={debug:h.DEBUG,verbose:h.VERBOSE,info:h.INFO,warn:h.WARN,error:h.ERROR,silent:h.SILENT},vt=h.INFO,Ft={[h.DEBUG]:"log",[h.VERBOSE]:"log",[h.INFO]:"info",[h.WARN]:"warn",[h.ERROR]:"error"},Mt=(e,t,...n)=>{if(t<e.logLevel)return;const r=new Date().toISOString(),s=Ft[t];if(s)console[s](`[${r}]  ${e.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};let Pt=class{constructor(t){this.name=t,this._logLevel=vt,this._logHandler=Mt,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in h))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?Nt[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,h.DEBUG,...t),this._logHandler(this,h.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,h.VERBOSE,...t),this._logHandler(this,h.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,h.INFO,...t),this._logHandler(this,h.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,h.WARN,...t),this._logHandler(this,h.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,h.ERROR,...t),this._logHandler(this,h.ERROR,...t)}};const kt=(e,t)=>t.some(n=>e instanceof n);let he,fe;function Bt(){return he||(he=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function $t(){return fe||(fe=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Ke=new WeakMap,Q=new WeakMap,Ve=new WeakMap,U=new WeakMap,se=new WeakMap;function Ht(e){const t=new Promise((n,r)=>{const s=()=>{e.removeEventListener("success",a),e.removeEventListener("error",i)},a=()=>{n(y(e.result)),s()},i=()=>{r(e.error),s()};e.addEventListener("success",a),e.addEventListener("error",i)});return t.then(n=>{n instanceof IDBCursor&&Ke.set(n,e)}).catch(()=>{}),se.set(t,e),t}function xt(e){if(Q.has(e))return;const t=new Promise((n,r)=>{const s=()=>{e.removeEventListener("complete",a),e.removeEventListener("error",i),e.removeEventListener("abort",i)},a=()=>{n(),s()},i=()=>{r(e.error||new DOMException("AbortError","AbortError")),s()};e.addEventListener("complete",a),e.addEventListener("error",i),e.addEventListener("abort",i)});Q.set(e,t)}let Z={get(e,t,n){if(e instanceof IDBTransaction){if(t==="done")return Q.get(e);if(t==="objectStoreNames")return e.objectStoreNames||Ve.get(e);if(t==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return y(e[t])},set(e,t,n){return e[t]=n,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function Kt(e){Z=e(Z)}function Vt(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...n){const r=e.call(j(this),t,...n);return Ve.set(r,t.sort?t.sort():[t]),y(r)}:$t().includes(e)?function(...t){return e.apply(j(this),t),y(Ke.get(this))}:function(...t){return y(e.apply(j(this),t))}}function Ut(e){return typeof e=="function"?Vt(e):(e instanceof IDBTransaction&&xt(e),kt(e,Bt())?new Proxy(e,Z):e)}function y(e){if(e instanceof IDBRequest)return Ht(e);if(U.has(e))return U.get(e);const t=Ut(e);return t!==e&&(U.set(e,t),se.set(t,e)),t}const j=e=>se.get(e);function Ue(e,t,{blocked:n,upgrade:r,blocking:s,terminated:a}={}){const i=indexedDB.open(e,t),o=y(i);return r&&i.addEventListener("upgradeneeded",c=>{r(y(i.result),c.oldVersion,c.newVersion,y(i.transaction),c)}),n&&i.addEventListener("blocked",c=>n(c.oldVersion,c.newVersion,c)),o.then(c=>{a&&c.addEventListener("close",()=>a()),s&&c.addEventListener("versionchange",l=>s(l.oldVersion,l.newVersion,l))}).catch(()=>{}),o}const jt=["get","getKey","getAll","getAllKeys","count"],Gt=["put","add","delete","clear"],G=new Map;function ge(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(G.get(t))return G.get(t);const n=t.replace(/FromIndex$/,""),r=t!==n,s=Gt.includes(n);if(!(n in(r?IDBIndex:IDBObjectStore).prototype)||!(s||jt.includes(n)))return;const a=async function(i,...o){const c=this.transaction(i,s?"readwrite":"readonly");let l=c.store;return r&&(l=l.index(o.shift())),(await Promise.all([l[n](...o),s&&c.done]))[0]};return G.set(t,a),a}Kt(e=>({...e,get:(t,n,r)=>ge(t,n)||e.get(t,n,r),has:(t,n)=>!!ge(t,n)||e.has(t,n)}));/**
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
 */class Wt{constructor(t){this.container=t}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(qt(n)){const r=n.getImmediate();return`${r.library}/${r.version}`}else return null}).filter(n=>n).join(" ")}}function qt(e){const t=e.getComponent();return(t==null?void 0:t.type)==="VERSION"}const ee="@firebase/app",pe="0.10.2";/**
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
 */const O=new Pt("@firebase/app"),zt="@firebase/app-compat",Yt="@firebase/analytics-compat",Jt="@firebase/analytics",Xt="@firebase/app-check-compat",Qt="@firebase/app-check",Zt="@firebase/auth",en="@firebase/auth-compat",tn="@firebase/database",nn="@firebase/database-compat",rn="@firebase/functions",sn="@firebase/functions-compat",an="@firebase/installations",on="@firebase/installations-compat",cn="@firebase/messaging",ln="@firebase/messaging-compat",un="@firebase/performance",dn="@firebase/performance-compat",hn="@firebase/remote-config",fn="@firebase/remote-config-compat",gn="@firebase/storage",pn="@firebase/storage-compat",mn="@firebase/firestore",_n="@firebase/firestore-compat",Cn="firebase",En="10.11.1",In={[ee]:"fire-core",[zt]:"fire-core-compat",[Jt]:"fire-analytics",[Yt]:"fire-analytics-compat",[Qt]:"fire-app-check",[Xt]:"fire-app-check-compat",[Zt]:"fire-auth",[en]:"fire-auth-compat",[tn]:"fire-rtdb",[nn]:"fire-rtdb-compat",[rn]:"fire-fn",[sn]:"fire-fn-compat",[an]:"fire-iid",[on]:"fire-iid-compat",[cn]:"fire-fcm",[ln]:"fire-fcm-compat",[un]:"fire-perf",[dn]:"fire-perf-compat",[hn]:"fire-rc",[fn]:"fire-rc-compat",[gn]:"fire-gcs",[pn]:"fire-gcs-compat",[mn]:"fire-fst",[_n]:"fire-fst-compat","fire-js":"fire-js",[Cn]:"fire-js-all"};/**
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
 */const bn=new Map,wn=new Map,me=new Map;function _e(e,t){try{e.container.addComponent(t)}catch(n){O.debug(`Component ${t.name} failed to register with FirebaseApp ${e.name}`,n)}}function S(e){const t=e.name;if(me.has(t))return O.debug(`There were multiple attempts to register component ${t}.`),!1;me.set(t,e);for(const n of bn.values())_e(n,e);for(const n of wn.values())_e(n,e);return!0}function je(e,t){const n=e.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),e.container.getProvider(t)}/**
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
 */const yn={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},ae=new xe("app","Firebase",yn);/**
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
 */const Sn=En;function I(e,t,n){var r;let s=(r=In[e])!==null&&r!==void 0?r:e;n&&(s+=`-${n}`);const a=s.match(/\s|\//),i=t.match(/\s|\//);if(a||i){const o=[`Unable to register library "${s}" with version "${t}":`];a&&o.push(`library name "${s}" contains illegal characters (whitespace or "/")`),a&&i&&o.push("and"),i&&o.push(`version name "${t}" contains illegal characters (whitespace or "/")`),O.warn(o.join(" "));return}S(new X(`${s}-version`,()=>({library:s,version:t}),"VERSION"))}/**
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
 */const Tn="firebase-heartbeat-database",An=1,P="firebase-heartbeat-store";let W=null;function Ge(){return W||(W=Ue(Tn,An,{upgrade:(e,t)=>{switch(t){case 0:try{e.createObjectStore(P)}catch(n){console.warn(n)}}}}).catch(e=>{throw ae.create("idb-open",{originalErrorMessage:e.message})})),W}async function Dn(e){try{const n=(await Ge()).transaction(P),r=await n.objectStore(P).get(We(e));return await n.done,r}catch(t){if(t instanceof re)O.warn(t.message);else{const n=ae.create("idb-get",{originalErrorMessage:t==null?void 0:t.message});O.warn(n.message)}}}async function Ce(e,t){try{const r=(await Ge()).transaction(P,"readwrite");await r.objectStore(P).put(t,We(e)),await r.done}catch(n){if(n instanceof re)O.warn(n.message);else{const r=ae.create("idb-set",{originalErrorMessage:n==null?void 0:n.message});O.warn(r.message)}}}function We(e){return`${e.name}!${e.options.appId}`}/**
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
 */const On=1024,Rn=30*24*60*60*1e3;class Ln{constructor(t){this.container=t,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new vn(n),this._heartbeatsCachePromise=this._storage.read().then(r=>(this._heartbeatsCache=r,r))}async triggerHeartbeat(){var t,n;const s=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),a=Ee();if(!(((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((n=this._heartbeatsCache)===null||n===void 0?void 0:n.heartbeats)==null))&&!(this._heartbeatsCache.lastSentHeartbeatDate===a||this._heartbeatsCache.heartbeats.some(i=>i.date===a)))return this._heartbeatsCache.heartbeats.push({date:a,agent:s}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(i=>{const o=new Date(i.date).valueOf();return Date.now()-o<=Rn}),this._storage.overwrite(this._heartbeatsCache)}async getHeartbeatsHeader(){var t;if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const n=Ee(),{heartbeatsToSend:r,unsentEntries:s}=Nn(this._heartbeatsCache.heartbeats),a=$e(JSON.stringify({version:2,heartbeats:r}));return this._heartbeatsCache.lastSentHeartbeatDate=n,s.length>0?(this._heartbeatsCache.heartbeats=s,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),a}}function Ee(){return new Date().toISOString().substring(0,10)}function Nn(e,t=On){const n=[];let r=e.slice();for(const s of e){const a=n.find(i=>i.agent===s.agent);if(a){if(a.dates.push(s.date),Ie(n)>t){a.dates.pop();break}}else if(n.push({agent:s.agent,dates:[s.date]}),Ie(n)>t){n.pop();break}r=r.slice(1)}return{heartbeatsToSend:n,unsentEntries:r}}class vn{constructor(t){this.app=t,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return At()?Dt().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const n=await Dn(this.app);return n!=null&&n.heartbeats?n:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(t){var n;if(await this._canUseIndexedDBPromise){const s=await this.read();return Ce(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:s.lastSentHeartbeatDate,heartbeats:t.heartbeats})}else return}async add(t){var n;if(await this._canUseIndexedDBPromise){const s=await this.read();return Ce(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:s.lastSentHeartbeatDate,heartbeats:[...s.heartbeats,...t.heartbeats]})}else return}}function Ie(e){return $e(JSON.stringify({version:2,heartbeats:e})).length}/**
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
 */function Fn(e){S(new X("platform-logger",t=>new Wt(t),"PRIVATE")),S(new X("heartbeat",t=>new Ln(t),"PRIVATE")),I(ee,pe,e),I(ee,pe,"esm2017"),I("fire-js","")}Fn("");/**
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
 */var u;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(u||(u={}));const Mn={debug:u.DEBUG,verbose:u.VERBOSE,info:u.INFO,warn:u.WARN,error:u.ERROR,silent:u.SILENT},Pn=u.INFO,kn={[u.DEBUG]:"log",[u.VERBOSE]:"log",[u.INFO]:"info",[u.WARN]:"warn",[u.ERROR]:"error"},Bn=(e,t,...n)=>{if(t<e.logLevel)return;const r=new Date().toISOString(),s=kn[t];if(s)console[s](`[${r}]  ${e.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};class qe{constructor(t){this.name=t,this._logLevel=Pn,this._logHandler=Bn,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in u))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?Mn[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,u.DEBUG,...t),this._logHandler(this,u.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,u.VERBOSE,...t),this._logHandler(this,u.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,u.INFO,...t),this._logHandler(this,u.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,u.WARN,...t),this._logHandler(this,u.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,u.ERROR,...t),this._logHandler(this,u.ERROR,...t)}}function $n(){const e=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof e=="object"&&e.id!==void 0}function ze(){try{return typeof indexedDB=="object"}catch{return!1}}function Hn(){return new Promise((e,t)=>{try{let n=!0;const r="validate-browser-context-for-indexeddb-analytics-module",s=self.indexedDB.open(r);s.onsuccess=()=>{s.result.close(),n||self.indexedDB.deleteDatabase(r),e(!0)},s.onupgradeneeded=()=>{n=!1},s.onerror=()=>{var a;t(((a=s.error)===null||a===void 0?void 0:a.message)||"")}}catch(n){t(n)}})}function xn(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
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
 */const Kn="FirebaseError";class v extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=Kn,Object.setPrototypeOf(this,v.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,x.prototype.create)}}class x{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},s=`${this.service}/${t}`,a=this.errors[t],i=a?Vn(a,r):"Error",o=`${this.serviceName}: ${i} (${s}).`;return new v(s,o,r)}}function Vn(e,t){return e.replace(Un,(n,r)=>{const s=t[r];return s!=null?String(s):`<${r}?>`})}const Un=/\{\$([^}]+)}/g;/**
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
 */const jn=1e3,Gn=2,Wn=4*60*60*1e3,qn=.5;function te(e,t=jn,n=Gn){const r=t*Math.pow(n,e),s=Math.round(qn*r*(Math.random()-.5)*2);return Math.min(Wn,r+s)}/**
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
 */function Ye(e){return e&&e._delegate?e._delegate:e}class k{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}}const Je="@firebase/installations",ie="0.6.7";/**
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
 */const Xe=1e4,Qe=`w:${ie}`,Ze="FIS_v2",zn="https://firebaseinstallations.googleapis.com/v1",Yn=60*60*1e3,Jn="installations",Xn="Installations";/**
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
 */const Qn={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},R=new x(Jn,Xn,Qn);function et(e){return e instanceof v&&e.code.includes("request-failed")}/**
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
 */function tt({projectId:e}){return`${zn}/projects/${e}/installations`}function nt(e){return{token:e.token,requestStatus:2,expiresIn:er(e.expiresIn),creationTime:Date.now()}}async function rt(e,t){const r=(await t.json()).error;return R.create("request-failed",{requestName:e,serverCode:r.code,serverMessage:r.message,serverStatus:r.status})}function st({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function Zn(e,{refreshToken:t}){const n=st(e);return n.append("Authorization",tr(t)),n}async function at(e){const t=await e();return t.status>=500&&t.status<600?e():t}function er(e){return Number(e.replace("s","000"))}function tr(e){return`${Ze} ${e}`}/**
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
 */async function nr({appConfig:e,heartbeatServiceProvider:t},{fid:n}){const r=tt(e),s=st(e),a=t.getImmediate({optional:!0});if(a){const l=await a.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const i={fid:n,authVersion:Ze,appId:e.appId,sdkVersion:Qe},o={method:"POST",headers:s,body:JSON.stringify(i)},c=await at(()=>fetch(r,o));if(c.ok){const l=await c.json();return{fid:l.fid||n,registrationStatus:2,refreshToken:l.refreshToken,authToken:nt(l.authToken)}}else throw await rt("Create Installation",c)}/**
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
 */function it(e){return new Promise(t=>{setTimeout(t,e)})}/**
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
 */function rr(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const sr=/^[cdef][\w-]{21}$/,ne="";function ar(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const n=ir(e);return sr.test(n)?n:ne}catch{return ne}}function ir(e){return rr(e).substr(0,22)}/**
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
 */function K(e){return`${e.appName}!${e.appId}`}/**
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
 */const ot=new Map;function ct(e,t){const n=K(e);lt(n,t),or(n,t)}function lt(e,t){const n=ot.get(e);if(n)for(const r of n)r(t)}function or(e,t){const n=cr();n&&n.postMessage({key:e,fid:t}),lr()}let A=null;function cr(){return!A&&"BroadcastChannel"in self&&(A=new BroadcastChannel("[Firebase] FID Change"),A.onmessage=e=>{lt(e.data.key,e.data.fid)}),A}function lr(){ot.size===0&&A&&(A.close(),A=null)}/**
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
 */const ur="firebase-installations-database",dr=1,L="firebase-installations-store";let q=null;function oe(){return q||(q=Ue(ur,dr,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(L)}}})),q}async function H(e,t){const n=K(e),s=(await oe()).transaction(L,"readwrite"),a=s.objectStore(L),i=await a.get(n);return await a.put(t,n),await s.done,(!i||i.fid!==t.fid)&&ct(e,t.fid),t}async function ut(e){const t=K(e),r=(await oe()).transaction(L,"readwrite");await r.objectStore(L).delete(t),await r.done}async function V(e,t){const n=K(e),s=(await oe()).transaction(L,"readwrite"),a=s.objectStore(L),i=await a.get(n),o=t(i);return o===void 0?await a.delete(n):await a.put(o,n),await s.done,o&&(!i||i.fid!==o.fid)&&ct(e,o.fid),o}/**
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
 */async function ce(e){let t;const n=await V(e.appConfig,r=>{const s=hr(r),a=fr(e,s);return t=a.registrationPromise,a.installationEntry});return n.fid===ne?{installationEntry:await t}:{installationEntry:n,registrationPromise:t}}function hr(e){const t=e||{fid:ar(),registrationStatus:0};return dt(t)}function fr(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const s=Promise.reject(R.create("app-offline"));return{installationEntry:t,registrationPromise:s}}const n={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},r=gr(e,n);return{installationEntry:n,registrationPromise:r}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:pr(e)}:{installationEntry:t}}async function gr(e,t){try{const n=await nr(e,t);return H(e.appConfig,n)}catch(n){throw et(n)&&n.customData.serverCode===409?await ut(e.appConfig):await H(e.appConfig,{fid:t.fid,registrationStatus:0}),n}}async function pr(e){let t=await be(e.appConfig);for(;t.registrationStatus===1;)await it(100),t=await be(e.appConfig);if(t.registrationStatus===0){const{installationEntry:n,registrationPromise:r}=await ce(e);return r||n}return t}function be(e){return V(e,t=>{if(!t)throw R.create("installation-not-found");return dt(t)})}function dt(e){return mr(e)?{fid:e.fid,registrationStatus:0}:e}function mr(e){return e.registrationStatus===1&&e.registrationTime+Xe<Date.now()}/**
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
 */async function _r({appConfig:e,heartbeatServiceProvider:t},n){const r=Cr(e,n),s=Zn(e,n),a=t.getImmediate({optional:!0});if(a){const l=await a.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const i={installation:{sdkVersion:Qe,appId:e.appId}},o={method:"POST",headers:s,body:JSON.stringify(i)},c=await at(()=>fetch(r,o));if(c.ok){const l=await c.json();return nt(l)}else throw await rt("Generate Auth Token",c)}function Cr(e,{fid:t}){return`${tt(e)}/${t}/authTokens:generate`}/**
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
 */async function le(e,t=!1){let n;const r=await V(e.appConfig,a=>{if(!ht(a))throw R.create("not-registered");const i=a.authToken;if(!t&&br(i))return a;if(i.requestStatus===1)return n=Er(e,t),a;{if(!navigator.onLine)throw R.create("app-offline");const o=yr(a);return n=Ir(e,o),o}});return n?await n:r.authToken}async function Er(e,t){let n=await we(e.appConfig);for(;n.authToken.requestStatus===1;)await it(100),n=await we(e.appConfig);const r=n.authToken;return r.requestStatus===0?le(e,t):r}function we(e){return V(e,t=>{if(!ht(t))throw R.create("not-registered");const n=t.authToken;return Sr(n)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function Ir(e,t){try{const n=await _r(e,t),r=Object.assign(Object.assign({},t),{authToken:n});return await H(e.appConfig,r),n}catch(n){if(et(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await ut(e.appConfig);else{const r=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await H(e.appConfig,r)}throw n}}function ht(e){return e!==void 0&&e.registrationStatus===2}function br(e){return e.requestStatus===2&&!wr(e)}function wr(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+Yn}function yr(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function Sr(e){return e.requestStatus===1&&e.requestTime+Xe<Date.now()}/**
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
 */async function Tr(e){const t=e,{installationEntry:n,registrationPromise:r}=await ce(t);return r?r.catch(console.error):le(t).catch(console.error),n.fid}/**
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
 */async function Ar(e,t=!1){const n=e;return await Dr(n),(await le(n,t)).token}async function Dr(e){const{registrationPromise:t}=await ce(e);t&&await t}/**
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
 */function Or(e){if(!e||!e.options)throw z("App Configuration");if(!e.name)throw z("App Name");const t=["projectId","apiKey","appId"];for(const n of t)if(!e.options[n])throw z(n);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function z(e){return R.create("missing-app-config-values",{valueName:e})}/**
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
 */const ft="installations",Rr="installations-internal",Lr=e=>{const t=e.getProvider("app").getImmediate(),n=Or(t),r=je(t,"heartbeat");return{app:t,appConfig:n,heartbeatServiceProvider:r,_delete:()=>Promise.resolve()}},Nr=e=>{const t=e.getProvider("app").getImmediate(),n=je(t,ft).getImmediate();return{getId:()=>Tr(n),getToken:s=>Ar(n,s)}};function vr(){S(new k(ft,Lr,"PUBLIC")),S(new k(Rr,Nr,"PRIVATE"))}vr();I(Je,ie);I(Je,ie,"esm2017");/**
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
 */const ye="analytics",Fr="firebase_id",Mr="origin",Pr=60*1e3,kr="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",ue="https://www.googletagmanager.com/gtag/js";/**
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
 */const _=new qe("@firebase/analytics");/**
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
 */const Br={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-intialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},C=new x("analytics","Analytics",Br);/**
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
 */function $r(e){if(!e.startsWith(ue)){const t=C.create("invalid-gtag-resource",{gtagURL:e});return _.warn(t.message),""}return e}function gt(e){return Promise.all(e.map(t=>t.catch(n=>n)))}function Hr(e,t){let n;return window.trustedTypes&&(n=window.trustedTypes.createPolicy(e,t)),n}function xr(e,t){const n=Hr("firebase-js-sdk-policy",{createScriptURL:$r}),r=document.createElement("script"),s=`${ue}?l=${e}&id=${t}`;r.src=n?n==null?void 0:n.createScriptURL(s):s,r.async=!0,document.head.appendChild(r)}function Kr(e){let t=[];return Array.isArray(window[e])?t=window[e]:window[e]=t,t}async function Vr(e,t,n,r,s,a){const i=r[s];try{if(i)await t[i];else{const c=(await gt(n)).find(l=>l.measurementId===s);c&&await t[c.appId]}}catch(o){_.error(o)}e("config",s,a)}async function Ur(e,t,n,r,s){try{let a=[];if(s&&s.send_to){let i=s.send_to;Array.isArray(i)||(i=[i]);const o=await gt(n);for(const c of i){const l=o.find(f=>f.measurementId===c),d=l&&t[l.appId];if(d)a.push(d);else{a=[];break}}}a.length===0&&(a=Object.values(t)),await Promise.all(a),e("event",r,s||{})}catch(a){_.error(a)}}function jr(e,t,n,r){async function s(a,...i){try{if(a==="event"){const[o,c]=i;await Ur(e,t,n,o,c)}else if(a==="config"){const[o,c]=i;await Vr(e,t,n,r,o,c)}else if(a==="consent"){const[o]=i;e("consent","update",o)}else if(a==="get"){const[o,c,l]=i;e("get",o,c,l)}else if(a==="set"){const[o]=i;e("set",o)}else e(a,...i)}catch(o){_.error(o)}}return s}function Gr(e,t,n,r,s){let a=function(...i){window[r].push(arguments)};return window[s]&&typeof window[s]=="function"&&(a=window[s]),window[s]=jr(a,e,t,n),{gtagCore:a,wrappedGtag:window[s]}}function Wr(e){const t=window.document.getElementsByTagName("script");for(const n of Object.values(t))if(n.src&&n.src.includes(ue)&&n.src.includes(e))return n;return null}/**
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
 */const qr=30,zr=1e3;class Yr{constructor(t={},n=zr){this.throttleMetadata=t,this.intervalMillis=n}getThrottleMetadata(t){return this.throttleMetadata[t]}setThrottleMetadata(t,n){this.throttleMetadata[t]=n}deleteThrottleMetadata(t){delete this.throttleMetadata[t]}}const pt=new Yr;function Jr(e){return new Headers({Accept:"application/json","x-goog-api-key":e})}async function Xr(e){var t;const{appId:n,apiKey:r}=e,s={method:"GET",headers:Jr(r)},a=kr.replace("{app-id}",n),i=await fetch(a,s);if(i.status!==200&&i.status!==304){let o="";try{const c=await i.json();!((t=c.error)===null||t===void 0)&&t.message&&(o=c.error.message)}catch{}throw C.create("config-fetch-failed",{httpStatus:i.status,responseMessage:o})}return i.json()}async function Qr(e,t=pt,n){const{appId:r,apiKey:s,measurementId:a}=e.options;if(!r)throw C.create("no-app-id");if(!s){if(a)return{measurementId:a,appId:r};throw C.create("no-api-key")}const i=t.getThrottleMetadata(r)||{backoffCount:0,throttleEndTimeMillis:Date.now()},o=new ts;return setTimeout(async()=>{o.abort()},n!==void 0?n:Pr),mt({appId:r,apiKey:s,measurementId:a},i,o,t)}async function mt(e,{throttleEndTimeMillis:t,backoffCount:n},r,s=pt){var a;const{appId:i,measurementId:o}=e;try{await Zr(r,t)}catch(c){if(o)return _.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${c==null?void 0:c.message}]`),{appId:i,measurementId:o};throw c}try{const c=await Xr(e);return s.deleteThrottleMetadata(i),c}catch(c){const l=c;if(!es(l)){if(s.deleteThrottleMetadata(i),o)return _.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:i,measurementId:o};throw c}const d=Number((a=l==null?void 0:l.customData)===null||a===void 0?void 0:a.httpStatus)===503?te(n,s.intervalMillis,qr):te(n,s.intervalMillis),f={throttleEndTimeMillis:Date.now()+d,backoffCount:n+1};return s.setThrottleMetadata(i,f),_.debug(`Calling attemptFetch again in ${d} millis`),mt(e,f,r,s)}}function Zr(e,t){return new Promise((n,r)=>{const s=Math.max(t-Date.now(),0),a=setTimeout(n,s);e.addEventListener(()=>{clearTimeout(a),r(C.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function es(e){if(!(e instanceof v)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class ts{constructor(){this.listeners=[]}addEventListener(t){this.listeners.push(t)}abort(){this.listeners.forEach(t=>t())}}async function ns(e,t,n,r,s){if(s&&s.global){e("event",n,r);return}else{const a=await t,i=Object.assign(Object.assign({},r),{send_to:a});e("event",n,i)}}/**
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
 */async function rs(){if(ze())try{await Hn()}catch(e){return _.warn(C.create("indexeddb-unavailable",{errorInfo:e==null?void 0:e.toString()}).message),!1}else return _.warn(C.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function ss(e,t,n,r,s,a,i){var o;const c=Qr(e);c.then(p=>{n[p.measurementId]=p.appId,e.options.measurementId&&p.measurementId!==e.options.measurementId&&_.warn(`The measurement ID in the local Firebase config (${e.options.measurementId}) does not match the measurement ID fetched from the server (${p.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(p=>_.error(p)),t.push(c);const l=rs().then(p=>{if(p)return r.getId()}),[d,f]=await Promise.all([c,l]);Wr(a)||xr(a,d.measurementId),s("js",new Date);const g=(o=i==null?void 0:i.config)!==null&&o!==void 0?o:{};return g[Mr]="firebase",g.update=!0,f!=null&&(g[Fr]=f),s("config",d.measurementId,g),d.measurementId}/**
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
 */class as{constructor(t){this.app=t}_delete(){return delete M[this.app.options.appId],Promise.resolve()}}let M={},Se=[];const Te={};let Y="dataLayer",is="gtag",Ae,_t,De=!1;function os(){const e=[];if($n()&&e.push("This is a browser extension environment."),xn()||e.push("Cookies are not available."),e.length>0){const t=e.map((r,s)=>`(${s+1}) ${r}`).join(" "),n=C.create("invalid-analytics-context",{errorInfo:t});_.warn(n.message)}}function cs(e,t,n){os();const r=e.options.appId;if(!r)throw C.create("no-app-id");if(!e.options.apiKey)if(e.options.measurementId)_.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${e.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw C.create("no-api-key");if(M[r]!=null)throw C.create("already-exists",{id:r});if(!De){Kr(Y);const{wrappedGtag:a,gtagCore:i}=Gr(M,Se,Te,Y,is);_t=a,Ae=i,De=!0}return M[r]=ss(e,Se,Te,t,Ae,Y,n),new as(e)}function ls(e,t,n,r){e=Ye(e),ns(_t,M[e.app.options.appId],t,n,r).catch(s=>_.error(s))}const Oe="@firebase/analytics",Re="0.10.3";function us(){S(new k(ye,(t,{options:n})=>{const r=t.getProvider("app").getImmediate(),s=t.getProvider("installations-internal").getImmediate();return cs(r,s,n)},"PUBLIC")),S(new k("analytics-internal",e,"PRIVATE")),I(Oe,Re),I(Oe,Re,"esm2017");function e(t){try{const n=t.getProvider(ye).getImmediate();return{logEvent:(r,s,a)=>ls(n,r,s,a)}}catch(n){throw C.create("interop-component-reg-failed",{reason:n})}}}us();const J="@firebase/remote-config",Le="0.4.7";/**
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
 */const ds="remote-config";/**
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
 */const hs={"registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser"},m=new x("remoteconfig","Remote Config",hs);function fs(e){const t=Ye(e);return t._initializePromise||(t._initializePromise=t._storageCache.loadFromStorage().then(()=>{t._isInitializationComplete=!0})),t._initializePromise}/**
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
 */class gs{constructor(t,n,r,s){this.client=t,this.storage=n,this.storageCache=r,this.logger=s}isCachedDataFresh(t,n){if(!n)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const r=Date.now()-n,s=r<=t;return this.logger.debug(`Config fetch cache check. Cache age millis: ${r}. Cache max age millis (minimumFetchIntervalMillis setting): ${t}. Is cache hit: ${s}.`),s}async fetch(t){const[n,r]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(r&&this.isCachedDataFresh(t.cacheMaxAgeMillis,n))return r;t.eTag=r&&r.eTag;const s=await this.client.fetch(t),a=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return s.status===200&&a.push(this.storage.setLastSuccessfulFetchResponse(s)),await Promise.all(a),s}}/**
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
 */function ps(e=navigator){return e.languages&&e.languages[0]||e.language}/**
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
 */class ms{constructor(t,n,r,s,a,i){this.firebaseInstallations=t,this.sdkVersion=n,this.namespace=r,this.projectId=s,this.apiKey=a,this.appId=i}async fetch(t){const[n,r]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),a=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":t.eTag||"*"},o={sdk_version:this.sdkVersion,app_instance_id:n,app_instance_id_token:r,app_id:this.appId,language_code:ps()},c={method:"POST",headers:i,body:JSON.stringify(o)},l=fetch(a,c),d=new Promise((E,w)=>{t.signal.addEventListener(()=>{const de=new Error("The operation was aborted.");de.name="AbortError",w(de)})});let f;try{await Promise.race([l,d]),f=await l}catch(E){let w="fetch-client-network";throw(E==null?void 0:E.name)==="AbortError"&&(w="fetch-timeout"),m.create(w,{originalErrorMessage:E==null?void 0:E.message})}let g=f.status;const p=f.headers.get("ETag")||void 0;let b,F;if(f.status===200){let E;try{E=await f.json()}catch(w){throw m.create("fetch-client-parse",{originalErrorMessage:w==null?void 0:w.message})}b=E.entries,F=E.state}if(F==="INSTANCE_STATE_UNSPECIFIED"?g=500:F==="NO_CHANGE"?g=304:(F==="NO_TEMPLATE"||F==="EMPTY_CONFIG")&&(b={}),g!==304&&g!==200)throw m.create("fetch-status",{httpStatus:g});return{status:g,eTag:p,config:b}}}/**
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
 */function _s(e,t){return new Promise((n,r)=>{const s=Math.max(t-Date.now(),0),a=setTimeout(n,s);e.addEventListener(()=>{clearTimeout(a),r(m.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function Cs(e){if(!(e instanceof v)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class Es{constructor(t,n){this.client=t,this.storage=n}async fetch(t){const n=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(t,n)}async attemptFetch(t,{throttleEndTimeMillis:n,backoffCount:r}){await _s(t.signal,n);try{const s=await this.client.fetch(t);return await this.storage.deleteThrottleMetadata(),s}catch(s){if(!Cs(s))throw s;const a={throttleEndTimeMillis:Date.now()+te(r),backoffCount:r+1};return await this.storage.setThrottleMetadata(a),this.attemptFetch(t,a)}}}/**
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
 */const Is=60*1e3,bs=12*60*60*1e3;class ws{constructor(t,n,r,s,a){this.app=t,this._client=n,this._storageCache=r,this._storage=s,this._logger=a,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:Is,minimumFetchIntervalMillis:bs},this.defaultConfig={}}get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}}/**
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
 */function $(e,t){const n=e.target.error||void 0;return m.create(t,{originalErrorMessage:n&&(n==null?void 0:n.message)})}const T="app_namespace_store",ys="firebase_remote_config",Ss=1;function Ts(){return new Promise((e,t)=>{try{const n=indexedDB.open(ys,Ss);n.onerror=r=>{t($(r,"storage-open"))},n.onsuccess=r=>{e(r.target.result)},n.onupgradeneeded=r=>{const s=r.target.result;switch(r.oldVersion){case 0:s.createObjectStore(T,{keyPath:"compositeKey"})}}}catch(n){t(m.create("storage-open",{originalErrorMessage:n==null?void 0:n.message}))}})}class As{constructor(t,n,r,s=Ts()){this.appId=t,this.appName=n,this.namespace=r,this.openDbPromise=s}getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(t){return this.set("last_fetch_status",t)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(t){return this.set("last_successful_fetch_timestamp_millis",t)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(t){return this.set("last_successful_fetch_response",t)}getActiveConfig(){return this.get("active_config")}setActiveConfig(t){return this.set("active_config",t)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(t){return this.set("active_config_etag",t)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(t){return this.set("throttle_metadata",t)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}async get(t){const n=await this.openDbPromise;return new Promise((r,s)=>{const i=n.transaction([T],"readonly").objectStore(T),o=this.createCompositeKey(t);try{const c=i.get(o);c.onerror=l=>{s($(l,"storage-get"))},c.onsuccess=l=>{const d=l.target.result;r(d?d.value:void 0)}}catch(c){s(m.create("storage-get",{originalErrorMessage:c==null?void 0:c.message}))}})}async set(t,n){const r=await this.openDbPromise;return new Promise((s,a)=>{const o=r.transaction([T],"readwrite").objectStore(T),c=this.createCompositeKey(t);try{const l=o.put({compositeKey:c,value:n});l.onerror=d=>{a($(d,"storage-set"))},l.onsuccess=()=>{s()}}catch(l){a(m.create("storage-set",{originalErrorMessage:l==null?void 0:l.message}))}})}async delete(t){const n=await this.openDbPromise;return new Promise((r,s)=>{const i=n.transaction([T],"readwrite").objectStore(T),o=this.createCompositeKey(t);try{const c=i.delete(o);c.onerror=l=>{s($(l,"storage-delete"))},c.onsuccess=()=>{r()}}catch(c){s(m.create("storage-delete",{originalErrorMessage:c==null?void 0:c.message}))}})}createCompositeKey(t){return[this.appId,this.appName,this.namespace,t].join()}}/**
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
 */class Ds{constructor(t){this.storage=t}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}async loadFromStorage(){const t=this.storage.getLastFetchStatus(),n=this.storage.getLastSuccessfulFetchTimestampMillis(),r=this.storage.getActiveConfig(),s=await t;s&&(this.lastFetchStatus=s);const a=await n;a&&(this.lastSuccessfulFetchTimestampMillis=a);const i=await r;i&&(this.activeConfig=i)}setLastFetchStatus(t){return this.lastFetchStatus=t,this.storage.setLastFetchStatus(t)}setLastSuccessfulFetchTimestampMillis(t){return this.lastSuccessfulFetchTimestampMillis=t,this.storage.setLastSuccessfulFetchTimestampMillis(t)}setActiveConfig(t){return this.activeConfig=t,this.storage.setActiveConfig(t)}}/**
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
 */function Os(){S(new k(ds,e,"PUBLIC").setMultipleInstances(!0)),I(J,Le),I(J,Le,"esm2017");function e(t,{instanceIdentifier:n}){const r=t.getProvider("app").getImmediate(),s=t.getProvider("installations-internal").getImmediate();if(typeof window>"u")throw m.create("registration-window");if(!ze())throw m.create("indexed-db-unavailable");const{projectId:a,apiKey:i,appId:o}=r.options;if(!a)throw m.create("registration-project-id");if(!i)throw m.create("registration-api-key");if(!o)throw m.create("registration-app-id");n=n||"firebase";const c=new As(o,r.name,n),l=new Ds(c),d=new qe(J);d.logLevel=u.ERROR;const f=new ms(s,Sn,n,a,i,o),g=new Es(f,c),p=new gs(g,c,l,d),b=new ws(r,p,l,c,d);return fs(b),b}}Os();const Ct=N.createContext({});function Ne({children:e}){const[t,n]=N.useState();return D.jsx(Ct.Provider,{value:{logEvent:t,setLogEvent:n},children:e})}try{Ne.displayName="AnalyticsContextProvider",Ne.__docgenInfo={description:"",displayName:"AnalyticsContextProvider",props:{}}}catch{}const Rs=N.createContext({remoteConfig:null,setRemoteConfig:null,remoteConfigData:null,setRemoteConfigData:null});function ve({children:e}){const[t,n]=N.useState(null),[r,s]=N.useState(null);return D.jsx(Rs.Provider,{value:{remoteConfig:t,setRemoteConfig:n,remoteConfigData:r,setRemoteConfigData:s},children:e})}try{ve.displayName="RemoteContextProvider",ve.__docgenInfo={description:"",displayName:"RemoteContextProvider",props:{}}}catch{}function Ls(){return N.useContext(Ct)}var Et=(e=>(e.CLICKED_BOOKING="hasClickedBooking",e.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",e.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",e.CLICKED_CONSULT_CGU="hasClickedConsultCGU",e.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",e.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",e.CLICKED_CREATE_VENUE="hasClickedCreateVenue",e.CLICKED_ADD_BANK_INFORMATIONS="hasClickedAddBankInformation",e.CLICKED_NO_PRICING_POINT_SELECTED_YET="hasClickedNoPricingPointSelectedYet",e.CLICKED_ADD_VENUE_IN_OFFERER="hasClickedAddVenueInOfferer",e.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",e.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",e.CLICKED_SAVE_VENUE="hasClickedSaveVenue",e.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",e.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",e.CLICKED_DOWNLOAD_BOOKINGS_OTHER_FORMAT="hasClickedDownloadBookingOtherFormat",e.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",e.CLICKED_EDIT_PROFILE="hasClickedEditProfile",e.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ="hasClickedHomeStatsPendingOffersFaq",e.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",e.CLICKED_HELP_CENTER="hasClickedHelpCenter",e.CLICKED_HOME="hasClickedHome",e.CLICKED_LOGOUT="hasClickedLogout",e.CLICKED_MODIFY_OFFERER="hasClickedModifyOfferer",e.CLICKED_OFFER="hasClickedOffer",e.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",e.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",e.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",e.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK="hasClickedPartnerBlockPreviewVenueLink",e.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK="hasClickedPartnerBlockCopyVenueLink",e.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK="hasClickedPartnerBlockDmsApplicationLink",e.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK="hasClickedPartnerBlockCollectiveHelpLink",e.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",e.CLICKED_PRO="hasClickedPro",e.CLICKED_REIMBURSEMENT="hasClickedReimbursement",e.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",e.CLICKED_STATS="hasClickedOffererStats",e.CLICKED_TICKET="hasClickedTicket",e.CLICKED_TOGGLE_HIDE_OFFERER_NAME="hasClickedToggleHideOffererName",e.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",e.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",e.CLICKED_HELP_LINK="hasClickedHelpLink",e.CLICKED_RESET_FILTERS="hasClickedResetFilter",e.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",e.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",e.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",e.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",e.FIRST_LOGIN="firstLogin",e.PAGE_VIEW="page_view",e.SIGNUP_FORM_ABORT="signupFormAbort",e.SIGNUP_FORM_SUCCESS="signupFormSuccess",e.TUTO_PAGE_VIEW="tutoPageView",e.DELETE_DRAFT_OFFER="DeleteDraftOffer",e.CLICKED_NO_VENUE="hasClickedNoVenue",e.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",e.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",e.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",e.CLICKED_ADD_IMAGE="hasClickedAddImage",e.CLICKED_DELETE_STOCK="hasClickedDeleteStock",e.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",e.CLICKED_DOWNLOAD_OFFER_BOOKINGS="hasDownloadedBookings",e))(Et||{});const Fe={"help-link":"_help-link_1c4y5_2","help-link-text":"_help-link-text_1c4y5_10"},Ns=()=>{const{logEvent:e}=Ls();return D.jsxs("a",{onClick:()=>e==null?void 0:e(Et.CLICKED_HELP_LINK,{from:location.pathname}),className:Fe["help-link"],href:"https://aide.passculture.app/hc/fr/articles/4411991940369--Acteurs-culturels-Comment-poster-une-offre-%C3%A0-destination-d-un-groupe-scolaire-",rel:"noreferrer",target:"_blank",children:[D.jsx(bt,{src:It,alt:"",width:"42"}),D.jsx("span",{className:Fe["help-link-text"],children:"Aide"})]})},Ks={title:"components/HelpLink",component:Ns,decorators:[e=>D.jsx("div",{style:{width:500,height:500},children:D.jsx(e,{})})]},B={};var Me,Pe,ke;B.parameters={...B.parameters,docs:{...(Me=B.parameters)==null?void 0:Me.docs,source:{originalSource:"{}",...(ke=(Pe=B.parameters)==null?void 0:Pe.docs)==null?void 0:ke.source}}};const Vs=["Default"];export{B as Default,Vs as __namedExportsOrder,Ks as default};
