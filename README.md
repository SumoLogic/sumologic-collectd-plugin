# Collectd Sumo Logic Output Plugin

This is a plugin for [collectd](https://collectd.org/).
It is fully free and fully open source. The license is Apache 2.0, meaning you are pretty much free to use it however you want in whatever way.

## Getting Started

### 1. Install collectd on you matchine

### 2. Install Sumo Logic output plugin into collectd

### 3. Setup Sumo Logic output plugin configurations
Sumo Logic output plugin supports following prarmeters. 
#### Required parameter
The paramer below is required and must be specified in the module config. 

|Name|Description|Type|Required|
|:---|:---|:---|:---|
|URL|The URL to send logs to. This should be given when creating a Metrics HTTP Source on Sumo Logic web app. See [Metrics Http Source](https://not_ready_yet)|String|True|

#### Basic parameters
The paramers below are not strictly required. It is recommended to set these parameters as they prove to be extremely useful to categorize your metrics and search by them.

|Name|Description|Type|Required|
|:---|:---|:---|:---|
|SourceName|Name of the metrics source. `_sourceName` can be used to search metrics from this source.|String|False|
|HostName|Name of metrics host. `_hostName` can be used to search metrics from this host.|String|False|
|SourceCategory|Category of the collected metrics. `_sourceCategory` can be used to search metrics from this category.|String|False|
|Dimensions|Key value pairs that contribute to identifying a metric. Collectd data have intrinsic dimensions with keys as `host`, `plugin`, `plugin_instance`, `type`, `type_instance`, `ds_name`, `ds_type`. The Additional dimensions specified here can help separating metrics collected from this collectd instance with metircs collected from other collectd instances.|Srings in the format of `key1` `val1` `key2` `val2` ... |False|
|Metadata|Key value pairs that do not contribute to identifying a metric. `Metadata` are primarily used to assist in searching metrics. Collectd data may have internal metadata. The additional metadata specified here can be used to enrich the existing metadata set.|Srings in the format of `key1` `val1` `key2` `val2` ...|False|

#### Advanced parameters
The parameters below are for advanced users. They have reasonal defaults. Normal users do not have to update these values.  

|Name|Description|Type|Default|Required|
|:---|:---|:---|:---|:---|
|MaxBatchSize|x|x|x|x|
|MaxBatchInterval|x|x|x|x|
|HttpPostInterval|x|x|x|x|
|RetryInitialDelay|x|x|x|x|
|RetryMaxAttempts|x|x|x|x|
|RetryMaxDelay|x|x|x|x|
|RetryBackOff|x|x|x|x|
|RetryJitterMin|x|x|x|x|
|RetryJitterMax|x|x|x|x|
|MaxRequestsToBuffer|x|x|x|x|

#### Restrictions

### 4. Start sending metrics

### 5. View metrics in Sumo Logic web app

### Furthermore
